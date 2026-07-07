<p align="center">
  <img src="banner.jpg" alt="NASA Apollo 10 Mission Control room with operators monitoring consoles" width="100%" />
</p>

# Chief Of Staff: The Operating Picture

Know what changed, what matters, what is blocked, and what needs you.

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Most agent setups create a second job for the human: remembering who is doing what, which repo has the truth, which decision is blocking five threads, and which update actually deserves attention.

`chief-of-staff` is an operational agent profile for that missing layer. It maintains a cross-project operating picture across projects, decisions, agents, blockers, and open loops so you can spend less time reconstructing context and more time making the few calls that matter.

## Use It When

| You have... | It gives you... |
| --- | --- |
| Multiple projects moving at once | One current view of status, risk, and next action. |
| Agents working across repos or chats | A durable record of who is doing what and where the work lives. |
| Decisions scattered across threads | Decision tracking organized around what is decided, pending, or blocking. |
| Recurring requests with local preferences | Workflow memory that learns how you like repeated work handled. |
| Too much status noise | A bias toward asking only when judgment, authority, access, priority, money, reputation, irreversible state, or definition of done is at stake. |

## What It Owns

The chief of staff does not replace your project agents. It keeps the operating layer coherent around them.

| Area | What gets tracked |
| --- | --- |
| Projects | Active projects, linked repositories, owners, current status, and next checks. |
| Decisions | Open decisions, settled decisions, who needs to weigh in, and what is blocked until a call is made. |
| Open loops | Unanswered asks, stale follow-ups, missing approvals, and context that should not disappear into chat. |
| Agents | Which agents are active, what they are working on, and where their artifacts live. |
| Blockers | Access gaps, dependency conflicts, unclear priorities, and risks that need attention. |
| Workflow memory | Repeatable task patterns stored in the agent home so future work starts with the right defaults. |

## GitHub Is The Office

In the `touch-grass` flow, GitHub is the source of truth.

The chief of staff expects a tracking repository with the user. That repo tracks projects, decisions, open loops, linked project repositories, active agents, blockers, risks, and discovered coordination artifacts. Project work stays in the project repos. The tracking repo points to it, summarizes it, and keeps the current operating picture easy to scan.

That matters because chat is a poor archive. The chief of staff leaves durable files the next agent, future you, or a collaborator can inspect without replaying a whole conversation.

## The Daily Operating Report

Every day, the tracking repo should link its current report from the top-level `README.md`.

The report answers the same five questions every time:

```markdown
# Daily Operating Picture

## What Changed

- Planning work moved from proposal to review.
- A project agent opened a new blocker in the linked app repo.
- Yesterday's open question about release scope was answered.

## What Matters

- One decision now controls two downstream tasks.
- The highest-risk blocker is access, not implementation.

## What Is Blocked

- Release notes cannot finish until the release boundary is confirmed.
- The testing agent is waiting on a runnable build.

## What Needs User Input

- Choose whether the release includes the new onboarding flow.
- Approve or reject the proposed GitHub tracking layout.

## What Happens Next

- Dispatch the tester once the build is available.
- Update the decision log after release scope is confirmed.
- Close stale loops that no longer matter.
```

The point is not a prettier status report. The point is less context reconstruction.

## Workflow Memory

The profile ships with workflow memory under:

```text
~/.agents/homes/chief-of-staff/workflows/
```

At the start of a session, the chief of staff lists available workflows and picks the closest one before acting. If no workflow fits, it uses `unknown-task`: clarify only as much as the task deserves, do useful work, then capture the pattern so the next request starts sharper.

This is how "do marketing research," "report a bug," or "prep the daily update" becomes a learned operating habit instead of a fresh prompt every time.

## Source-Backed Behavior

This model card is not the runtime prompt. The installable profile lives in `agents/chief-of-staff/agent.yaml`.

The source profile defines:

| Field | Value |
| --- | --- |
| Schema | `awesome-agents/v1` |
| Profile id | `chief-of-staff` |
| Kind | `operational-agent-profile` |
| Default model | `gpt-5.5` |
| Reasoning effort | `high` |
| Declared skill | `tenex-edge` |
| Workflow script | `agents/chief-of-staff/scripts/workflows.py` |
| Default workflow | `agents/chief-of-staff/references/default-workflows/unknown-task.md` |

## What It Will Not Do

- It will not become the project implementer by default. It coordinates, clarifies, tracks, and dispatches unless asked to implement directly.
- It will not hard-code a universal escalation policy. Your decision boundaries belong to your operating model.
- It will not make you organize the system for it. Filing, retrieval, and polish are part of the job.
- It will not bury durable state in chat when a tracking repo is available.
- It will not over-design the tracking system before the operating picture is useful.

## Install

Install the chief of staff profile:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

List the available `touch-grass` profiles first:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

After install, `awesome-agents` renders the profile for the selected harness and installs agent-owned scripts and references into the chief-of-staff home directory.

## Best Fit

Use `chief-of-staff` when the main problem is not writing code, reviewing code, or testing an app. Use it when the problem is operational clarity: too many agents, repos, decisions, and partial updates competing for your attention.

It is the agent that keeps the room legible.
