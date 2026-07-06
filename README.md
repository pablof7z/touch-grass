# touch-grass

**Production-grade agent profiles and skills for teams that demand autonomous agents that actually ship.**

Stop babysitting your AI. `touch-grass` is a curated collection of **operational agent profiles** and **reusable skills** designed for agents that need real autonomy, meaningful agency, and clean collaboration with humans—without becoming deadweight or requiring constant supervision.

## The Problem

Most agent frameworks treat autonomy as a side effect. The result:
- Agents that need hand-holding for basic decisions
- Vague decision trails that leave you wondering what happened
- Wasted human review cycles on low-stakes choices
- Agents that disappear into rabbit holes instead of shipping

## The Solution

`touch-grass` applies proven operational patterns from high-performing teams. Our profiles encode decision-making rules, publication gates, and collaboration boundaries so agents work like competent team members—not oracles that need constant prompting.

**Our bias:** Agents should make progress by default, ship useful artifacts, ask humans only when it matters, and leave a clear trail of decisions.

---

## Quick Start

### List available profiles:

```bash
npx awesome-agents add pablof7z/touch-grass --list
```

### Install the planning agent (Codex):

```bash
npx awesome-agents add pablof7z/touch-grass --agent planning-agent --harness codex --global
```

### Install any profile + harness combo:

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Agent profiles are installed from `agents/<slug>/`. Agent-owned scripts and state live under `~/.agents/homes/<slug>/`.

---

## The Profiles

### 🎯 `planning-agent`

**When to use:** Before you implement something complex.

Creates architecture/design planning PRs that actually save you review time.

- **Scans** your repo constraints and codebase patterns
- **Writes** concise, testable architecture plans
- **Publishes** hosted review artifacts
- **Decides** whether to proceed or pause for feedback—autonomously

Result: You get a PR with a clear implementation roadmap *before* work begins. No wasted sprints.

**Location:** `agents/planning-agent/agent.yaml`

---

### 📊 `chief-of-staff`

**When to use:** When you have multiple agents or projects going at once.

Maintains a real-time operating picture across your projects. Tracks decisions, open loops, linked repos, active agents, and daily reports.

- **Centralizes** project state so you focus on judgment, not status updates
- **Automates** recurring request types through script-managed workflows
- **Publishes** daily reports so you always know what moved

Result: Your team runs like a command center, not a chaos zone.

**Location:** `agents/chief-of-staff/agent.yaml`

---

### 📱 `ios-tester`

**When to use:** You want black-box iOS testing at scale.

Uses simulator tooling and project notes to test installed apps like a real user would.

- **Black-box testing** (not source-code introspection)
- **Simulator-native** (no brittle UI automation)
- **User-mindset** testing based on your project notes

**Location:** `agents/ios-tester/agent.yaml`

---

### 🎨 `ios-ux-ui-critic`

**When to use:** You need UX/UI critique without the product meeting.

Black-box inspection of your iOS app experience, rendered as coherent critique.

- **Runs on simulator**
- **Grounds critique** in your project context
- **Identifies** friction and UX gaps like a senior designer

**Location:** `agents/ios-ux-ui-critic/agent.yaml`

---

## Repository Philosophy

- **Skills compose.** They should work together, not step on each other.
- **Autonomy with guard rails.** Agents decide low-stakes things; humans decide high-stakes things. Both need to be obvious.
- **Determinism where it counts.** Repetitive workflows belong in scripts, not prompts.
- **Sharp instructions.** Skills should be small, clear, and easy for another agent to apply.

---

## Repository Goals

✅ Build skills and operational agent profiles that compose well  
✅ Maximize useful autonomy while preserving human review for high-impact decisions  
✅ Move deterministic mechanics into scripts  
✅ Keep skill instructions small, sharp, and easy for another agent to apply  

---

## What's Inside

- **`agents/`** – Operational agent profiles (reusable agent identities + operating models)
- **`skills/`** – Composable skills and capabilities
- **`docs/product/`** – Product thinking, decisions, and boundaries
- **`scripts/`** – Shared automation and workflow mechanics

---

## For Product & Team Context

See [`docs/product/`](docs/product/) for:
- **`foundations.md`** – Repository purpose, naming, and public positioning
- **`operational-agent-profiles.md`** – What makes a profile, not a skill
- **`planning-agent.md`** – Planning workflow and decision boundaries
- **`chief-of-staff.md`** – Tracking model and workflow memory
- **`open-questions.md`** – Unresolved problems we're thinking through

---

## Contributing

We're building this for teams that have outgrown generic agent patterns. If you're using operational profiles or skills that work well together, we'd love to see them.

**Contribution bar:** Your profile or skill should solve a real operational problem and compose cleanly with the others.

---

## License

MIT

---

**Built for teams that expect their agents to ship.**
