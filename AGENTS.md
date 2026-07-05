# AGENTS.md

## Project Overview

`touch-grass` is a public collection of interoperable skills for increasing agent autonomy, agency, and human collaboration. The goal is to make agents better at doing real work end to end while keeping humans in the loop at the right moments: when judgment, architectural feedback, approval, or social coordination matters.

The repository should grow as a coherent set of skills that work well together rather than as isolated utilities. Prefer skill boundaries that let one skill produce structured output another skill can consume.

## Repository Layout

- `skills/<skill-name>/SKILL.md`: Required skill instructions and frontmatter.
- `skills/<skill-name>/scripts/`: Deterministic automation that agents should call instead of reimplementing.
- `skills/<skill-name>/references/`: Detailed schemas and workflow references loaded only when needed.
- `skills/<skill-name>/agents/openai.yaml`: UI-facing metadata for the skill.
- `agents/profiles/*.agent.yaml`: Neutral source definitions for reusable agent profiles.
- `.claude/agents/` and `.opencode/agents/`: Harness-specific adapters generated or maintained from `agents/profiles/`.

## Skill Design Principles

- Keep agent-facing instructions concise.
- Put fragile, repetitive, or environment-specific mechanics in scripts.
- Let agents handle judgment and content; let scripts handle publishing, rendering, uploads, and command orchestration.
- Return structured errors from scripts so agents can recover or ask humans for specific help.
- Do not require agents to know incidental implementation details such as audio formats, hosting services, or upload protocols when a script can own them.

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
