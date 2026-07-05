#!/usr/bin/env python3
"""Publish a GitHub planning PR with hosted plan page and external audio.

The agent-facing contract is JSON in, JSON out. Agents provide planning fields;
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

    high_level_words = str(payload["high_level_plan"]).split()
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
    payload["summary"] = str(payload.get("summary") or payload["high_level_plan"])
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


def render_plan_markdown(payload: dict[str, Any], page_url: str | None, audio_url: str | None) -> str:
    diagram = payload.get("diagram_mermaid")
    sections = [
        f"# {payload['title']}",
        "## Summary",
        str(payload["summary"]).strip(),
    ]
    if diagram:
        sections.extend(["## Boundaries", f"```mermaid\n{str(diagram).strip()}\n```"])
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
    diagram = payload.get("diagram_mermaid")
    parts = [
        f"# {payload['title']}",
        "## 1. Very High Level",
        str(payload["high_level_plan"]).strip(),
    ]
    if diagram:
        parts.append(f"```mermaid\n{str(diagram).strip()}\n```")
    parts.extend(
        [
            f"Detailed plan: `docs/plans/{payload['slug']}/plan.md`",
            f"Hosted plan page: {page_url}",
            "## 2. TTS Version",
            "Use the hosted plan page for the audio player, or open the generated narration directly:",
            f"[Open the hosted audio player]({page_url})",
            f"[Open the narration]({audio_url})",
            "## 3. Existing Rules Or ADRs",
            markdown_bullets(as_list(payload["rules_adr_check"])),
            "## 4. Possible Rule Or ADR Violation",
            markdown_bullets(as_list(payload["possible_rule_loosening"])),
            "## 5. Possible Rule Tightening",
            markdown_bullets(as_list(payload["possible_rule_tightening"])),
            "## 6. Alternatives Considered",
            markdown_bullets(as_list(payload["alternatives_considered"])),
            "## 7. Certainty",
            f"{payload['certainty_percent']} percent. Decision: `{payload['decision']}`.",
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


def render_page(payload: dict[str, Any], audio_url: str, pr_url: str | None = None) -> str:
    diagram = str(payload.get("diagram_mermaid") or "").strip()
    diagram_block = ""
    mermaid_script = ""
    if diagram:
        diagram_block = f"""
          <section class="section">
            <h2>Boundaries</h2>
            <pre class="mermaid">{html.escape(diagram)}</pre>
          </section>"""
        mermaid_script = """
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral" });
    </script>"""

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
      <div class="grid">
        <div>
{diagram_block}
          <section class="section">
            <h2>Very High Level</h2>
            <p>{html.escape(payload['high_level_plan'])}</p>
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
{mermaid_script}
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
.mermaid { overflow-x: auto; background: #fbfcfa; border: 1px solid var(--line); border-radius: 8px; padding: 10px; }
audio { width: 100%; margin: 4px 0 10px; }
.links { display: grid; gap: 8px; }
.links a { display: block; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; background: #fbfcfa; text-decoration: none; font-weight: 600; }
.certainty { font-size: 42px; line-height: 1; font-weight: 800; color: var(--accent-dark); }
.certainty.pause { color: var(--pause); }
@media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .topbar { align-items: flex-start; flex-direction: column; } }
"""


def ensure_pages_worktree(root: Path, base_branch: str) -> tuple[Path, bool]:
    pages_dir = Path(tempfile.mkdtemp(prefix="gh-plan-pr-pages-"))
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
        return pr_url
    created = run(
        [
            "gh",
            "pr",
            "create",
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

    ensure_commands(no_install=args.no_install)
    payload = validate_payload(load_payload(args.payload))
    root = repo_root(args.repo_root)

    if args.dry_run:
        respond(
            {
                "ok": True,
                "dry_run": True,
                "payload": {
                    "title": payload["title"],
                    "slug": payload["slug"],
                    "branch": payload["branch"],
                    "decision": payload["decision"],
                    "certainty_percent": payload["certainty_percent"],
                },
                "pr_body": render_pr_body(payload, "https://example.invalid/plan", "https://example.invalid/audio"),
            }
        )

    with tempfile.TemporaryDirectory(prefix="gh-plan-pr-audio-") as tmp:
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
        }
    )


if __name__ == "__main__":
    main()
