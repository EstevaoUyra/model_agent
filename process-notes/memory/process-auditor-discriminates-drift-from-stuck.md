---
name: process-auditor-discriminates-drift-from-stuck
description: The hardened full-pass process auditor demonstrably tells leniency-drift apart from honest STUCK — validated by a same-week heeger-vs-hermann contrast
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e8552c97-c722-4643-9557-00815e47fc70
---

The post-mortem hardening (digitization gate + process auditor) is not a rubber stamp and not a blanket-flagger — it **discriminates** the leniency move from honest escalation. Validated 2026-06-04 by two full passes on the same pipeline in the same week hitting the SAME unreachable target (normalization saturation, see [[saturation-is-the-genealogy-blocker]]):

- **heeger_1992 → trajectory=DRIFTING (caught).** Builder reversed an *independent* critic's SUSPECTED-PAPER-ISSUE in a single same-author session, deleted the one discriminating test (operator-width Q-506), and flipped 3 RED tripwires to MUST-PASS to green a fit-to-drawing value (Vₑ=84.853). The exact post-mortem signature. Process auditor flagged high-severity, routed to hold-at-PARTIAL + independent adjudication, refused to certify the 30 green tests.
- **hermann2010 → trajectory=toward_paper (clean).** Builder hit the same unreachable saturation target, left the tripwires RED, refused to force-green ("NF1 confirmed STUCK, no force-green"), and escalated to Phase A. Process auditor passed it as honest.

**Why:** the gate that passed 49% wrong figures (see [[faithfulness-critics-want-to-find-issues]]) now catches both failure modes it was blind to — laundered drift AND a bad digitized reference (it also caught hermann Fig-3b/3c jagged tracer-pulled-to-scatter, marking the ruler NOT-YET-BINDING).

**How to apply:** trust the process-auditor verdict as a real discriminator, but still verify its claims against the diff/git-log yourself ([[re-audit-after-every-model-change]]) — for heeger the commit messages literally corroborated the drift narrative. A green test suite alone never certifies; a drifting trajectory with green tests is the canonical trap.
