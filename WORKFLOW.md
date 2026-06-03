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
critique agents** — a spec-review panel returns a verdict, the *organizer* writes
`APPROVED` on it, and the verdict combines the faithfulness rubric + multi-subagent
VLM + the standing **Faithfulness Auditor** — with the human called **once, at the
end**. See the program plan.

> **2026-06-02 redesign — read this.** The first autonomous run's verdict was a
> 3-voter VLM majority against a *paper-blind qualitative checklist*. A corpus audit
> found **49% of figures major-or-wrong despite green verdicts**; the attacker/defender
> judge meant to counter lenient LLM verdicts **never ran**. The root cause: the
> process measured *internal self-consistency*, never *distance to the paper* — no
> agent ever held the full paper and the implementation together. The redesign
> ([proposals/faithfulness-enforcement-2026-06-02.md](proposals/faithfulness-enforcement-2026-06-02.md))
> adds the **Faithfulness Auditor** (`skills/audit-faithfulness`, the paper+code
> critic), makes the previously-"non-binding" figure dimensions binding, splits the
> reviewer verdict from the gate, and gives failing the gate **consequences** (below).
> The governing principle, non-negotiable: **a false-pass is far costlier than a
> false-fail** — in a faithfulness library the verdict's error-bias is the *inverse*
> of a CI test suite's. Critique comes from agents incentivized to **find divergences**,
> never to drive tests green.

## Roles

- **Article extractor (Phase A)** — reads `paper/`, writes `article_aware/`.
- **Implementation agent (Phase B)** — reads `article_aware/` (read-only) +
  `logs/`; writes `implementation/`; appends to `logs/spec_questions.md`.
  **Never reads `paper/`.**
- **Critique / judge agents** — the spec-review panel and the attacker/defender
  verdict judges (DESIGN §3); see the program plan for how they substitute for
  the human gates.
- **Faithfulness Auditor** (`skills/audit-faithfulness`) — post-build critic that
  holds the *full paper + implementation + lineage* and finds divergences (the one
  instrument that compares to the paper). Report-only.
- **Process Auditor** (`skills/audit-process`) — meta-critic that reads the *change /
  reasoning trail* (SQs, assumption rationales, diffs, commit reasons, diagnosis logs)
  — **not** the paper — and flags whether the trajectory is drifting toward leniency.
  Report-only.

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
  human audits the *ledger*, not the code. **Self-check before finishing: grep
  your tests for hard-coded numeric literals; every binding threshold must be a
  ledger entry read via the calibration fixture** (only definitional constants
  like the Gaussian-kurtosis 3.0, and float guards like 1e-9, may stay inline,
  annotated). Wave-2: 2 of 6 extractions still buried one — the gate caught them;
  prevent it at the source.
- **One convention, everywhere.** Unit/scale conventions (contrast
  fraction-vs-percent, curve-peak-vs-raw-coefficient) must be singular and
  identical across spec, calibration, and provenance.
- **Verify internal consistency** with a throwaway reference implementation
  before finalizing: does the spec's own recipe actually satisfy its qualitative
  claims?

**Gate:** `article_aware/APPROVED` (empty sentinel). **Verdict and gate are
separate** (a single agent that judges *and* writes its own gate is grading its own
homework — it under-blocks to keep the program moving). The reviewer returns only a
structured verdict; the **organizer writes `APPROVED`** on `verdict==approved`. Use
**≥2 genuinely independent reviewers** (a real panel, not N=1); disagreement routes
to the human. Reviewers attack the spec for completeness (can a paper-blind agent
build it?) and faithfulness (is every assumption evidenced *and quoted*?), and —
because an extractor and a reviewer reading the same dense passage share misreadings —
every `audited:true` value is cross-checked against a **captured verbatim quote** and,
where available, the lineage/author-code, not a single correlated re-read.

**Sufficiency, not just necessity (the 2026-06-02 lesson).** A checklist or shape
test is validated by showing a *deliberately-wrong* artifact **fails** it — not only
that the right one passes. Before `APPROVED`: every shape claim must be shown to fail
on a degenerate curve (monotone/plateau/flat); every figure checklist must bind the
discriminating dimensions (normalization convention, width, baseline, panel layout —
see `skills/extract-figure`). A known-bad artifact that passes is a hard reject.

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
   per-subagent splits, not just the adjudicated result. **Regenerate every figure
   from the committed model immediately before any agent reads it** — as a
   **deterministic verifier/organizer render step, never as a claim by the impl
   agent** (Wave-2 bell figure_4 was a stale noise PNG while the model produced
   localized=0.95 filters — wasting a fix cycle).
   **The VLM-checklist verdict establishes internal consistency and gestalt — NOT
   faithfulness to the paper.** It is a build-loop tripwire, not the faithfulness
   gate (it passed 49% major-or-wrong figures in the first run). Faithfulness to the
   paper is established only by the **Faithfulness Auditor** (`skills/audit-faithfulness`),
   which compares the freshly-rendered figure, the code equations, and the ledger
   values against the *paper itself*. Do **not** re-derive a "never false-green"
   reassurance from the re-render discipline — staleness was one failure mode; the
   dominant one is a self-consistent model that is uniformly wrong, which no amount of
   re-rendering catches.
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
(`A-NNN`). A cheap static check (`neuromodels/framework/static_checks/check_citations.py`,
run manually — no CI wired) verifies **presence + resolution**: every tag resolves to
a real entry in that model's `citations.yaml` / `assumptions.yaml`. It does **not**
check that the cited passage actually grounds the function — presence is a weak proxy
(one `C-NNN` can be sprayed across unrelated functions). Real per-claim grounding is
the **Faithfulness Auditor's** job, against the paper; the provenance table
(`stated-in-paper | relative-only | inferred | evidence | sensitivity`) is the
artifact a human trusts, not the docstring tag.

**Acceptance (ARCHITECTURE §5).** A model is `reproduced` only when ALL hold:
every stage has contract tests; every plotted quantity a deterministic measurement
test (an internal-consistency tripwire — it does **not** establish paper fidelity);
the VLM backstop passes (gestalt); the **modification smoke test** passes by editing
a **real `implementation/calibration.yaml` entry and regenerating the figure from
disk** (a resolver monkeypatch does NOT count — it proves only that a value is read,
not that a scientist's edit re-verifies); and the **Faithfulness Auditor returns no
unresolved `DIVERGENT` / `ILLUSTRATIVE-NOT-REPRODUCED` / `SUSPECTED-PAPER-ISSUE`
finding**. Any such finding makes the model **`partial`, never `reproduced`**, until
the organizer or human dispositions it. If the smoke test can't be met without
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
  program**.

- **The non-halt policy belongs to the PROGRAM, never to the VERDICT (2026-06-02).**
  "Keep moving to the next model" is a program rule; it must not leak into the gate as
  "log the failure and continue." A failed figure / auditor finding is **load-bearing**:
  it writes a durable status to a corpus re-queue the organizer's between-wave step
  reads and re-spawns, and any model with an open finding is reported **`partial`,
  never `reproduced`**. A computed-but-inert `notGreen` list (the first run's bug) is
  forbidden. **Distinguish three exits** — the agent that hit the wall may **not**
  self-certify which:
  - `UNRESOLVED` — effort exhausted (cap hit). A *process debt*, eligible for re-queue.
  - `DEFERRED-SCOPE` — a genuine scope boundary. A **human-ratified** decision; an
    agent may *propose* it, only the human closes it. A deferral stays **open** until
    retried with the improved process OR human-ratified — closing one as "scope"
    without a retry is itself the human's call, not a convenient relabel.
  - `SUSPECTED-PAPER-ISSUE` — the faithful build contradicts the paper. A first-class
    faithfulness finding routed to the human (VISION: the map of where the paper is
    wrong is a deliverable), **never** an assumption that flips the test and re-greens.
- **Falsification triggers** (modification smoke test impossible; calibration
  ledger not materially cleaner than ad-hoc; agents serving the scaffold more
  than reproducing) → **stop and escalate a redesign pass**, don't patch around
  (ARCHITECTURE_WATCHLIST).

## Adversarial judge

For claims that resist deterministic + VLM checks, a pair of judges (attacker,
defender) each see exactly `rubric` / `context` / `under_review` and nothing else
— not the paper, run/test IDs, each other's output, or prior runs. CLI:
`neuromodels judge run --rubric-file … --context-file … --under-review-file …`.

**The judge is paper-BLIND by construction, so it is NOT a faithfulness instrument**
— it adjudicates internal/logical claims, never "does this match the paper." Do not
route faithfulness verdicts to it; that is the **Faithfulness Auditor's** job (which
is paper-, code-, and lineage-aware on purpose). Honesty note: in the first
autonomous run the judge was **never actually invoked** (the per-claim rubric/context
setup was skipped under throughput pressure), so the real verdict was the lenient VLM
majority alone — a documented contributor to the 49% miss. Either wire it in for the
resisting-claim class it was built for, or do not list it as an active gate.

## The two standing critics — orthogonal forces toward faithfulness

The first run had no instrument that measured distance to the paper, and none that
watched *how decisions were made*. Two critic phases close both gaps. They are
**independent forces looking at completely different data**, and both are
report-only, find-issues-incentivized (a false-pass is far costlier than a
false-fail), and never the builder:

| | Faithfulness Auditor | Process Auditor |
|---|---|---|
| **skill** | `skills/audit-faithfulness` | `skills/audit-process` |
| **data** | the paper + the implementation (+ lineage) | the change/reasoning trail: SQs, assumption rationales, diffs, commit reasons, diagnosis & test logs |
| **question** | does the model match the paper? | is the way we got here drifting toward green instead of faithfulness? |
| **needs the paper?** | yes — it *is* the standard | **no** — it audits the reasoning, not the match |
| **catches** | wrong equation/value/figure; constructed results; laundered contradictions | goalpost-moving, contradiction-laundering, scope-as-escape, proxy-substitution, the *aggregate drift* |

**When they run (critic phases).** Both run *after a paper has accumulated an
iteration trail*, not per-figure:

- **At model-close** — both are acceptance inputs (§5). A model with an unresolved
  Faithfulness finding **or** a `drifting-toward-leniency` process verdict is
  `partial`, never `reproduced`.
- **Between waves, at corpus scale** — the Process Auditor runs a corpus-level pass:
  some drift is only visible across models (the same lenient move repeated — the
  normalization inversion across pestilli/heeger/doostani had one Phase-A origin no
  per-model view could see).

They are complementary, not redundant: a model can pass the faithfulness audit today
yet show a drift trajectory that predicts tomorrow's failure; and when a faithfulness
miss *does* surface, the process auditor's pinpointed decision is usually the fastest
explanation of *why* it happened.

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
