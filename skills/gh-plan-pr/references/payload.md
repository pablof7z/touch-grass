# `publish_plan_pr.py` Payload

Pass a JSON object to `scripts/publish_plan_pr.py`.

## Required Fields

- `title`: Human-readable plan title.
- `high_level_plan`: Concise plan body. Keep under 450 words.
- `tts_friendly_version`: Spoken version of the plan. Avoid file paths, dense code identifiers, and visually dependent phrasing.
- `rules_adr_check`: String or list of strings.
- `possible_rule_loosening`: String or list of strings.
- `possible_rule_tightening`: String or list of strings.
- `alternatives_considered`: String or list of strings.
- `certainty_percent`: Integer from 0 to 100.
- `decision`: `ready` or `pause`.
- `detailed_plan`: Longer Markdown plan with rollout, validation, rollback, observability, migration, risks, and open questions as relevant.

## Optional Fields

- `slug`: URL and folder slug. Derived from `title` when omitted.
- `base_branch`: Defaults to `main`.
- `branch`: Defaults to `plan/<slug>`.
- `summary`: Short hero summary for the hosted plan page. Defaults to `high_level_plan`.
- `diagram_mermaid`: Mermaid source without surrounding backticks.
- `rule_adr_violation`: Alias for `possible_rule_loosening`.
- `ready_comment`: Comment to use when `decision` is `ready`.
- `pause_comment`: Comment to use when `decision` is `pause`.
- `pr_title`: Defaults to `Plan: <title>`.
- `blossom_server`: Defaults to `https://blossom.primal.net`.

## Example

```json
{
  "title": "Field Clinic Intake Sync",
  "slug": "field-clinic-intake-sync",
  "high_level_plan": "Add an offline-first intake lane for field clinic teams...",
  "diagram_mermaid": "flowchart LR\n  Mobile --> Outbox\n  Outbox --> API",
  "tts_friendly_version": "This plan adds offline intake syncing for field clinic teams...",
  "rules_adr_check": [
    "Satisfies ADR 0001 because boundaries are explicit.",
    "Satisfies ADR 0003 because review and promotion are auditable."
  ],
  "possible_rule_loosening": "No rule needs loosening.",
  "possible_rule_tightening": "Consider requiring offline workflows to define idempotency and conflict policy.",
  "alternatives_considered": [
    "Direct mobile write: simpler, weaker conflict control.",
    "General offline framework: broader dependency surface."
  ],
  "certainty_percent": 88,
  "decision": "ready",
  "detailed_plan": "## Summary\n\nLonger implementation plan..."
}
```
