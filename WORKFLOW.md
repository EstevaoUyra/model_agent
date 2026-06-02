# Workflow — how to reproduce a model end-to-end

Operational guide for one model reproduction. *Where* things live:
[REPO_STRUCTURE.md](REPO_STRUCTURE.md). *Why* the shape: [DESIGN.md](DESIGN.md).
*What each model must become*: [ARCHITECTURE.md](ARCHITECTURE.md). *What is
actually built*: [STATUS.md](STATUS.md). For the **autonomous reproduction
program** (waves, critique-agent gates, the no-stop policy), see
[proposals/reproduction-program-plan-2026-06-02.md](proposals/reproduction-program-plan-2026-06-02.md).

Two phases separated by a hard article-access boundary:

- **Phase A (article-aware):** read `paper/`, produce the self-sufficient
  `article_aware/` contract. Gate: `article_aware/APPROVED`.
- **Phase B (no article access):** implement from the spec alone; iterate
  against tests + figures. **Never reads `paper/`.**

The boundary is the load-bearing design choice: anything not in `article_aware/`
is, by definition, an underspecification → recorded as an `Assumption`.

## Reality, and the autonomous program — read this first

The real loop is **skills + plain `pytest` (a plugin logs to `test_runs.jsonl`)
+ VLM subagents + a documented iteration cap**, driven by the organizer. The
"framework runner", the stuck-detector / `STUCK` gate, the citation static-check,
the `relaxed`/`pending_human_review` statuses, `CurveTolerance`,
`paper_issues.md`, and `review_queue/` that earlier drafts described **were never
built and have been removed** (STATUS.md).

Gates are *canonically* human (Phase-A `APPROVED`, faithfulness verdict). In the
**autonomous reproduction program** they are substituted by **adversarial
critique agents** — a spec-review panel writes `APPROVED` in the human's stead,
and the verdict combines the faithfulness rubric + multi-subagent VLM +
attacker/defender judge — with the human called **once, at the end**. See the
program plan.

## Roles

- **Article extractor (Phase A)** — reads `paper/`, writes `article_aware/`.
- **Implementation agent (Phase B)** — reads `article_aware/` (read-only) +
  `logs/`; writes `implementation/`; appends to `logs/spec_questions.md`.
  **Never reads `paper/`.**
- **Critique / judge agents** — the spec-review panel and the attacker/defender
  verdict judges (DESIGN §3); see the program plan for how they substitute for
  the human gates.

## Phase A — article-aware

Produce everything a paper-blind implementer needs. Follow
`skills/extract-spec/SKILL.md` and `skills/extract-figure/SKILL.md`. Artifacts
under `article_aware/`:

- `spec/model_spec.yaml` — state variables, parameters, equations, components,
  the ordered **paper-derived pipeline (dataflow)**, and `simulation_protocols`
  (each declaring its `expected_outputs`). Pydantic-validated.
- `spec/calibration.yaml` — the **paper-derived** parameter ledger
  (ARCHITECTURE §3); Phase-A-owned, `source: C-NNN`.
- `spec/citations.yaml` (`C-NNN`) · `spec/assumptions.yaml` (`A-NNN`).
- `pseudocode/<figure>_protocol.md` — inputs, procedure, named outputs, expected
  behavior, one per protocol.
- `figures/figure_<N>.md`, `figure_<N>_visual_checklist.md`, and the paper figure
  image — central to the VLM flow.
- `extracted_data/test_figure_<N>.py` — qualitative claims as ordinary pytest
  tests asserting on the protocol's named outputs / the measurement record.
  Reduce to deterministic wherever possible. **For visual words** ("saturates",
  "sigmoidal") the VLM is the binding check and the deterministic test is a
  regression tripwire — and tighten the proxy so passing it implies the visual
  reads right. **Shape claims** (turnover / end-stopping / peak / saturation) must
  assert the STRICT structure — e.g. an interior argmax that exceeds *both*
  endpoints by a ledger margin — so a monotonic/plateau curve fails (Wave-1
  spratling figure_5b: a loose proxy passed a curve with no end-stopping; the
  independent VLM, not the impl agent's self-check, caught it). **For schematic figures**, assert spatial-layout structure
  (positions live in the measurement record) — guards the "Figure-1 class"
  (deterministically perfect, visually broken).
- **Literature-grounding / parameter-provenance table** (the adopted process
  upgrade): for each significant parameter/choice — `value | stated-in-paper |
  relative-only | inferred | evidence (cited ref / lineage / follow-up / original
  code) | sensitivity`. This evidence is what lets the final review trust the
  reproduction cheaply.

**Faithfulness rules (extraction) — Wave-1 retro, non-negotiable.**

- **Never confabulate.** Do not assert a mechanism or a quantitative claim the
  paper does not state. Every test claim traces to a specific paper passage
  (cite it) or is an explicit `A-NNN` assumption with provenance — never a
  fabricated claim wearing a real `C-NNN`. (Wave 1: an extractor invented a false
  "identity dictionary ⇒ coefficients unchanged" mechanism and a kurtosis claim
  the paper never makes — caught by the spec-review panel.)
- **Thresholds live in the ledger.** Binding numeric thresholds go in
  `calibration.yaml` (`audited:false` + `A-NNN`), not hidden in test code — the
  human audits the *ledger*, not the code.
- **One convention, everywhere.** Unit/scale conventions (contrast
  fraction-vs-percent, curve-peak-vs-raw-coefficient) must be singular and
  identical across spec, calibration, and provenance.
- **Verify internal consistency** with a throwaway reference implementation
  before finalizing: does the spec's own recipe actually satisfy its qualitative
  claims?

**Gate:** `article_aware/APPROVED` (empty sentinel). The human writes it; in the
autonomous program the spec-review panel writes it after attacking the spec for
completeness (can a paper-blind agent build it?) and faithfulness (is every
assumption evidenced?).

## Phase B — implementation

Reads only `article_aware/` + `logs/`. Build to the ARCHITECTURE shape
(`src/<pkg>/stages/` + `manifest.yaml`, `measurements.py`, `views.py`,
`protocols.py`, `implementation/calibration.yaml`, `artifacts/`). The closed
loop:

1. Implement bottom-up along the spec `pipeline`, smallest helpers first.
2. Run `pytest` — the plugin logs each test to `logs/test_runs.jsonl`; follow
   `skills/run-tests`. **Deterministic tests assert on the measurement record**
   (golden-file style), so a passing test and the figure cannot disagree.
3. Generate figure PNGs; run the **multi-subagent VLM compare**
   (`skills/compare-figure`): **≥3 subagents + a parent image-read** for changed
   / contested / soft-blocked figures, 1 for stable-green. Persist the
   per-subagent splits, not just the adjudicated result.
4. Diagnose each issue, tagged `model | figure_generation | spec_scope`, and
   route the fix accordingly. **Before sweeping calibration knobs**, write the
   closed form for the recorded quantity and identify which knob can actually
   move the failing value (avoids the "nothing works, looks stuck" trap).
5. Repeat until **deterministic green + VLM pass**, or the **iteration cap**
   trips → escalate (below).

**Figure faithfulness (Wave-1 figure_1 lesson).** For schematic figures the view
must reproduce the *specified iconography* — the exact glyphs/panels the visual
checklist names (e.g. a sigmoid + arrow-stack pool, two Gabors in a dashed RF
ellipse) — not simplified box/text placeholders; correct topology with wrong
iconography still fails the binding checklist. For multi-panel paper figures,
render the model panels in the paper's layout so the generated PNG lines up with
`article_aware/figures/figure_<N>.*`.

**Calibration.** Implementation-side knobs, 1D-discretization, and frozen-fit
stub magnitudes go in `implementation/calibration.yaml` (Phase-B-writable,
ARCHITECTURE §3) — **never as literals in stage code**. Fitting/training is a
**stubbed** stage: a frozen, **hashed, provenanced** learned-parameter artifact
under `artifacts/`; the forward path consumes it deterministically.

**Citation/Assumption docstring discipline.** Every function in
`implementation/src/` carries `Citation:` (`C-NNN`) and/or `Assumption:`
(`A-NNN`). A cheap **presence** check enforces presence only (not quality);
quality is a periodic audit. (The presence check is built as part of this
program — STATUS.md.)

**Acceptance (ARCHITECTURE §5).** Every stage has contract tests; every plotted
quantity a deterministic measurement test; the VLM backstop passes; and the
**modification smoke test** passes — swap one stage for a trivial variant *via
config only*, with zero edits to unrelated code. If (4) can't be met without
touching unrelated code, the decomposition is wrong — fix the contracts.

## Escalation

- **Spec questions** → append to `logs/spec_questions.md` (`SQ-NNN`,
  append-only, self-contained: `spec_ref`, `question`, `chosen_assumption`, and
  `human_resolution` once resolved). The agent continues with the chosen
  assumption.
- **Cap reached / no progress (the "STUCK" condition).** The stuck-detector
  isn't built; honor the documented iteration cap + repeated-diff signal. In the
  autonomous program a STUCK model is **deferred to a later wave** — retried once
  neighbors and the improved process may unblock it — **never allowed to halt the
  program**; residual unreproduced models at the end are recorded as learning
  (program plan §6).
- **Falsification triggers** (modification smoke test impossible; calibration
  ledger not materially cleaner than ad-hoc; agents serving the scaffold more
  than reproducing) → **stop and escalate a redesign pass**, don't patch around
  (ARCHITECTURE_WATCHLIST).

## Adversarial judge

For claims that resist deterministic + VLM checks, a pair of judges (attacker,
defender) each see exactly `rubric` / `context` / `under_review` and nothing else
— not the paper, run/test IDs, each other's output, or prior runs. CLI:
`neuromodels judge run --rubric-file … --context-file … --under-review-file …`.
Canonically the human decides; in the autonomous program the verdict combines the
judge with the leaf rubric + VLM panel (program plan §1).

## Spec edits invalidate prior passes

The plugin records `spec_commit_hash` (git tree hash of `article_aware/`) on
every test row. It is an **advisory** filter (no tooling): if `article_aware/`
changes mid-Phase-B, rerun affected tests. Selective dependency-aware
invalidation is deferred.

## Sanity checks

Exploratory diagnostics, **never tests** — the moment you write `assert`, it is a
test. Follow `skills/write-sanity-check`. They live in
`implementation/sanity_checks/`; generated `_outputs/` are gitignored.

## Commit cadence (program plan §7)

Per-model submodule, on its own **feature branch**: after spec+pseudocode; after
data+figures+`APPROVED`; when a component's tests pass; when a figure goes green
(deterministic + VLM). **Push throughout.** The model `main` is advanced once, by
a squash-merge PR, before the final review. **Commit only inside the model repo**
— never the parent (a real past incident: an agent `--amend`-ed the parent); the
parent's submodule-pointer bumps are the organizer's serial job.
