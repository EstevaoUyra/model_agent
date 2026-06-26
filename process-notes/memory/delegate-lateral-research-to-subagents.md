---
name: delegate-lateral-research-to-subagents
description: "Routinely spawn subagents for lateral research (paper reading, web/literature, broad exploration) to protect the main context"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 09ed1889-e814-447c-b94b-277dfbf09c57
---

The user wants lateral research **routinely** delegated to spawned
subagents, not done in the main thread: reading papers/PDFs, web/Scholar
literature research, broad multi-source exploration. They called the main
context "precious" and this practice "something you should be doing
routinely" — it is the default, not the exception.

**Why:** the orchestrator/architect role degrades if its context fills with
raw source material and search transcripts; delegation keeps the main thread
high-level and decision-focused.

**How to apply:** when a step needs long external reading or broad research,
spawn background subagents with tight, scoped prompts that return only
conclusions (≤~500 words, structured, sources cited) — not raw dumps. Run
several in parallel on differentiated angles. Continue orchestration while
they run; synthesize their returns. Pairs with
[[work-autonomously-escalate-rarely]] (delegation is part of working
autonomously, not a reason to pause).
