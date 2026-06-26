---
name: paper-resolvable-findings-arent-human-routed
description: "A finding resolvable from the paper's own ground truth (ladder rung 1) must not be routed \"human-only\"; the process auditor flagging such a resolution as drift is a false positive"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a651000f-a156-41c6-b8cc-3db390b5524f
---

A finding that is resolvable from the paper's OWN on-disk ground truth (escalation-ladder rung 1 — e.g. the paper's own digitized figure) does **not** need human-only routing, and a builder closing it with a paper-grounded value is **correct, not drift**. The escalation ladder resolves rung 1 (paper) and rung 2 (lineage/author code) WITHOUT a human; human is the last resort only.

**Why:** On boynton_2009 (2026-06-15) a fix pass lowered a discriminator threshold 0.05→0.02, grounded at rung 1 (the paper's own digitized Fig.2B c=0 gap = 0.026). The process auditor flagged it as drift purely because the finding had been routed "human-only" and the builder closed it. User: *"If it was solvable why would it need a human? Doesn't make sense."* The value was independently confirmed paper-grounded and discriminator-preserving — so the "human-only" routing was the error, and the drift flag was a false positive. Ratified (PR #9), drifting cleared. The same over-routing recurred in the same batch: bienenstock_cooper_munro_1982's spec audit argued a "human DECISION" framing of the φ root cause was itself a cap-artifact the paper settles.

**How to apply:** When a process/spec auditor flags a builder closure as drift, first check the RUNG: if the closing value is resolved from the paper's own figure/text (rung 1) or lineage (rung 2) and a separate faithfulness audit confirms it, ratify it — do not reopen. Reserve human-only routing for what the ladder genuinely cannot resolve. BUT hold the distinction: a value that is *shared across models* (divisive-norm saturation / φ-form — see [[saturation-is-the-genealogy-blocker]]) is a coordination decision, NOT a single-paper rung-1 resolution; that one still must not be resolved unilaterally 3×. Drift-vs-honest discrimination still matters ([[process-auditor-discriminates-drift-from-stuck]], [[faithfulness-critics-want-to-find-issues]]) — this just sharpens it: goalpost-moving toward green is drift; rung-1 grounding toward the paper is not.
