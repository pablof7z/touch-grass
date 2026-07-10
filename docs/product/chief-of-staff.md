# Chief Of Staff

These notes capture the chief-of-staff operational agent inside the `touch-grass` flow.

## Role

The user requested a `chief-of-staff` profile and clarified that the chief of staff should become an operational agent inside the `touch-grass` flow.

The user clarified:

- The role should be modeled as chief of staff, not as executive assistant, COO, strategist, project manager, editor, or another substitute role.
- It should protect the user's time and focus.
- It should oversee what other agents across all projects are working on.
- It should compare agent activity against the priorities the user has provided.
- It should be proactive, give updates, and escalate when something requires the user's input.
- It will work closely with `~/Work/tenex-edge` as the communications fabric.
- It will also work with `~/touch-grass` agents, which are a work in progress and expected to expand.
- The chief of staff will be committed to `~/touch-grass`.

Implementation correction:

- The chief of staff should exist as a reusable operational agent definition under `agents/chief-of-staff/agent.yaml`.
- The chief of staff must not be modeled as a skill.
- The chief of staff should not require a Codex adapter. Generic agent-profile tooling should understand the canonical profile directly.
- Supporting workflow machinery belongs under `agents/chief-of-staff/scripts/` and `agents/chief-of-staff/references/`, not under `skills/`.

## Source Of Truth And Tracking

The user clarified source-of-truth and tracking expectations:

- Within the `touch-grass` flow, GitHub is the source of truth.
- The chief of staff should have its own repo with the user.
- That repo should track things, including links to other repos where project work is actually happening.
- The repo should also track whatever else is discovered that the chief of staff should track.
- The chief-of-staff repo should be organized around projects and decisions.
- For updates, the chief of staff should keep a report updated for today.
- The current-day report should be linked from the top-level `README.md`.
- The report should be organized in files.
- The user has ADHD and wants the chief of staff to handle polish and organization concerns.

## Per-User Operating Model

These should not be hard-coded into the general chief-of-staff approach:

- Escalation criteria are up to the user and should be modeled per user's chief of staff.
- Autonomous decision boundaries are also per-user constraints.

Product clarification:

- This chief-of-staff profile is an operational agent inside the `touch-grass` flow, not the previously rejected meta profile for maintaining `touch-grass` itself.
- The general chief-of-staff agent should separate invariant approach from per-user operating-model configuration.
- The chief of staff is a profile because it is an agent identity and operating model, not a capability package.

## Workflow Memory

The user brainstormed a workflow-memory layer for the chief of staff:

- When the user asks the chief of staff to do something it has not done before, the agent should create a workflow in its home directory.
- The workflow directory should be `~/.agents/homes/chief-of-staff/workflows/`.
- Workflows should be maintained by a script.
- The chief of staff should start sessions by running a script that lists all workflows and the one-line summary of when to use each one.
- A default workflow should ship as `unknown-task`.
- `unknown-task` applies when the agent is asked to perform a new task and has no matching workflow.
- For simple tasks, the chief of staff should not ask annoying follow-up questions; it should err on the side of doing rather than asking.
- The user framed this as "ask for forgiveness instead of permission."
- The agent should capture the initial workflow, execute what the user wanted, and review how it went so the workflow can be changed, amended, or improved.
- The workflow layer should learn what user phrases such as "go and do marketing research" or "report a bug" mean in practice for that user's chief of staff.

Product clarification:

- Workflow capture should not be treated as a command to add bureaucracy.
- It should help the chief of staff learn repeatable patterns from actual work.

Follow-up decision (2026-07-10):

- Workflows must live in a git repo, not as loose files in
  `~/.agents/homes/chief-of-staff/workflows/`, so they carry over between
  machines instead of being pinned to whichever machine first captured them.
- As soon as the user's tracking repo exists, the chief of staff should move
  `workflows/` into it and replace the home-directory path with a symlink into
  the cloned repo.
- `scripts/workflows.py` should detect on every run whether `workflows/` is a
  plain directory instead of a symlink and print a loud warning nudging the
  move, rather than silently tolerating an un-tracked local directory.

Correction (2026-07-10, same day):

- Scope is the whole chief-of-staff home directory
  (`~/.agents/homes/chief-of-staff/`), not just `workflows/` — everything
  under home (workflows, references, etc.) is durable operating state that
  should live in the tracking repo and be symlinked back, not only workflow
  memory.
- The in-repo destination should mirror the local path exactly:
  `<tracking-repo>/.agents/homes/chief-of-staff/`, not an ad hoc
  `<tracking-repo>/chief-of-staff/workflows/` layout.
- This must NOT be codified as prose in `agent.yaml`'s `instructions` block —
  that block is carried in the agent's context on every session forever, and
  this is a one-time operational nudge, not standing doctrine the agent needs
  to reason about each turn. Instead, `scripts/workflows.py` alone detects
  (at runtime, on every invocation) whether the home directory is a symlink
  and warns on stderr if not; the agent only sees it when it actually runs
  the script, and it goes away permanently once the move is done.

Session-start entrypoint (2026-07-10):

- Replace the static "list workflows at the start of each session" instruction
  with a single scripted entrypoint the agent runs each session:
  `scripts/session_start.py`.
- The script decides what context to inject rather than the instructions
  hard-coding it. It upserts the home directory, then:
  - if the home dir is not yet tracked in a git repo (not a symlink), injects
    `references/SETUP.md` — a runbook that walks the agent through creating/
    identifying the tracking repo, migrating home contents into
    `<repo>/.agents/homes/chief-of-staff/`, and symlinking back;
  - if it is tracked, injects the session brief: tracked location, available
    workflows, and an optional agent-authored `BRIEF.md` re-surfaced every
    session.
- Rationale: a deterministic entrypoint gives one place to steer the agent's
  self-evolution — onboarding, cron/heartbeat status, proactive tracking,
  daily-report pointers — without growing the standing instructions the agent
  carries in context every turn. Grow behavior by adding brief sections in the
  script, not prose in `agent.yaml`.
- `BRIEF.md` is the flexible proactive hook: the agent (or user) drops standing
  reminders / cron state there and they resurface each session.

## Public Model-Card Direction

The user requested that each agent profile eventually have a public-facing
profile README, following the `awesome-agents` convention where
`agents/<agent-slug>/README.md` complements the runtime `agent.yaml` and powers a
site model-card page.

For `chief-of-staff`, the user wants the public profile to be more salesy and
benefit-led than a normal documentation page. Taste Skill was named as the
reference for posture: strong first impression, immediate usefulness, concrete
examples, and "what is in it for me" energy without saying that phrase
explicitly.

Five independent README proposal directions were requested:

- Operating Picture: know what moved, what matters, what is blocked, and what
  needs user input.
- Attention Firewall: protect the user's focus by letting low-risk work continue
  and escalating only meaningful decisions.
- Workflow Memory: turn repeated user requests into learned operating workflows.
- Human Judgment Router: route agent work around authority, priority, access,
  money, reputation, and irreversible-state boundaries.
- GitHub As The Office: make GitHub the durable source of truth for projects,
  decisions, open loops, linked repos, active agents, blockers, and reports.

The proposals should use real usable photo banners, not AI-generated images, and
should stay independent until the user chooses a direction.

The user rejected the first proposal pass because every draft led with too much
information: how the agent works, implementation details, install commands, and
long skimmable sections that did not create desire. Future profile READMEs
should sell the outcome first. Installation and mechanics belong near the end,
after the page has made a browsing user interested.
