# Planning Agent

These notes capture the GitHub planning PR workflow for agent-assigned work.

Current position: this workflow is an operational agent profile, not a skill. The
old `gh-plan-pr` skill concept is retired and replaced by
`agents/planning-agent/agent.yaml`, with agent-owned scripts and references.
This keeps planning judgment, workflow, and handoff behavior in the agent
definition while deterministic publishing mechanics remain in a bundled script.

## User-Specified Flow

The user specified:

- When new work is assigned to an agent, it should be evaluated against criteria.
- If a task is complex, the agent should create a PR with an architectural/design plan.
- The PR body should be concise, bullet-pointed, and skimmable.
- More nuanced and detailed planning belongs in a documentation file committed in the PR.
- The PR template should be much more minimal: only the very high-level material at the top.
- The published hosted page should carry the weight of the plan data.
- Planning PRs should open as draft PRs to avoid CI running.

Required plan structure:

1. Very high level, maximum 450 words, optionally with Mermaid or a flowchart when it helps express boundaries.
2. A TTS version of the plan.
3. Whether the plan violates existing repo rules or ADRs.
4. If it could violate a rule or ADR, whether loosening or breaking that rule would improve the design.
5. Whether a rule should be tightened or a new rule introduced.
6. Alternative designs considered.
7. Certainty percentage that this is the right approach.

## Proceed Or Pause Behavior

The user specified:

- If the plan has high certainty or a relatively small surface, add a follow-up comment briefly explaining why it is a slum-dunk.
- That comment should include `Ready to implement`.
- If the agent has not been told otherwise, it should proceed to implementation right away.
- Implementation may be delegated to another agent, possibly using a slightly less capable model.
- The planning workflow should err on the side of continuing implementation, not pausing for architectural plan feedback.

Pause cases should be limited to things like:

- Large architectural impact.
- A situation where a more robust or cleaner design would be possible if an existing rule or ADR were relaxed.
- A powerful alternative design that is a strong competitor to the proposed approach.

When pausing:

- The agent should trigger another agent for feedback.
- Ideally the feedback agent uses a different provider, for example Anthropic Opus or Fable if the current agent is running an OpenAI model.
- The mechanism for communicating with or launching that other agent should not be over-specified in the publisher script; the planning agent should use the coordination mechanism available in its runtime.

## Hosted Plan Pages

The user accepted the GitHub Pages approach:

- "the gh-pages approach is very solid"
- The planning workflow should include GitHub Pages as part of the output.
- The agent should call a script to generate the PR and hosted plan artifacts.

The underlying product idea:

- GitHub PR markdown is not the rich rendering surface.
- The PR should stay concise.
- GitHub Pages can host the richer human-facing plan page.

## Issue 1 Rendering Feedback

The user later clarified that the first hosted plan page made the boundary diagram too hard to understand:

- A bare boundary diagram is not enough. Important boundary changes should be highlighted through color, annotation, or both.
- In some cases, the boundary view should support richer generated visualization such as D3-style graph data, current versus proposed state, or a comparison toggle.
- Boundary visuals should be possible to enlarge or open fullscreen because embedded diagrams can be too small.
- The high-level plan should not render as a large paragraph. It should be scannable as bullets or similarly structured highlights.

Product position: agents should provide structured planning content and judgment, including which boundaries matter and what changed. The publisher script should turn that structure into readable PR markdown and a richer hosted page with annotations, comparison views, fullscreen behavior, and optional graph rendering.

## Agent Replacement

The user clarified that `gh-plan-pr` should not exist as a skill. The durable
artifact should be a planning agent installable through `awesome-agents`.

The planning agent owns:

- when a planning PR is warranted,
- repository context scanning,
- plan content and boundary judgment,
- ready versus pause decisions,
- implementation or review handoff.

The bundled script owns:

- generated narration,
- audio conversion and upload,
- GitHub Pages rendering,
- draft PR creation or update,
- ready/pause comments.

Primitive reusable skills such as standalone GitHub Pages publishing or
TTS narration may exist later, but they are not required for this first
replacement. Avoid fragmenting the workflow before reuse is proven.

## TTS And Media Boundary

The user specified:

- The agent should not know about MP3, Blossom, or media implementation details.
- The agent should only know that it must provide a `TTS-friendly-version`.
- The script should handle audio generation, conversion, upload, GitHub Pages, and PR generation.
- MP3 files should not be committed to the repo.
- Audio should be uploaded to Blossom.
- The user suggested `nak` likely supports Blossom upload.
- The upload target discussed was `blossom.primal.net`.

The product boundary:

- Agents provide structured content and judgment.
- Scripts own deterministic mechanics and incidental implementation details.

## Publisher Script Expectations

The user specified that the planning agent's `scripts/publish_plan_pr.py` should:

- Check whether required commands are available.
- If a required command is missing, naively try a one-shot install depending on architecture and platform, especially Linux or macOS.
- If the command is still unavailable, return the issue to the agent.
- Example failure: "`nak` is not available -- please install it from <url>`."

The user also accepted that:

- The script should be the interface the agent calls.
- The script can require the `TTS-friendly-version` field and hide all media and publishing details behind that interface.
