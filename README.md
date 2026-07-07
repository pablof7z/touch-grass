<p align="center">
  <strong>touch-grass</strong><br />
  <em>Operational agent profiles for AI teammates that need to plan, test, coordinate, and ship with the right human judgment points.</em>
</p>

<p align="center">
  <a href="#install">Install</a> |
  <a href="#start-here">Start here</a> |
  <a href="#profiles">Profiles</a> |
  <a href="#how-it-works">How it works</a> |
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img alt="Profiles: 4" src="https://img.shields.io/badge/profiles-4-111111" />
  <img alt="Schema: awesome-agents/v1" src="https://img.shields.io/badge/schema-awesome--agents%2Fv1-2f6f5f" />
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-f3c969" />
</p>

# touch-grass

Most agent setups still make the human carry the operating model: when to plan, when to ask, what to publish, how to hand off, and how much autonomy is safe.

`touch-grass` packages that missing layer as reusable operational agent profiles. Each profile defines a real agent identity, its responsibilities, its decision boundaries, the tools it should use, and the artifacts it should leave behind.

Use it when you want agents that can make progress without constant supervision, but still stop for human judgment when it actually matters.

## Install

List the available profiles:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

Install the planning agent for Codex:

```bash
npx awesome-agents add pablof7z/touch-grass --agent planning-agent --harness codex --global
```

Install any profile and harness combination:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Profiles install from `agents/<agent-slug>/`. Agent-owned scripts, references, and runtime notes live under `~/.agents/homes/<agent-slug>/`.

## Start Here

| If you need... | Start with... | Why |
| --- | --- | --- |
| A plan before complex implementation | `planning-agent` | Turns a real task into a reviewable planning PR, then decides whether to proceed or pause. |
| A clear operating picture across agents and projects | `chief-of-staff` | Tracks projects, decisions, blockers, open loops, and agent activity without making the user organize everything. |
| Black-box iOS flow verification | `ios-tester` | Uses an iOS simulator like a user, without reading source code or product docs. |
| iOS UX/UI critique | `ios-ux-ui-critic` | Reviews the experienced app, not the implementation, and reports product-level friction. |

## Profiles

### `planning-agent`

For implementation work that deserves architecture review before code starts.

It scans repo constraints, writes a concise architecture plan, publishes a planning PR with review artifacts, and makes a ready-or-pause recommendation. For small work, it says a planning PR is not warranted and keeps momentum.

Path: `agents/planning-agent/agent.yaml`

### `chief-of-staff`

For users running multiple projects, agents, decisions, and blockers at once.

It keeps a cross-project operating picture, protects the user's attention, tracks open loops, and maintains workflow memory so recurring requests become easier over time.

Path: `agents/chief-of-staff/agent.yaml`

### `ios-tester`

For black-box iOS app testing through the simulator.

It launches the app, exercises the requested flow only through visible UI, captures evidence, and reports pass, fail, blocker, or product feedback. It deliberately avoids source-code inspection.

Path: `agents/ios-tester/agent.yaml`

### `ios-ux-ui-critic`

For product critique of an iOS app experience.

It uses the app like a user and reviews discoverability, hierarchy, navigation, copy, accessibility, platform fit, and cross-screen consistency. It judges the interface the user sees, not the code behind it.

Path: `agents/ios-ux-ui-critic/agent.yaml`

## How It Works

`touch-grass` separates agent profiles from skills.

A profile is an operational identity. It says who the agent is, what it owns, what it must not do, where its source of truth lives, what tools it uses, and when a human should be pulled in.

A skill is a reusable capability an agent can load. Skills belong in `skills/<skill-name>/SKILL.md` when added. Operational agents belong in `agents/<agent-slug>/agent.yaml`.

This boundary matters because a planning agent, chief of staff, tester, or critic is not just a prompt. It is a job with durable responsibilities and a repeatable operating model.

## What Makes A Good Profile

- It solves a real operational problem.
- It has clear authority boundaries.
- It makes low-risk progress without asking for permission.
- It pauses for product, architecture, safety, access, or reputation decisions.
- It leaves durable artifacts instead of hiding important state in chat.
- It pushes deterministic mechanics into scripts.
- It stays portable instead of mutating local machine setup.

## Repository Map

| Path | Purpose |
| --- | --- |
| `agents/<agent-slug>/agent.yaml` | Canonical operational agent definition. |
| `agents/<agent-slug>/scripts/` | Deterministic automation owned by that agent. |
| `agents/<agent-slug>/references/` | Agent-specific schemas, notes, and workflow references. |
| `docs/product/` | Product notes, decisions, corrections, and open questions. |
| `AGENTS.md` | Repository instructions for agents working on this repo. |

## Product Notes

The product model is still evolving. Durable context lives in [`docs/product/`](docs/product/), including:

- [`foundations.md`](docs/product/foundations.md) for public positioning and naming.
- [`operational-agent-profiles.md`](docs/product/operational-agent-profiles.md) for the profile-vs-skill boundary.
- [`planning-agent.md`](docs/product/planning-agent.md) for planning workflow rules.
- [`chief-of-staff.md`](docs/product/chief-of-staff.md) for operating-picture and workflow-memory rules.
- [`open-questions.md`](docs/product/open-questions.md) for unresolved product questions.

## Contributing

Contributions should make agents more useful in real work, not just add another prompt.

Before adding a profile or skill, decide which artifact it really is:

- Add a profile when the artifact defines an agent identity, responsibilities, sources of truth, and operating boundaries.
- Add a skill when the artifact defines a reusable capability or workflow that different agents can load.

Contribution bar:

- Keep instructions concise.
- Put fragile or repetitive mechanics in scripts.
- Return machine-readable errors from scripts when possible.
- Document input shapes and failure modes in `references/`.
- Update `docs/product/` when the product model, positioning, or boundaries change.

## License

MIT
