#!/usr/bin/env python3
"""Manage lightweight, agent-owned runbook memory."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULTS_DIR = SKILL_DIR / "references" / "default-runbooks"
ALLOWED_STATUSES = {"default", "draft", "active", "retired"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage reusable runbook memory.")
    parser.add_argument(
        "--runbooks-dir",
        help=(
            "Runbook directory. Defaults to RUNBOOK_DIR, then "
            "$AGENT_HOME/runbooks, then ~/.agents/homes/runbook/runbooks."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create the store and seed bundled defaults.")
    init_parser.add_argument("--json", action="store_true")

    list_parser = subparsers.add_parser("list", help="List runbook summaries.")
    list_parser.add_argument("--no-defaults", action="store_true", help="Do not seed bundled defaults.")
    list_parser.add_argument("--include-retired", action="store_true")
    list_parser.add_argument("--json", action="store_true")

    show_parser = subparsers.add_parser("show", help="Print one runbook.")
    show_parser.add_argument("slug")

    path_parser = subparsers.add_parser("path", help="Print the store path or one runbook path.")
    path_parser.add_argument("slug", nargs="?")

    capture_parser = subparsers.add_parser("capture", help="Create a draft runbook.")
    capture_parser.add_argument("slug")
    capture_parser.add_argument("--summary", required=True)
    capture_parser.add_argument("--trigger", action="append", default=[])
    capture_parser.add_argument("--body", help="Runbook body. Reads stdin when piped.")
    capture_parser.add_argument("--force", action="store_true")

    rewrite_parser = subparsers.add_parser("rewrite", help="Replace the canonical runbook body.")
    rewrite_parser.add_argument("slug")
    rewrite_parser.add_argument("--body", help="Replacement body. Reads stdin when piped.")

    review_parser = subparsers.add_parser("review", help="Append a consequential review note.")
    review_parser.add_argument("slug")
    review_parser.add_argument("--note", help="Review note. Reads stdin when piped.")

    status_parser = subparsers.add_parser("set-status", help="Set runbook lifecycle status.")
    status_parser.add_argument("slug")
    status_parser.add_argument("status", choices=sorted(ALLOWED_STATUSES - {"default"}))

    validate_parser = subparsers.add_parser("validate", help="Validate runbook metadata and filenames.")
    validate_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    runbooks_dir = resolve_runbooks_dir(args.runbooks_dir)

    if args.command == "init":
        ensure_store(runbooks_dir)
        seeded = seed_defaults(runbooks_dir)
        payload = {"runbooks_dir": str(runbooks_dir), "seeded": seeded}
        print(json.dumps(payload, indent=2) if args.json else str(runbooks_dir))
        return 0

    if args.command == "list":
        ensure_store(runbooks_dir)
        if not args.no_defaults:
            seed_defaults(runbooks_dir)
        runbooks = list_runbooks(runbooks_dir, include_retired=args.include_retired)
        if args.json:
            print(json.dumps({"runbooks_dir": str(runbooks_dir), "runbooks": runbooks}, indent=2))
        else:
            for runbook in runbooks:
                print(f"{runbook['slug']}\t{runbook['status']}\t{runbook['summary']}")
        return 0

    if args.command == "show":
        ensure_store(runbooks_dir)
        seed_defaults(runbooks_dir)
        path = existing_runbook_path(runbooks_dir, args.slug)
        print(path.read_text(encoding="utf-8"), end="")
        return 0

    if args.command == "path":
        ensure_store(runbooks_dir)
        print(runbook_path(runbooks_dir, args.slug) if args.slug else runbooks_dir)
        return 0

    if args.command == "capture":
        ensure_store(runbooks_dir)
        path = runbook_path(runbooks_dir, args.slug)
        if path.exists() and not args.force:
            fail(f"{path} already exists; pass --force only when replacement is intentional")
        body = args.body if args.body is not None else read_stdin_or_default(args.slug)
        content = render_runbook(args.slug, args.summary, args.trigger, body)
        atomic_write(path, content)
        print(path)
        return 0

    if args.command == "rewrite":
        path = existing_runbook_path(runbooks_dir, args.slug)
        body = args.body if args.body is not None else read_stdin_required("rewrite requires --body or stdin")
        current = path.read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(current)
        frontmatter = set_frontmatter_scalar(frontmatter, "updated", today())
        atomic_write(path, join_frontmatter(frontmatter, body.strip()))
        print(path)
        return 0

    if args.command == "review":
        path = existing_runbook_path(runbooks_dir, args.slug)
        note = args.note if args.note is not None else read_stdin_required("review requires --note or stdin")
        current = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(current)
        frontmatter = set_frontmatter_scalar(frontmatter, "updated", today())
        updated_body = body.rstrip() + f"\n\n## Review {today()}\n\n{note.strip()}\n"
        atomic_write(path, join_frontmatter(frontmatter, updated_body.rstrip()))
        print(path)
        return 0

    if args.command == "set-status":
        path = existing_runbook_path(runbooks_dir, args.slug)
        current = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(current)
        attrs = parse_frontmatter(frontmatter)
        if attrs.get("status") == "default":
            fail("the bundled default runbook cannot be promoted or retired in place; copy it to a new slug")
        frontmatter = set_frontmatter_scalar(frontmatter, "status", args.status)
        frontmatter = set_frontmatter_scalar(frontmatter, "updated", today())
        atomic_write(path, join_frontmatter(frontmatter, body.rstrip()))
        print(path)
        return 0

    if args.command == "validate":
        ensure_store(runbooks_dir)
        seed_defaults(runbooks_dir)
        report = validate_store(runbooks_dir)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for item in report["files"]:
                marker = "ok" if not item["errors"] else "error"
                print(f"{marker}\t{item['path']}")
                for error in item["errors"]:
                    print(f"  - {error}")
            print(f"{report['valid']} valid, {report['invalid']} invalid")
        return 1 if report["invalid"] else 0

    fail(f"unknown command: {args.command}")


def resolve_runbooks_dir(cli_value: str | None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser().resolve()
    if env_value := os.environ.get("RUNBOOK_DIR"):
        return Path(env_value).expanduser().resolve()
    if agent_home := os.environ.get("AGENT_HOME"):
        return (Path(agent_home).expanduser() / "runbooks").resolve()
    return Path("~/.agents/homes/runbook/runbooks").expanduser().resolve()


def ensure_store(runbooks_dir: Path) -> None:
    runbooks_dir.mkdir(parents=True, exist_ok=True)


def seed_defaults(runbooks_dir: Path) -> list[str]:
    seeded: list[str] = []
    if not DEFAULTS_DIR.exists():
        return seeded
    for source in sorted(DEFAULTS_DIR.glob("*.md")):
        target = runbooks_dir / source.name
        if not target.exists():
            shutil.copyfile(source, target)
            seeded.append(source.stem)
    return seeded


def list_runbooks(runbooks_dir: Path, *, include_retired: bool) -> list[dict[str, Any]]:
    runbooks: list[dict[str, Any]] = []
    for path in sorted(runbooks_dir.glob("*.md")):
        frontmatter, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        attrs = parse_frontmatter(frontmatter)
        status = str(attrs.get("status", "draft"))
        if status == "retired" and not include_retired:
            continue
        runbooks.append(
            {
                "slug": str(attrs.get("slug", path.stem)),
                "summary": str(attrs.get("summary", "(no summary)")),
                "triggers": attrs.get("triggers", []),
                "status": status,
                "updated": attrs.get("updated"),
                "path": str(path),
            }
        )
    return runbooks


def validate_store(runbooks_dir: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    invalid = 0

    for path in sorted(runbooks_dir.glob("*.md")):
        errors: list[str] = []
        try:
            frontmatter, _ = split_frontmatter(path.read_text(encoding="utf-8"))
            attrs = parse_frontmatter(frontmatter)
        except ValueError as exc:
            attrs = {}
            errors.append(str(exc))

        slug = attrs.get("slug")
        summary = attrs.get("summary")
        status = attrs.get("status", "draft")

        if not isinstance(slug, str) or not slug:
            errors.append("missing required scalar: slug")
        elif not SLUG_RE.fullmatch(slug):
            errors.append("slug must contain lowercase letters, numbers, hyphens, or underscores")
        else:
            if path.stem != slug:
                errors.append(f"filename must be {slug}.md")
            if slug in seen:
                errors.append(f"duplicate slug also used by {seen[slug]}")
            else:
                seen[slug] = str(path)

        if not isinstance(summary, str) or not summary.strip():
            errors.append("missing required scalar: summary")
        if status not in ALLOWED_STATUSES:
            errors.append(f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")
        if "triggers" in attrs and not isinstance(attrs["triggers"], list):
            errors.append("triggers must be a YAML list")

        if errors:
            invalid += 1
        files.append({"path": str(path), "slug": slug, "errors": errors})

    return {"runbooks_dir": str(runbooks_dir), "valid": len(files) - invalid, "invalid": invalid, "files": files}


def runbook_path(runbooks_dir: Path, slug: str | None) -> Path:
    if slug is None:
        return runbooks_dir
    clean = slugify(slug)
    if not clean:
        fail("runbook slug cannot be empty")
    return runbooks_dir / f"{clean}.md"


def existing_runbook_path(runbooks_dir: Path, slug: str) -> Path:
    path = runbook_path(runbooks_dir, slug)
    if not path.exists():
        fail(f"{path} does not exist")
    return path


def render_runbook(slug: str, summary: str, triggers: list[str], body: str) -> str:
    clean = slugify(slug)
    if not clean:
        fail("runbook slug cannot be empty")
    trigger_lines = "\n".join(f"  - {json.dumps(trigger, ensure_ascii=False)}" for trigger in triggers)
    if not trigger_lines:
        trigger_lines = "  - Add representative triggers after the first real use."
    frontmatter = (
        f"slug: {clean}\n"
        f"summary: {json.dumps(summary.strip(), ensure_ascii=False)}\n"
        f"triggers:\n{trigger_lines}\n"
        f"status: draft\n"
        f"created: {today()}\n"
        f"updated: {today()}"
    )
    text = body.strip() or default_body(clean)
    return join_frontmatter(frontmatter, f"# {titleize(clean)}\n\n{text}")


def split_frontmatter(text: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("file must begin with YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter is missing its closing --- line")
    return normalized[4:end], normalized[end + 5 :]


def join_frontmatter(frontmatter: str, body: str) -> str:
    return f"---\n{frontmatter.strip()}\n---\n\n{body.strip()}\n"


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    attrs: dict[str, Any] = {}
    current_list: str | None = None

    for raw_line in frontmatter.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        list_match = re.match(r"^\s{2,}-\s+(.*)$", raw_line)
        if list_match and current_list:
            attrs.setdefault(current_list, []).append(parse_scalar(list_match.group(1)))
            continue

        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", raw_line)
        if not match:
            current_list = None
            continue

        key, value = match.group(1), (match.group(2) or "").strip()
        if value:
            attrs[key] = parse_scalar(value)
            current_list = None
        else:
            attrs[key] = []
            current_list = key

    return attrs


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            decoded = json.loads(value)
            return str(decoded)
        except json.JSONDecodeError:
            pass
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def set_frontmatter_scalar(frontmatter: str, key: str, value: str) -> str:
    replacement = f"{key}: {value}"
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if pattern.search(frontmatter):
        return pattern.sub(replacement, frontmatter, count=1)
    return frontmatter.rstrip() + "\n" + replacement


def read_stdin_or_default(slug: str) -> str:
    if not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            return text
    return default_body(slugify(slug))


def read_stdin_required(message: str) -> str:
    if sys.stdin.isatty():
        fail(message)
    text = sys.stdin.read()
    if not text.strip():
        fail(message)
    return text


def default_body(slug: str) -> str:
    return f"""## Outcome

Describe what useful completion looks like.

## Sources Of Truth

List where current facts must be checked instead of remembered here.

## Approach

1. Describe the learned procedure after the first meaningful run.
2. Include judgment branches only where they materially change execution.

## Done When

State the completion checks and durable outputs.

## Review History

- Created from the first meaningful encounter with `{slug}`."""


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower()).strip("-_")


def titleize(slug: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug) if part)


def today() -> str:
    return dt.date.today().isoformat()


def fail(message: str) -> None:
    raise SystemExit(message)


if __name__ == "__main__":
    raise SystemExit(main())
