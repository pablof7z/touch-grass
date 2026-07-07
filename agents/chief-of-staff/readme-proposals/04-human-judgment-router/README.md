<p align="center">
  <img src="banner.jpg" alt="A roadway barrier in front of a traffic control building" width="100%" />
</p>

# Chief Of Staff

**The Human Judgment Router for autonomous agent work.**

Your agents should not interrupt you for every small fork in the road. They
should keep moving, then stop when a choice touches authority, priority, access,
money, reputation, or irreversible state.

`chief-of-staff` gives agent teams that operating layer. It tracks the work in
GitHub, watches open loops, keeps a daily operating report, and brings you the
decisions that need human judgment instead of a stream of status noise.

## Install

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff
```

Target a harness explicitly:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness codex --global
```

This installs an operational agent profile, not a skill. The canonical profile
lives at `agents/chief-of-staff/agent.yaml`; agent-owned scripts and references
install into the agent home for the selected harness.

## What You Get

- **A human judgment queue**: questions sorted by why they need you, not by who
  asked first.
- **A GitHub-backed operating picture**: projects, decisions, blockers, open
  loops, linked repos, and active agents stay in durable files.
- **A daily operating report**: what changed, what matters, what is blocked,
  what needs input, and what happens next.
- **Agent coordination without chat drift**: duplicate work, stale blockers,
  missing owners, and priority drift get surfaced before they cost a day.
- **Workflow memory**: repeated requests become learned workflows under
  `~/.agents/homes/chief-of-staff/workflows/`.

## The Router

| Signal | Work Continues When | You Get Pulled In When |
| --- | --- | --- |
| Authority | The agent already has permission to act. | A new owner, commitment, or approval boundary appears. |
| Priority | The work fits stated priorities. | Two useful paths compete for the same time or attention. |
| Access | Existing credentials and repos cover the task. | New access, secrets, accounts, or private data are needed. |
| Money | The path has no spend or pricing decision. | A purchase, subscription, refund, or budget tradeoff appears. |
| Reputation | The change stays internal or reversible. | Public claims, customer promises, publishing, or brand risk appear. |
| Irreversible State | The action can be undone or safely retried. | Data deletion, migration, production state, or legal exposure enters the path. |

The point is not to ask fewer questions at all costs. The point is to ask the
right ones, with enough context for you to answer fast.

## Proof Artifacts

| Artifact | What It Answers |
| --- | --- |
| `README.md` in the tracking repo | Where is today's report, and where does the operating picture live? |
| Daily report | What changed? What matters? What is blocked? What needs input? What happens next? |
| Project index | Which projects exist, where is the real work, and who is active on each one? |
| Decision log | Which choices are open, decided, or blocking multiple projects? |
| Open-loop list | What question, promise, bug, review, or follow-up still needs closure? |
| Agent roster | Which agents are working, where, and on what next step? |
| Workflow memory | What has this user asked for before, and how should that request run next time? |

Project work stays in the linked project repositories. The chief-of-staff repo
points to that work, keeps the cross-project state clean, and stops important
context from disappearing into chat history.

## A Day With It

```md
## Needs User Input

| Decision | Why You Are Needed | Options | Recommended Next Step |
| --- | --- | --- | --- |
| Publish the iOS test findings? | Public reputation and customer messaging | Publish now, wait for fix, send privately | Send privately until the blocker is fixed. |
| Reassign the landing page agent? | Priority conflict across two projects | Keep current owner, reassign, pause | Reassign if checkout work remains the top priority today. |

## Blocked

- `planning-agent` needs repo access before it can publish the architecture PR.
- `ios-tester` found a login blocker and linked the simulator evidence.

## Next

- Keep low-risk research running.
- Update the decision log after the publishing choice.
- Check stale blockers before tomorrow's report.
```

That is the job: keep motion visible, keep judgment points explicit, and keep
the user out of clerical work.

## Use It When

- You have multiple agents, repos, or projects moving at once.
- You keep losing decisions in chat scrollback.
- You want agents to continue on low-risk work without asking permission.
- You need one current report instead of a pile of status messages.
- You want GitHub to act as the shared office for work state.

## Do Not Use It When

- You need a single-purpose implementer that writes the code itself.
- You want a project manager that makes business decisions without your
  operating model.
- You do not have enough parallel work to justify a cross-project operating
  picture.

## Operating Boundaries

`chief-of-staff` coordinates, clarifies, tracks, routes, and dispatches. It does
not become the default implementer unless you ask it to.

It also does not hard-code your escalation thresholds. You decide the operating
model for authority, budget, risk, publishing, access, and autonomy. The profile
keeps that model visible and routes work around it.

## Profile Card

| Field | Value |
| --- | --- |
| Kind | `operational-agent-profile` |
| Profile ID | `chief-of-staff` |
| Core job | Protect user attention while keeping cross-project work moving. |
| Source of truth | GitHub tracking repo with linked project repositories. |
| Default report | Current-day operating report linked from the tracking repo README. |
| Workflow home | `~/.agents/homes/chief-of-staff/workflows/` |
| Declared skill | `tenex-edge` |

## Banner Credit

Photo by Ries Bosch on Unsplash. See [`banner-source.md`](banner-source.md) for
source and license details.
