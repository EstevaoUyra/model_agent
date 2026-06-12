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

## What enters the library — scope and selection

The four pillars are the bar a *chosen* paper must clear. This section is the
prior question: **which papers we choose at all.** Two axes — what makes a paper
*eligible*, and how far the library's *scope* is meant to reach.

### Selection criteria — a paper is eligible when

- **It is reproducible from published materials.** The paper, its supplementary
  information, and its **figure images** must together contain enough to *build
  and parametrize* the model. Author-released code or fits, when they exist, are
  the highest-leverage faithfulness grounding (see the bottleneck section below)
  — but they are **not a precondition for entry**. If the published materials
  alone underdetermine the model, that is what the Assumption ledger and logged
  spec-questions are for; if they underdetermine it *fatally*, the paper is out.
- **Unavailable empirical data is fine — when it is only a comparison target.**
  A paper is eligible even when the experimental data it plots against is not
  available to us, **provided that data is used only to compare with the model's
  output, not to construct or parametrize the model.** The model is built and
  fixed from the paper's equations and stated parameters; the missing data would
  only have been overlaid for validation. What *disqualifies* a paper is a model
  that cannot be built or parametrized without data we do not have — a fitted
  model whose fit needs the held-out recordings, not a forward model whose curve
  merely gets compared to them. (In practice this means the unavailable-data
  panels are reproduced as the model's prediction, with the empirical overlay
  noted as out-of-reach rather than faked.)
- **It is cheap enough to iterate on.** Reproduction is an iterative loop, so a
  model must be tractable to run many times over. Models that demand heavy
  training or large-scale simulation are excluded, or — where the *trained
  result* is what matters, not the training — the expensive stage is **stubbed
  or frozen** (e.g. freeze a released/learned basis rather than re-train it),
  with the freeze recorded as an explicit scope decision.

### Scope — vision is the seed, not the boundary

The current corpus is entirely vision (early/mid visual cortex), and that is a
**starting point, not the project's subject.** Vision was chosen for the
maintainer's prior expertise and a mild standing preference — not because the
library is *about* vision. The explicit intent is to **progressively widen
coverage to other areas of neuroscience** as the process hardens.

Note that the only diversity axis exercised so far is **computational motif**
(divisive normalization · sparse/efficient coding · predictive coding) — all
still within vision. That axis stress-tests the *process*; it is not the limit
of the *domain*. Over time the library should grow along **both** axes: new
motifs *and* new neuroscience areas. A future corpus-expansion plan that only
proposes more vision papers has read this scope too narrowly.

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
