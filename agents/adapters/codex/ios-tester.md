---
slug: ios-tester
profile: ../../profiles/ios-tester.md
harness: codex
model: gpt-5.5
reasoning_effort: medium
required_skills:
  - xcodebuildmcp-cli
  - tenex-edge
---

# Codex Adapter: iOS Tester

Load the canonical profile at `agents/profiles/ios-tester.md`.

Run with a small, execution-focused Codex model configuration:

- Model: `gpt-5.5`
- Reasoning effort: `medium`

This profile is for black-box iOS app execution through `xcodebuildmcp` and
tenex-edge reporting. It must not read code or pre-create any local agent home
directories. At runtime, the agent manages its own notes under:

`~/.agents/homes/ios-tester/<project>/notes`
