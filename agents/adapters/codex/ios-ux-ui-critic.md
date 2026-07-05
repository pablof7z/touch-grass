---
slug: ios-ux-ui-critic
profile: ../../profiles/ios-ux-ui-critic.md
harness: codex
model: gpt-5.5
reasoning_effort: xhigh
fallback_model: claude-opus
required_skills:
  - xcodebuildmcp-cli
  - tenex-edge
---

# Codex Adapter: iOS UX/UI Critic

Load the canonical profile at `agents/profiles/ios-ux-ui-critic.md`.

Run with a high-reasoning Codex configuration, or Opus when the harness supports
that model choice:

- Preferred model: `gpt-5.5`
- Reasoning effort: `xhigh`
- Fallback/alternate model: `claude-opus`

This profile is for black-box UX/UI critique through `xcodebuildmcp` and
tenex-edge reporting. It must not read code or pre-create any local agent home
directories. At runtime, the agent manages its own notes under:

`~/.agents/homes/ios-ux-ui-critic/<project>/notes`
