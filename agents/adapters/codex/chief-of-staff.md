---
slug: chief-of-staff
profile: ../../profiles/chief-of-staff.md
harness: codex
model: gpt-5.5
reasoning_effort: high
required_skills:
  - tenex-edge
---

# Codex Adapter: Chief Of Staff

Load the canonical profile at `agents/profiles/chief-of-staff.md`.

This adapter installs the chief-of-staff as a Codex agent profile. It must not
be treated as a skill.

At the start of a session, run the workflow listing script from the installed or
checked-out `touch-grass` source when available:

```bash
python3 agents/scripts/chief-of-staff/workflows.py list
```

Use tenex-edge as the coordination fabric when the task involves other agents or
cross-project communication.

Run with a high-reasoning Codex configuration:

- Model: `gpt-5.5`
- Reasoning effort: `high`

This profile is for chief-of-staff coordination across projects and agents. It
must maintain its own notes and workflows under:

`~/.agents/homes/chief-of-staff/`
