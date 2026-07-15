---
slug: unknown-task
summary: Use when no existing runbook clearly matches the delegated task.
triggers:
  - The request represents a new task type.
  - Existing runbooks differ materially in intent, outcome, or authority.
  - The closest runbook is stale or too vague to trust.
status: default
created: 2026-07-15
updated: 2026-07-15
---

# Unknown Task

## Approach

1. Understand the requested outcome and inspect available context.
2. Clarify only when the answer materially changes safety, authority, priority, access, money, reputation, external commitments, irreversible state, or the definition of done.
3. For reversible and low-risk choices, make reasonable assumptions and continue.
4. Complete enough of the work to discover the real procedure.
5. Capture a runbook only when the task is likely to recur or a durable non-obvious lesson was learned.
6. Review the run and incorporate only future-relevant lessons.

## Bias

Useful work comes before process maintenance. The user should not have to design the runbook merely to delegate the first instance of a task.
