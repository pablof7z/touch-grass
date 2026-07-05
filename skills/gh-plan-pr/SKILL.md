---
name: gh-plan-pr
description: Publish minimal draft GitHub planning pull requests for complex assigned work. Use when an agent receives implementation work that may need architecture/design review, rule or ADR analysis, a high-level PR body, a detailed plan document, TTS-friendly narration, hosted GitHub Pages presentation, proceed/pause decisioning, or a "Ready to implement" follow-up comment before implementation.
---

# GitHub Plan PR

## Overview

Use this skill when assigned work may be complex enough to deserve a draft planning PR before implementation. The agent supplies judgment and structured plan content; `scripts/publish_plan_pr.py` handles publishing mechanics including generated narration, hosted plan pages, minimal PR body creation, and follow-up comments.

## Decision Rule

Proceed directly to implementation for small, local, low-risk changes. Use this skill when one or more apply:

- The task changes major architecture, ownership boundaries, persistence, security posture, data model, or user-visible workflows.
- The task may violate or require reinterpreting repository rules, ADRs, or established patterns.
- A cleaner design may require loosening an existing rule.
- A new rule or ADR may be needed.
- A powerful alternative design deserves explicit comparison.
- Rollout, rollback, migration, observability, or auditability needs planning before code changes.

Err toward continuing implementation after publishing the plan. Pause only for large architectural impact, meaningful rule/ADR tension, or a strong alternative design that could materially outperform the proposed approach.

## Workflow

1. Scan the repository for `AGENTS.md`, `README*`, `CONTRIBUTING*`, `docs/`, ADRs, architecture docs, rules, and nearby implementation patterns.
2. Decide whether a planning PR is warranted.
3. Build a JSON payload matching `references/payload.md`.
4. Include a `tts_friendly_version`; do not reason about audio formats, media hosting, Blossom, `nak`, or GitHub Pages.
5. Run:

```bash
python3 skills/gh-plan-pr/scripts/publish_plan_pr.py plan.json
```

6. Read the script's JSON result. If `ok` is false, report the returned issue or fix the missing input/dependency if it is safe and obvious.
7. If the script reports a ready decision, proceed to implementation unless the user instructed otherwise.
8. If the script reports a pause decision, request independent architecture feedback through the available cross-agent review mechanism when one exists.

## Required Plan Shape

Provide these fields for the hosted plan page and detailed plan document:

- Very high-level plan, maximum 450 words.
- Optional Mermaid diagram when it clarifies boundaries or flow.
- TTS-friendly version written for spoken audio.
- Existing rule/ADR compliance.
- Whether violating or loosening a rule/ADR might improve the design.
- Whether tightening or adding a rule should be considered.
- Alternatives considered.
- Certainty percentage.
- Decision: `ready` or `pause`.

Put nuanced implementation details, rollout, validation, rollback, migration, observability, and open questions in `detailed_plan`.

The generated GitHub PR body should stay minimal: very high-level plan, optional boundary diagram, hosted plan page link, detailed plan link, narration link, certainty, and decision. The hosted page carries the deeper data.

## Publisher Script Boundary

Treat `scripts/publish_plan_pr.py` as the only interface for publishing. The script owns:

- command availability checks,
- naive one-shot dependency installation attempts on macOS and Linux,
- narration generation from `tts_friendly_version`,
- audio conversion and upload,
- GitHub Pages rendering,
- minimal draft PR body generation,
- PR creation or update,
- proceed/pause comments.

Do not duplicate those mechanics manually unless the script returns a clear blocker.

## References

- Read `references/payload.md` when constructing or debugging the JSON payload.
