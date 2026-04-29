# Workflow — How to reproduce a model end-to-end

This document is the operational guide for reproducing a model with this
system. For *where* things live, see [REPO_STRUCTURE.md](REPO_STRUCTURE.md).
For *why* the workflow is shaped this way, see [DESIGN.md](DESIGN.md).

The pipeline has five steps in two phases, separated by a hard
article-access boundary:

- **Phase A** (article-aware): extract a self-sufficient specification
  and qualitative claims from the paper. Ends with the human writing
  `article_aware/APPROVED`.
- **Phase B** (no article access): write tests from the spec, then
  implement the model bottom-up. Iterate on failing tests; escalate when
  stuck.

---

## Roles

- **Article extractor** — reads `paper/`, writes `article_aware/`. Done
  when the human writes `APPROVED`.
- **Implementation agent** — reads `article_aware/` (read-only),
  `implementation/`, and `logs/`. Writes `implementation/` and appends
  to `logs/spec_questions.md`. Cannot read the paper.
- **Adversarial judges** — invoked by the runner for qualitative and
  compliance tests. See §"Adversarial judge usage" below.

---

## Phase A — article-aware

The extractor produces every artifact a downstream agent needs to
implement the model *without re-reading the paper*. Anything it can't
find in `article_aware/` is by definition an underspecification, recorded
as an `Assumption`. This is the property that makes the whole approach
work; protect it.

### Step 1 — Extract the spec

Produce four artifacts under `article_aware/spec/` and `pseudocode/`.

**`spec/citations.yaml`** — numbered `C-NNN` references into the paper.
Cite each equation, each parameter table, each qualitative claim source,
each figure caption you'll rely on. Citations are write-once and
referenced from the spec, code docstrings, and tests.

```yaml
- id: C-001
  source: "Author Year"
  location: "Eq. 3, p. 4"
  text: "<short verbatim quote or close paraphrase>"
  notes: "<optional>"
```

**`spec/assumptions.yaml`** — named `A-NNN` records for every
underspecification. Lead with what was assumed, then *why*, alternatives
considered, and what scope is affected. Knowing why later lets a reader
judge edge cases.

```yaml
- id: A-001
  name: integration_timestep
  description: "Euler integration with dt=0.01 (paper does not specify)"
  rationale: "Stable for the dominant time constant tau=10ms; ..."
  alternatives_considered:
    - "RK4 with dt=0.1"
    - "Euler with dt=0.001"
  affects:
    - "simulation_protocol.figure_4"
  spec_refs:
    - "components.simulator"
```

**`spec/model_spec.yaml`** — structured Pydantic-validated YAML.
Required top-level fields:

- `state_variables` — names, dimensions, units, initial conditions.
- `parameters` — names, values (or `value: null` plus `underspecified_by:
  A-NNN`), units, source citation IDs.
- `equations` — symbolic form or natural-language description with
  citation. Each has a stable ID (`EQ-NNN`).
- `components` — named building blocks with parameter and equation refs.
- `pipeline` — **ordered** computation steps from input to recorded
  response. Each step references an equation and lists its
  inputs/outputs. Steps may be `optional: true` with an `applies_when`
  condition. The pipeline is what makes the spec executable; without it,
  a downstream reader has to reverse-engineer the dataflow from the
  equations.
- `simulation_protocols` — one per pseudocode file. Per-protocol
  parameter overrides, link to the pseudocode document, references to
  expected data and qualitative-claim files.

**`pseudocode/<figure>_protocol.md`** — plain markdown, one per protocol.
Inputs, parameter sweeps, procedure (step-by-step), outputs (with named
variables — these names are the contract that test files use), expected
behavior with citation refs.

### Step 2 — Extract figure data and qualitative claims

For each figure to be reproduced, produce the appropriate combination of:

**`extracted_data/<figure>.csv`** — numeric data digitized from the
figure (when option (a) — pointwise reproduction — is in scope).

**`extracted_data/<figure>_qualitative.yaml`** — qualitative claims with
a deterministic-reducible flag. **Reduce to deterministic wherever
possible** — they're cheaper, more reliable, and don't burn judge budget.

```yaml
figure: "Figure 4B"
claims:
  - id: Q-001
    statement: "Attended response exceeds unattended response at all contrasts shown."
    citation_ref: C-021
    reducible_to_deterministic: true
    deterministic_form: "(attended_response > unattended_response).all()"
  - id: Q-002
    statement: "The response curve is approximately sigmoidal in shape."
    reducible_to_deterministic: false
```

**`reproduced_figures/<figure>.png`** — plotted from the extracted data.
Same plot type, same information content as the paper figure; styling
need not match. This is a **human-review artifact**: the human compares
it to the paper figure to verify extraction quality.

### Approval gate

When the human is satisfied, they write `article_aware/APPROVED` (an
empty file is fine). Phase B tooling refuses to start without it.

### Phase A commit cadence

Commit the per-model submodule:
- After step 1 (spec + pseudocode in place).
- After step 2 (data + qualitative + reproduced figures in place).
- After human approval (`APPROVED` written).

---

## Phase B — implementation

The implementation agent reads only `article_aware/` (and `logs/`),
never `paper/`. It writes `implementation/` and may append to
`logs/spec_questions.md`.

### Step 3 — Write the test suite

Tests are derived from `model_spec.yaml`, `pseudocode/`, and
`extracted_data/*_qualitative.yaml`. They define the contract the
implementation must satisfy.

Use the framework's `deterministic_test` decorator (and curve /
qualitative / compliance variants when those land):

```python
from neuromodels.framework.testing import deterministic_test

@deterministic_test(
    spec_ref="simulation_protocols.figure_2A",
    claim_id="Q-004",
    paper_issue=None,
)
def test_figure_2A_attended_ge_unattended():
    out = protocols.run_figure_2A()
    assert (out["attended_CRF"] >= out["unattended_CRF"]).all()
```

Tolerance types (when implementing curve tests against extracted CSVs):

```python
@dataclass
class CurveTolerance:
    max_rel: float       # max pointwise relative error
    nrmse: float         # normalized RMSE (by signal range)
    pearson: float       # min Pearson correlation
    abs_floor: float = 1e-9
```

All three metrics are computed and logged on every curve test. A test
passes only if all three pass. Logging all three matters for diagnosis:
shape passes but pointwise fails → wrong amplitude/scaling; pointwise
passes but shape fails → tolerance too loose.

**Test status values:**

- `pass` — all checks satisfied.
- `fail` — at least one check failed; failure recorded with metric values.
- `pending_human_review` — qualitative or compliance test awaiting a
  human verdict.
- `relaxed` — references a `paper_issue` that downgrades it (e.g.,
  qualitative-only when the original was numeric); reported as relaxed,
  not passing.
- `error` — test infrastructure failure (not a test failure).

### Step 4 — Implement the model bottom-up

Follow the `pipeline` in `model_spec.yaml`: implement each step in
order, smallest helpers first. Run tests frequently.

**Citation/Assumption docstring discipline.** Every function in
`implementation/src/` must have, in its docstring, either a `Citation:`
or an `Assumption:` field (or both). Citations reference `C-NNN`; assumptions
reference `A-NNN`. A function that wraps and composes other cited
functions only needs citations for the *additional* logic it introduces
— small functions have small citation lists.

```python
def attended_response(stim, attention_field):
    """Compute the attended response by gain modulation.

    Args:
        stim: Stimulus drive, shape (n_neurons,).
        attention_field: Attention gain, shape (n_neurons,).

    Returns:
        Modulated response, shape (n_neurons,).

    Citation: C-014  # Eq. 7, gain modulation by attention
    """
    return stim * attention_field
```

A static check (`framework/static_checks/`) verifies *presence* of one
of these fields on every function. It does not verify *quality* — the
cited paragraph might not actually support the function's behavior. Periodic
human audit is required.

### Step 5 — Iterate

The implementation agent runs tests through the framework runner (not
raw `pytest`) so every invocation is logged and participates in stuck
detection. During iteration:

- Run the **narrowest relevant test** after each implementation attempt.
- Expand to file-scoped tests after the narrow one passes.
- Run the **full model test suite** at each implementation milestone.
- Stop working on a test immediately if the runner emits a `STUCK` gate
  for that test; address the gate before continuing.

The runner creates an attempt commit in the model repo before each test
invocation when there are working-tree changes. The recorded
`commit_hash` is the model commit actually tested.

### Phase B commit cadence

The framework runner handles attempt commits automatically. In addition,
make milestone commits when:

- A new pipeline component passes its tests.
- A new figure protocol's tests all pass.
- The spec is revised (this also invalidates prior passes — see
  "Spec edits" below).

---

## Sanity checks (Phase B authoring rule)

Sanity checks are **exploratory diagnostics**, not tests. They print
summary statistics to stdout (token-friendly, agent reads) and save PNGs
to a gitignored `_outputs/` directory (visual, human reads). They make
no assertions.

**Sanity check vs test:**

> If you can write `assert P(output)` for a property P that should
> *always* hold → test.
> If you want to look at the output and form a judgement → sanity check.

The moment you write `assert`, it's a test, not a sanity check.

**Where they live:**

```
implementation/sanity_checks/
  check_<topic>.py                # one file per topic; multiple checks inside
  check_<topic>_outputs/          # GITIGNORED — PNG + text per check
  README.md                       # one-line index of checks (optional)
```

**Naming:** `check_<component_or_question>.py`. Examples:
`check_stimulus_drive.py`, `check_attention_field.py`,
`check_full_pipeline_trace.py`.

**Use the framework helpers** in `neuromodels.framework.explore` for
consistent stat printing and PNG output:

```python
from neuromodels.framework.explore import (
    require_plotting,
    output_dir,
    matrix_stats,
    matrix_excerpt,
    write_text,
    save_heatmap_grid,
)
```

`require_plotting()` raises with an install hint if matplotlib/seaborn
are missing — they live under the optional `sanity` extra:
`pip install -e ".[sanity]"`.

**Token discipline.** If an array has more than ~10 elements along a
dimension, print stats (use `matrix_stats`) instead of values. Cap
stdout per check at ~30 lines. Push the visual surface to PNGs.

**When to write or extend a sanity check:**

- After implementing a new pipeline step → exercise it across a few
  configurations.
- When a test fails in a way you don't immediately understand → write
  or extend a sanity check that gives you the intuition.
- Before declaring a component "done" → re-run the relevant sanity check
  and confirm the output looks right.

**Lifecycle.** Keep, evolve, don't delete. They become part of the
model's permanent documentation. If a component changes meaningfully,
update the sanity check; don't remove it.

**Citation/Assumption docstrings.** Recommended *yes* for sanity checks
that exercise specific equations (cite the equation), *no* for full
pipeline traces (a citation list would be the whole model). A simple
docstring with the purpose is enough for the latter.

**Don't substitute for understanding.** Sanity checks build intuition;
they don't replace analysis of a failing test. The fix to a failing
test is still the failure description plus reasoning, not "I ran the
sanity check and it looks fine."

---

## Escalation channels

When work blocks, route to the right channel:

### Spec questions (impl agent → human)

Append to `logs/spec_questions.md` when the implementation agent
discovers a spec ambiguity or genuine missing information that it can
work around but wants the human to revisit. The file is **append-only,
no read-back** — each entry must stand alone.

```
## SQ-<n> — <short title>
date: <ISO8601>
spec_ref: <citation_id or assumption_id or section path>
question: <the concern>
chosen_assumption: <what the agent did instead, with link to assumption_id>
```

The agent then continues with the chosen assumption. The human reviews
periodically and decides whether to revise the spec or leave the
assumption.

### Paper issues (human-only)

`logs/paper_issues.md` records suspected paper errors, ambiguities, or
known errata. Distinct from underspecification (which is an
`Assumption`); the workflow for resolving them differs.

```yaml
- id: PI-001
  test: test_figure_4b_attended_vs_unattended
  type: suspected_paper_error  # | paper_ambiguity | known_erratum
  description: "Figure 4B y-axis label appears inconsistent with text on p. 7."
  action: "assertion relaxed to qualitative ordering only"
  references:
    - "Erratum, Journal Vol X, p. Y"
```

Tests reference `PI-NNN` IDs in their `paper_issue` decorator argument
and report status `relaxed` rather than `pass`. The aggregated log can
answer "what is relaxed because of paper issues" separately from "what
is stuck."

### STUCK gate (framework → impl agent)

When the stuck detector emits a signal, it writes a `STUCK` file at the
model root with the offending `test_id`, recent attempt summary, and
the most recent failure's `issue_description`. The implementation agent
refuses to continue working on that test until the file is removed.

The human investigates and takes one of: revise the spec, register a
paper issue, relax the test, or clear the signal and tell the agent to
keep trying.

### Pending review gate (judges → human)

Tests in `pending_human_review` block any downstream work that depends
on them. The agent may continue with unblocked work in the meantime.

---

## Spec edits and re-validation

If the human edits any file in `article_aware/` after Phase B has
started, every prior test pass was validated against the *old* spec.
The runner records `spec_commit_hash` on every test row; queries that
ask "what is currently passing" filter to rows whose `spec_commit_hash`
matches the current head of `article_aware/`.

In v1 this is an advisory filter — the human or agent reads it and
reruns affected tests. Selective dependency-aware invalidation is on the
deferred list.

---

## Adversarial judge usage

For qualitative or compliance tests that resist deterministic reduction,
the framework invokes a pair of LLM judges (attacker and defender) with
no autonomous decision authority — the human always decides.

### Inputs

Each judge receives exactly three sections:

- `rubric` — the standard the object is being evaluated against.
- `context` — scoped background needed to understand the rubric.
- `under_review` — the code, data, or output being judged.

Judges do **not** receive the paper, run IDs, test IDs, spec refs,
review queue paths, other tests, the other judge's output, or prior
judge runs on the same test.

### Basic CLI

```bash
neuromodels judge run \
  --rubric-file rubric.md \
  --context-file context.md \
  --under-review-file output.txt
```

Prints the judge result as JSON by default (markdown also supported).
Writing `logs/review_queue/` files is the caller's responsibility, not
part of the basic judge CLI.

---

## Stuck detection: what gets logged

The aggregated test log (`logs/test_runs.csv`) writes one row per test
execution regardless of how it was invoked. Key fields used by the
stuck detector:

- `diff_hash` — hash of the diff vs. the last failing run of the same
  `test_id`.
- `lines_changed` — count of changed lines in that diff.
- `regions_jaccard_prior` — Jaccard similarity of changed line ranges
  against prior attempts in the current debugging session for this test.

A "debugging session" is scoped per `test_id`: it begins at the first
failure and ends when the test passes, is relaxed, or the human clears
it. See [DESIGN.md](DESIGN.md) for trigger thresholds and the rationale
behind diff-based detection.

### Useful queries on the log

The CSV is intentionally simple to start. Expected queries (pandas
one-liners):

- "All currently failing tests, latest attempt only."
- "All tests relaxed because of paper issues."
- "Attempt history for a given `test_id`."
- "Tests in `pending_human_review` for current run."
