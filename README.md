# touch-grass

`touch-grass` is a public set of skills and operational agent profiles for agents that need more autonomy, better agency, and cleaner human collaboration.

The project bias is practical: agents should make progress by default, publish useful artifacts, ask for human input only when it matters, and leave a clear trail of decisions.

## Install Agent Profiles

Inspect available profiles:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

Install the planning agent for Codex:

```bash
npx awesome-agents add pablof7z/touch-grass --agent planning-agent --harness codex --global
```

Install another profile or harness by changing `--agent` and `--harness`:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

`awesome-agents` installs operational agent profiles from `agents/<slug>/`.
Agent-owned scripts and references are installed under
`~/.agents/homes/<slug>/`.

## Agent Profiles

### `chief-of-staff`

Maintains a cross-project operating picture for agent work. It tracks projects, decisions, open loops, linked repositories, active agents, and daily reports so the user can focus on judgment instead of coordination overhead.

The tracking repo stays organized around projects and decisions, with the current-day report linked from its top-level `README.md`.

It also maintains script-managed workflows under the chief of staff's home directory so new request types become repeatable without making the user manage process.

The reusable agent definition lives at `agents/chief-of-staff/agent.yaml`.

### `planning-agent`

Creates architecture/design planning PRs for complex implementation work. It
scans repository constraints, writes a concise plan payload, renders hosted
review artifacts through its bundled publisher script, opens or updates a draft
PR, and decides whether implementation should proceed or pause for feedback.

The planning behavior is an operational agent profile, not a skill. Its reusable
definition lives at `agents/planning-agent/agent.yaml`, with agent-owned support
material under `agents/planning-agent/scripts/` and
`agents/planning-agent/references/`.

### `ios-tester`

Black-box iOS testing profile that uses simulator tooling and project notes to test installed apps like a user.

### `ios-ux-ui-critic`

Black-box iOS UX/UI critique profile that uses simulator tooling and project notes to inspect the installed app experience.

## Repository Goals

- Build skills and operational agent profiles that compose well with each other.
- Maximize useful autonomy while preserving human review for high-impact decisions.
- Move deterministic mechanics into scripts.
- Keep skill instructions small, sharp, and easy for another agent to apply.
