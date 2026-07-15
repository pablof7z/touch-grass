---
name: runbook
description: "Learn durable procedures from repeated delegation. Use when an agent should recognize a recurring request, recover how this user expects it done, execute from a lightweight runbook, or turn a successful new task into reusable procedural memory without making the user design the process."
---

# Runbook

Turn repeated requests into lightweight, revisable procedures learned from real work.

Runbook memory records **how to do a kind of task**. It is not a source of truth for current project state, facts, priorities, credentials, or permissions.

## Storage

Choose one stable runbook directory before using the script:

1. Prefer `<agent-home>/runbooks` when the agent has a durable home.
2. Otherwise use a stable agent-specific directory under `~/.agents/homes/<agent-slug>/runbooks`.
3. Share a runbook directory across agents only when the user deliberately wants shared procedures.

Pass it with `--runbooks-dir` or set `RUNBOOK_DIR`. Do not place secrets in runbook files.

## Operating Loop

### 1. Orient compactly

Run:

```bash
python3 scripts/runbooks.py --runbooks-dir <dir> list --json
```

Read the compact index. Do not load every runbook body. Select the closest runbook by intent, expected outcome, sources of truth, and output contract—not merely by topic words. Load at most the best one or two candidates with `show`.

Use `unknown-task` when no runbook clearly applies, a candidate is stale, or applying it would require guessing across materially different task shapes.

### 2. Execute from memory, not under its authority

Treat a matched runbook as a tested default, not an instruction hierarchy.

Current user instructions, host rules, repository instructions, live authoritative systems, safety constraints, and explicit permissions override runbook memory. Verify unstable or high-impact details at execution time.

Adapt the procedure when the present case differs. Preserve useful uncertainty and conditional branches instead of forcing every run into one rigid checklist.

### 3. Keep judgment gates narrow

For simple, reversible, low-risk work, make reasonable assumptions and proceed.

Ask before continuing only when the missing answer materially changes safety, authority, priority, access, money, reputation, external commitments, irreversible state, or the definition of done. Continue all independent safe work while a gated branch waits.

When escalating, bring the exact decision, relevant context, options, recommendation, and what remains unblocked.

### 4. Learn after doing

After a run, update runbook memory only when a durable lesson was earned. Useful signals include:

- the user corrected the process or output;
- the request is explicitly or predictably recurring;
- the task required a non-obvious sequence, source of truth, tool, handoff, or completion check;
- reusing the procedure would materially reduce future friction.

Do not create runbooks for one-off facts, transient project state, raw conversation summaries, obvious generic steps, or details already owned by a better source of truth.

For a new reusable task:

1. Complete enough of the work to learn the real task shape.
2. Capture a draft runbook with `capture`.
3. Record what actually worked, failed, or required judgment with `review`.
4. Rewrite the canonical body when the review changes future execution; do not leave durable lessons buried only in an append-only log.

For an existing runbook, record only consequential deviations. Do not append ritual reviews after uneventful runs.

### 5. Prevent overfitting and decay

A first run produces a hypothesis, not a law. Keep new runbooks in `draft` status until either the user confirms the procedure or a later run validates it.

When evidence conflicts:

- distinguish stable preference from one-case necessity;
- encode conditions and alternatives where both are valid;
- retain explicit uncertainty when the right rule is not known;
- retire or rewrite stale runbooks instead of quietly stacking contradictions.

Use `validate` periodically. Consolidate long review histories into the canonical procedure and keep only review notes that still explain a meaningful decision.

## Commands

```bash
# Seed defaults and list the compact runbook index
python3 scripts/runbooks.py --runbooks-dir <dir> list

# Read one runbook
python3 scripts/runbooks.py --runbooks-dir <dir> show <slug>

# Create a draft from the first meaningful run
python3 scripts/runbooks.py --runbooks-dir <dir> capture <slug> \
  --summary "When to use it" \
  --trigger "A representative request"

# Append a consequential lesson
python3 scripts/runbooks.py --runbooks-dir <dir> review <slug> \
  --note "What should change next time and why"

# Check metadata and duplicate slugs
python3 scripts/runbooks.py --runbooks-dir <dir> validate
```

Read [Runbook Format](references/runbook-format.md) when creating or substantially revising a runbook. Read [Unknown Task](references/default-runbooks/unknown-task.md) when no runbook matches.

## Boundaries

- Do not make runbook maintenance block useful work.
- Do not confuse procedural memory with factual memory or project truth.
- Do not infer broad preferences from a single accidental outcome.
- Do not copy credentials, private tokens, or sensitive raw data into runbooks.
- Do not create multiple near-duplicate runbooks when one conditional runbook is clearer.
- Do not let an old runbook silently override a newer user instruction or authoritative convention.
