---
name: organizer-doesnt-implement-trust-the-process
description: The organizer orchestrates — it does not write model/implementation code or pre-decide faithfulness conventions; trust the verification process to surface divergences and route corrections to the right phase
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

When a faithfulness issue surfaces (e.g. the model's view normalizes per-pair-to-1.0
while the paper uses a shared sub-1.0 scale), do **not** reach in and implement the fix
or pre-decide the convention. Writing model/view code is **Phase B**; establishing how
the paper normalizes is **Phase A reading the source**. The organizer does neither.

**The process is built to catch exactly this**, so trust it: the audited digitization is
the reference (the ruler); the tier tests + the **faithfulness auditor** run against it
and surface the divergence ("normalization convention must match the paper" is already a
binding auditor check); the finding **routes to the implementer** (Phase B fixes it; if
the paper's reference is underspecified it's a spec question Phase A answers). The
organizer **runs that loop and routes**, it does not short-circuit it by coding.

A tell I missed: I framed the divergences the process *would* surface as "false
divergences to pre-empt." They aren't false — they're the **true** divergence the process
exists to report. Treating the process working as a problem to route around is the bug.

**The user's challenge (2026-06-03):** *"You shouldn't be implementing model code. Is
there some reason you don't trust the process to naturally lead to this correction?"* —
No good reason; it was a default-to-do-it-myself reflex. This is a **recurring over-reach**
(cf. "don't do it with your own context, otherwise we don't learn the process"). Default
to letting the agents / the verification loop do the work; the organizer authors
*process* synthesis and decisions, never model code.

Relates to [[organizer-operating-model]], [[capture-discovered-knowledge-in-artifacts]],
[[faithfulness-critics-want-to-find-issues]].
