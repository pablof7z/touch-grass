<p align="center">
  <img src="assets/readme-banner.png" alt="A patch of real grass in a minimalist white gift box labeled Grass" width="100%" />
</p>

# touch-grass

Operational agents that know their job. Skills that help them learn the work.

AI agents can write code, run tools, and answer questions. The harder problem is
getting them to act like real collaborators: one plans before risky work, one
tests the product like a user, one keeps the operating picture clear, and one
knows when a human decision is actually needed.

`touch-grass` is a public collection of reusable agent profiles for that layer.

<p>
  <img alt="Profiles: 4" src="https://img.shields.io/badge/profiles-4-111111" />
  <img alt="Skills: external" src="https://img.shields.io/badge/skills-external-2f6f5f" />
  <img alt="Schema: awesome-agents/v1" src="https://img.shields.io/badge/schema-awesome--agents%2Fv1-2f6f5f" />
</p>

## Install

List what is available:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

Install a profile:

```bash
npx awesome-agents add pablof7z/touch-grass --agent planning-agent --harness codex --global
```

Install the runbook skill used by compatible profiles:

```bash
npx skills add pablof7z/skills --skill runbook
```

## Shared Skill

### Runbook from `pablof7z/skills`

For recurring work that should get easier each time instead of starting over.

The runbook skill recognizes familiar requests, loads only the closest learned
procedure, and captures durable lessons after real work. Runbooks remember how a
kind of task gets done without pretending to be the source of truth for current
facts, priorities, credentials, or permissions.

It ships from [pablof7z/skills](https://github.com/pablof7z/skills) with an
`unknown-task` fallback and a deterministic script for listing, capturing,
reviewing, rewriting, retiring, and validating runbooks.

## Agents

### Planning Agent

For work that should not start as blind editing.

The planning agent turns a real implementation request into a reviewable planning
PR: what will change, which boundaries matter, which alternatives were rejected,
how certain the plan is, and whether the next move is `ready` or `pause`.

It is for architecture, persistence, migrations, security posture, repo rules,
rollout, rollback, and user-visible workflow changes.

Try the sample planner without publishing anything:

```bash
python3 agents/planning-agent/scripts/publish_plan_pr.py examples/field-clinic-plan.json --dry-run --no-install
```

### Chief Of Staff

For agent-heavy work where the problem is no longer "can an agent do a task?"
but "what is happening across all these tasks?"

The chief of staff keeps the room legible: active projects, decisions, blockers,
open loops, priorities, and the few questions that need the user's judgment.

It is not an implementer by default. It protects attention, keeps durable state
in the right place, and uses the runbook skill to learn repeated requests.

Install it for a tenex-edge flow:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

### iOS Tester

For "test this flow" when the answer has to come from the app, not the source.

The iOS tester launches the product in a simulator, uses visible UI only, and
reports pass, fail, blocker, or product feedback. It is explicitly forbidden
from reading code or product docs to infer behavior.

Use it when you want evidence from the user's path through the app.

### iOS UX/UI Critic

For iOS product feedback from the experience on screen.

The critic reviews hierarchy, navigation, discoverability, copy, accessibility,
platform fit, empty states, errors, and cross-screen consistency. It judges the
interface the user sees, not the implementation behind it.

Use it when a flow technically exists but still feels confusing, heavy, hidden,
or unfinished.

## What This Prevents

- Planning hidden in chat instead of reviewable artifacts.
- Agents asking the human to coordinate every handoff.
- Tests that pass because the agent read the code instead of using the product.
- UX critique that explains implementation instead of user friction.
- Repeated work that never becomes a reusable operating model.

## Profiles Are Not Skills

A profile is an agent identity: job, authority, boundaries, tools, memory, and
escalation rules.

A skill is a reusable capability that different agents can load.

`touch-grass` keeps that boundary because real work needs owners, not just more
instructions.

## Trust Notes

- Installed profiles may write agent-owned state under `~/.agents/homes/`.
- The external runbook script writes only to the selected runbook directory and
  has no network side effects.
- The planning-agent dry run is local and does not push, upload, or create a PR.
- Full planning-agent publishing can create draft PRs, render plan pages, and
  upload narration through its script.
- The iOS profiles are black-box by design.
- No telemetry service is configured in this repo.
- A `LICENSE` file still needs to be added before the license is explicit.

## Contributing

Add profiles for reusable agent jobs. Add reusable capabilities to the shared
skills catalog.

Keep the public promise sharp, put deterministic mechanics in scripts, and update
`docs/product/` when the product model changes.
