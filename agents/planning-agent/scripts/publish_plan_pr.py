#!/usr/bin/env python3
"""Publish a planning agent PR with hosted plan page and external audio.

The agent-facing contract is JSON in, JSON out. The planning agent provides fields;
this script owns command checks, TTS generation, Blossom upload, gh-pages output,
PR creation/update, and follow-up comments.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


INSTALL_URLS = {
    "git": "https://git-scm.com/downloads",
    "gh": "https://cli.github.com/",
    "ffmpeg": "https://ffmpeg.org/download.html",
    "nak": "https://github.com/fiatjaf/nak",
    "say": "https://support.apple.com/guide/terminal/make-your-mac-speak-apd33d4c4f3a/mac",
    "espeak-ng": "https://github.com/espeak-ng/espeak-ng",
}

DEFAULT_BLOSSOM_SERVER = "https://blossom.primal.net"

BOUNDARY_STATUS_LABELS = {
    "new": "New",
    "changed": "Changed",
    "removed": "Removed",
    "existing": "Existing",
    "external": "External",
    "risk": "Risk",
}

BOUNDARY_STATUS_ORDER = ["new", "changed", "removed", "existing", "external", "risk"]


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    input_text: str | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def respond(payload: dict[str, Any], code: int = 0) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(code)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def refresh_path() -> None:
    home = Path.home()
    extras = [
        home / "go" / "bin",
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
    ]
    current = os.environ.get("PATH", "")
    for item in extras:
        value = str(item)
        if item.exists() and value not in current.split(os.pathsep):
            current = value + os.pathsep + current
    os.environ["PATH"] = current


def install_with_package_manager(command: str) -> None:
    system = platform.system()
    package = {
        "espeak-ng": "espeak-ng",
    }.get(command, command)

    attempts: list[list[str]] = []
    if system == "Darwin":
        if command == "say":
            return
        if shutil.which("brew"):
            attempts.append(["brew", "install", package])
        if command == "nak" and shutil.which("go"):
            attempts.append(["go", "install", "github.com/fiatjaf/nak@latest"])
    elif system == "Linux":
        prefix = [] if os.geteuid() == 0 else ["sudo"]
        if shutil.which("apt-get"):
            attempts.append(prefix + ["apt-get", "update"])
            attempts.append(prefix + ["apt-get", "install", "-y", package])
        elif shutil.which("dnf"):
            attempts.append(prefix + ["dnf", "install", "-y", package])
        elif shutil.which("pacman"):
            attempts.append(prefix + ["pacman", "-Sy", "--noconfirm", package])
        if command == "nak" and shutil.which("go"):
            attempts.append(["go", "install", "github.com/fiatjaf/nak@latest"])

    for attempt in attempts:
        try:
            run(attempt, check=False, timeout=600)
        except Exception:
            pass
        refresh_path()
        if command_exists(command):
            return


def ensure_commands(no_install: bool = False) -> None:
    refresh_path()
    required = ["git", "gh", "ffmpeg", "nak"]
    if platform.system() == "Darwin":
        required.append("say")
    else:
        required.append("espeak-ng")

    missing = [cmd for cmd in required if not command_exists(cmd)]
    if missing and not no_install:
        for command in missing:
            install_with_package_manager(command)
        refresh_path()
        missing = [cmd for cmd in required if not command_exists(cmd)]

    if missing:
        respond(
            {
                "ok": False,
                "error": "missing_commands",
                "missing": [
                    {
                        "command": command,
                        "install_url": INSTALL_URLS.get(command),
                        "message": f"{command} is not available. Please install it from {INSTALL_URLS.get(command, 'the upstream project')} and rerun the script.",
                    }
                    for command in missing
                ],
            },
            code=2,
        )


def load_payload(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        respond({"ok": False, "error": "invalid_json", "message": str(exc)}, code=2)
    if not isinstance(data, dict):
        respond({"ok": False, "error": "invalid_payload", "message": "Payload must be a JSON object."}, code=2)
    return data


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "plan"


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def compact_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def split_label(text: str) -> tuple[str, str]:
    if ":" not in text:
        return "", text
    label, rest = text.split(":", 1)
    label = compact_text(label)
    rest = compact_text(rest)
    if 0 < len(label.split()) <= 5 and len(label) <= 48 and rest:
        return label, rest
    return "", text


def normalize_plan_point(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        label = compact_text(item.get("label") or item.get("title") or item.get("heading") or "")
        text = compact_text(item.get("text") or item.get("body") or item.get("summary") or item.get("description") or "")
        if not text and label:
            text = label
            label = ""
        return {
            "label": label,
            "text": text,
            "highlight": bool(item.get("highlight") or item.get("important") or item.get("emphasis")),
        }
    text = compact_text(item)
    label, rest = split_label(text)
    return {"label": label, "text": rest, "highlight": False}


def split_high_level_text(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and all(re.match(r"^([-*]|\d+[.)])\s+", line) for line in lines):
        return [re.sub(r"^([-*]|\d+[.)])\s+", "", line).strip() for line in lines]

    paragraphs = [line.strip() for line in re.split(r"\n\s*\n", text) if line.strip()]
    if len(paragraphs) > 1:
        return paragraphs

    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if item.strip()]
    if len(sentences) > 1 and len(text.split()) > 35:
        return sentences

    return [text] if text else []


def high_level_points(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("high_level_points", payload["high_level_plan"])
    if isinstance(value, list):
        points = [normalize_plan_point(item) for item in value]
    else:
        points = [normalize_plan_point(item) for item in split_high_level_text(str(value).strip())]
    return [point for point in points if point["text"]]


def markdown_plan_points(points: list[dict[str, Any]]) -> str:
    if not points:
        return "- None."
    rendered = []
    for point in points:
        text = point["text"]
        if point["label"]:
            text = f"**{point['label']}:** {text}"
        if point["highlight"]:
            text = f"**Important:** {text}"
        rendered.append(f"- {text}")
    return "\n".join(rendered)


def html_plan_points(points: list[dict[str, Any]]) -> str:
    if not points:
        return "<ul><li>None.</li></ul>"
    items = []
    for point in points:
        classes = "plan-point is-highlighted" if point["highlight"] else "plan-point"
        label = f"<strong>{html.escape(point['label'])}</strong> " if point["label"] else ""
        items.append(f'<li class="{classes}">{label}{html.escape(point["text"])}</li>')
    return '<ul class="plan-points">' + "".join(items) + "</ul>"


def normalize_status(value: Any) -> str:
    status = compact_text(value or "changed").lower().replace(" ", "-").replace("_", "-")
    aliases = {
        "add": "new",
        "added": "new",
        "create": "new",
        "created": "new",
        "modify": "changed",
        "modified": "changed",
        "change": "changed",
        "update": "changed",
        "updated": "changed",
        "delete": "removed",
        "deleted": "removed",
        "remove": "removed",
        "removed": "removed",
        "unchanged": "existing",
        "current": "existing",
        "outside": "external",
    }
    status = aliases.get(status, status)
    return status if status in BOUNDARY_STATUS_LABELS else "changed"


def normalize_boundary_change(item: Any) -> dict[str, str]:
    if isinstance(item, dict):
        status = normalize_status(item.get("status") or item.get("kind") or item.get("type"))
        label = compact_text(item.get("label") or item.get("title") or item.get("name") or BOUNDARY_STATUS_LABELS[status])
        description = compact_text(item.get("description") or item.get("text") or item.get("body") or "")
        return {"status": status, "label": label, "description": description}
    text = compact_text(item)
    label, description = split_label(text)
    return {"status": "changed", "label": label or "Change", "description": description}


def normalize_boundary_changes(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    changes = [normalize_boundary_change(item) for item in items]
    return [change for change in changes if change["label"] or change["description"]]


def normalize_boundary_views(raw: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, str]]:
    views: list[dict[str, str]] = []
    for key, label in (("current_diagram_mermaid", "Current"), ("proposed_diagram_mermaid", "Proposed")):
        diagram = compact_text(raw.get(key) or "")
        if diagram:
            views.append({"label": label, "diagram_mermaid": str(raw[key]).strip()})

    for item in raw.get("views") or []:
        if not isinstance(item, dict):
            continue
        diagram = str(item.get("diagram_mermaid") or item.get("mermaid") or "").strip()
        if diagram:
            views.append(
                {
                    "label": compact_text(item.get("label") or item.get("title") or f"View {len(views) + 1}"),
                    "diagram_mermaid": diagram,
                }
            )

    primary = str(raw.get("diagram_mermaid") or payload.get("diagram_mermaid") or "").strip()
    if primary and not views:
        views.append({"label": compact_text(raw.get("label") or "Proposed"), "diagram_mermaid": primary})
    return views


def normalize_boundary_graph(raw_graph: Any) -> dict[str, Any] | None:
    if not isinstance(raw_graph, dict):
        return None
    raw_nodes = raw_graph.get("nodes")
    raw_links = raw_graph.get("links") or raw_graph.get("edges")
    if not isinstance(raw_nodes, list) or not isinstance(raw_links, list):
        return None

    nodes = []
    for item in raw_nodes:
        if isinstance(item, dict):
            node_id = compact_text(item.get("id") or item.get("name") or item.get("label") or "")
            if not node_id:
                continue
            nodes.append(
                {
                    "id": node_id,
                    "label": compact_text(item.get("label") or item.get("name") or node_id),
                    "status": normalize_status(item.get("status")),
                }
            )
        else:
            node_id = compact_text(item)
            if node_id:
                nodes.append({"id": node_id, "label": node_id, "status": "existing"})

    links = []
    node_ids = {node["id"] for node in nodes}
    for item in raw_links:
        if not isinstance(item, dict):
            continue
        source = compact_text(item.get("source") or item.get("from") or "")
        target = compact_text(item.get("target") or item.get("to") or "")
        if source not in node_ids or target not in node_ids:
            continue
        links.append(
            {
                "source": source,
                "target": target,
                "label": compact_text(item.get("label") or item.get("name") or ""),
                "status": normalize_status(item.get("status")),
            }
        )

    if not nodes or not links:
        return None
    return {
        "label": compact_text(raw_graph.get("label") or raw_graph.get("title") or "Interactive graph"),
        "nodes": nodes,
        "links": links,
    }


def boundary_spec(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("boundary_visualization") or payload.get("boundary_visual") or {}
    if not isinstance(raw, dict):
        raw = {}
    graph = normalize_boundary_graph(raw.get("graph") or raw.get("d3_graph") or payload.get("boundary_graph"))
    changes = normalize_boundary_changes(raw.get("changes", payload.get("boundary_changes")))
    views = normalize_boundary_views(raw, payload)
    description = compact_text(raw.get("description") or raw.get("summary") or payload.get("boundary_summary") or "")

    statuses = {change["status"] for change in changes}
    if graph:
        statuses.update(node["status"] for node in graph["nodes"])
        statuses.update(link["status"] for link in graph["links"])
    ordered_statuses = [status for status in BOUNDARY_STATUS_ORDER if status in statuses]

    return {
        "title": compact_text(raw.get("title") or "Boundary Changes"),
        "description": description,
        "views": views,
        "graph": graph,
        "changes": changes,
        "statuses": ordered_statuses,
        "has_content": bool(views or graph or changes or description),
    }


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    aliases = {
        "possible_rule_loosening": payload.get("possible_rule_loosening", payload.get("rule_adr_violation")),
    }
    for key, value in aliases.items():
        if key not in payload and value is not None:
            payload[key] = value

    required = [
        "title",
        "high_level_plan",
        "tts_friendly_version",
        "rules_adr_check",
        "possible_rule_loosening",
        "possible_rule_tightening",
        "alternatives_considered",
        "certainty_percent",
        "decision",
        "detailed_plan",
    ]
    missing = [key for key in required if payload.get(key) in (None, "")]
    if missing:
        respond({"ok": False, "error": "missing_payload_fields", "missing": missing}, code=2)

    try:
        certainty = int(payload["certainty_percent"])
    except Exception:
        respond({"ok": False, "error": "invalid_certainty_percent", "message": "certainty_percent must be an integer."}, code=2)
    if not 0 <= certainty <= 100:
        respond({"ok": False, "error": "invalid_certainty_percent", "message": "certainty_percent must be between 0 and 100."}, code=2)
    payload["certainty_percent"] = certainty

    decision = str(payload["decision"]).lower().strip()
    if decision not in {"ready", "pause"}:
        respond({"ok": False, "error": "invalid_decision", "message": "decision must be 'ready' or 'pause'."}, code=2)
    payload["decision"] = decision

    high_level_words = " ".join(point["text"] for point in high_level_points(payload)).split()
    if len(high_level_words) > 450:
        respond(
            {
                "ok": False,
                "error": "high_level_plan_too_long",
                "message": f"high_level_plan is {len(high_level_words)} words; maximum is 450.",
            },
            code=2,
        )

    payload["slug"] = slugify(str(payload.get("slug") or payload["title"]))
    payload["base_branch"] = str(payload.get("base_branch") or "main")
    payload["branch"] = str(payload.get("branch") or f"plan/{payload['slug']}")
    payload["pr_title"] = str(payload.get("pr_title") or f"Plan: {payload['title']}")
    default_summary = " ".join(point["text"] for point in high_level_points(payload))
    payload["summary"] = str(payload.get("summary") or default_summary)
    payload["blossom_server"] = str(payload.get("blossom_server") or DEFAULT_BLOSSOM_SERVER).rstrip("/")
    return payload


def repo_root(start: Path) -> Path:
    proc = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(proc.stdout.strip())


def repo_name_with_owner(root: Path) -> str:
    proc = run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], cwd=root)
    return proc.stdout.strip()


def ensure_branch(root: Path, base_branch: str, branch: str) -> None:
    run(["git", "fetch", "origin", base_branch], cwd=root, check=False)
    base_ref = f"origin/{base_branch}"
    run(["git", "checkout", "-B", branch, base_ref], cwd=root)


def markdown_bullets(items: list[str]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item}" for item in items)


def markdown_boundary(payload: dict[str, Any]) -> str | None:
    spec = boundary_spec(payload)
    if not spec["has_content"]:
        return None

    sections = [f"## {spec['title']}"]
    if spec["description"]:
        sections.append(spec["description"])

    if spec["changes"]:
        items = []
        for change in spec["changes"]:
            text = change["description"] or change["label"]
            if change["label"] and change["description"]:
                text = f"**{change['label']}:** {change['description']}"
            items.append(f"- [{change['status']}] {text}")
        sections.append("### Change Annotations\n" + "\n".join(items))

    for view in spec["views"]:
        sections.append(f"### {view['label']}\n\n```mermaid\n{view['diagram_mermaid']}\n```")

    if spec["graph"]:
        sections.append(
            "### Interactive Boundary Graph\n"
            "The hosted plan page renders a D3 boundary graph from the structured payload data."
        )

    return "\n\n".join(sections)


def render_plan_markdown(payload: dict[str, Any], page_url: str | None, audio_url: str | None) -> str:
    boundary = markdown_boundary(payload)
    sections = [
        f"# {payload['title']}",
        "## Summary",
        str(payload["summary"]).strip(),
        "## Very High Level",
        markdown_plan_points(high_level_points(payload)),
    ]
    if boundary:
        sections.append(boundary)
    sections.extend(
        [
            "## Detailed Plan",
            str(payload["detailed_plan"]).strip(),
            "## Rule And ADR Check",
            markdown_bullets(as_list(payload["rules_adr_check"])),
            "## Possible Rule Or ADR Loosening",
            markdown_bullets(as_list(payload["possible_rule_loosening"])),
            "## Possible Rule Tightening",
            markdown_bullets(as_list(payload["possible_rule_tightening"])),
            "## Alternatives Considered",
            markdown_bullets(as_list(payload["alternatives_considered"])),
            "## Certainty",
            f"{payload['certainty_percent']} percent.",
            "## Decision",
            str(payload["decision"]),
            "## Hosted Artifacts",
            f"- Plan page: {page_url or 'Generated after publishing.'}",
            f"- TTS audio: {audio_url or 'Generated after publishing.'}",
        ]
    )
    return "\n\n".join(sections).strip() + "\n"


def render_pr_body(payload: dict[str, Any], page_url: str, audio_url: str) -> str:
    boundary = markdown_boundary(payload)
    parts = [
        f"# {payload['title']}",
        f"Hosted plan page: {page_url}",
        "## Very High Level",
        markdown_plan_points(high_level_points(payload)),
    ]
    if boundary:
        parts.append(boundary)
    parts.extend(
        [
            "## Review Links",
            "\n".join(
                [
                    f"- Hosted plan page: {page_url}",
                    f"- Detailed plan: `docs/plans/{payload['slug']}/plan.md`",
                    f"- Narration: {audio_url}",
                    f"- Certainty: {payload['certainty_percent']} percent",
                    f"- Decision: `{payload['decision']}`",
                ]
            ),
        ]
    )
    return "\n\n".join(parts).strip() + "\n"


def generate_audio(payload: dict[str, Any], workdir: Path) -> Path:
    text = str(payload["tts_friendly_version"]).strip()
    if platform.system() == "Darwin":
        source = workdir / "tts.aiff"
        run(["say", "-o", str(source), text])
    else:
        source = workdir / "tts.wav"
        run(["espeak-ng", "-w", str(source), text])
    output = workdir / "tts.mp3"
    run(["ffmpeg", "-y", "-i", str(source), "-codec:a", "libmp3lame", "-q:a", "2", str(output)])
    return output


def find_url(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("url", "href", "download_url"):
            if isinstance(value.get(key), str) and value[key].startswith("http"):
                return value[key]
        for child in value.values():
            found = find_url(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_url(child)
            if found:
                return found
    return None


def upload_audio(payload: dict[str, Any], audio_path: Path) -> str:
    server = payload["blossom_server"]
    proc = run(["nak", "blossom", "--server", server, "upload", str(audio_path)], check=False, timeout=300)
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        respond(
            {
                "ok": False,
                "error": "blossom_upload_failed",
                "message": "nak failed to upload generated narration.",
                "server": server,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "hint": "Ensure nak is authenticated if the Blossom server requires signing. See https://github.com/fiatjaf/nak.",
            },
            code=3,
        )
    for candidate in (proc.stdout, combined):
        text = candidate.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
            found = find_url(parsed)
            if found:
                return found
            sha = find_sha(parsed)
            if sha:
                return f"{server}/{sha}"
        except Exception:
            pass
    match = re.search(r"https?://[^\s\"'<>]+", combined)
    if match:
        return match.group(0)
    sha_match = re.search(r"\b[a-f0-9]{64}\b", combined)
    if sha_match:
        return f"{server}/{sha_match.group(0)}"
    respond(
        {
            "ok": False,
            "error": "blossom_upload_unparseable",
            "message": "nak upload succeeded but no audio URL could be parsed.",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        },
        code=3,
    )


def find_sha(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("sha256", "sha", "hash"):
            item = value.get(key)
            if isinstance(item, str) and re.fullmatch(r"[a-f0-9]{64}", item):
                return item
        for child in value.values():
            found = find_sha(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_sha(child)
            if found:
                return found
    return None


def html_list(items: list[str]) -> str:
    if not items:
        return "<ul><li>None.</li></ul>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def status_badge(status: str) -> str:
    label = BOUNDARY_STATUS_LABELS.get(status, "Changed")
    return f'<span class="status-badge status-{html.escape(status)}">{html.escape(label)}</span>'


def json_script_data(value: Any) -> str:
    return json.dumps(value, sort_keys=True).replace("<", "\\u003c").replace("&", "\\u0026")


def html_boundary(payload: dict[str, Any]) -> tuple[str, str]:
    spec = boundary_spec(payload)
    if not spec["has_content"]:
        return "", ""

    tabs = []
    views = []
    for index, view in enumerate(spec["views"]):
        view_id = f"boundary-view-{index}"
        active = " is-active" if index == 0 else ""
        tabs.append(
            f'<button type="button" class="tab-button{active}" data-boundary-tab="{view_id}">{html.escape(view["label"])}</button>'
        )
        views.append(
            f"""
            <div class="boundary-view{active}" data-boundary-view="{view_id}">
              <pre class="mermaid">{html.escape(view['diagram_mermaid'])}</pre>
            </div>"""
        )

    graph_json = ""
    if spec["graph"]:
        view_id = f"boundary-view-{len(views)}"
        active = " is-active" if not views else ""
        tabs.append(
            f'<button type="button" class="tab-button{active}" data-boundary-tab="{view_id}">{html.escape(spec["graph"]["label"])}</button>'
        )
        graph_id = f"boundary-graph-data-{payload['slug']}"
        views.append(
            f"""
            <div class="boundary-view{active}" data-boundary-view="{view_id}">
              <div class="d3-boundary" data-boundary-graph="{graph_id}" role="img" aria-label="{html.escape(spec['graph']['label'])}"></div>
            </div>"""
        )
        graph_json = f'<script type="application/json" id="{graph_id}">{json_script_data(spec["graph"])}</script>'

    description = f'<p class="section-note">{html.escape(spec["description"])}</p>' if spec["description"] else ""
    legend = ""
    if spec["statuses"]:
        legend_items = "".join(status_badge(status) for status in spec["statuses"])
        legend = f'<div class="boundary-legend" aria-label="Boundary change legend">{legend_items}</div>'

    annotations = ""
    if spec["changes"]:
        items = []
        for change in spec["changes"]:
            label = f"<strong>{html.escape(change['label'])}</strong> " if change["label"] else ""
            description = html.escape(change["description"] or "")
            items.append(f"<li>{status_badge(change['status'])}{label}{description}</li>")
        annotations = f"""
            <div class="boundary-annotations">
              <h3>Change Annotations</h3>
              <ul>{''.join(items)}</ul>
            </div>"""

    tab_bar = ""
    if len(tabs) > 1:
        tab_bar = f'<div class="tab-bar" data-boundary-tabs>{"".join(tabs)}</div>'

    has_mermaid = bool(spec["views"])
    has_graph = bool(spec["graph"])
    assets = ""
    if graph_json:
        assets += "\n" + graph_json
    if has_graph:
        assets += """
    <script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>"""
    assets += boundary_interaction_script(has_mermaid=has_mermaid, has_graph=has_graph)

    return (
        f"""
          <section class="section boundary-panel" data-boundary-panel>
            <div class="section-heading">
              <h2>{html.escape(spec['title'])}</h2>
              <button type="button" class="fullscreen-button" data-boundary-fullscreen>Open fullscreen</button>
            </div>
            {description}
            {legend}
            {tab_bar}
            <div class="boundary-stage">
              {''.join(views)}
            </div>
            {annotations}
          </section>""",
        assets,
    )


def boundary_interaction_script(*, has_mermaid: bool, has_graph: bool) -> str:
    common_script = """
    <script>
      function setupBoundaryPanels() {
        document.querySelectorAll("[data-boundary-panel]").forEach((panel) => {
          const tabs = Array.from(panel.querySelectorAll("[data-boundary-tab]"));
          const views = Array.from(panel.querySelectorAll("[data-boundary-view]"));
          const activate = (id) => {
            tabs.forEach((tab) => {
              const selected = tab.dataset.boundaryTab === id;
              tab.classList.toggle("is-active", selected);
              tab.setAttribute("aria-selected", String(selected));
            });
            views.forEach((view) => {
              view.classList.toggle("is-active", view.dataset.boundaryView === id);
            });
            panel.classList.add("is-ready");
          };
          if (tabs.length > 0) {
            tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab.dataset.boundaryTab)));
            activate(tabs[0].dataset.boundaryTab);
          }

          const fullscreen = panel.querySelector("[data-boundary-fullscreen]");
          if (fullscreen && panel.requestFullscreen) {
            fullscreen.addEventListener("click", async () => {
              if (document.fullscreenElement === panel) {
                await document.exitFullscreen();
              } else {
                await panel.requestFullscreen();
              }
              renderBoundaryGraphs(true);
            });
          } else if (fullscreen) {
            fullscreen.remove();
          }
        });
      }

      function renderBoundaryGraphs(force = false) {
        if (!window.d3) return;
        document.querySelectorAll("[data-boundary-graph]").forEach((container) => {
          if (container.dataset.rendered === "true" && !force) return;
          const source = document.getElementById(container.dataset.boundaryGraph);
          if (!source) return;
          const graph = JSON.parse(source.textContent);
          container.replaceChildren();
          const width = Math.max(container.clientWidth || 720, 560);
          const height = Math.max(Math.min(width * 0.52, 520), 340);
          const colors = {
            new: "#1f6f5b",
            changed: "#b45309",
            removed: "#8f2432",
            existing: "#647067",
            external: "#2563eb",
            risk: "#7c2d12"
          };
          const nodes = graph.nodes.map((node) => ({ ...node }));
          const links = graph.links.map((link) => ({ ...link }));
          const svg = d3.select(container)
            .append("svg")
            .attr("viewBox", `0 0 ${width} ${height}`)
            .attr("width", "100%")
            .attr("height", height);
          svg.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 7)
            .attr("markerHeight", 7)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#647067");
          const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((node) => node.id).distance(150).strength(0.65))
            .force("charge", d3.forceManyBody().strength(-520))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(58));
          const link = svg.append("g")
            .attr("class", "graph-links")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", (item) => colors[item.status] || colors.changed)
            .attr("stroke-width", 2.5)
            .attr("marker-end", "url(#arrow)");
          const node = svg.append("g")
            .attr("class", "graph-nodes")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .call(d3.drag()
              .on("start", (event, item) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                item.fx = item.x;
                item.fy = item.y;
              })
              .on("drag", (event, item) => {
                item.fx = event.x;
                item.fy = event.y;
              })
              .on("end", (event, item) => {
                if (!event.active) simulation.alphaTarget(0);
                item.fx = null;
                item.fy = null;
              }));
          node.append("circle")
            .attr("r", 28)
            .attr("fill", (item) => colors[item.status] || colors.changed)
            .attr("fill-opacity", 0.14)
            .attr("stroke", (item) => colors[item.status] || colors.changed)
            .attr("stroke-width", 2.5);
          node.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", 4)
            .text((item) => item.label)
            .each(function wrap() {
              const text = d3.select(this);
              const words = text.text().split(/\\s+/).reverse();
              const lines = [];
              let line = [];
              let word;
              while ((word = words.pop())) {
                line.push(word);
                if (line.join(" ").length > 16) {
                  lines.push(line.join(" "));
                  line = [];
                }
              }
              if (line.length) lines.push(line.join(" "));
              text.text("");
              lines.slice(0, 3).forEach((lineText, index) => {
                text.append("tspan")
                  .attr("x", 0)
                  .attr("dy", index === 0 ? `${-(lines.length - 1) * 0.45}em` : "1.1em")
                  .text(lineText);
              });
            });
          const label = svg.append("g")
            .attr("class", "graph-labels")
            .selectAll("text")
            .data(links.filter((item) => item.label))
            .join("text")
            .attr("text-anchor", "middle")
            .text((item) => item.label);
          simulation.on("tick", () => {
            link
              .attr("x1", (item) => item.source.x)
              .attr("y1", (item) => item.source.y)
              .attr("x2", (item) => item.target.x)
              .attr("y2", (item) => item.target.y);
            node.attr("transform", (item) => `translate(${item.x},${item.y})`);
            label
              .attr("x", (item) => (item.source.x + item.target.x) / 2)
              .attr("y", (item) => (item.source.y + item.target.y) / 2);
          });
          container.dataset.rendered = "true";
        });
      }

      setupBoundaryPanels();
      renderBoundaryGraphs();
      window.addEventListener("resize", () => renderBoundaryGraphs(true));
    </script>"""
    mermaid_script = ""
    if has_mermaid:
        mermaid_script = """
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: false, theme: "neutral" });
      await mermaid.run({ nodes: Array.from(document.querySelectorAll(".mermaid")) });
    </script>"""
    if not has_graph and not has_mermaid:
        return common_script
    return common_script + mermaid_script


def render_page(payload: dict[str, Any], audio_url: str, pr_url: str | None = None) -> str:
    boundary_block, boundary_assets = html_boundary(payload)
    decision_label = "Ready to implement" if payload["decision"] == "ready" else "Pause for architecture feedback"
    decision_class = "ready" if payload["decision"] == "ready" else "pause"
    pr_link = f'<a href="{html.escape(pr_url)}">Open PR</a>' if pr_url else ""

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(payload['title'])}</title>
    <link rel="stylesheet" href="../../assets/style.css">
  </head>
  <body>
    <main class="shell">
      <nav class="topbar">
        <a href="../../">Planning pages</a>
        {pr_link}
      </nav>
      <section class="hero">
        <div class="eyebrow">Architecture plan</div>
        <h1>{html.escape(payload['title'])}</h1>
        <p class="summary">{html.escape(payload['summary'])}</p>
        <div class="meta">
          <span class="pill {decision_class}">{decision_label}</span>
          <span class="pill">{payload['certainty_percent']} percent certainty</span>
        </div>
      </section>
{boundary_block}
      <div class="grid">
        <div>
          <section class="section">
            <h2>Very High Level</h2>
            {html_plan_points(high_level_points(payload))}
          </section>
          <section class="section">
            <h2>Existing Rules Or ADRs</h2>
            {html_list(as_list(payload['rules_adr_check']))}
          </section>
          <section class="section">
            <h2>Rule Tension And Tightening</h2>
            <h3>Possible loosening</h3>
            {html_list(as_list(payload['possible_rule_loosening']))}
            <h3>Possible tightening</h3>
            {html_list(as_list(payload['possible_rule_tightening']))}
          </section>
          <section class="section">
            <h2>Alternatives Considered</h2>
            {html_list(as_list(payload['alternatives_considered']))}
          </section>
        </div>
        <aside>
          <section class="card">
            <h2>TTS Version</h2>
            <audio controls preload="metadata" src="{html.escape(audio_url)}"></audio>
            <p>Audio-friendly narration generated from the planning payload.</p>
          </section>
          <section class="card">
            <h2>Certainty</h2>
            <div class="certainty {decision_class if decision_class == 'pause' else ''}">{payload['certainty_percent']}%</div>
            <p>{html.escape(decision_label)}.</p>
          </section>
          <section class="card links">
            <h2>Links</h2>
            {pr_link}
            <a href="{html.escape(audio_url)}">Open narration</a>
            <a href="../../docs/plans/{html.escape(payload['slug'])}/plan.md">Detailed plan file</a>
          </section>
        </aside>
      </div>
    </main>
{boundary_assets}
  </body>
</html>
"""


STYLE_CSS = """:root {
  color-scheme: light;
  --bg: #f7f7f3;
  --panel: #ffffff;
  --text: #20231f;
  --muted: #5d665c;
  --line: #d9ded4;
  --accent: #1f6f5b;
  --accent-dark: #164d40;
  --pause: #8f2432;
  --new: #1f6f5b;
  --changed: #b45309;
  --removed: #8f2432;
  --existing: #647067;
  --external: #2563eb;
  --risk: #7c2d12;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
}
a { color: var(--accent-dark); }
.shell { width: min(1040px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }
.topbar { display: flex; justify-content: space-between; gap: 16px; margin-bottom: 28px; color: var(--muted); font-size: 14px; }
.topbar a { text-decoration: none; }
.hero { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }
.eyebrow { color: var(--accent-dark); font-size: 13px; font-weight: 700; text-transform: uppercase; }
h1 { max-width: 840px; margin: 8px 0 12px; font-size: clamp(34px, 6vw, 62px); line-height: 1.02; letter-spacing: 0; }
h2 { margin: 0 0 12px; font-size: 20px; letter-spacing: 0; }
h3 { margin: 14px 0 8px; font-size: 15px; }
p { margin: 0 0 12px; }
ul { margin: 0; padding-left: 20px; }
li + li { margin-top: 6px; }
.summary { max-width: 780px; color: var(--muted); font-size: 18px; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.pill { display: inline-flex; min-height: 30px; padding: 5px 10px; border: 1px solid var(--line); border-radius: 999px; background: #fff; color: var(--muted); font-size: 13px; }
.pill.ready { border-color: #abd3c5; color: var(--accent-dark); }
.pill.pause { border-color: #e3bac0; color: var(--pause); }
.grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 360px); gap: 20px; align-items: start; }
.section, .card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; }
.section + .section, .card + .card { margin-top: 16px; }
.section-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.section-heading h2 { margin: 0; }
.section-note { max-width: 760px; color: var(--muted); }
.fullscreen-button, .tab-button {
  min-height: 34px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: var(--text);
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
.fullscreen-button { padding: 6px 10px; white-space: nowrap; }
.fullscreen-button:hover, .tab-button:hover { border-color: var(--accent); color: var(--accent-dark); }
.boundary-panel { margin-bottom: 20px; }
.boundary-panel:fullscreen {
  overflow: auto;
  min-height: 100vh;
  padding: 28px;
  background: var(--bg);
  border: 0;
  border-radius: 0;
}
.boundary-panel:fullscreen .boundary-stage { min-height: calc(100vh - 260px); }
.boundary-legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  margin-right: 8px;
  padding: 2px 8px;
  border: 1px solid currentColor;
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.2;
}
.status-new { color: var(--new); }
.status-changed { color: var(--changed); }
.status-removed { color: var(--removed); }
.status-existing { color: var(--existing); }
.status-external { color: var(--external); }
.status-risk { color: var(--risk); }
.tab-bar { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.tab-button { padding: 6px 12px; color: var(--muted); }
.tab-button.is-active { border-color: var(--accent); background: #eef8f4; color: var(--accent-dark); }
.boundary-stage { position: relative; overflow-x: auto; }
.boundary-panel.is-ready .boundary-view:not(.is-active) {
  position: absolute;
  width: 100%;
  height: 0;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}
.boundary-view { min-width: 0; }
.mermaid {
  overflow-x: auto;
  min-height: 260px;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
}
.d3-boundary {
  min-height: 360px;
  overflow: hidden;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 8px;
}
.d3-boundary text { fill: var(--text); font-size: 12px; font-weight: 700; pointer-events: none; }
.graph-labels text { fill: var(--muted); font-size: 11px; font-weight: 700; paint-order: stroke; stroke: #fbfcfa; stroke-width: 4px; }
.boundary-annotations { margin-top: 14px; }
.boundary-annotations ul, .plan-points { display: grid; gap: 8px; padding-left: 0; list-style: none; }
.boundary-annotations li, .plan-point {
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfa;
}
.plan-point.is-highlighted { border-color: #e1c16e; background: #fff8df; }
audio { width: 100%; margin: 4px 0 10px; }
.links { display: grid; gap: 8px; }
.links a { display: block; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; background: #fbfcfa; text-decoration: none; font-weight: 600; }
.certainty { font-size: 42px; line-height: 1; font-weight: 800; color: var(--accent-dark); }
.certainty.pause { color: var(--pause); }
@media (max-width: 760px) {
  .grid { grid-template-columns: 1fr; }
  .topbar, .section-heading { align-items: flex-start; flex-direction: column; }
  .fullscreen-button { width: 100%; }
  .mermaid { min-height: 220px; }
}
"""


def ensure_pages_worktree(root: Path, base_branch: str) -> tuple[Path, bool]:
    pages_dir = Path(tempfile.mkdtemp(prefix="planning-agent-pages-"))
    remote = run(["git", "ls-remote", "--heads", "origin", "gh-pages"], cwd=root)
    if remote.stdout.strip():
        run(["git", "worktree", "add", str(pages_dir), "gh-pages"], cwd=root)
        return pages_dir, True
    run(["git", "worktree", "add", "--detach", str(pages_dir), f"origin/{base_branch}"], cwd=root)
    run(["git", "switch", "--orphan", "gh-pages"], cwd=pages_dir)
    existing = [item for item in pages_dir.iterdir() if item.name != ".git"]
    if existing:
        run(["git", "rm", "-rf", "."], cwd=pages_dir, check=False)
    return pages_dir, False


def update_pages_index(pages_dir: Path) -> None:
    plan_links = []
    plans_root = pages_dir / "plans"
    if plans_root.exists():
        for plan_dir in sorted(item for item in plans_root.iterdir() if item.is_dir()):
            title = plan_dir.name.replace("-", " ").title()
            index = plan_dir / "index.html"
            if index.exists():
                text = index.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r"<h1>(.*?)</h1>", text)
                if match:
                    title = re.sub(r"<.*?>", "", match.group(1))
            plan_links.append(f'<a href="plans/{html.escape(plan_dir.name)}/">{html.escape(title)}</a>')
    links = "\n".join(f"          {link}" for link in plan_links) or "          <p>No plans published yet.</p>"
    (pages_dir / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Planning Pages</title>
    <link rel="stylesheet" href="assets/style.css">
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <div class="eyebrow">Planning pages</div>
        <h1>Hosted architecture plans</h1>
        <p class="summary">Generated planning pages for complex agent-assigned work.</p>
      </section>
      <section class="card links">
{links}
      </section>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )


def publish_pages(root: Path, payload: dict[str, Any], audio_url: str, pr_url: str | None) -> str:
    name_with_owner = repo_name_with_owner(root)
    pages_url = f"https://{name_with_owner.split('/')[0]}.github.io/{name_with_owner.split('/')[1]}/"
    plan_page_url = f"{pages_url}plans/{payload['slug']}/"
    pages_dir, _ = ensure_pages_worktree(root, payload["base_branch"])
    try:
        (pages_dir / ".nojekyll").write_text("\n", encoding="utf-8")
        (pages_dir / "assets").mkdir(parents=True, exist_ok=True)
        (pages_dir / "assets" / "style.css").write_text(STYLE_CSS, encoding="utf-8")
        docs_dir = pages_dir / "docs" / "plans" / payload["slug"]
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "plan.md").write_text(render_plan_markdown(payload, plan_page_url, audio_url), encoding="utf-8")
        page_dir = pages_dir / "plans" / payload["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(render_page(payload, audio_url, pr_url), encoding="utf-8")
        update_pages_index(pages_dir)
        run(["git", "add", "."], cwd=pages_dir)
        staged = run(["git", "diff", "--cached", "--quiet"], cwd=pages_dir, check=False)
        if staged.returncode != 0:
            run(["git", "commit", "-m", f"Publish plan page for {payload['slug']}"], cwd=pages_dir)
            run(["git", "push", "-u", "origin", "gh-pages"], cwd=pages_dir)
        ensure_github_pages(root)
    finally:
        run(["git", "worktree", "remove", "--force", str(pages_dir)], cwd=root, check=False)
    return plan_page_url


def ensure_github_pages(root: Path) -> None:
    repo = repo_name_with_owner(root)
    check = run(["gh", "api", f"repos/{repo}/pages"], cwd=root, check=False)
    if check.returncode == 0:
        return
    run(
        [
            "gh",
            "api",
            "--method",
            "POST",
            f"repos/{repo}/pages",
            "-f",
            "source[branch]=gh-pages",
            "-f",
            "source[path]=/",
        ],
        cwd=root,
        check=False,
    )


def commit_plan_branch(root: Path, payload: dict[str, Any], plan_page_url: str | None, audio_url: str | None) -> None:
    ensure_branch(root, payload["base_branch"], payload["branch"])
    plan_dir = root / "docs" / "plans" / payload["slug"]
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "plan.md").write_text(render_plan_markdown(payload, plan_page_url, audio_url), encoding="utf-8")
    run(["git", "add", str(plan_dir / "plan.md")], cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode != 0:
        run(["git", "commit", "-m", f"Add plan for {payload['slug']}"], cwd=root)
    run(["git", "push", "-u", "origin", payload["branch"]], cwd=root)


def create_or_update_pr(root: Path, payload: dict[str, Any], body: str) -> str:
    existing = run(
        ["gh", "pr", "view", payload["branch"], "--json", "url", "--jq", ".url"],
        cwd=root,
        check=False,
    )
    if existing.returncode == 0 and existing.stdout.strip():
        pr_url = existing.stdout.strip()
        run(["gh", "pr", "edit", pr_url, "--title", payload["pr_title"], "--body-file", "-"], cwd=root, input_text=body)
        run(["gh", "pr", "ready", pr_url, "--undo"], cwd=root, check=False)
        return pr_url
    created = run(
        [
            "gh",
            "pr",
            "create",
            "--draft",
            "--base",
            payload["base_branch"],
            "--head",
            payload["branch"],
            "--title",
            payload["pr_title"],
            "--body-file",
            "-",
        ],
        cwd=root,
        input_text=body,
    )
    return created.stdout.strip().splitlines()[-1]


def comment_decision(root: Path, payload: dict[str, Any], pr_url: str) -> str:
    if payload["decision"] == "ready":
        body = payload.get(
            "ready_comment",
            "Ready to implement: this plan is sufficiently bounded, aligned with repository constraints, and ready to proceed unless instructed otherwise.",
        )
        if "Ready to implement" not in body:
            body = "Ready to implement: " + str(body)
    else:
        body = payload.get(
            "pause_comment",
            "Pausing for architecture feedback: this plan has enough architectural impact, rule/ADR tension, or alternative-design uncertainty to justify independent review.",
        )
    proc = run(["gh", "pr", "comment", pr_url, "--body", str(body)], cwd=root)
    return proc.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a planning PR from a JSON payload.")
    parser.add_argument("payload", type=Path, help="Path to plan payload JSON.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root or any path inside it.")
    parser.add_argument("--no-install", action="store_true", help="Do not attempt one-shot dependency installs.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and render locally without uploading, pushing, or creating a PR.")
    args = parser.parse_args()

    payload = validate_payload(load_payload(args.payload))

    if args.dry_run:
        respond(
            {
                "ok": True,
                "dry_run": True,
                "payload": {
                    "title": payload["title"],
                    "slug": payload["slug"],
                    "branch": payload["branch"],
                    "draft_pr": True,
                    "decision": payload["decision"],
                    "certainty_percent": payload["certainty_percent"],
                },
                "pr_body": render_pr_body(payload, "https://example.invalid/plan", "https://example.invalid/audio"),
            }
        )

    ensure_commands(no_install=args.no_install)
    root = repo_root(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="planning-agent-audio-") as tmp:
        audio_path = generate_audio(payload, Path(tmp))
        audio_url = upload_audio(payload, audio_path)

    commit_plan_branch(root, payload, None, audio_url)
    page_url = publish_pages(root, payload, audio_url, None)
    plan_path = root / "docs" / "plans" / payload["slug"] / "plan.md"
    plan_path.write_text(render_plan_markdown(payload, page_url, audio_url), encoding="utf-8")
    run(["git", "add", str(plan_path)], cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode != 0:
        run(["git", "commit", "-m", f"Link hosted artifacts for {payload['slug']}"], cwd=root)
        run(["git", "push", "-u", "origin", payload["branch"]], cwd=root)
    pr_body = render_pr_body(payload, page_url, audio_url)
    pr_url = create_or_update_pr(root, payload, pr_body)
    page_url = publish_pages(root, payload, audio_url, pr_url)
    pr_body = render_pr_body(payload, page_url, audio_url)
    create_or_update_pr(root, payload, pr_body)
    comment_url = comment_decision(root, payload, pr_url)

    respond(
        {
            "ok": True,
            "title": payload["title"],
            "slug": payload["slug"],
            "decision": payload["decision"],
            "certainty_percent": payload["certainty_percent"],
            "pr_url": pr_url,
            "comment_url": comment_url,
            "plan_page_url": page_url,
            "audio_url": audio_url,
            "branch": payload["branch"],
            "draft_pr": True,
        }
    )


if __name__ == "__main__":
    main()
