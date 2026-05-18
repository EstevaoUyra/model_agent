# ARCHITECTURE — the structure every reproduction must produce

STATUS.md says what the framework *has*. This says what every reproduced
model *must be shaped like*. It is a **scaffold of contracts, not a
prescription of internals** — the contracts are load-bearing; how a stage
computes its output is the agent's business.

The end goal is not "figures match the paper." It is a substrate where a
scientist who starts from a reproduced model can cheaply **(a) verify
faithfulness and (b) swap one component — a function, a stage, the input
encoding — and re-verify**, and likewise change *what a figure measures*
without rewriting opaque plot code. Every contract below exists to serve
that goal. Grounded in NeuroML/LEMS, SciUnit, PyNN, showyourwork, Hydra,
and golden-file regression practice (see `proposals/` for the research
synthesis).

This is **v1, expected to change with experience.** The "named stages"
abstraction is a working hypothesis; see
[ARCHITECTURE_WATCHLIST.md](ARCHITECTURE_WATCHLIST.md) for what we are
deliberately watching for and what would falsify it.

---

## 1. Model = a typed-contract stage pipeline

A model is an **ordered list of named stages**. The *contract* is the
primary artifact; the ordering is secondary.

Each stage declares, as data (in `model_spec.yaml`):

- `name` — stable identifier (e.g. `stimulus_drive`, `attention_field`,
  `suppression`, `normalization`, `readout`).
- `consumes` / `produces` — named, typed quantities with shape **and
  units/dimensions**. Units are part of the contract (LEMS lesson:
  silent unit drift on a swap is the #1 hidden-coupling failure).
- `citation` / `assumption` — `C-NNN` / `A-NNN` (still a convention; not
  tooling-enforced — STATUS.md).
- `params` — the names it reads from the calibration ledger (§3). A stage
  contains **no tunable numeric literals**.

Rules:

- **Pure by default.** A stage is a pure function of `consumes` + resolved
  `params`. Stateful/dynamical stages are allowed but must declare and
  isolate their state explicitly (`state:` in the contract).
- **The integrator/solver is its own stage.** Never fuse the model
  definition with the numerical method — they must be independently
  swappable (PyNN/reproducibility lesson).
- **Fitting/training is a separate, optional stage** that emits a
  **persisted learned-parameter artifact** (`artifacts/<name>.npz|json`).
  In **v1 it may be stubbed**: the artifact is supplied/frozen and the
  forward path consumes it deterministically. (DESIGN.md §1 non-goal is
  amended accordingly — see that file.)
- **Variants are config, not code.** Constrained/ablation variants
  (diagonal-covariance control, response-gain-only, etc.) are selected by
  a named config, never by editing stage code.
- **Swap = replace one stage honoring its contract.** Nothing else
  changes. A reproduction is not done until a *modification smoke test*
  proves this (see §5).
- **A model may depend on another reproduced model.** A stage can import a
  stage from another model's package (e.g. an extension paper that reuses a
  prior model's forward path). Declared as a dependency in `model_spec.yaml`.

## 2. Figures = protocol → measurement → view

Three separable layers. The middle one is the contract.

- **protocol** — runs the model over a stimulus/parameter sweep, returns
  raw model outputs. (Today's `run_figure_<N>()`.)
- **measurement** — *pure, side-effect-free* functions: raw outputs → a
  small **typed, schema-versioned measurement record** (the plotted/tested
  quantities AND structural facts: CRF arrays, half-max, ratios,
  abs-diff, **and spatial-layout positions**). This record is the **single
  source of truth**.
- **view** — a thin declarative renderer that *only reads* the measurement
  record (panels-as-data). It recomputes nothing. Style lives here and
  only here.

Consequences (all required):

- **Deterministic tests assert on the measurement record** (golden-file /
  regression style). The figure is drawn from the *same* record, so a
  passing test and the figure can never disagree.
- The Figure-1 class bug (deterministically perfect, visually broken) is
  structurally prevented: layout positions are *in* the record, so a
  deterministic test guards spatial structure the plot shows.
- Changing **what a figure measures/checks** = edit one measurement
  function + refresh its golden record. Changing **style** = view only.
  Neither requires reading the other layer.
- The VLM is the **backstop for what code cannot assert** (gestalt,
  "looks sigmoidal", labeling), not the primary check (idea #3:
  code-first).

## 3. Calibration is data, not constants

One versioned ledger per model (`calibration.yaml`), **namespaced per
stage/protocol** (flat ledgers rot). Each entry:

```
<stage>.<param>: { value: ..., units: ..., source: C-NNN|A-NNN|SQ-NNN,
                    audited: true|false, note: ... }
```

- Model code receives the **resolved** ledger; it holds no tunable
  literals.
- The **resolved-ledger hash is recorded in every measurement record and
  every test/VLM verdict** — a figure is always traceable to exact
  calibration.
- This retires the SQ-001/002/004 sprawl: every `chosen_assumption` SQ is
  one ledger entry with `audited: false`. The state report counts and
  lists unaudited entries; the human audits the *ledger*, not the code.

## 4. The closed loop (auto inner, human milestone gates)

One bounded cycle, agent-autonomous between gates:

```
regenerate figures
  → run measurement/deterministic tests   (cheap inner loop)
  → if all green: VLM backstop (≥2 subagents for contested/changed figs)
  → structured diagnosis, each issue tagged: model | figure_gen | spec_scope
  → targeted fix (route by tag)
  → repeat
```

- **Stop when:** all deterministic green AND VLM backstop passes; **or**
  the iteration cap / repeated-diff signal trips (the stuck detector is
  not built — STATUS.md — so v1 uses a documented cap the agent must honor
  and then escalate).
- **One artifact per iteration** appended to a reviewable per-figure
  diagnosis log. `update-state` rewrites `models/<m>/README.md` as the
  human entry point.
- Human gates: at milestones (a stage's contract tests pass; a figure goes
  green) and on escalation (spec question, cap reached).

## 5. Acceptance — verifiable AND modifiable

A figure/model is **done** only when all hold:

1. Every stage has **contract tests** (capability-keyed; reused across swaps).
2. Every plotted quantity has a **deterministic measurement test**.
3. The **VLM backstop** passes (≥2 subagents; parent-adjudicates splits).
4. A **modification smoke test** passes: swap one stage for a trivial
   variant *via config only*; the pipeline, tests, and figure regenerate
   with **zero edits to unrelated code**. This is the operational
   definition of "a scientist can change it."

If (4) cannot be met without touching unrelated code, the decomposition is
wrong — fix the contracts, not the test.

---

## Per-model layout (supersedes the REPO_STRUCTURE.md block)

```
models/<m>/
  paper/                      raw PDF (extractor only)
  article_aware/              PROTECTED — Phase A contract
    spec/model_spec.yaml      state vars, params, STAGES (§1), protocols
    spec/calibration.yaml     the ledger (§3)  [NEW]
    spec/citations.yaml  spec/assumptions.yaml
    pseudocode/<fig>_protocol.md
    figures/figure_<N>.md  figure_<N>_visual_checklist.md  figure_<N>.<img>
    extracted_data/test_figure_<N>.py   measurement-record assertions (§2)
    APPROVED
  implementation/
    src/<pkg>/stages/         one module per stage (§1)  [NEW shape]
    src/<pkg>/measurements.py pure measurement fns (§2)   [NEW]
    src/<pkg>/protocols.py    run_figure_<N>() → raw outputs
    src/<pkg>/views.py        declarative renderers (§2)  [renamed figures.py]
    artifacts/                persisted learned params (§1)  [NEW, gitignored if large]
    figure_outputs/           generated PNGs (gitignored)
    tests/                    contract + internal tests
    sanity_checks/
  logs/
    test_runs.jsonl  figure_comparisons/  spec_questions.md
    figure_diagnoses/           per-figure iteration log (§4)  [NEW]
  README.md                     the reviewable state report (update-state)
```

`[NEW]` items are the scaffold deltas from the current
`reynolds_heeger_2009` shape. Existing models migrate opportunistically;
new models start in this shape.
