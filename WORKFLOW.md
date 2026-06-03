# How to reproduce a model — the process

This is **the single authoritative description of how a paper should be reproduced**:
the phases, the artifacts, how tests are generated, the structure each model must
take, and how faithfulness is verified. It is the *how*.

- *Why this project exists / what "faithful" means*: [VISION.md](VISION.md) (the four
  pillars — the apex standard; faithfulness wins every conflict).
- *What is actually built (vs. described)*: [STATUS.md](STATUS.md) — **canonical on
  reality; wins on any conflict.** This document describes the target process; where a
  mechanism here is not yet tooling, STATUS.md says so.

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

**Gate — `article_aware/APPROVED`.** Verdict and gate are **separate**: a reviewer
returns a structured verdict; the **organizer writes `APPROVED`** on it. Use **≥2
independent reviewers** (a real panel, not N=1 self-certifying its own gate);
disagreement routes to the human. Before `APPROVED`: every checklist must pass the
**sufficiency test** (§3) and every `audited:true` value must carry a captured verbatim
quote (§5).

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

### 3b. Figure / visual tests — `figure_<N>_visual_checklist.md`

The checklist is the binding set of pass/fail visual claims for a figure. **It is
authored by looking at the paper's figure image**, and it is the standard the
Faithfulness Auditor (§6) and any VLM check the rendered figure against.

- **The checklist is generated FROM the paper figure image** (`figure_<N>.<img>`).
  Each binding item is a claim about *what the paper's figure actually shows*, on the
  **discriminating dimensions**: the **normalization convention** (state explicitly
  which curve/quantity is pinned to 1.0 — the single most common silent divergence),
  **curve shape and width/bandwidth**, **baseline / floor / asymptote**, **panel
  layout** (enumerate the panels the paper has; *forbid panels it does not* — never
  pre-bless "the difference curve, if plotted"), and **axes** (range, scale, sign
  convention, labels, ticks). Comparative phrasing is fine, but it must **fail when the
  figure stops matching the paper** — "robust to scale" must never mean "tolerant of
  the divergence that matters."
- **Scope: model panels only.** If the paper figure overlays empirical *data points /
  error bars* the model does not produce, their absence is **not** a finding — but the
  model curves, axes, and layout must match.
- **No paper figure image ⇒ HARD BLOCKER. Stop — do not work around it.** The figure
  cannot be reproduced or verified without it; there is **no fallback, no paper-blind
  checklist, no weaker "tier."** Do NOT author a checklist from the model's intended
  behavior and call it verification — that loop grounds nothing (the 2026-06-03
  finding: extractor, VLM, and auditor all end up "verifying" the model against a
  description of itself). Instead:
  1. **Raise a blocker** (`PAPER_IMAGES_NOTE.md` in the figures dir) recording what was
     tried to obtain the image.
  2. **The work is BLOCKED.** That figure — and the model's sign-off, which depends on
     it — stays `BLOCKED` and **can only be resumed once the figure image is supplied**
     (by the human). A blocked figure is never `faithful`, `dispositioned`, or
     `reproduced`, and the model is **not complete** while any required figure is
     blocked. Paper *text* is **not** a substitute — the binding check is a visual
     comparison and requires the image.
  - (If a "figure" has no paper counterpart at all — a diagnostic the reproduction
    invented — it is not a reproduction target: move it to `sanity_checks/`; it does
    not get an in-scope checklist.)
- **Every in-scope figure is therefore in exactly one of two states: `paper-verified`
  (checked against the paper image) or `BLOCKED` (no image).** There is no "verified
  against the checklist" state, and a `BLOCKED` figure blocks the model.

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
depend on another model's **primitive forward stages**, never on its *calibrated
protocol* (that drags un-re-derivable calibration across as magic numbers — own it in
your own `implementation/calibration.yaml` instead).

### 4b. Figures = protocol → measurement → view

- **protocol** — runs the sweep, returns raw model outputs (`run_figure_<N>()`).
- **measurement** — pure functions → a typed, schema-versioned **measurement record**
  (plotted/tested quantities AND structural facts incl. spatial-layout positions). The
  single source of truth.
- **view** — a thin declarative renderer that *only reads the record* and writes
  `implementation/figure_outputs/figure_<N>.png`. Recomputes nothing; style lives here.

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
2. Every in-scope figure checklist was **authored from the paper image** and holds
   against it; **no required figure is `BLOCKED` for a missing image** (a blocked
   figure makes the model incomplete — §3b).
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
    figures/figure_<N>.<img>            whole paper figure  [no image ⇒ blocker, §3b]
    figures/figure_<N>_layout.yaml      panel grid: positions + reproduced vs `not reproduced`
    figures/figure_<N>/panel_<X>.<img>  per-panel crop of the paper figure
    figures/figure_<N>/panel_<X>.md     per-panel description: axis limits (x/y/right, scale) + checklist
    extracted_data/test_<fig>.py
  implementation/            # Phase B
    src/<pkg>/stages/ + manifest.yaml   measurements.py  views.py  protocols.py
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
