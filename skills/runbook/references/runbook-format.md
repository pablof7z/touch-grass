# Runbook Format

Runbook files are Markdown with a small YAML metadata envelope and a free-form body. Keep the envelope predictable; let the body remain as structured or irregular as the real work requires.

## Recommended metadata

```yaml
---
slug: report-bug
summary: Use when the user asks to turn observed product behavior into a filed bug report.
triggers:
  - Report this bug.
  - File the issue we just found.
status: draft
created: 2026-07-15
updated: 2026-07-15
---
```

Required fields:

- `slug`: stable lowercase identifier.
- `summary`: one sentence describing when to use the runbook.

Recommended fields:

- `triggers`: representative phrases or conditions, not an exhaustive classifier.
- `status`: `default`, `draft`, `active`, or `retired`.
- `created` and `updated`: ISO dates.

## Body

Use only the sections that earn their keep. Typical sections are:

- **Outcome** — what useful completion looks like.
- **Inputs** — what must be available or inferred.
- **Sources of truth** — where current facts must be checked.
- **Approach** — the procedure, heuristics, or decision branches.
- **Judgment gates** — what requires permission or human judgment.
- **Output** — destination, shape, audience, and level of polish.
- **Done when** — completion checks and durable side effects.
- **Failure and recovery** — common blockers and safe fallback behavior.
- **Learned preferences** — durable user preferences with conditions where relevant.
- **Review history** — only consequential lessons not yet obvious from the canonical body.

A runbook may contain doubt, exceptions, competing approaches, and unresolved questions. Do not force messy knowledge into a false deterministic checklist.

## What does not belong

Do not store:

- credentials or secrets;
- current issue status, project priorities, or other transient facts;
- copied chat transcripts;
- facts that should be fetched from an authoritative system;
- incidental details from one run presented as universal preference.

Link to authoritative artifacts instead of duplicating them.

## Script inputs and failures

Pass a writable directory with `--runbooks-dir`, set `RUNBOOK_DIR`, or set
`AGENT_HOME` and let the script use its `runbooks/` child. Without any override,
the script uses `~/.agents/homes/runbook/runbooks/`.

- `capture` requires a slug and `--summary`; repeat `--trigger` as needed. Pass
  the body with `--body` or stdin, or let the script create a starter body.
- `rewrite` requires an existing slug and a replacement body from `--body` or
  stdin.
- `review` requires an existing slug and a note from `--note` or stdin.
- `set-status` accepts `draft`, `active`, or `retired`; the bundled
  `unknown-task` default cannot be changed in place.
- `validate --json` returns the report as JSON and exits with status 1 when any
  file is invalid.

The script exits nonzero for missing files, duplicate capture targets, empty
required input, invalid status changes, malformed frontmatter, or filesystem
errors. It does not perform network requests or silently overwrite an existing
runbook unless `capture --force` is explicitly used.

## Lifecycle

- `draft`: learned from one run; usable but provisional.
- `active`: explicitly confirmed or successfully reused.
- `retired`: superseded, misleading, or no longer relevant. Preserve it only when its history remains useful.
- `default`: bundled fallback supplied by the skill.

Promote based on evidence, not elapsed time. Rewrite the canonical body when the procedure changes. Review history should explain evolution, not become the procedure itself.
