# AGENTS.md

## Project Overview

`touch-grass` is a public collection of interoperable skills and operational agent profiles for increasing agent autonomy, agency, and human collaboration. The goal is to make agents better at doing real work end to end while keeping humans in the loop at the right moments: when judgment, architectural feedback, approval, or social coordination matters.

The repository should grow as a coherent set of skills and reusable agent profiles that work well together rather than as isolated utilities. Prefer skill boundaries that let one skill produce structured output another skill can consume. Agent profiles are different artifacts: they define reusable agent identities and operating models.

## Repository Layout

- `skills/<skill-name>/SKILL.md`: Required skill instructions and frontmatter.
- `skills/<skill-name>/scripts/`: Deterministic automation that agents should call instead of reimplementing.
- `skills/<skill-name>/references/`: Detailed schemas and workflow references loaded only when needed.
- `skills/<skill-name>/agents/openai.yaml`: UI-facing metadata for the skill.
- `agents/profiles/<profile-name>.md`: Canonical operational agent profile definitions.
- `agents/adapters/<harness>/<profile-name>.md`: Harness-specific installation and runtime notes for a profile.
- `agents/scripts/<profile-name>/`: Deterministic automation that belongs to an agent profile rather than a skill.
- `agents/references/<profile-name>/`: Profile-specific default notes, templates, and workflow references.
- `docs/product/`: Product notes that capture the underlying ideas, decisions, corrections, and changes of mind behind the skills.

## Product Notes

- Keep `docs/product/` up to date as the product model evolves.
- Capture explicit user statements, agreements, corrections, and changes of mind.
- Do not delete older product notes merely because the direction changed. A changed mind is itself useful context because it can reveal a sharper product boundary, pain point, or principle.
- When direction changes, add a clarifying note that records the new position and why the earlier idea was changed or rejected if that reason was stated.
- Do not hallucinate product strategy. Mark extrapolation as a proposal, not a fact.

## Skill Design Principles

- Keep agent-facing instructions concise.
- Put fragile, repetitive, or environment-specific mechanics in scripts.
- Let agents handle judgment and content; let scripts handle publishing, rendering, uploads, and command orchestration.
- Return structured errors from scripts so agents can recover or ask humans for specific help.
- Do not require agents to know incidental implementation details such as audio formats, hosting services, or upload protocols when a script can own them.

## Agent Profile Design Principles

- Do not model an operational agent profile as a skill.
- Put reusable agent identity, responsibilities, source-of-truth rules, and boundaries in `agents/profiles/`.
- Put harness-specific execution details in `agents/adapters/`.
- Put supporting scripts and references under `agents/scripts/` and `agents/references/` unless they are genuinely reusable skills.

## Development Workflow

- Inspect files with `rg` and `sed` before editing.
- Use the repository's normal patch/edit workflow; avoid unrelated churn.
- Validate skill metadata before committing when a compatible validator is available.
- Test scripts with `--dry-run` or sample payloads when available.

## Code Style

- Use Python standard library first for bundled scripts.
- Avoid hidden network side effects in validation paths.
- Keep shell calls explicit and return useful stderr/stdout on failure.
- Prefer JSON for machine-readable script output.

## Pull Request Guidelines

- Keep changes scoped to one skill or one cross-skill convention at a time.
- Include a short explanation of how the skill interoperates with the broader `touch-grass` goal.
- For scripts, document required input shape and failure modes in `references/`.
