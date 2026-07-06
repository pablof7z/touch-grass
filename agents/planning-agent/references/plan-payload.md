# Planning PR Payload

Pass a JSON object to `agents/planning-agent/scripts/publish_plan_pr.py`, or to
the installed copy at `~/.agents/homes/planning-agent/scripts/publish_plan_pr.py`.

## Required Fields

- `title`: Human-readable plan title.
- `high_level_plan`: Concise plan body. Keep under 450 words. A string is accepted for compatibility, but bullets or `high_level_points` are preferred.
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
- `high_level_points`: List of strings or objects for the visible high-level bullets. Object fields: `label`, `text`, and optional `highlight`.
- `diagram_mermaid`: Mermaid source without surrounding backticks. Kept for compatibility; prefer `boundary_visualization` for new payloads.
- `boundary_visualization`: Structured boundary display for the hosted page and PR. Supported fields:
  - `title`: Defaults to `Boundary Changes`.
  - `description`: One or two sentences explaining what the reader should notice.
  - `changes`: List of strings or objects with `label`, `description`, and `status`.
  - `current_diagram_mermaid`: Mermaid source for the current state.
  - `proposed_diagram_mermaid`: Mermaid source for the proposed state.
  - `views`: Additional Mermaid views as objects with `label` and `diagram_mermaid`.
  - `graph`: D3-rendered graph data with `nodes` and `links`.
- `boundary_changes`: Top-level alias for `boundary_visualization.changes`.
- `boundary_graph`: Top-level alias for `boundary_visualization.graph`.
- `rule_adr_violation`: Alias for `possible_rule_loosening`.
- `ready_comment`: Comment to use when `decision` is `ready`.
- `pause_comment`: Comment to use when `decision` is `pause`.
- `pr_title`: Defaults to `Plan: <title>`.
- `blossom_server`: Defaults to `https://blossom.primal.net`.

Boundary status values drive color coding and legend labels: `new`, `changed`, `removed`, `existing`, `external`, and `risk`. Common aliases such as `added`, `updated`, and `deleted` are normalized.

Boundary graph shape:

```json
{
  "nodes": [
    { "id": "Mobile", "label": "Mobile intake", "status": "existing" },
    { "id": "Outbox", "label": "Encrypted outbox", "status": "new" }
  ],
  "links": [
    { "source": "Mobile", "target": "Outbox", "label": "writes", "status": "new" }
  ]
}
```

## Example

```json
{
  "title": "Field Clinic Intake Sync",
  "slug": "field-clinic-intake-sync",
  "high_level_plan": "Add an offline-first intake lane for field clinic teams...",
  "high_level_points": [
    { "label": "Client boundary", "text": "Mobile clients write signed packets into an encrypted local outbox.", "highlight": true },
    { "label": "Server boundary", "text": "The sync API validates, deduplicates, and stages packets for clinical review." }
  ],
  "boundary_visualization": {
    "description": "The new boundary is the outbox-to-sync lane; patient records stay behind the existing review path.",
    "changes": [
      { "status": "new", "label": "Encrypted outbox", "description": "Adds a durable local handoff boundary." },
      { "status": "existing", "label": "Patient record", "description": "Still updates only after review." }
    ],
    "proposed_diagram_mermaid": "flowchart LR\n  Mobile[Mobile intake] --> Outbox[Encrypted outbox]\n  Outbox --> API[Sync API]\n  API --> Review[Review queue]\n  Review --> Record[Patient record]"
  },
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
