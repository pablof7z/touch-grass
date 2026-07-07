<p align="center">
  <img src="./banner.jpg" alt="Person organizing colorful sticky notes on a wall, used as a banner for the Workflow Memory Agent." width="100%">
</p>

# Chief Of Staff: The Workflow Memory Agent

Your agent team should not make you remember the work.

Chief Of Staff keeps the operating picture current across projects, decisions,
open loops, active agents, blockers, and next actions. It turns repeated asks
into reusable workflows, uses GitHub as the source of truth, and brings you only
the questions that actually need your judgment.

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff
```

For the `touch-grass` TENEX Edge workflow:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

## The Promise

Most agents can do tasks. This one remembers how work moves.

The first time you say, "go do marketing research" or "report a bug," Chief Of
Staff does the work and captures the workflow that made it work. The next time,
it has a named operating pattern: what to check, where truth lives, what output
you expect, which decisions are yours, and which parts should continue without
interrupting you.

No extra admin layer. No demand that you write SOPs before work can happen.
Workflow memory is captured from real work and improved after each run.

## What It Keeps Current

| Operating area | What the agent tracks |
| --- | --- |
| Projects | Active work, linked repositories, owners, next actions, and stale threads. |
| Decisions | Open decisions, resolved choices, dependencies, and who needs to weigh in. |
| Open loops | Follow-ups that are easy to lose in chat, with enough context to resume. |
| Agents | What other agents are doing, where their work lives, and where they overlap. |
| Blockers | Access, authority, priority, reputation, money, and irreversible-state issues. |
| Reports | A current-day operating report linked from the tracking repo README. |

## Workflow Memory

Chief Of Staff maintains user-specific workflows under:

```text
~/.agents/homes/chief-of-staff/workflows/
```

At the start of a session, it lists available workflows and chooses the closest
match. If none fits, it uses `unknown-task`:

1. Refine the ask only as much as the task deserves.
2. Make reasonable assumptions for simple, reversible, low-risk work.
3. Ask only when the answer materially changes priority, authority, access,
   money, reputation, irreversible state, or the definition of done.
4. Capture the initial workflow once the task shape is clear.
5. Execute the work the user wanted.
6. Review the result and update the workflow with lessons, triggers, output
   shape, sources of truth, and user preferences.

The result is memory that stays operational. It is not a pile of notes. It is a
better next run.

## Daily Operating Report

Chief Of Staff keeps a current-day report in the tracking repository and links
it from the top-level `README.md`. The report answers the questions that matter:

- What changed?
- What matters?
- What is blocked?
- What needs user input?
- What happens next?

That report is the attention firewall. You should not have to scan five chats,
three repos, and a stale TODO list to know where things stand.

## GitHub Is The Office

In the `touch-grass` flow, GitHub is the durable source of truth.

Chief Of Staff expects a tracking repository organized around projects and
decisions. Project work stays in the linked project repositories. The tracking
repo points to the real work, records the operating picture, and keeps the
current report visible.

This matters because chat is a terrible filing cabinet. GitHub gives the agent a
place to leave durable context that other agents and humans can inspect.

## Proof You Can Inspect

This profile is source-backed. The public model card is not the runtime prompt.
The installable behavior lives in the source profile and support material:

- `agents/chief-of-staff/agent.yaml` defines the operational agent identity,
  source-of-truth rules, boundaries, model preference, and declared skills.
- `agents/chief-of-staff/scripts/workflows.py` owns deterministic workflow
  mechanics so the agent does not reimplement file operations by hand.
- `agents/chief-of-staff/references/default-workflows/unknown-task.md` gives the
  default behavior for a new task shape.
- `docs/product/chief-of-staff.md` records the product decisions behind the
  tracking repo, daily report, and workflow-memory model.

## When To Use It

Use Chief Of Staff when context switching is the expensive part of your work:

- You have multiple projects moving at once.
- You dispatch work to agents and need to know what is actually happening.
- You want decisions, blockers, and open loops pulled out of chat and into a
  durable operating picture.
- You want low-risk work to keep moving without asking you to manage the
  filing system.
- You want repeated requests to become learned workflows instead of repeated
  explanations.

## What It Does Not Try To Be

Chief Of Staff is not the default implementer for every project. It coordinates,
tracks, clarifies, files, reports, and routes judgment. If you ask it to
implement directly, it can help, but its core value is keeping the whole system
coherent while other agents do their work.

It also does not hard-code your escalation rules. Authority, autonomy, and risk
boundaries belong to your configured operating model.

## Model Card

| Field | Value |
| --- | --- |
| Profile id | `chief-of-staff` |
| Kind | `operational-agent-profile` |
| Source | `pablof7z/touch-grass` |
| Primary skill | `tenex-edge` |
| Source of truth | GitHub tracking repository |
| Memory model | User-specific workflows in `~/.agents/homes/chief-of-staff/workflows/` |

Install it when you want your agent team to create less context debt every time
it helps you.
