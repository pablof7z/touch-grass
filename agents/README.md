# Agent Definitions

This directory contains source-of-truth agent profile definitions and harness-specific adapters.

There is not yet a single well-known profile format that is portable across the major coding-agent harnesses. The current practical pattern is:

- Keep a neutral source definition in `agents/profiles/`.
- Generate or maintain harness adapters from that source.
- Keep adapter files thin and obvious so drift is easy to review.

## Layout

- `profiles/*.agent.yaml`: neutral, repo-owned profile definitions.
- `adapters/codex/*.config.toml`: examples for Codex named profiles. Codex profile files are user-level overlays, so these are templates to copy into `$CODEX_HOME`.
- `.claude/agents/*.md`: Claude Code project subagents.
- `.opencode/agents/*.md`: OpenCode project agents.

## Compatibility Notes

- `AGENTS.md` is the broadest repo-level instruction surface.
- Skills are the broadest reusable workflow surface.
- Claude Code project subagents live in `.claude/agents/` and are Markdown files with YAML frontmatter.
- OpenCode project agents can live in `.opencode/agents/` as Markdown files with YAML frontmatter.
- Codex has `--profile`, but named profiles are loaded from user-level `$CODEX_HOME/<profile>.config.toml`, not from a portable project-local profile folder.
- Grok Build is young and should be treated as compatibility-by-convention for now: keep relying on `AGENTS.md` and skills until it publishes a stable project agent profile format.

## Source Definition Rules

- Treat `profiles/*.agent.yaml` as canonical.
- Prefer capability classes over vendor-specific model names in source definitions.
- Put harness-specific model IDs, permission modes, and tool names only in adapters.
- Keep every adapter traceable to a source profile with `source_profile`.
