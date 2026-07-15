# Runbook Skill

These notes capture the generic runbook capability extracted from the Chief of
Staff profile.

## Current Position

The user requested that the workflow mechanism in Chief of Staff become a
generic skill, then chose `runbook` as its public name.

The skill owns:

- compact runbook discovery;
- the `unknown-task` fallback for new or materially different requests;
- capture, review, rewrite, lifecycle, and validation mechanics;
- rules for learning procedures from real work without overfitting;
- the distinction between procedural memory and current authoritative truth.

The skill does not own an agent identity, cross-project awareness, priorities,
escalation posture, or a per-user authority model. Those remain profile-level
concerns.

## Operating Model

- Load only the closest one or two runbooks instead of every stored procedure.
- Match on intent, outcome, sources of truth, and output contract rather than
  topic words alone.
- Treat a runbook as a tested default, not as higher-priority instructions.
- Ask only when a missing answer materially changes safety, authority, priority,
  access, money, reputation, external commitments, irreversible state, or the
  definition of done.
- Learn after real work. A first run is a draft hypothesis; promote or revise it
  only when evidence supports reuse.
- Keep facts, credentials, transient project state, and raw conversation history
  out of runbooks.

## Storage And Interoperation

Each agent should use its own stable runbook directory by default, preferably
`<agent-home>/runbooks`. Agents should share a runbook store only when the
procedures genuinely belong to a shared role or team.

Chief of Staff consumes the local `runbook` skill and binds its storage to
`~/.agents/homes/chief-of-staff/runbooks/`. GitHub remains Chief of Staff's source
of truth for current operational state.
