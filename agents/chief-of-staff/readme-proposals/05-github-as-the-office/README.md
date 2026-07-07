<p align="center">
  <img src="./banner.jpg" alt="GitHub open in a desktop browser, used as the operating surface for project coordination" width="100%" />
</p>

<p align="center">
  <strong>Chief Of Staff</strong><br />
  <em>Turn GitHub into the office where your agents leave state, decisions, blockers, and next steps.</em>
</p>

<p align="center">
  <a href="#install">Install</a> |
  <a href="#why-it-exists">Why it exists</a> |
  <a href="#what-it-keeps-current">What it keeps current</a> |
  <a href="#daily-operating-report">Daily report</a> |
  <a href="#proof-it-is-working">Proof</a>
</p>

<p align="center">
  <img alt="Profile: chief-of-staff" src="https://img.shields.io/badge/profile-chief--of--staff-111111" />
  <img alt="Schema: awesome-agents/v1" src="https://img.shields.io/badge/schema-awesome--agents%2Fv1-2f6f5f" />
  <img alt="Source of truth: GitHub" src="https://img.shields.io/badge/source%20of%20truth-GitHub-2f6f5f" />
</p>

# Chief Of Staff

Run multiple projects and agents without making chat your memory system.

The `chief-of-staff` agent gives your work a durable operating room in GitHub. It tracks what changed, what matters, what is blocked, which agents are active, which decisions are still open, and what needs your judgment today.

You still make the calls that need you. The chief of staff handles the filing, linking, summarizing, and follow-through that usually leaks into your attention.

## Install

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

List available profiles first:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

This README is the public model-card page for the profile. The installable operating model lives in `agents/chief-of-staff/agent.yaml`.

## Why It Exists

Agents can move fast, but coordination still fails in ordinary chat:

| Chat drift | GitHub as the office |
| --- | --- |
| Status is buried in threads. | Status lives in current files and issues. |
| Decisions are remembered by whoever was there. | Decisions get durable records and links. |
| Blockers get rediscovered. | Blockers keep owners, context, and next actions. |
| The user becomes the router. | The chief of staff routes only meaningful questions. |
| Agent work fragments across repos. | Project repos stay linked from one operating picture. |

The point is not more process. The point is less remembering.

## What It Keeps Current

The chief of staff expects a user-facing tracking repository and treats it as the source of truth.

A useful tracking repo usually contains:

| Artifact | What it answers |
| --- | --- |
| `README.md` | Where is today's operating report? |
| `reports/YYYY-MM-DD.md` | What changed today, what matters, what is blocked, and what happens next? |
| `projects/<project>.md` | What is the current state of this project and where is the real work happening? |
| `decisions/<decision>.md` | What decision is pending, made, deferred, or blocking other work? |
| `open-loops.md` | What still needs closure? |
| `agents.md` | Which agents are active, what are they doing, and what do they need? |
| `blockers.md` | What is stuck, who owns the next move, and when should it be checked again? |

Project implementation stays in the linked project repositories. The tracking repo points to the work instead of duplicating it.

## Daily Operating Report

Every day gets a current report linked from the top-level `README.md`.

```markdown
# Operating Report: 2026-07-07

## What Changed

- Planning agent published the API migration plan in `project-a`.
- iOS tester found a blocked login path in `project-b`.
- Research agent finished vendor notes and linked the evidence.

## What Matters

- The API migration now blocks two feature branches.
- The login issue affects onboarding and should be resolved before launch review.

## Blocked

| Blocker | Owner | Needed next |
| --- | --- | --- |
| API auth decision | User | Pick token lifetime policy |
| Test account access | Chief of staff | Request fresh credentials |

## Needs User Input

- Decide whether auth tokens expire after 24 hours or 7 days.
- Confirm whether vendor B is still in scope.

## Next

- Dispatch implementation after the auth decision is made.
- Ask iOS tester to rerun onboarding after credentials are restored.
```

You get the operating picture without rereading the day.

## Workflow Memory

The chief of staff learns how you work.

When you ask for something new, it starts from the closest known workflow under:

```text
~/.agents/homes/chief-of-staff/workflows/
```

If nothing fits, it uses `unknown-task`: clarify only what matters, do the work when the risk is low, then capture the workflow so the next request is easier.

That means "go do marketing research", "report this bug", and "find what is blocking launch" can become repeatable operating patterns instead of one-off chat archaeology.

## What You See

- Fewer status pings.
- Fewer "where did that land?" searches.
- Fewer decisions hidden inside agent transcripts.
- More links to the exact repo, issue, PR, report, or decision record.
- A daily summary that tells you where your judgment is actually needed.

## Proof It Is Working

You should be able to open the tracking repo and answer these in under a minute:

| Question | Proof |
| --- | --- |
| What changed today? | The top-level `README.md` links today's report. |
| What needs me? | The report has a short `Needs User Input` section. |
| What is blocked? | `blockers.md` has owners, context, and next actions. |
| Where is project work happening? | Each project file links to the real implementation repo. |
| Which agents are active? | `agents.md` shows current work, status, and dependencies. |
| What decisions are open? | Decision files show status, rationale, and downstream impact. |

If those answers are not obvious, the office is messy. The chief of staff cleans it up.

## Good Fit

Use this profile when:

- you run several projects at once;
- you delegate work to multiple agents;
- GitHub is already where your durable work should land;
- you want a daily operating picture instead of scattered status updates;
- you need an agent to protect attention, not create more meetings.

## Not A Runtime Prompt

This README is public-facing model-card copy for `awesome-agents`. It explains the promise, install path, and expected operating artifacts.

The runtime profile remains the canonical source for agent behavior:

```text
agents/chief-of-staff/agent.yaml
```
