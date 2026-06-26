---
name: organizer-operating-model
description: "How the user wants the organizer/architect role run — delegate heavy work to briefed subagents, author synthesis yourself, iterate empirically then consolidate"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 09ed1889-e814-447c-b94b-277dfbf09c57
---

When in the organizer/architect role on this project, the user wants this
operating model (constructed deliberately over the 2026-05-18 session):

- **Delegate all heavy or lateral work to briefed subagents** in isolated
  nested repos — reproductions, migrations, refactors, paper reading, web
  research. Not just research ([[delegate-lateral-research-to-subagents]])
  — implementation too. The organizer does **not** code the models.
- **Author the thinking yourself**: design docs, scaffolds, agent briefs,
  synthesis of returns, and the decision surface. Briefs are the
  organizer's instrument; each anchors the agent on the canonical docs +
  scope + a git-safety clause + a concise report contract.
- **Empirical loop**: commit the best scaffold version, run real agents
  against it, fix defects from what actually breaks (with a committed
  evidence trail), and **consolidate into one reviewable design-pass
  document only when the validation loop closes** — the user declined
  consolidation while the loop was open, requested it once closed.
- **Reviewable artifacts are first-class**: STATUS.md (what's built) vs
  ARCHITECTURE.md (target contracts) vs a dated `proposals/design-pass-*`
  (decision surface). Correct your own record when a number proves loose —
  an evidence trail that overstates is worthless.
- **Surface milestone decisions via AskUserQuestion**, proceed
  autonomously between them ([[work-autonomously-escalate-rarely]]). The
  user steers at architecture forks, not steps.

**Why:** the user is building a substrate where the organizer's leverage
is design judgment and orchestration, not implementation throughput;
protecting that judgment (and the main context) is the whole point.
