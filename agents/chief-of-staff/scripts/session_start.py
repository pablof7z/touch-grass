#!/usr/bin/env python3
"""Chief-of-staff session bootstrap / brief.

Single entrypoint the agent runs at the start of every session. It prepares and
prints the operating context the session needs, deciding *what* to inject:

  * Ensures the home directory exists (upsert).
  * If the home directory is not yet tracked in a git repo — i.e. it is a plain
    directory, not a symlink into a clone — prints ``references/SETUP.md`` so the
    agent walks the user through creating/linking the tracking repo.
  * Otherwise prints the session brief: where home is tracked, the available
    workflows, and any standing brief the agent left for itself.

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
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = AGENT_DIR / "references"
SETUP_DOC = REFERENCES_DIR / "SETUP.md"
DEFAULT_HOME = Path("~/.agents/homes/chief-of-staff").expanduser()

# Reuse the workflow-listing logic instead of duplicating it.
sys.path.insert(0, str(SCRIPT_DIR))
import workflows as wf  # noqa: E402


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

    sections += ["", "## Workflows", "", workflow_list(home)]
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


def workflow_list(home: Path) -> str:
    workflows_dir = home / "workflows"
    wf.ensure_workflows_dir(workflows_dir)
    wf.seed_defaults(workflows_dir)
    workflows = wf.list_workflows(workflows_dir)
    if not workflows:
        return "(no workflows yet — capture one with scripts/workflows.py when a task shape is clear)"
    return "\n".join(f"- {w['slug']}: {w['summary']}" for w in workflows)


if __name__ == "__main__":
    raise SystemExit(main())
