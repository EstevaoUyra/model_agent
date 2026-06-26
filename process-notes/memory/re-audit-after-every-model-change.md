---
name: re-audit-after-every-model-change
description: "After any model change, run a fresh SEPARATE faithfulness audit and update the README with it as the verdict of record — the implementer's self-report and green tests do not certify"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

After changing the model (a fix, an improvement pass), **always run a fresh separate
faithfulness audit of the changed model, and update the README with that audit as the
current verdict of record.** Do not commit on the implementer's self-report, your own
spot-check, or a green test tally — those are exactly the self-grading the separation of
powers exists to defeat.

**The user's rule (2026-06-03):** *"Did you do an audit after the model changes? We should
always update the readme with an up-to-date audit."* I was about to commit a Phase-B fix on
Phase B's self-report + my own render spot-check.

**Why it is non-negotiable — proven the same hour:** the post-change re-audit caught what
the implementer's report, my spot-check, AND the green tests all missed — three
`audited:false` `suppressive_drive_gain`s retuned above the paper-reuse default "to make the
CRFs saturate." Nothing else flags an `audited:false` knob: no test asserts it, no quote
backs it, the implementer doesn't disclose it. Only a fresh paper-aware auditor surfaces it.
(It turned out to be pre-existing, not that pass — but I only knew that by *verifying the
auditor's claim against the diff*, which is its own lesson: verify the auditor too.)

**How to apply:**
- model change → spawn a **separate** auditor (audit-faithfulness skill, paper-aware,
  re-renders) → it produces the current per-figure verdict.
- Put that verdict table in the README as the **verdict of record** (the implementer's
  numbers and the organizer's eye are not it).
- Verify the auditor's specific claims (e.g. "this pass changed X") against the diff before
  acting — auditors mis-attribute.

Relates to [[faithfulness-critics-want-to-find-issues]],
[[organizer-doesnt-implement-trust-the-process]], [[vlm-eye-is-arbiter-over-tools]].
