# Foundations

These notes capture the base product direction for `touch-grass`.

## Core Direction

- The repo is named `touch-grass`.
- It is public.
- It should contain "these type of skills."
- The artifacts are "skills," not "Codex skills."
- The skills should interoperate well together.
- The aim is "maximum autonomy/agency/human-collaboration."

## Repository Shape

The user requested:

- Create a public GitHub repo named `touch-grass`.
- Add `AGENTS.md`.
- The `AGENTS.md` should mention the goal of constructing a public repo of a "touch grass" set of skills.
- Those skills should interoperate well.
- The aim is maximum autonomy, agency, and human collaboration.
- Create, commit, publish, and document the first skill in the repo.

The user later asked how to install it with `npx skills`.
The user then requested adding the `npx skills` install commands to the README.

The user later clarified that the repository can also contain operational agent
profiles. Those profiles must not be collapsed into skills because a profile is
an agent identity and operating model, while a skill is a loadable capability or
workflow.

The user later clarified a stronger boundary for the planning PR workflow:
`gh-plan-pr` should not exist as a skill. It should be replaced by a planning
agent profile installed through `awesome-agents`, with any scripts and references
owned by that agent profile.

## Positioning Corrections

The user corrected:

- Do not call them "Codex skills."
- Call them "skills."

The user also said:

- "the readme is a sales page"

This is captured as a product signal, not a completed positioning rewrite.

The user later pointed to the Taste Skill README as a stronger public-facing
reference because it is more marketable and speaks to the user more directly.
The requested README direction is to reorganize the page around a clear promise,
fast install path, practical artifact chooser, and cleaner public presentation.

## Product Memory Shape

The user later corrected the product-notes structure:

- `docs/product` should not become a single massive notes file.
- Nuance, details, and explicit user statements should be reflected in self-organizing notes.
- Product notes should be split by product area so future agents can load the relevant context.
