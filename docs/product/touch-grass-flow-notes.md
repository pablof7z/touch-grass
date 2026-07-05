# Touch Grass Flow Notes

These are factual notes from the working conversation. They are intended as raw material for later product formalization and website copy.

## Capture Policy

- Only record things the user explicitly said or explicitly agreed to.
- Do not infer hidden motivations or roadmap.
- Do not turn implementation accidents into product principles unless the user accepted them.
- Use "Open" for unresolved questions.

## Core Direction

- The repo is named `touch-grass`.
- It is public.
- It should contain "these type of skills."
- The skills should interoperate well together.
- The aim is "maximum autonomy/agency/human-collaboration."
- The artifacts are "skills," not "Codex skills."

## First Skill: Planning PR Flow

The first concrete skill is a GitHub planning PR workflow for agent-assigned work.

The user specified:

- When new work is assigned to an agent, it should be evaluated against criteria.
- If a task is complex, the agent should create a PR with an architectural/design plan.
- The PR body should be concise, bullet-pointed, and skimmable.
- More nuanced and detailed planning belongs in a documentation file committed in the PR.

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
- The skill should err on the side of continuing implementation, not pausing for architectural plan feedback.

Pause cases should be limited to things like:

- Large architectural impact.
- A situation where a more robust or cleaner design would be possible if an existing rule or ADR were relaxed.
- A powerful alternative design that is a strong competitor to the proposed approach.

When pausing:

- The agent should trigger another agent for feedback.
- Ideally the feedback agent uses a different provider, for example Anthropic Opus or Fable if the current agent is running an OpenAI model.
- The mechanism for communicating with or launching that other agent should not be specified in this skill; it will be handled by a later skill.

## Hosted Plan Pages

The user accepted the GitHub Pages approach:

- "the gh-pages approach is very solid"
- The skill should include GitHub Pages as part of the workflow.
- The agent should call a script to generate the PR and hosted plan artifacts.

The underlying product idea:

- GitHub PR markdown is not the rich rendering surface.
- The PR should stay concise.
- GitHub Pages can host the richer human-facing plan page.

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

The user specified that `scripts/publish_plan_pr.py` should:

- Check whether required commands are available.
- If a required command is missing, naively try a one-shot install depending on architecture and platform, especially Linux or macOS.
- If the command is still unavailable, return the issue to the agent.
- Example failure: "`nak` is not available -- please install it from <url>`."

The user also accepted that:

- The script should be the interface the agent calls.
- The script can require the `TTS-friendly-version` field and hide all media and publishing details behind that interface.

## Repository And Installation

The user requested:

- Create a public GitHub repo named `touch-grass`.
- Add `AGENTS.md`.
- The `AGENTS.md` should mention the goal of constructing a public repo of a "touch grass" set of skills.
- Those skills should interoperate well.
- The aim is maximum autonomy, agency, and human collaboration.
- Create, commit, publish, and document the first skill in the repo.

The user later asked how to install it with `npx skills`.

## Naming And Positioning Corrections

The user corrected:

- Do not call them "Codex skills."
- Call them "skills."

The user also said:

- "the readme is a sales page"

This is captured as a product signal, not a request that was implemented in that turn.

## Agent Profiles

The user asked whether there is a well-known structure to organize profile definitions compatible with different harnesses, mentioning:

- Codex `--profile`.
- Claude.
- OpenCode.
- Grok CLI.

A meta profile for working on `touch-grass` itself was created and then rejected.

The user clarified:

- The created profile was a meta profile for working on `touch-grass` itself.
- It was not an agent that would work within the `touch-grass` flow.
- The user then requested removing that profile from the repo.

Product implication:

- Future agent profiles, if added, should likely be operational agents inside the `touch-grass` flow, not maintainers for the repo itself, unless explicitly requested.

## Explicit Non-Goals Or Avoidances

- Do not commit generated MP3 files to the repo.
- Do not make the agent reason about MP3, Blossom, `nak`, GitHub Pages internals, or audio hosting details.
- Do not specify the later cross-agent communication mechanism inside `gh-plan-pr`.
- Do not call the project artifacts "Codex skills."
- Do not preserve the removed meta agent profile as part of the repo.

## Open Questions

- What exact Blossom authentication/signing setup should the publisher script assume?
- What should the next operational workflow agents be?
- Should the repo define a neutral operational agent-profile schema later, or wait until a concrete workflow needs one?
- What should the website say beyond the implementation details already committed?
