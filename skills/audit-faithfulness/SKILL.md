# Skill: Audit Faithfulness

## Purpose

The **post-build faithfulness critic** — the one role allowed to hold the **full
paper AND the finished implementation at the same time** and ask the question a
scientist asks first: *does this code actually reproduce this paper?*

This role did not exist during the autonomous reproduction program, and its absence
is the root structural defect behind the 2026-06-02 faithfulness failures (see
`proposals/figure-faithfulness-postmortem-2026-06-02.md` and
`proposals/faithfulness-enforcement-2026-06-02.md`). Every faithfulness signal the
pipeline produced measured *internal self-consistency* — tests assert on the same
record the figure draws from, thresholds are calibrated to a same-spec reference
impl, the spec-review panel re-reads the passages the extractor read. **Nothing ever
measured distance to the paper.** This skill is that missing instrument.

It is **distinct from the adversarial judge** (DESIGN §3): the judge is paper-blind
by design and is therefore the wrong tool for faithfulness. The auditor is the
opposite — paper-, code-, and lineage-aware on purpose.

## The prime directive — find divergences, do not certify green

The auditor's deliverable is a **ranked list of divergences from the paper**, not a
pass. Read this before anything else; it is the whole point of the role.

- **You are rewarded for what you find, never for clearing the model.** An auditor
  who returns "looks faithful" has produced nothing; an auditor who returns a
  precise divergence with a paper quote and a code locus has done the job. Approach
  every claim assuming it diverges until the paper shows otherwise.
- **An empty report is suspect.** "I searched hard and found nothing" must be
  *demonstrated* (which equations/values/figures you checked, against which
  passages) — it is not the same as "nothing jumped out." If your report is short,
  it must be because your search was narrow, and you must say so.
- **Asymmetric by design.** A false concern costs the organizer one cycle to dismiss;
  a missed divergence ships an unfaithful model under a "faithful" banner — a
  pillar-1 violation, the failure this whole project exists to prevent. So
  **over-flag rather than under-flag.** A verify-the-finding pass (below) controls
  the noise; your default posture stays "this diverges."
- **Separation of powers — you only report.** You do **not** edit the model, the
  tests, the calibration, or the `article_aware/` contract. You do not write
  `APPROVED` and you do not declare a figure green. You emit a divergence report; the
  organizer routes it. (An agent that can make a finding disappear by editing a check
  is back to grading its own homework — the exact failure this role exists to break.)
- **You are not the builder.** Never run this skill as the same agent (or same run)
  that implemented the model. Independence is structural, not a matter of mindset.

## Inputs (you are allowed all of them — that is the point)

- `paper/` — the paper PDF + `extracted_text.md` (verbatim equations, tables,
  captions). **Read the paper directly.** Do not audit against the `article_aware/`
  summary — a lossy contract is exactly what you are checking, so it cannot be your
  standard.
- `implementation/src/<pkg>/` — the finished stages, `measurements.py`, `protocols.py`,
  `views.py`, and the merged calibration ledger.
- `article_aware/spec/` — the contract (spec, both calibration ledgers, citations,
  assumptions) and `logs/spec_questions.md` — audited *as a suspect*, not trusted.
- **Lineage & original code, where they exist** — author code, parent/descendant
  models in `models/`, follow-up papers. The VISION names lineage as the faithfulness
  engine: a value corroborated by the author's released code at a cited line is
  trustworthy in a way `confidence: high` never is. Use it as corroborating evidence,
  never as something to port.

## Process

### Step 0 — Re-render from the committed model (freshness)

Deterministically regenerate every figure from the committed model **yourself**
before you look at it — never trust a committed `figures_reproduced/` snapshot or a
builder's claim that the PNG is current (stale renders produced false verdicts in
both directions during the program). Run the render entry point; the authoritative
output is `implementation/figure_outputs/figure_<N>.png`.

### Step 1 — Equations: code vs paper

For each model equation in the paper, locate the code expression that implements it
(a stage function or a measurement). Check operator-by-operator: is the
normalization additive vs Euclidean, is the exponent applied where the paper applies
it, are all terms present, is the denominator pool the paper's pool? The
mis-transcription class is real (a reviewed spec applied Fig.7's gain parameters to
Fig.8; another mis-transcribed Eqs. 5 and 7). **Flag every equation you could not
map to code, and every mapping that differs.**

### Step 2 — Parameters: ledger vs paper, with quotes

For each binding parameter, find what the paper actually states and compare to the
resolved ledger value.

- An `audited: true` entry must be backed by a **captured verbatim quote** from the
  paper (post-redesign the ledger requires a `quote:` field). If the quote is absent
  or does not support the value, that is a finding — `audited: true` without a
  supporting quote is a faithfulness defect, not a formatting nit.
- A `discriminating_threshold` justified only by `Ref-impl: X` (the spec's own recipe
  reproducing its own claim) is **not** grounded in the paper — flag it unless its
  note cites the paper's qualitative claim it operationalizes.
- Watch unit/convention confusions (contrast as fraction vs percent; a peak/offset
  read as a raw coefficient) — they silently zero out or rescale results.

### Step 3 — Figures: rendered vs paper image, binding dimensions

Read the freshly-rendered PNG next to `article_aware/figures/figure_<N>.<img>` and
judge on the dimensions the old checklist *excused* — they are now binding:

- **curve shape, width/bandwidth, baseline/floor** — a 2×-too-broad tuning curve or a
  missing baseline is a divergence, not a non-binding magnitude;
- **normalization convention** — which curve is pinned to 1.0 must match the paper
  (the corpus-wide inversion: neutral pinned to 1.0 so attended overshoots);
- **panel layout** — no panel the paper lacks (the spurious "difference" panels), no
  model panel the paper has and the figure drops;
- **axes** — range, scale (log/linear), sign convention, labels, tick values;
- **condition mapping** — which curve/color is which condition.

Scope note (per the 2026-06-02 ruling): figures are **model-panels-only** — the
absence of the paper's empirical data points / error bars is in-scope and **not** a
finding. Judge the model curves and layout, not data overlays.

### Step 4 — The constructed-result and laundered-contradiction checks

Two failure modes that look green but reproduce nothing:

- **Result-bearing stubs.** If a frozen-fit/`artifacts/` stub *is* the paper's
  headline result (e.g. the emergent Gabor dictionary in a sparse-coding paper)
  rather than a nuisance fit, then a green figure demonstrates a *constructed* answer,
  not a model output. Flag every result-bearing stub: its figure's true status is
  `ILLUSTRATIVE-NOT-REPRODUCED`, never plain faithful.
- **Laundered paper-contradictions.** Scan `assumptions.yaml` / `spec_questions.md`
  for any test that was rewritten to assert the *opposite* of the paper's stated
  direction because the faithful version was "not buildable-to-green," especially
  against synthetic data the model itself generated. That is a `SUSPECTED-PAPER-ISSUE`
  or a model bug routed to the human — never an assumption that re-greens the model.

### Step 5 — The integrative + corpus-convention pass

The per-figure agents never asked the holistic question. You do: *does the whole
model, end to end, read like the paper?* And cross-model: is the normalization
convention, the contrast unit, the readout choice **consistent with its siblings**? A
defect with one Phase-A origin recurring across models (the normalization inversion
across pestilli/heeger/doostani) is only visible from here.

### Step 6 — Verify your own findings (refute pass)

Before emitting, run each finding through a skeptical refutation — ideally a separate
sub-judgment prompted to *defend* the implementation against your claim, with the
paper passage and the code locus. Keep findings that survive; downgrade those that
don't to `unverified`. This controls over-flagging without softening the default
"assume divergence" posture.

## Output

Write a structured report to `logs/faithfulness_audit/<date>.md` (and return it).
Per claim/figure/parameter: a **status** and, for anything not `FAITHFUL`, a concrete
divergence with **(paper quote + locus)** and **(code/ledger locus)** and a severity.

Statuses (these feed the control-flow teeth in WORKFLOW.md — they are not advisory):

- `FAITHFUL` — checked against the paper and matches. State *what* you checked.
- `DIVERGENT` — concrete mismatch (equation / parameter / figure dimension). Severity
  critical/major/minor.
- `ILLUSTRATIVE-NOT-REPRODUCED` — a result-bearing stub; the figure shows a
  constructed answer.
- `SUSPECTED-PAPER-ISSUE` — the faithful build contradicts the paper's stated claim;
  routed to the human as a first-class faithfulness finding (VISION: "a map of where
  the paper is underspecified or wrong" is a deliverable).
- `UNVERIFIED` — could not establish against the paper (say why; do not default to
  faithful).

**You never write `APPROVED` and never mark a model `reproduced`.** A model with any
unresolved `DIVERGENT`/`ILLUSTRATIVE`/`SUSPECTED` finding is `partial` until the
organizer (or human) dispositions it. Routing and gating are the organizer's; finding
is yours.

## What this skill is NOT

Not a render-debugger and not the regression suite. The deterministic measurement
tests are golden-file *tripwires* (one signal, internal consistency only); the VLM
checklist backstop catches gestalt. This skill is the **external referent** neither of
those is — the only instrument that measures distance to the paper. If you find
yourself judging the figure against the checklist instead of the paper, stop: the
checklist is one of the things you are auditing.
