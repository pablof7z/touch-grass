# touch-grass

`touch-grass` is a public set of skills and operational agent profiles for agents that need more autonomy, better agency, and cleaner human collaboration.

The project bias is practical: agents should make progress by default, publish useful artifacts, ask for human input only when it matters, and leave a clear trail of decisions.

## Install Skills

Inspect available skills:

```bash
npx --yes skills add pablof7z/touch-grass --list
```

Install `gh-plan-pr` globally:

```bash
npx --yes skills add pablof7z/touch-grass --skill gh-plan-pr --global --yes
```

Install `gh-plan-pr` into the current project:

```bash
npx --yes skills add pablof7z/touch-grass --skill gh-plan-pr --yes
```

Restart the agent session after installing so the new skill is loaded.

`npx skills` installs skills. Operational agents under `agents/<slug>/` are separate artifacts.

## Agent Profiles

### `chief-of-staff`

Maintains a cross-project operating picture for agent work. It tracks projects, decisions, open loops, linked repositories, active agents, and daily reports so the user can focus on judgment instead of coordination overhead.

The tracking repo stays organized around projects and decisions, with the current-day report linked from its top-level `README.md`.

It also maintains script-managed workflows under the chief of staff's home directory so new request types become repeatable without making the user manage process.

The reusable agent definition lives at `agents/chief-of-staff/agent.yaml`.

### `ios-tester`

Black-box iOS testing profile that uses simulator tooling and project notes to test installed apps like a user.

### `ios-ux-ui-critic`

Black-box iOS UX/UI critique profile that uses simulator tooling and project notes to inspect the installed app experience.

## Skills

### `gh-plan-pr`

Publishes planning PRs for complex assigned work. The agent supplies structured planning content and a TTS-friendly narration; the bundled script handles the mechanics:

- dependency checks and naive one-shot installs,
- TTS generation,
- audio upload to Blossom,
- GitHub Pages plan rendering,
- planning PR creation or update,
- proceed/pause PR comments.

The agent does not need to know about audio formats, Blossom, `nak`, or GitHub Pages internals.

## Repository Goals

- Build skills and operational agent profiles that compose well with each other.
- Maximize useful autonomy while preserving human review for high-impact decisions.
- Move deterministic mechanics into scripts.
- Keep skill instructions small, sharp, and easy for another agent to apply.
