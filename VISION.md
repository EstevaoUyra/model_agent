# VISION — what this project is for

This is the apex document: the *why behind the why*. [WORKFLOW.md](WORKFLOW.md)
explains *how* a model is reproduced (the process, the structure, the test
generation, the verification regime); this explains what the whole project is trying
to *be*, and what must never be traded away to get there. When a design choice is
unclear, ask which pillar it serves. When two pillars conflict, the ordering here
decides.

> **Status discipline.** This document describes the *target* and the *north
> star*, not what is built. [STATUS.md](STATUS.md) remains the canonical map of
> reality and wins on any conflict. Aspirations that are not yet built are
> marked *(not built)*. We write the vision down precisely so that it stops
> masquerading as machinery that exists — the failure mode STATUS.md was
> created to correct.

---

## The product

A **growing library of computational models — each a faithful, understandable,
and selectively modifiable reproduction of a published paper — produced by a
rigorous, repeatable agent process that is itself part of the library.**

Four pillars. They are **not a flat list**: they are ordered, they conflict,
and the design lives in the conflicts.

### Pillar 1 — Faithful (non-negotiable)

The library faithfully represents the paper. This is **adamant and cannot be
traded** for any other pillar. A model that is elegant, modifiable, and cheap
to extend but diverges from the paper is worthless — worse than worthless,
because it is *believable*. Every other pillar operates strictly within the
constraint that faithfulness wins.

The deliverable is not only the working model but a **map of where the paper is
underspecified or wrong**: every gap filled becomes an explicit, *evidenced*
Assumption; every suspected error a logged issue. Surfacing underspecification
is a first-class output, not a byproduct.

### Pillar 2 — Understandable

The code is a means of *understanding* the model, not merely running it.
Readability is a real design constraint, weighed in every implementation
choice — not a polish applied at the end. A scientist should read a stage and
see the science, not reverse-engineer intent from array gymnastics.

*Tension with Pillar 1:* the paper's own formulation may be opaque, and clarity
can mean reorganizing *away* from the paper's notation. That is allowed — but
the departure must stay auditable back to the paper (citations) and must never
change behavior. Faithful first; then as clear as faithfulness permits.

### Pillar 3 — Modifiable, but selectively and by scientific judgment

The library exists to be *used* in future work, which requires that pieces be
modifiable. But modifiability is **selective and principled**, not arbitrary:

- **Not everything is a piece — and "what is a piece" is a scientific question,
  not a code question.** A modifiable unit is a thing a *scientist* would
  conceive of as a swappable hypothesis (the attention field, the suppression
  kernel, the readout) — not wherever the code happens to factor cleanly.
  Seams are chosen by **scientific ontology**, not data-flow convenience.
- **The choice of seams is a scientific judgment, and it must be made
  explicit** *(not built today — this is the gap)*. Each seam should carry its
  rationale, in one of three kinds:
  - **natural** — a genuine scientific component; *here is the hypothesis a
    scientist would swap, and why*.
  - **imposed** — a convenience seam cut through coupled math for the sake of
    modifiability; a reader must know it is **not a joint of nature**. (Today's
    `boundary: imposed` flag is the *confession*; the positive scientific
    rationale is what's missing.)
  - **atomic** — the code *could* be split, but the science says it is one
    thing; **do not cut here**.

*Tension with Pillar 1:* a faithful reproduction wants the paper's structure; a
modifiable one wants clean seams. Coupled equations are where they collide —
and **Pillar 1 wins**: the seam becomes `imposed`, with the forced duplication
pushed into the open rather than pretended away. Acceptance requires that
swapping one piece *via config* re-verifies with zero edits to unrelated code —
but only for the seams the science endorses.

### Pillar 4 — The process is part of the library

The library is **never finished**; the *method* for extending it is itself a
deliverable, **co-equal with the models**. We cannot trust an arbitrary agent
to reproduce a model with the required rigor — so the process (the prompts, the
tools, the structure, the guardrails) must be deliberately *engineered* and
*learned from trials*.

This reframes what the models *are*: each reproduction is also an **experiment
on the process**. What the agent lacked, where it silently diverged, which
guardrail caught it — that is the real yield. The process is product **only to
the extent the trials have validated it**; documentation that runs ahead of
evidence is the failure mode (STATUS.md is both the symptom and the corrective).

---

## The current bottleneck — and where the process must grow next

The binding constraint today is **the human's time to validate faithfulness.**
Faithfulness you cannot afford to verify is, operationally, indistinguishable
from unfaithfulness. So the next thing the process must produce is *not* more
reproduction quality — it is **faithfulness the human can trust cheaply.**

> **Update 2026-06-03 — substantially built.** The intended shape below was realized
> as the **faithfulness regime**: a paper-aware Faithfulness Auditor + a change-trail
> Process Auditor (the "role distinct from the adversarial judge" called for below),
> explicit **verification tiers** (paper-verified / text-verified / self-referential),
> and a consolidated trust-triage report. See [WORKFLOW.md](WORKFLOW.md) §6 and
> `proposals/faithfulness-rerun-report-2026-06-03.md`. The text below is retained as
> the design intent it was built to.

The intended shape, as designed in discussion so far:

- **Researched assumptions.** An assumption is not "I guessed X" but "I guessed
  X, *and here is the evidence*." Research draws on, in descending authority:
  the **author's original code** (ground truth, if it can be found — the
  single highest-leverage move), the model's **lineage** (ancestor/descendant
  models already in this library), **sibling/related papers**, and
  **mathematical necessity**. Genuinely free choices the paper never constrains
  are *flagged*, not hidden.
- **Evidence-grounded confidence.** Confidence is *defined by the evidence tier
  found* — which is auditable — not a number the agent emits on vibes. The
  human trusts "corroborated by the author's code, line X," not
  "confidence: high."
- **A trust-triage report, sorted by confidence × impact.** The artifact's job
  is to *spend the human's attention*: uncertain × consequential items at the
  top, each with a specific question attached; the safe zone clearly marked so
  the human can stop reading. The human becomes an **adjudicator of flagged
  items**, not an **auditor of everything**.
- **The lineage is a faithfulness engine, not only a reuse engine.** A
  descendant that consumes an ancestor's stage and reproduces its result is
  *independent corroboration* of the ancestor; a descendant that silently
  contradicts it is a red flag. The interdependence built for reuse doubles as
  cross-validation.
- **Critique agents, used with care.** A critique layer earns its place only if
  it is **high-precision on "this is fine"** (so the human can genuinely skip
  what it clears) and honest about uncertainty (so it *routes* rather than
  rubber-stamps). This needs a role **distinct from the existing adversarial
  judge**: the judge is deliberately *isolated* (no paper access) for
  internal-consistency review, but faithfulness is a question about the
  *external world* — so the **faithfulness auditor** must be allowed and
  required to research the paper, the original code, and the lineage.

---

## How the other documents serve this

- [WORKFLOW.md](WORKFLOW.md) — the single authoritative *how*: the Phase A/B process,
  the structure each model must take (stage pipeline, protocol→measurement→view,
  calibration ledgers — the structural expression of Pillars 2 and 3), how tests are
  generated, the faithfulness regime, the per-model layout, and the falsification
  triggers. (Consolidated 2026-06-03 from the former DESIGN / ARCHITECTURE /
  REPO_STRUCTURE / ARCHITECTURE_WATCHLIST.)
- [STATUS.md](STATUS.md) — what is actually built. **Canonical on reality; wins over
  the aspirations here.**
- [AGENTS.md](AGENTS.md) — the thin operational entry point for an agent session.

When this document and a mechanism doc disagree about **intent**, this one
wins — fix the mechanism. When this document and STATUS.md disagree about
**reality**, STATUS.md wins — fix this document's marking.
