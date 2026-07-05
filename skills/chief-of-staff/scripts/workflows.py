#!/usr/bin/env python3
"""Manage chief-of-staff workflow memory."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_HOME = Path("~/.agents/homes/chief-of-staff").expanduser()
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULTS_DIR = SKILL_DIR / "references" / "default-workflows"


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage chief-of-staff workflows.")
    parser.add_argument("--home-dir", default=os.environ.get("CHIEF_OF_STAFF_HOME"), help="Override the chief-of-staff home directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List workflows and when to use them.")
    list_parser.add_argument("--no-defaults", action="store_true", help="Do not seed bundled default workflows before listing.")
    list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    show_parser = subparsers.add_parser("show", help="Show a workflow file.")
    show_parser.add_argument("slug")

    path_parser = subparsers.add_parser("path", help="Print the workflows directory or one workflow path.")
    path_parser.add_argument("slug", nargs="?")

    capture_parser = subparsers.add_parser("capture", help="Create an initial workflow file.")
    capture_parser.add_argument("slug")
    capture_parser.add_argument("--summary", required=True, help="One-line summary of when to use this workflow.")
    capture_parser.add_argument("--trigger", action="append", default=[], help="Trigger phrase or condition. Repeatable.")
    capture_parser.add_argument("--body", help="Workflow body. If omitted, stdin is used when piped.")
    capture_parser.add_argument("--force", action="store_true", help="Overwrite an existing workflow.")

    append_parser = subparsers.add_parser("append", help="Append a lesson or review note to a workflow.")
    append_parser.add_argument("slug")
    append_parser.add_argument("--note", help="Lesson or review note. If omitted, stdin is used when piped.")

    args = parser.parse_args()
    home = Path(args.home_dir).expanduser() if args.home_dir else DEFAULT_HOME
    workflows_dir = home / "workflows"

    if args.command == "list":
        ensure_workflows_dir(workflows_dir)
        if not args.no_defaults:
            seed_defaults(workflows_dir)
        workflows = list_workflows(workflows_dir)
        if args.json:
            print(json.dumps({"workflows_dir": str(workflows_dir), "workflows": workflows}, indent=2))
        else:
            for workflow in workflows:
                print(f"{workflow['slug']}\t{workflow['summary']}")
        return 0

    if args.command == "show":
        path = workflow_path(workflows_dir, args.slug)
        print(path.read_text())
        return 0

    if args.command == "path":
        ensure_workflows_dir(workflows_dir)
        print(workflow_path(workflows_dir, args.slug) if args.slug else workflows_dir)
        return 0

    if args.command == "capture":
        ensure_workflows_dir(workflows_dir)
        path = workflow_path(workflows_dir, args.slug)
        if path.exists() and not args.force:
            raise SystemExit(f"{path} already exists; pass --force to overwrite")
        body = args.body if args.body is not None else read_stdin_or_default(args.slug)
        content = render_workflow(args.slug, args.summary, args.trigger, body)
        path.write_text(content)
        print(path)
        return 0

    if args.command == "append":
        ensure_workflows_dir(workflows_dir)
        path = workflow_path(workflows_dir, args.slug)
        if not path.exists():
            raise SystemExit(f"{path} does not exist; use capture first")
        note = args.note if args.note is not None else read_stdin_required("append requires --note or stdin")
        with path.open("a") as handle:
            handle.write(f"\n## Review {today()}\n\n{note.strip()}\n")
        print(path)
        return 0

    raise SystemExit(f"unknown command: {args.command}")


def ensure_workflows_dir(workflows_dir: Path) -> None:
    workflows_dir.mkdir(parents=True, exist_ok=True)


def seed_defaults(workflows_dir: Path) -> None:
    if not DEFAULTS_DIR.exists():
        return
    for source in DEFAULTS_DIR.glob("*.md"):
        target = workflows_dir / source.name
        if not target.exists():
            target.write_text(source.read_text())


def list_workflows(workflows_dir: Path) -> list[dict[str, str]]:
    workflows = []
    for path in sorted(workflows_dir.glob("*.md")):
        attrs = parse_frontmatter(path.read_text())
        workflows.append({
            "slug": attrs.get("slug", path.stem),
            "summary": attrs.get("summary", "(no summary)"),
            "path": str(path),
        })
    return workflows


def workflow_path(workflows_dir: Path, slug: str) -> Path:
    clean = slugify(slug)
    if not clean:
        raise SystemExit("workflow slug cannot be empty")
    return workflows_dir / f"{clean}.md"


def render_workflow(slug: str, summary: str, triggers: list[str], body: str) -> str:
    clean = slugify(slug)
    trigger_lines = "\n".join(f"  - {trigger}" for trigger in triggers) or "  - Add triggers after the first real use."
    text = body.strip() or "Describe the repeatable steps after the first real use."
    return f"""---
slug: {clean}
summary: {summary}
triggers:
{trigger_lines}
status: draft
created: {today()}
---

# {titleize(clean)}

{text}
"""


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    attrs: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            attrs[match.group(1)] = match.group(2).strip().strip('"')
    return attrs


def read_stdin_or_default(slug: str) -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return f"""## Approach

1. Clarify only if needed.
2. Execute the user's request.
3. Record what worked and what should change next time.

## Review Notes

- Created from first encounter with `{slug}`.
"""


def read_stdin_required(message: str) -> str:
    if sys.stdin.isatty():
        raise SystemExit(message)
    text = sys.stdin.read()
    if not text.strip():
        raise SystemExit(message)
    return text


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower()).strip("-")


def titleize(slug: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug) if part)


def today() -> str:
    return dt.date.today().isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
