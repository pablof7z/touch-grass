# Operational Agent Profiles

These notes capture product thinking about reusable operational agent profiles in `touch-grass`.

## Cross-Harness Profile Question

The user asked whether there is a well-known structure to organize profile definitions compatible with different harnesses, mentioning:

- Codex `--profile`.
- Claude.
- OpenCode.
- Grok CLI.

## Rejected Meta Profile

A meta profile for working on `touch-grass` itself was created and then rejected.

The user clarified:

- The created profile was a meta profile for working on `touch-grass` itself.
- It was not an agent that would work within the `touch-grass` flow.
- The user then requested removing that profile from the repo.

Product implication:

- Future agent profiles, if added, should likely be operational agents inside the `touch-grass` flow, not maintainers for the repo itself, unless explicitly requested.

## Local Setup Boundary

Explicit non-goal:

- Do not treat reusable agent profiles as local machine setup.
- They belong in `~/touch-grass`.
- They should not install TENEX agents, mutate `~/.tenex`, or pre-create agent home directories on the author's computer.

## iOS Operational Agent Profiles

The user requested two reusable Codex-oriented operational profiles:

- `ios-tester`: an execution-focused black-box iOS tester using `xcodebuildmcp-cli`, a simple `gpt-5.5` medium-effort model, tenex-edge replies, and per-project notes under `~/.agents/homes/ios-tester/<project>/notes`.
- `ios-ux-ui-critic`: the same simulator and tenex-edge flow, but focused on UX/UI product critique with a stronger model setting such as `gpt-5.5` xhigh or Opus, and notes under `~/.agents/homes/ios-ux-ui-critic/<project>/notes`.

The user emphasized that both profiles must be reusable artifacts in `~/touch-grass`, not configuration applied to the current computer. The profiles must say that each runtime agent manages its own home directory and notes.

Both agents should avoid reading code entirely. They should interact with the installed app like users through an iOS simulator, use their own notes as prior black-box memory, and report back through tenex-edge while mentioning whoever asked for the work.

## Chief Of Staff Profile

The chief of staff is also a reusable operational agent profile.

Implementation correction:

- It should live under `agents/profiles/chief-of-staff.md`.
- Harness adapters should live under `agents/adapters/<harness>/`.
- It must not be modeled as a skill.
- Supporting workflow mechanics should live under `agents/scripts/chief-of-staff/` and `agents/references/chief-of-staff/`.
