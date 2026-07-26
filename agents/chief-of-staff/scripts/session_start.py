#!/usr/bin/env python3
"""Chief-of-staff session bootstrap / brief.

Single entrypoint the agent runs at the start of every session. It prepares and
prints the operating context the session needs, deciding *what* to inject:

  * Ensures the home directory exists (upsert).
  * If the home directory is not yet tracked in a git repo — i.e. it is a plain
    directory, not a symlink into a clone — prints ``references/SETUP.md`` so the
    agent walks the user through creating/linking the tracking repo.
  * Otherwise prints the session brief: where home is tracked, the available
    runbooks, and any standing brief the agent left for itself.

Kept deterministic and side-effect-light on purpose: the agent runs this every
session, so it must be fast and predictable. This is the seam for guiding the
agent's self-evolution — grow it by adding sections to ``build_brief`` (cron
status, proactive tracking, daily-report pointer, etc.) rather than by adding
prose to the agent's standing instructions.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = AGENT_DIR / "references"
SETUP_DOC = REFERENCES_DIR / "SETUP.md"
DEFAULT_HOME = Path("~/.agents/homes/chief-of-staff").expanduser()


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and print the chief-of-staff session context.")
    parser.add_argument(
        "--home-dir",
        default=os.environ.get("CHIEF_OF_STAFF_HOME"),
        help="Override the chief-of-staff home directory.",
    )
    args = parser.parse_args()
    home = Path(args.home_dir).expanduser() if args.home_dir else DEFAULT_HOME

    home.mkdir(parents=True, exist_ok=True)

    if is_tracked(home):
        print(build_brief(home))
    else:
        print(build_setup(home))
    return 0


def is_tracked(home: Path) -> bool:
    """Setup is complete iff the home dir is a symlink into a git repo."""
    return home.is_symlink()


def build_setup(home: Path) -> str:
    if not SETUP_DOC.exists():
        return f"SETUP guide missing at {SETUP_DOC}; home {home} is not tracked in a git repo."
    guide = SETUP_DOC.read_text().replace("{{HOME}}", str(home))
    return "\n".join([guide.rstrip(), "", present_home_contents(home)])


def present_home_contents(home: Path) -> str:
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in home.iterdir())
    if not entries:
        return "Currently in your home dir: (empty — nothing to migrate yet)."
    listed = ", ".join(entries)
    return f"Currently in your home dir (migrate the real ones): {listed}"


def build_brief(home: Path) -> str:
    sections: list[str] = ["# Chief-of-Staff session brief", ""]
    sections.append(tracked_location(home))

    standing = standing_brief(home)
    if standing:
        sections += ["", "## Standing brief", "", standing]

    sections += ["", "## Runbooks", "", runbook_list(home)]
    return "\n".join(sections)


def tracked_location(home: Path) -> str:
    target = home.resolve()
    root = git_toplevel(target)
    if root:
        return f"Home is tracked in git at `{root}` (via `{home}` -> `{target}`)."
    return f"Home resolves to `{target}` (via `{home}`), but no git repo was detected there."


def git_toplevel(path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    top = out.stdout.strip()
    return top or None


def standing_brief(home: Path) -> str:
    """Optional agent-authored note re-surfaced every session.

    Drop reminders, cron status, or proactive follow-ups in ``BRIEF.md`` and
    they resurface here each session without touching standing instructions.
    """
    brief = home / "BRIEF.md"
    if brief.exists() and brief.read_text().strip():
        return brief.read_text().strip()
    return ""


def runbook_list(home: Path) -> str:
    """Compact index of this agent's runbooks.

    Read-only on purpose: the ``runbook`` skill owns the store (seeding,
    capture, lifecycle, validation). This only surfaces what is already there,
    so the brief stays fast and side-effect-light. Use
    ``runbooks.py --runbooks-dir <dir> show <slug>`` to load a body.
    """
    runbooks_dir = home / "runbooks"
    if not runbooks_dir.is_dir():
        return NO_RUNBOOKS

    entries = []
    for path in sorted(runbooks_dir.glob("*.md")):
        attrs = parse_frontmatter(path.read_text(encoding="utf-8"))
        if attrs.get("status") == "retired":
            continue
        entries.append(f"- {attrs.get('slug', path.stem)}: {attrs.get('summary', '(no summary)')}")

    if not entries:
        return NO_RUNBOOKS
    return "\n".join(entries)


NO_RUNBOOKS = (
    "(no runbooks yet — the `runbook` skill seeds `unknown-task` and captures "
    "new ones into `<home>/runbooks/` once a task shape is clear)"
)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Top-level scalar keys from a runbook's YAML frontmatter.

    Deliberately minimal: the brief only needs `slug`, `summary`, and `status`,
    so nested values (e.g. `triggers:`) are skipped rather than parsed.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    attrs: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip("'\"")
        if value:
            attrs[key.strip()] = value
    return attrs


if __name__ == "__main__":
    raise SystemExit(main())
