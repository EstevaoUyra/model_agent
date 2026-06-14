# How to reproduce a model — the process

This is **the single authoritative description of how a paper should be reproduced**:
the phases, the artifacts, how tests are generated, the structure each model must
take, and how faithfulness is verified. It is the *how*.

- *Why this project exists / what "faithful" means*: [VISION.md](VISION.md) (the four
  pillars — the apex standard; faithfulness wins every conflict).
- *What is actually built (vs. described)*: [STATUS.md](STATUS.md) — **canonical on
  reality; wins on any conflict.** This document describes the target process; where a
  mechanism here is not yet tooling, STATUS.md says so.
- *The agent graph (visual companion)*: [WORKFLOW-graph.md](WORKFLOW-graph.md) — the
  `full-pass` agents as a directed graph (each agent once; caps as loops). **Any change
  to the workflow here must be reflected in that graph, and vice versa.**

> **The one rule that subsumes the rest.** A reproduction is faithful only to the
> extent it is *checked against the paper*. Every gate, test, and verdict in this
> document exists to measure **distance to the paper**, not internal self-consistency.
> The failure this process is built to prevent (post-mortem 2026-06-02): a checklist
> derived from the model's own intended behavior, satisfied by a figure the model
> produces, "verifying" nothing. When the paper material to check against does not
> exist, say so — do not manufacture a green that nobody grounded.

---

## 1. Two phases, one hard boundary

Reproduction is split into two phases separated by a **paper-access boundary**, the
most important design choice in the system:

- **Phase A — article-aware extraction.** Reads `paper/` (the PDF + extracted text +
  figure images). Produces the self-sufficient `article_aware/` contract. This is the
  *only* phase that may read the paper.
- **Phase B — implementation (paper-blind).** Reads `article_aware/` (read-only) +
  `logs/`. Implements the model. **Never reads `paper/`.** Anything missing from
  `article_aware/` is, by definition, an underspecification → logged as an
  `Assumption`, never recovered by peeking at the paper.

The boundary forces the spec to be *complete and executable*: if Phase B could peek,
the spec would silently degrade into a partial summary. It is enforced by
**working-directory scope (tool config), not prompt text** — prompts are a hint, tool
config is the guarantee.

A third, separate role — the **faithfulness regime** (§6) — runs *after* a build and
*is* allowed the paper. It does not relax the boundary (the blind build already
happened); it is the instrument that measures the result against the paper.

**Boundaries (enforced by tooling):**

| Role | reads `paper/` | reads `article_aware/` | writes `article_aware/` | writes `implementation/` |
|---|---|---|---|---|
| Extractor (Phase A) | **yes** | yes | yes | no |
| Implementer (Phase B) | **no** | yes (read-only) | no (append `logs/spec_questions.md` only) | yes |
| Faithfulness Auditor (§6) | **yes** | yes | **no** (report only) | **no** (report only) |
| Process Auditor (§6) | no (reads the change-trail, not the paper) | yes | no | no |
| Adversarial judge | no (rubric/context/under-review only) | no | no | no |

---

## 2. Phase A — the article-aware contract

Produce everything a paper-blind implementer needs, under `article_aware/`. Follow
`skills/extract-spec/SKILL.md` and `skills/extract-figure/SKILL.md`.

- `spec/model_spec.yaml` — state variables, parameters, equations (`EQ-NNN`),
  components, the ordered **paper-derived pipeline** (dataflow; Phase B cannot
  reverse-engineer order from equations alone), and `simulation_protocols` (each
  declaring the exact `expected_outputs` its runner returns).
- `spec/calibration.yaml` — the **paper-derived** parameter ledger (§5). Phase-A-owned.
- `spec/citations.yaml` (`C-NNN`) · `spec/assumptions.yaml` (`A-NNN`).
- `pseudocode/<figure>_protocol.md` — inputs, sweeps, procedure, named outputs (the
  output names are the runner contract), expected behavior.
- `figures/figure_<N>.md` — role in the paper + **verbatim caption** + per-panel
  expected behavior derived from the equations.
- `figures/figure_<N>.<img>` — **the paper's figure image** (see §3, this is
  load-bearing).
- `figures/figure_<N>_visual_checklist.md` — the binding visual claims (§3).
- `extracted_data/test_<figure>.py` — the deterministic claim tests (§3).
- **Literature-grounding / parameter-provenance table** — per significant
  parameter: `value | stated-in-paper | relative-only | inferred | evidence (cited
  ref / author code / lineage) | sensitivity`. This is what lets a human trust the
  reproduction cheaply (VISION's trust-triage).

**Faithfulness rules for extraction (non-negotiable):**

- **Never confabulate.** Every test claim traces to a specific paper passage (cite it)
  or is an explicit `A-NNN` assumption with provenance — never a fabricated claim
  wearing a real `C-NNN`.
- **One convention everywhere.** Unit/scale conventions (contrast fraction vs percent;
  curve-peak vs raw-coefficient; which curve is normalized to 1.0) singular and
  identical across spec, calibration, pseudocode, and provenance.
- **Classify every frozen-fit / stubbed-learning stage** (§5): `nuisance_fit` (stub it
  freely) vs `result_bearing` (the learned object *is* the paper's headline claim —
  stubbing it means the figure shows a *constructed* answer; mark it
  `ILLUSTRATIVE-NOT-REPRODUCED`, never plain green).
- **Verify internal consistency** with a throwaway reference implementation before
  finalizing — *but never let "the recipe reproduces its own claim" stand in for "the
  value matches the paper"* (see §5, `discriminating_threshold`).

**Gate — verdict ≠ gate.** A reviewer returns a structured verdict; the gate is a
*separate* decision on it (the ≥2-reviewer panel below). Before passing: every checklist
must pass the **sufficiency test** (§3) and every `audited:true` value must carry a
captured verbatim quote (§5).

> **As realized in `full-pass.js` (2026-06-14).** The contract gate is a **single**
> adversarial `audit-spec` agent (author ≠ auditor *is* enforced), returning a structured
> `SPEC_VERDICT` the workflow branches on — the "verdict ≠ gate" separation is honored as
> *data*, not a written `article_aware/APPROVED` file (there is no human-approval step in the
> automated pass). The **≥2-reviewer panel** is the *target*, not current behavior; the live
> control is author≠auditor + an adversarial single auditor. Revisit if trials show a single
> auditor misses contract faults.

---

## 3. How tests are generated (the load-bearing section)

Two test surfaces. Both must measure distance to the **paper**, not to the model.

### Panels are the unit (decompose first)

A paper figure is usually a **composite of panels**; reproduce and verify at the
**panel** level, then reassemble at the figure level. Do this *before* writing a
panel's tests.

- **Split out every data-bearing panel** and describe/test it on its own (a
  schematic/config/legend panel is layout, not a data panel). At extraction, **crop the
  paper figure into its panels** (`figures/figure_<N>/panel_<X>.<img>` + `panel_<X>.md`)
  so each is an isolated comparison unit in its own coordinate frame — shrinking every
  comparison to one panel vs one panel.
- **Axis limits are a HARD, code-checkable requirement per plot panel.** Each
  `panel_<X>.md` states the panel's x-range, y-range (including any right/twin axis), and
  scale (log/linear). The view sets these limits **explicitly — never auto-scale** — and
  a **deterministic test** asserts the rendered limits equal the paper panel's (read off
  the Axes or the view config). Pinning the axes to the paper's catches magnitude
  divergences exactly (a curve that overflows the paper's axis *fails*) and makes
  **shape** divergences obvious (curves on identical axes).
- **Figure-level reassembly matches the paper's layout.** The reproduced
  `figure_<N>.png` concatenates the reproduced panels in the paper's arrangement, with an
  explicit empty **`not reproduced`** panel wherever the paper had a panel we do not
  reproduce (empirical-data panels, schematics). The figure image therefore *lines up*
  with the paper's — omissions visible and honest — never a clean single panel
  masquerading as the whole figure.

The deterministic (§3a) and figure (§3b) tests below are written **per panel**, inside
this fixed, paper-matched frame.

### 3a. Deterministic claim tests — `extracted_data/test_<figure>.py`

Ordinary pytest files asserting on the protocol's named outputs / the measurement
record (§4). Rules:

- **Assert on the measurement record (golden-file style)** — so a passing test and the
  rendered figure are drawn from the same record. ⚠️ This proves *internal
  consistency only*, NOT fidelity to the paper. Count the deterministic test and the
  figure it shares a record with as **one** signal, never two.
- **Shape claims assert the STRICT structure.** "End-stopping" = an interior argmax
  that exceeds *both* endpoints by a ledger margin, so a monotone/plateau curve *fails*.
  A loose proxy that a degenerate curve passes is a defect.
- **Binding thresholds live in the ledger, with a `kind`** (§5) — not as literals in
  test code.
- **Validate every test for SUFFICIENCY, not just necessity.** Before `APPROVED`,
  demonstrate that a *deliberately-wrong* input **fails** the test (a monotone curve, an
  inverted normalization, a degenerate value). A test a known-bad artifact passes is
  too loose by construction — a hard reject. "The right answer passes" is necessary but
  not sufficient; the gap between the two is where leniency hides.

### 3b. Figure tests — classify the panel, digitize (tools + a separate critic), three tiers

A figure's binding check compares the model's output to the paper's **digitized
reference**, both rendered through the **same Phase-A-owned view**. But **classify the
panel first** — the type decides which tools apply and what "faithful" even means (full
taxonomy: `proposals/figure-digitization-design-2026-06-03.md`):

- **Mode 1 — quantitative plot** (line/curve, scatter+regression, bar, histogram, polar):
  recoverable (x, y) — the digitize path below. The faithful quantity is **type-specific**:
  pointwise curve shape for a tuning/CRF curve, **regression slope/R** for a scatter,
  distribution stats for a histogram, per-bar heights for a bar chart — not one metric.
- **Mode 2 — image/structure** (learned-filter dictionary, heatmap, RF map, image patches):
  no curve to extract; faithfulness is **emergent statistics**, and a stochastic output
  (a learned dictionary) must **never** be pixel-matched. Needs Mode-2 tooling — if none
  exists yet, **BLOCKED**, never forced through a curve tracer (a category error).
- **Mode 3 — schematic** (circuit/architecture diagram, stimulus layout): structural
  checklist, no digitization.

For a Mode-1 panel, Phase A produces the reference like this:

1. **Digitize with the tools** (`neuromodels/framework/figures`, via `skills/digitize-figure`):
   calibrate the axes, trace each curve (respecting the tracer's monochrome-overlap limit —
   envelope where same-colour curves coincide), **match the paper's normalization scale**
   (never per-panel→1.0 where the paper shares a scale across panels), smooth with PCHIP,
   and **validate adversarially against an overlay on the paper pixels — the eye is the
   arbiter over the tools.** The tools (calibration, tracer, PCHIP) are approximate exactly
   where the scan is hard; render the curves on the paper, **zoom suspect regions with
   `crop_region`** (an apex, a crossing, an axis corner), and treat any overshoot, wiggle, or
   axis-edge shift as a fault to *fix*, not confirm — "it tracks well" is not a verdict. Record
   a **provenance block** in
   `extracted_data/figure_<N>/panel_<X>_digitized.*` (figure-type → tools → calibration →
   per-curve method → caveats). The **~dozen points are the *comparison granularity*** (the
   shape check below), **not** a cap on extraction — digitize as densely/smoothly as the
   tools allow.
2. **Generate the view** for the panel/figure *from the digitization* — the plotting
   code (axis limits, scale, styling, layout, `not reproduced` placeholders). The view
   is a **Phase-A-owned contract**: it declares the measurement-record schema it plots
   and renders *any* record — the digitized reference OR the implementation's output —
   identically. **Phase B never touches it**, so presentation cannot deviate (wrong
   axes, auto-scaling, dropped/spurious panels become *impossible*, not merely caught).
   The view must carry the **paper's** scale (a per-panel max-normalize in the view is the
   same faithfulness bug as in the digitization).
3. **A SEPARATE critic audits the digitization** (`skills/audit-digitization`) against the
   paper — panel and figure level, faithfulness *and* whether the right tools were used. It
   is **never the digitizer and never the organizer** (both are invested in it landing): the
   digitizer *produces* the reference, a find-issues critic *passes/fails* it. A digitized
   reference carrying an unresolved finding is **not-yet-binding** — the tiers must not grade
   against it. (This **replaces the old "self-check"**, which was the digitizer grading its
   own homework — the leniency hole this split exists to close. The reference being a
   *ruler*, a wrong one silently mis-calibrates every test, so this audit is *prior* to the
   model faithfulness audit.)

**Three test tiers**, all codified on the measurement record, all derived from the
digitized reference, all with tolerances (close, not exact); each test is *evaluated on
the implementation's record* with its expected value/threshold *digitized from the
paper*:

- **Qualitative — MUST PASS.** Precise-but-weak structural claims — e.g. "curve A
  crosses curve B in the right half", "attended ≥ unattended over the central region",
  curve orderings, "the two curves converge at the high-contrast end". The robust floor
  a faithful figure always satisfies.
- **Hard — MUST PASS.** A **few** strong quantitative claims the agent is **confident**
  should be enforced — e.g. "A − B ≈ 10 over x∈[0.8,1.0] ± tol", "attended/unattended
  peak ratio ≈ 1.4 ± tol", "value at x=0.5 ≈ 0.7 ± tol". Write *only* the ones you are
  sure of; these bind faithfulness quantitatively.
- **Soft — MEASURED, REPORTED, NEVER BLOCKS.** Written exactly like hard tests, but
  non-blocking, because the digitization is **not trusted 100%**. Always measured,
  always reported (in `logs/figure_comparisons/` and the README), never fails the
  build. They surface candidate quantitative claims to the human, who **promotes a soft
  test to hard** (a one-line tier flip) or fixes the digitization from what the report
  shows.

The **tier is a declared, human-editable per-test attribute**, so promotion/demotion is
one line + a re-run. **Acceptance: qualitative + hard must pass; soft are reported and
never block.** This is how an imperfect digitization gives real quantitative power
without spurious failures — hard-enforce the confident few, soft-measure the rest, let
the human re-tier.

**Scope: model panels only.** If the paper figure overlays empirical *data points /
error bars* the model does not produce, their absence is **not** a finding — but the
model curves, axes, and layout must match.

The **mechanical dozen-point shape check** is a **soft** test generated *from the digitized
points themselves* (the model curve must pass within tolerance of each reference point
across the range), not from a few agent-chosen scalars — it is what catches a *shape*
divergence (a CRF that doesn't plateau, a too-pointy peak) that endpoint/ratio scalars miss.
The human promotes it to hard per panel once the digitization for that panel is trusted.

**The per-figure report (README + `logs/figure_comparisons/`) shows four things:**
(1) the **original** paper figure, (2) the figure **reproduced from the digitization**
(the reference render, or an overlay of it on the paper), (3) the figure **reproduced from
the implementation** (the model record through the same view), and (4) the **qualitative /
hard / soft test list with pass/fail each**, plus the **digitization-audit verdict**
(`logs/digitization_audit/`). (1)↔(2) is the *critic's* judgement of whether the
**digitization** is faithful to the paper (never a self-check); (2)↔(3) shows whether the
*model* is faithful; the test list is the explicit verdict, and the soft rows give the human
a one-step way to tighten the gate.

**No paper figure image ⇒ HARD BLOCKER.** You cannot digitize or verify a panel you
cannot see — there is no fallback, no paper-blind checklist, no weaker tier. Raise the
blocker (`PAPER_IMAGES_NOTE.md`, recording what was tried); the figure — and the model's
sign-off — stays `BLOCKED` until the image is supplied, and is never `faithful` /
`dispositioned` / `reproduced` (the model is incomplete while any required figure is
blocked). Paper *text* is not a substitute. (A "figure" with no paper counterpart is a
diagnostic → `sanity_checks/`, not an in-scope panel.) **Every in-scope figure is
`paper-verified` or `BLOCKED` — no in-between.**

---

## 4. Phase B — implementation, to the structure contract

Reads only `article_aware/` + `logs/`. Build to this shape (the contract is
load-bearing; how a stage computes is the agent's business).

### 4a. Model = a typed-contract stage pipeline

An ordered list of **named stages**, each declared as data in
`implementation/src/<pkg>/stages/manifest.yaml`:

- `name`, `consumes`/`produces` (named, typed quantities **with shapes and
  units** — silent unit drift on a swap is the #1 hidden-coupling failure).
- `citation`/`assumption` (`C-NNN`/`A-NNN`; resolved by `check_citations.py`, §STATUS).
- `seam: { kind: natural | imposed | atomic, rationale: <one sentence> }` —
  Pillar 3's scientific ontology, **required**. `natural` = the swappable hypothesis a
  scientist would conceive (name it); `imposed` = a convenience seam cut through coupled
  math (the confession — pair with a known-limitation + SQ); `atomic` = do not cut here,
  the science says it is one thing. A `natural` tag that merely relabels a data-flow
  boundary is a review reject.
- `params` — the ledger names it reads. **A stage holds no tunable numeric literals.**

Rules: pure by default (declare/isolate any state); the integrator/solver is its own
swappable stage; **fitting/training is a separate stage emitting a persisted, hashed,
provenanced artifact** (`artifacts/`), in v1 stubbed (§5); variants are config, not
code; a swap = replace one stage honoring its contract, nothing else; a model may
depend on another model's **primitive forward stages** — **but not by default; see
§4d** (build your own first, reuse later, audit the reuse) — and **never** on its
*calibrated protocol* (that drags un-re-derivable calibration across as magic numbers
— own it in your own `implementation/calibration.yaml` instead).

### 4b. Figures = protocol → measurement → view

- **protocol** — runs the sweep, returns raw model outputs (`run_figure_<N>()`).
- **measurement** — pure functions → a typed, schema-versioned **measurement record**
  (plotted/tested quantities AND structural facts incl. spatial-layout positions). The
  single source of truth.
- **view** — a thin declarative renderer that *only reads the record* and writes the
  figure PNG. Recomputes nothing. ⚠️ **The view is Phase-A-owned** (generated from the
  digitization, §3b): it lives under `article_aware/`, declares the record schema it
  plots, and renders *both* the digitized reference and the implementation's record
  **identically**. Phase B owns **protocol + measurement** (it produces the record) and
  **does not write the view** — so it cannot deviate on axes, layout, or style.

### 4c. The closed loop

Implement bottom-up along the spec pipeline → run `pytest` (the plugin logs to
`logs/test_runs.jsonl`) → iterate to deterministic-green → render figures (a
deterministic verifier/organizer render step, **never** a claim by the impl agent;
regenerate fresh before any agent reads a PNG — stale renders cause false verdicts) →
the verification regime (§6). Tag each diagnosis `model | figure_gen | spec_scope` and
route the fix accordingly. Honor the iteration cap, then escalate (§7) — never game a
test to green.

**Citation/assumption discipline.** Every `src/` function carries `Citation:` and/or
`Assumption:`. `check_citations.py` (manual, no CI — STATUS.md) checks every tag
*resolves* to a ledger entry; it does **not** check the passage supports the behavior —
that is the Faithfulness Auditor's job. Presence is a weak proxy; the provenance table
(§2) is the real instrument.

### 4d. Code reuse across reproductions — build first, reuse later, audit the reuse

**Default: build your own implementation from this paper's spec, from scratch.** The
independent reimplementation is what makes the reproduction a real test of the paper. If
you *start* by importing another model's forward model, you have not reproduced this
paper — you have **assumed** the other model equals it. (Cautionary case: `hermann2010`
reused Reynolds & Heeger 2009 *by default* and silently inherited R&H's broken
suppression-saturation — a bug it never independently surfaced, because it never built
its own forward model to disagree.)

**Reuse is wanted — but it is a deliberate, LATER step, never the starting point.** Only
after this model is built and **audited faithful on its own** may you replace a
from-scratch stage with a reused one from an ancestor model. And only through a **reuse
audit** (the `audit-reuse` skill): an *independent* model confirms the to-be-reused
implementation **matches THIS paper's description** of that stage — same equations, same
parameters, same behavior on this paper's protocols — *before* the reuse is adopted.
Record the adopted reuse as **lineage provenance** (`lineage_refs.yaml`, `LINEAGE-NNN`,
§5). If the audit finds a mismatch, do not reuse (or reuse only the matching sub-stage).

Why this ordering: reuse-by-default couples models, propagates the ancestor's bugs and
divergences downstream, and skips the very independent check the reproduction exists to
provide. **Build → audit faithful → then reuse-audit → then reuse** keeps reuse's
benefits (consistency, less duplicated work, an explicit genealogy) without its risk.

---

## 5. Calibration is data — two ledgers, typed provenance

Two ledgers by Phase owner; both namespaced per stage:

- `article_aware/spec/calibration.yaml` — **paper-derived** (`source: C-NNN`).
  Phase-A-owned, read-only to Phase B.
- `implementation/calibration.yaml` — implementation-side: 1D-discretization knobs,
  stub magnitudes, calibration carried from a depended-on model (`source: A-NNN |
  SQ-NNN`). Phase-B-writable.

**Every binding entry carries a `kind`** (the 2026-06-02 lesson — thresholds had been
calibrated to the spec's own reference impl, never the paper):

- `kind: paper_value` — a magnitude the paper states. `audited: true` **requires** a
  `quote:` field with the verbatim paper string + `C-NNN`. An `audited:true` with no
  quote — or with a synthesized/paraphrased quote, or `source: A-NNN` (an assumption
  is not a paper quote) — is a faithfulness defect, not a formatting nit.
- `kind: discriminating_threshold` — a margin separating hypotheses. Its note cites the
  paper's *qualitative* claim it operationalizes AND it ships a deliberately-wrong
  falsification (§3a). **`Ref-impl: X` is forbidden as the sole justification** of any
  binding magnitude.

Model code receives the merged resolved ledger (no literals in stage code); the
resolved-ledger hash is recorded in every measurement record and verdict. The state
report counts `audited:false` in both ledgers — a high count is honest, the point is
containment in one reviewable place.

---

## 6. Verification — the faithfulness regime

Deterministic tests (§3a) and any VLM/checklist check establish *internal consistency
and gestalt*. **Neither establishes fidelity to the paper.** That is the job of two
standing, report-only critics with **inverted error-bias** (in a faithfulness library a
false-pass is far costlier than a false-fail) — incentivized to *find divergences*,
never the builder, never able to edit what they judge:

| | Faithfulness Auditor (`skills/audit-faithfulness`) | Process Auditor (`skills/audit-process`) |
|---|---|---|
| **data** | the full paper + the finished implementation (+ original code/lineage) | the change/reasoning trail: SQs, assumption rationales, diffs, commit reasons, test/diagnosis logs — **not** the paper |
| **asks** | does the model match the paper? (equations operator-by-operator; ledger values vs paper quotes; rendered figures vs the paper image on the §3b dimensions) | is the *way we got here* drifting toward green instead of faithfulness? |
| **runs** | post-build (re-renders itself; never trusts a committed PNG) | after a paper accumulates an iteration trail; and a corpus-level pass between waves (cross-model drift) |

They are orthogonal and complementary: one catches wrong science, the other catches
reasoning drift the first misses (e.g. a fabricated `audited:true` quote whose *value*
happens to match the figures). The **adversarial judge** is paper-blind by construction
and therefore **not** a faithfulness instrument — use it only for internal/logical
claims that resist coding, never for "does this match the paper."

**Auditor output statuses (these have teeth — they are not advisory):**
`FAITHFUL` · `DIVERGENT` (contract/implementation — must be fixed) · `SUSPECTED-PAPER-
ISSUE` (the faithful build contradicts the paper — a first-class deliverable routed to
the human, never an assumption that flips a test and re-greens) · `ILLUSTRATIVE-NOT-
REPRODUCED` (a result-bearing stub; the figure shows a constructed answer) ·
`BLOCKED` (no paper figure image — §3b; the figure and the model's sign-off are blocked
until the image is supplied; never reported as faithful or dispositioned).

**Every in-scope figure is `paper-verified` or `BLOCKED` (§3b)** — there is no
in-between (no "checklist-only" or "self-referential" verified state). A `BLOCKED`
figure blocks the model's `reproduced` sign-off until its paper image is supplied.

### Acceptance — a model is `reproduced` only when ALL hold

1. Every stage has contract tests; every plotted quantity a deterministic measurement
   test (a consistency tripwire — §3a — not a fidelity check).
2. Every in-scope figure panel's **qualitative + hard** tests pass against the
   paper-digitized reference, and the digitization passed its **separate-critic audit**
   (`skills/audit-digitization`, never a self-check) vs the paper panel (§3b); soft tests
   are reported (never block). **No required figure is `BLOCKED`** for a missing image (a
   blocked figure makes the model incomplete — §3b).
3. A **modification smoke test** passes by **editing a real `implementation/
   calibration.yaml` entry on disk and regenerating the figure from the rebuilt
   model** — *not* a resolver monkeypatch (which proves only a value is read), and the
   swapped unit is a **stage** (enum/artifact), not a scalar knob. The orchestrator
   *collects* the outcome (a self-graded, unreported smoke test = no test). This is the
   operational definition of "a scientist can change it."
4. The **Faithfulness Auditor** returns no unresolved `DIVERGENT` / `ILLUSTRATIVE` /
   `SUSPECTED-PAPER-ISSUE`, and the **Process Auditor** does not return
   `drifting-toward-leniency`.

Any open finding → the model is **`partial`, never `reproduced`**, until the organizer
or human dispositions it. The headline status must derive from a paper-binding
instrument independent of the checklist chain — **never let the report that spends the
human's attention be authored by the signal it is supposed to audit.**

### How the orchestrated workflow enforces this (`full-pass.js`)

Until 2026-06-14 the acceptance list above was *described* but not *enforced* — the
workflow could exit `faithful` with several conditions unchecked (the gap documented in
`proposals/process-drift-register-2026-06-14.md`). It is now wired as concrete gates.
**Vocabulary:** the workflow emits `faithful | partial | blocked`; `reproduced` is the
human-facing name for **`faithful` with no open findings**. Mapping of acceptance items
to mechanism:

- **Item 1 (test coverage)** — delegated to the test suite + `audit-tests`; the
  orchestrator does not independently enumerate per-stage coverage *(target, not gated)*.
- **Item 2 (digitization is a verified ruler)** — **gated.** A `DIVERGENT`/`TOOL_MISUSE`
  digitization caps the exit at `partial` (the model is never graded `faithful` against
  an unconfirmed reference); a `BLOCKED` figure likewise. The audit returns a **per-panel**
  verdict so a bad panel can't hide in a rolled-up figure status.
- **Item 3 (modification smoke test)** — **partial.** The workflow runs a *minimal*
  smoke test: perturb one `calibration.yaml` **scalar** on disk, re-render, confirm the
  figure responds, revert. This proves the parameter is wired to the output; it is **not**
  the full Pillar-3 **stage-swap** test (§4a / VISION Pillar 3), which awaits explicit
  stage seams (*not built — the gap*). Recorded in the exit, not yet a hard gate.
- **Item 4 (auditors have teeth)** — **gated.** An open `GENUINE_DIVERGENCE` (≈
  `SUSPECTED-PAPER-ISSUE`/`ILLUSTRATIVE`) caps the exit at `partial`; a `drifting`
  Process-Auditor trajectory caps at `partial`. The conceptual statuses above map to the
  workflow's `FAITH_VERDICT` tags: `CONTRACT_BUG`/`CODE_BUG` = fixable `DIVERGENT`,
  `PAPER_ISSUE` = `SUSPECTED-PAPER-ISSUE`, `GENUINE_DIVERGENCE` = an unresolved divergence.
- **Coverage gate (the keystone)** — **gated.** Independent of content, every target
  figure must carry its three **committed** views (paper crop `article_aware/figures/
  figure_N.png` · digitized · implemented render `figures_reproduced/figure_N.png`) plus a
  committed faithfulness audit (`tools/check_figure_coverage.py`). A required step that
  silently did not run **blocks** the exit instead of riding along as a footnote — the
  structural fix for "the description drifted from what the machinery does."

The **figure-faithfulness instrument is `audit-faithfulness`** (re-render the model, compare
against the digitized reference — paper-grounded by the separate digitization audit — and the
paper). The older `compare-figure` / `neuromodels compare-figure-packet` VLM-checklist quorum is
**superseded** by it and is now an optional supplement, not part of the orchestrated loop.

---

## 7. Escalation, error-bias, and falsification triggers

- **Spec questions** → append to `logs/spec_questions.md` (`SQ-NNN`, self-contained:
  `spec_ref`, `question`, `chosen_assumption`, `human_resolution` once resolved). The
  agent proceeds on the chosen assumption.
- **The non-halt policy belongs to the PROGRAM, never the VERDICT.** "Move on to the
  next model" is a program rule; it must not leak into the gate as "log the failure and
  continue." A failed figure / auditor finding writes a durable status to a re-queue
  the organizer reads; a computed-but-inert failure list is forbidden. **Distinguish
  three exits** — the agent that hit the wall may not self-certify which: `UNRESOLVED`
  (effort exhausted — re-queueable process debt) · `DEFERRED-SCOPE` (human-ratified
  boundary; an agent may propose, only the human closes) · `SUSPECTED-PAPER-ISSUE`
  (routed to the human). A deferral stays *open* until retried or human-ratified.
- **Falsification triggers — stop and escalate a redesign, don't patch around:** the
  modification smoke test is impossible without touching unrelated code (the
  decomposition is wrong); the calibration ledger is not materially cleaner than ad-hoc
  literals; agents spend more effort serving the scaffold than reproducing the paper.

---

## 8. Per-model layout

```
models/<m>/                  # a private git submodule; the parent bumps the pointer
  paper/                     # raw PDF + extracted_text + figure images — extractor (Phase A) only
  article_aware/             # PROTECTED — Phase A contract
    spec/{model_spec,calibration,citations,assumptions}.yaml   APPROVED
    pseudocode/<fig>_protocol.md
    figures/figure_<N>.<img>            whole paper figure  [no image ⇒ HARD BLOCKER, §3b]
    figures/figure_<N>_layout.yaml      panel grid: positions + reproduced vs `not reproduced`
    figures/figure_<N>/panel_<X>.<img>           per-panel crop of the paper figure
    figures/figure_<N>/panel_<X>_digitized.*     ~dozen digitized curve points (the reference, §3b)
    figures/figure_<N>/panel_<X>.md              per-panel: axis limits + the qual/hard/soft test list
    figures/views.py                    Phase-A-owned VIEW (§3b/§4b): renders digitized reference AND impl record identically
    extracted_data/test_<fig>.py        codified qualitative/hard/soft panel tests (per-test tier flag)
  implementation/            # Phase B
    src/<pkg>/stages/ + manifest.yaml   measurements.py  protocols.py   [the VIEW is Phase-A — §3b/§4b]
    calibration.yaml   artifacts/ (frozen stubs)   tests/   sanity_checks/   figure_outputs/ (gitignored)
  logs/                      # test_runs.jsonl  figure_comparisons/  figure_diagnoses/
                             #   faithfulness_audit/  process_audit/  spec_questions.md
  figures_reproduced/        # COMMITTED paper-vs-reproduced snapshot (NOT pipeline-produced;
                             #   freshness NOT guaranteed — the authoritative render is figure_outputs/.
                             #   An auditor must render fresh, not trust this snapshot.)
  README.md                  # the reviewable per-model state report
```

`sanity_checks/` (exploratory, **no `assert`** — the moment you assert, it is a test in
`tests/`); generated `_outputs/` gitignored.

---

## 9. Git discipline & commit cadence

- Work on a **feature branch inside the model submodule** (`git -C models/<m>`);
  **never** a parent-repo git op from a model agent. The model `main` advances via a
  **squash-merge PR**; `guard-main-branch.sh` blocks a direct `git push origin main`.
- The parent's **submodule-pointer bumps are the organizer's serial job** — commit only
  inside the model repo; never `--amend` the parent from a model agent.
- Commit milestones: spec+pseudocode; data+figures+`APPROVED`; a component's tests
  green; a figure faithful/dispositioned. Push throughout. **Commit all work before
  the re-audit reads it** (an uncommitted fix the re-audit passed is lost work).

---

*Provenance: this document consolidates the former WORKFLOW + ARCHITECTURE +
REPO_STRUCTURE + DESIGN + ARCHITECTURE_WATCHLIST (2026-06-03), folding their
load-bearing content here and deleting the redundant files. Diagnosis behind the
faithfulness rules: `proposals/figure-faithfulness-postmortem-2026-06-02.md`,
`proposals/faithfulness-enforcement-2026-06-02.md`,
`proposals/faithfulness-rerun-report-2026-06-03.md`.*
