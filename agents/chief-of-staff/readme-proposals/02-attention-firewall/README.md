![NASA mission control room](banner.jpg)

# Chief Of Staff: The Attention Firewall

Protect your focus while your agents keep moving.

Chief Of Staff is an operational agent profile for people running multiple projects, repos, agents, decisions, and loose ends at once. It keeps the operating picture current, routes only the right questions back to you, and turns GitHub into the shared source of truth instead of letting important state disappear into chat.

Install it:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Use it when your real problem is not "I need another agent." Your real problem is that every agent creates more things to track.

## What It Protects

Your attention is the scarce resource.

Chief Of Staff watches the work around you so you do not have to hold the whole map in your head:

| Attention leak | What Chief Of Staff does |
| --- | --- |
| "What is everyone working on?" | Maintains a cross-project operating picture. |
| "Did we decide this already?" | Tracks decisions where future agents can find them. |
| "What is blocked?" | Pulls blockers, owners, and needed answers into the daily report. |
| "Which repo has the real work?" | Links project work instead of copying it into a second place. |
| "Why did this task get weird last time?" | Captures workflow memory so repeated work improves. |

The result is less tab hunting, less repeated explanation, and fewer half-remembered promises.

## The Daily Operating Report

Every working day should leave behind one readable report linked from the tracking repo `README.md`.

It answers five questions:

```markdown
# Daily Operating Report

## What Changed
- Planning agent opened a review PR for the billing migration.
- iOS tester found a blocker in onboarding.
- Research agent finished vendor notes and linked the source repo.

## What Matters
- Billing migration now gates the release timeline.
- Onboarding bug affects new-user activation.

## What Is Blocked
- Onboarding test pass needs a fixed simulator build.
- Billing decision needs product approval before implementation.

## What Needs User Input
- Approve the billing migration boundary.
- Decide whether onboarding polish blocks this release.

## What Happens Next
- Route billing plan review to the user.
- Ask iOS tester to rerun onboarding after the build lands.
```

That report is the attention firewall in practice. You get the judgment calls, not the entire mess.

## GitHub Becomes The Office

Chief Of Staff treats GitHub as the durable operating room.

Project work stays in project repos. The tracking repo points to it, records what changed, and keeps the coordination layer clean:

```text
tracking-repo/
  README.md                 # links today's report
  reports/YYYY-MM-DD.md     # daily operating picture
  projects/                 # active project briefs and repo links
  decisions/                # durable decisions and pending calls
  open-loops/               # loose ends that still need closure
  agents/                   # active agents, owners, and current work
  blockers/                 # blockers with owner, next step, and age
```

The exact shape can adapt to the user. The rule stays fixed: important coordination belongs in files, not buried in chat scrollback.

## What It Produces

| If you ask... | It should create or update... |
| --- | --- |
| "What is going on today?" | The current daily operating report. |
| "Track this project." | A project note with repo links, owners, status, blockers, and next moves. |
| "Remember this decision." | A decision record with context, outcome, and follow-up work. |
| "Find what is stuck." | A blocker list sorted by impact, owner, and age. |
| "Have the agents coordinate." | A coordination note that links agents, repos, artifacts, and handoffs. |
| "Do this kind of task next time." | A workflow memory file under `~/.agents/homes/chief-of-staff/workflows/`. |

This profile is not a prompt that sounds organized. It is an operating model that leaves receipts.

## Workflow Memory

Chief Of Staff learns repeatable work from the way you actually work.

At the start of a session, it lists known workflows and picks the closest one. If none fits, it uses `unknown-task`:

1. Clarify only when the answer changes priority, authority, access, money, reputation, irreversible state, or the definition of done.
2. For simple and reversible work, make a reasonable call and move.
3. Capture a first workflow once the task shape is clear.
4. Execute the work.
5. Review what happened and update the workflow with better triggers, commands, sources of truth, and preferences.

The point is not more process. The point is that "do marketing research," "report a bug," and "coordinate this launch" should get easier the second time.

## When To Use It

Install Chief Of Staff when:

- You run more than one active project.
- You use multiple agents and need to know who owns what.
- You want GitHub to hold the operating picture.
- You lose time to open loops, stale blockers, and repeated context setup.
- You want an agent to handle organization, filing, retrieval, and polish.

Do not use it as your default implementer. Chief Of Staff coordinates, clarifies, tracks, dispatches, and escalates. It can help directly when asked, but its main job is to protect the user's operating attention.

## Authority Boundaries

Chief Of Staff does not hard-code your escalation policy.

Each user needs their own operating model for:

- What the agent can decide alone.
- What requires approval.
- Which projects matter most.
- Which risks deserve interruption.
- How aggressive the agent should be about routing work to other agents.

The reusable profile supplies the invariant job: keep the picture clear, preserve the source of truth, surface the right questions, and make recurring work easier.

## Profile Card

| Field | Value |
| --- | --- |
| Slug | `chief-of-staff` |
| Kind | `operational-agent-profile` |
| Schema | `awesome-agents/v1` |
| Default model | `gpt-5.5` |
| Reasoning | `high` |
| Declared skill | `tenex-edge` |
| Source file | `agents/chief-of-staff/agent.yaml` |

## Install

Preview available profiles:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

Install Chief Of Staff for Tenex Edge:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Agent-owned scripts and references install under the profile home, including workflow memory support at:

```text
~/.agents/homes/chief-of-staff/workflows/
```

## Banner

Banner photo: NASA Shuttle Flight Control Room during STS-114 simulation activities. Source and license notes are in [`banner-source.md`](banner-source.md).
