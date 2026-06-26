---
name: work-autonomously-escalate-rarely
description: "User prefers high autonomy — proceed on best judgment, escalate only when genuinely weird or STUCK"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 09ed1889-e814-447c-b94b-277dfbf09c57
---

The user explicitly prefers autonomous execution: "keep going based on your
own best guess, unless dealing with something very weird or being STUCK."
They confirm proposed strategies tersely ("I agree") and then expect the
work carried through end-to-end — including follow-on actions like commits —
without per-step check-ins.

**Why:** they treat clarifying questions as expensive; a reasonable default
acted on beats a question for a choice with an obvious answer.

**How to apply:** make the call and proceed; surface decisions in the
summary, not as gating questions. Reserve AskUserQuestion / pausing for
genuine forks where the answer changes the work, "very weird" situations, or
a real blocker (the project's STUCK gate, or a hard-rule conflict such as
the AGENTS.md "Phase B never writes article_aware/" boundary — there, log a
spec question and move on rather than asking). When uncertain whether to
stop, prefer proceeding and reporting.
