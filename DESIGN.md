# Neuromodels — System Design

This document captures the architecture for an agentic system that reproduces
neuroscience computational models from a published article alone, producing a
clean Python implementation that researchers can extend.

It is the reference document for all subsequent work. When implementation
choices later look ambiguous, the answer is here. When this document is wrong,
update it before writing code.

---

## 1. Goals and non-goals

### Goals

- Given a published article describing a computational model, produce:
  - A structured specification of the model.
  - A clean Python implementation that passes a generated test suite.
  - A set of reproduced figures that visually correspond to those in the paper.
  - A log of every assumption made (where the paper underspecified) and every
    suspected paper issue (where the paper appears wrong or ambiguous).
- Surface underspecification as a first-class output, not as silent decisions
  buried in code.
- Provide a library structure such that researchers can extend or modify any
  model without re-reading the entire paper.
- Detect when the agent is stuck and escalate to a human, rather than burning
  iterations.

### Non-goals (v1)

- **Stochastic models.** Deterministic models only for the first version. The
  framework should not preclude stochastic support, but it will not be built
  out until the deterministic path is solid.
- **Full autonomy.** A human is in the loop for: approving the article-aware
  artifacts (spec, pseudocode, extracted data, reproduced figures), deciding
  the verdict on adversarial-judge reviews, and resolving stuck signals.
- **Multi-paper synthesis.** Each model run targets one paper. If the spec
  needs to be enriched from another paper, that is a human decision that
  produces a new round of extraction.
- **Reproducing real experimental data.** The target is the *paper's
  simulated outputs* (its figures and tables), not the empirical data those
  figures were compared against.

---

## 2. Pipeline overview

The pipeline has five steps, split into two phases by access to the source
article.

### Phase A — article-aware (steps 1–2)

The extractor agent has read access to the paper.

1. **Specification extraction.** Produces:
   - `spec/model_spec.yaml` — structured model: state variables, equations,
     parameters (with values where given, marked underspecified otherwise),
     simulation protocols.
   - `spec/citations.yaml` — numbered, referenceable citations into the paper.
   - `spec/assumptions.yaml` — named, referenceable assumptions where the
     paper underspecifies.
   - `pseudocode/*.md` — one per experimental protocol (typically one per
     figure or figure panel reproduced).
2. **Data extraction and figure reproduction.** Produces:
   - `extracted_data/*.csv` — numeric data digitized from paper figures.
   - `extracted_data/*_qualitative.yaml` — qualitative claims about each
     figure ("line A is always above line B", "attended condition exceeds
     unattended at high contrast").
   - `reproduced_figures/*.png` — figures plotted from the extracted data,
     intended to be visually compared by the human against the paper figures.

A human reviews Phase A outputs and creates an `APPROVED` sentinel file when
satisfied. No downstream step starts without it.

### Phase B — no article access (steps 3–5)

The implementation agent reads only the artifacts produced in Phase A. It has
no access to the paper itself or to the extractor's intermediate notes.

3. **Test suite implementation.** The agent writes the test suite from the
   spec, pseudocode, extracted data, and qualitative claims. Tests use the
   framework's decorators (Section 6).
4. **Model implementation.** The agent implements the model bottom-up,
   smallest components first, running tests frequently.
5. **Iterate.** The agent reruns tests; the framework logs results and
   computes stuck signals; the human is paged when needed.

### The cleavage matters

The hard split between Phase A and Phase B is the most important design
choice in this system. It forces the spec to be self-contained: anything the
implementation agent cannot find in the spec is, by definition, an
underspecification — and gets recorded as an assumption. Without this split,
the implementation agent would silently re-derive things from the paper, and
the spec would drift into being a partial summary rather than a complete
contract.

Tooling, not prompt instructions, enforces the split (Section 4).

---

## 3. Folder and repo structure

Monorepo layout. The framework is a Python package, installed in editable
mode (`pip install -e .` from the repo root). Models live in nested git
repositories tracked as submodules under `models/` and import from the
framework.

```
model_agent/                            # repo root
  pyproject.toml                        # framework package config
  DESIGN.md                             # this document
  AGENTS.md
  CLAUDE.md

  neuromodels/                          # the framework
    framework/
      testing/                          # decorators, runner, tolerance types
      llm/                              # shared LLM provider access
      judge/                            # adversarial judge orchestration
      logging/                          # aggregated log + queries
      stuck_detector/                   # diff-based stuck signal computation
      static_checks/                    # citation/assumption docstring check
      review/                           # review-queue file format and apply
    cli/                                # `neuromodels` CLI entry points
    tests/                              # framework tests

  models/
    reynolds_heeger_2009/               # git submodule; one repo per model
      paper/                            # source of truth
        paper.pdf
        extracted_text.md               # OCR/text extraction, optional
      article_aware/                    # PROTECTED — written in Phase A
        spec/
          model_spec.yaml
          citations.yaml
          assumptions.yaml
        pseudocode/
          figure_4_protocol.md
          figure_5_protocol.md
        extracted_data/
          figure_4b.csv
          figure_4b_qualitative.yaml
        reproduced_figures/
          figure_4b.png
        APPROVED                        # empty file; presence = human gate ok
      implementation/                   # written in Phase B
        src/rh_model/
          __init__.py
          normalization.py
          attention.py
        tests/
          test_normalization.py
          test_figure_4b.py
        sanity_checks/                   # exploratory scripts + generated local outputs
          check_stimulus_drive.py
          check_stimulus_drive_outputs/  # ignored; PNG/text outputs for humans + agents
      logs/
        test_runs.csv                   # aggregated test log
        spec_questions.md               # impl agent: append-only, no read-back
        paper_issues.md                 # human-only, structured entries
        review_queue/                   # one file per pending review
      README.md                         # generated; orientation for humans
```

### Defenses for choices

- **`article_aware/` as a single directory** makes the protection boundary one
  path prefix. Easy to enforce in tooling; obvious to humans inspecting the
  repo.
- **`paper/` separate from `article_aware/`** because the PDF is raw input
  with a different lifecycle from derived artifacts.
- **`APPROVED` sentinel file** is a cheap, version-controllable gate. Phase B
  tooling refuses to start without it.
- **Per-model submodules** give each reproduced model an independent history
  while keeping the framework and model collection discoverable from one
  parent repo.
- **`logs/` per model rather than central** because logs are inherently
  per-model and we want `git log` on one model directory to tell the full
  story.

---

## 4. Agent roles and tool-enforced boundaries

There are three agent roles. Each is enforced by tooling — file system
permissions, working-directory scoping, and tool configuration — not just by
prompt instructions. Prompts are a hint; tool config is a guarantee.

### 4.1 Article extractor (Phase A)

- **Read access:** `paper/`, `article_aware/`.
- **Write access:** `article_aware/` only.
- **Outputs:** spec, pseudocode, extracted data, qualitative claims,
  reproduced figures.
- **Termination:** when the human writes the `APPROVED` sentinel.

The extractor may run as one session or several (e.g., spec-extraction
session, then data-extraction session). What matters is that all artifacts
land in `article_aware/`.

### 4.2 Implementation agent (Phase B)

- **Read access:** `article_aware/` (read-only), `implementation/`,
  `logs/test_runs.csv`, `logs/paper_issues.md`.
- **Write access:** `implementation/`, `logs/spec_questions.md`
  (append-only, no read-back — see below).
- **Refuses to start** without `APPROVED`.
- **Cannot read** `paper/` or any extractor intermediate notes outside
  `article_aware/`. Enforced by Claude Code permission config / working
  directory scope, not by prompt.

#### `spec_questions.md` is strict write-only

The implementation agent can append entries but cannot read the file back
after writing, and cannot read its own prior entries. Rationale: prevents
the agent from second-guessing or rationalizing past escalations, and forces
each question to stand alone for the human reader. Looser variants are
possible later; we are starting strict.

Append format:

```
## SQ-<n> — <short title>
date: <ISO8601>
spec_ref: <citation_id or assumption_id or section path>
question: <the concern>
chosen_assumption: <what the agent did instead, with link to assumption_id>
```

The human reads these periodically and decides whether to revise the spec
(which triggers re-validation — see Section 10) or leave the assumption.

### 4.3 Adversarial judges (invoked by the runner or CLI)

A pair of LLM calls used during qualitative and compliance review. The
runner will use them for tests; the CLI exposes the same core functionality
for human or agent spot checks.

- **Attacker prompt:** find concrete reasons the under-review object does
  not pass the rubric.
- **Defender prompt:** find concrete reasons the under-review object passes
  the rubric.
- **Inputs to each:** only a `rubric`, `context`, and `under_review` object,
  plus the role-specific attacker/defender instruction. Not run IDs, test
  IDs, review metadata, the paper, other tests, or each other's output.
- **Output:** the judge returns both responses plus metadata such as
  `run_id`, timestamp, model, and provider. The caller decides whether to
  print it, log it, or write a pending human-review file.

No autonomous "majority vote" or "judge accept" path exists in v1. Building
that path would require calibration data we do not have yet; without it,
the system would silently inherit judge biases.

### 4.4 Boundary enforcement summary

| Agent          | Reads paper | Reads article_aware | Writes article_aware | Reads spec_questions | Writes spec_questions |
|----------------|-------------|---------------------|----------------------|----------------------|-----------------------|
| Extractor      | yes         | yes                 | yes                  | n/a                  | n/a                   |
| Implementation | no          | yes                 | no                   | no                   | append-only           |
| Judges         | no          | scoped section only | no                   | no                   | no                    |

---

## 5. Spec artifacts

Detailed schemas will be pinned once we have the first article in front of
us. This section fixes the *shape* and the cross-cutting conventions.

### 5.1 `spec/model_spec.yaml`

A structured Pydantic-validated YAML document. Contains:

- **State variables.** Names, dimensions, units, initial conditions.
- **Parameters.** Names, values (or `underspecified: true` with reference to
  an assumption ID), units, source citation ID.
- **Equations.** Either symbolic form or natural-language description with
  citation. Each equation has a stable ID for cross-referencing from code.
- **Components.** Hierarchical decomposition of the model into named
  components (used as `spec_ref` values in tests and `Citation` references
  in code docstrings).
- **Pipeline.** Ordered list of computation steps from a protocol's input
  configuration to the recorded response. Each step references an equation
  and lists its inputs/outputs. Steps may be marked `optional: true` with an
  `applies_when` condition (e.g., a baseline step that runs only when the
  protocol overrides a baseline parameter). The pipeline is the missing
  middle that makes the spec actually executable: without it, a reader has
  to reverse-engineer the dataflow from the equations.
- **Simulation protocols.** One per pseudocode file. Per-protocol parameter
  overrides, link to the pseudocode document, and references to expected
  data / qualitative-claim files.

Pydantic models give the agent and framework type validation; YAML
serialization keeps it human-readable on disk.

### 5.2 `spec/citations.yaml`

```yaml
- id: C-001
  source: "Reynolds & Heeger (2009)"
  location: "Eq. 3, p. 4"
  text: "<short verbatim quote or close paraphrase>"
  notes: "<optional>"
```

Citations are referenced by ID from the spec, from code docstrings (the
`Citation` field), and from test `spec_ref` values. They are write-once
during Phase A and treated as immutable references thereafter.

### 5.3 `spec/assumptions.yaml`

```yaml
- id: A-001
  name: "integration_timestep"
  description: "Euler integration with dt=0.01 (paper does not specify)"
  rationale: "Stable for the dominant time constant tau=10ms; faster steps
              do not change figure 4 within tolerance."
  alternatives_considered:
    - "RK4 with dt=0.1"
    - "Euler with dt=0.001"
  affects:
    - "simulation_protocol.figure_4"
  spec_refs:
    - "components.simulator"
```

Assumptions are first-class, named, referenceable. Each one records what was
assumed, why, what alternatives were considered, and what parts of the spec
or implementation depend on it. The structure exists so that when an
assumption later turns out wrong, the affected scope is discoverable.

### 5.4 `pseudocode/*.md`

Plain markdown, one per experimental protocol. Describes the protocol that
generates a paper figure or table: inputs, parameter sweeps, outputs,
expected plots. References citation IDs and assumption IDs.

### 5.5 `extracted_data/*.csv`

Numeric data digitized from paper figures, with a header documenting which
figure and which curve. One CSV per curve or per related curve group.

### 5.6 `extracted_data/*_qualitative.yaml`

```yaml
figure: "Figure 4B"
claims:
  - id: Q-001
    statement: "Attended response exceeds unattended response at all contrasts shown."
    reducible_to_deterministic: true
    deterministic_form: "(attended_response > unattended_response).all()"
  - id: Q-002
    statement: "The response curve is approximately sigmoidal in shape."
    reducible_to_deterministic: false
```

Qualitative claims are flagged for whether they reduce to deterministic
checks. The framework prefers the deterministic form when available. Only
the irreducible ones invoke the adversarial judge path.

### 5.7 `reproduced_figures/*.png`

Plots generated by the extractor agent from the extracted data, intended
solely as a human-review artifact: the human compares the reproduced figure
to the paper figure to verify extraction quality. They do not need to be
visually identical to the paper — same data, same plot type, same
information content is sufficient.

---

## 6. Test API

Built on **pytest** (industry standard, agents understand it, plugin
architecture for our log) with a thin decorator layer for our concepts.

### 6.1 Decorators

```python
@deterministic_test(spec_ref="normalization.divisive_form", paper_issue=None)
def test_normalization_at_zero_input():
    out = run_model(input=0)
    assert out == approx(0, abs=1e-9)


@curve_test(
    spec_ref="figure_4b",
    tolerance=CurveTolerance(max_rel=0.05, nrmse=0.05, pearson=0.95),
)
def test_figure_4b_curve():
    expected = load_extracted("figure_4b.csv")
    actual = simulate_protocol("figure_4_protocol")
    return expected, actual  # framework computes & logs all 3 metrics


@qualitative_test(
    spec_ref="attention_section",
    claim_id="Q-002",  # references qualitative.yaml
)
def test_attention_qualitative():
    return simulate_attended(), simulate_unattended()
    # framework: builds rubric/context/under_review for the judge,
    # marks pending_human_review


@compliance_test(spec_section="components.normalization")
def test_normalization_compliance():
    return get_module_source("rh_model.normalization")
    # framework: builds rubric/context/under_review for the judge;
    # human decides
```

### 6.2 Tolerance types

```python
@dataclass
class CurveTolerance:
    max_rel: float       # max pointwise relative error
    nrmse: float         # normalized RMSE (by signal range)
    pearson: float       # min Pearson correlation
    abs_floor: float = 1e-9  # absolute floor for near-zero values
```

All three metrics are computed and logged on every curve test. A test passes
only if all three pass. Logging all three matters for diagnosis: shape
passes but pointwise fails → wrong amplitude/scaling; pointwise passes but
shape fails → tolerance too loose.

Per-test tolerance overrides via decorator arguments. Default values pinned
in `framework/testing/defaults.py`; expected to iterate.

### 6.3 Test status values

- `pass` — all checks satisfied.
- `fail` — at least one check failed; failure recorded with metric values.
- `pending_human_review` — qualitative or compliance test awaiting a human
  verdict. The runner or review workflow may write judge outputs to
  `review_queue/`, but the basic judge CLI does not.
- `relaxed` — test references a `paper_issue` that downgrades it (e.g.,
  qualitative-only when the original was numeric); reported as relaxed, not
  passing.
- `error` — test infrastructure failure (not a test failure).

### 6.4 Aggregated log row schema

Every test execution writes one row to `logs/test_runs.csv` regardless of
how it was invoked. Schema:

| field                     | type   | notes                                              |
|---------------------------|--------|----------------------------------------------------|
| `run_id`                  | uuid   | groups all tests in one suite invocation           |
| `test_id`                 | str    | `path::function_name`                              |
| `timestamp`               | iso8601| start of test                                      |
| `status`                  | enum   | see 6.3                                            |
| `spec_ref`                | str    | from decorator                                     |
| `paper_issue_ref`         | str?   | nullable                                           |
| `metric_values`           | json   | tolerance metrics for curve tests; null otherwise  |
| `issue_description`       | str    | concise human-readable failure summary             |
| `attempt_n`               | int    | counter for this test_id across history            |
| `agent_rationale`         | str?   | optional; what the agent says it changed           |
| `commit_hash`             | str    | model repo commit tested by this run               |
| `framework_commit_hash`   | str    | parent framework repo commit used by this run      |
| `spec_commit_hash`        | str    | last commit touching `article_aware/`              |
| `diff_hash`               | str?   | hash of diff vs. last failing run of same test_id  |
| `lines_changed`           | int?   | from same diff                                     |
| `regions_jaccard_prior`   | float? | overlap of changed line ranges vs. prior attempts  |

### 6.5 Runner behavior

- Single-test, file-scoped, and full-suite invocations all write rows the
  same way. The log is invariant to scope.
- Curve and qualitative-deterministic tests record metric values even on
  pass, so the human can see margin.
- Tests in `pending_human_review` count as blocking but distinguishable from
  failures in summary output.
- After every run, `stuck_detector` reads recent rows and emits an unblock
  signal if any test crosses thresholds (Section 8).

### 6.6 Test-running contract

The implementation agent runs tests through the framework runner, not raw
`pytest`, so every invocation is logged and participates in stuck detection.

During Phase B, the implementation agent:

- Runs the narrowest relevant test after each logical implementation attempt.
- Expands to file-scoped tests after the narrow test passes.
- Runs the full model test suite at each implementation milestone.
- Stops working on a test immediately if the runner emits a `STUCK` gate for
  that test.

The runner creates an attempt commit in the model repo before each test
invocation when the model working tree has changes. `commit_hash` is the
model commit that was actually tested. If there are no model changes, the
runner may reuse the current model `HEAD`; repeated no-change attempts are
expected to produce identical diffs and can trigger the stuck detector.

The extractor agent does not run implementation tests. It may run schema,
formatting, plotting, and artifact-validation checks for `article_aware/`.

### 6.7 Qualitative sanity checks

Implementation agents should create **qualitative sanity checks** liberally
during Phase B whenever the model's behavior is hard to understand from narrow
assertion failures alone. These checks are exploratory diagnostics, not formal
tests: they summarize what a component or pipeline step appears to be doing at
a high level so both the agent and the human can quickly regain context.

Sanity checks live under `implementation/sanity_checks/` and should be named
for the component or question they illuminate, for example
`check_stimulus_drive.py`, `check_attention_field.py`,
`check_suppressive_drive.py`, or `check_full_pipeline_trace.py`. They may use
small grids, simplified stimuli, and a few representative parameter settings
instead of the full figure protocols. They should answer broad inspection
questions such as:

- "What does the stimulus drive look like for several input positions and
  contrasts?"
- "How do E, A, S, and R change step-by-step for one small protocol?"
- "Do heatmaps and summary statistics make the current failure mode obvious?"

Each check should save outputs to
`implementation/sanity_checks/<check_name>_outputs/`. PNG figures are strongly
preferred for human review: use matplotlib and seaborn when available, with
heatmaps for matrices and compact line plots for slices or sweeps. Text output
may also be saved in the same directory, such as matrix excerpts, min/max/mean,
peak location, integral/sum, shape, and any short interpretation the agent
needs to remember.

Agents should inspect the generated PNGs after running a sanity check, not just
produce them. For large matrices, the heatmap is the primary debugging surface:
open the image, look for the spatial/feature profile, peak location, symmetry,
saturation, suppression spread, edge effects, and any unexpected blank or
exploding regions. Use those observations to decide the next implementation
change, then rerun both the sanity check and the relevant formal tests.

Generated output directories are local artifacts and must be ignored by git.
The check scripts themselves are version-controlled when they remain useful
for future debugging. These scripts may evolve freely during implementation;
unlike tests, they do not define pass/fail correctness and should not be used
as a substitute for data-claim tests.

---

## 7. Adversarial judge protocol

### 7.1 Inputs

Each attacker/defender LLM call receives exactly three shared inputs:

- `rubric` — the standard the object is being evaluated against.
- `context` — scoped background needed to understand the rubric and object.
- `under_review` — the code, data, or output being judged.

Judges do **not** receive: the paper, run IDs, test IDs, spec refs, review
queue paths, other tests, the other judge's output, or prior judge runs on
the same test. If citations or assumptions are needed, the caller includes
only the relevant snippets inside `context`.

### 7.2 Prompts

- **Attacker:** asks for concrete reasons the under-review object fails the
  rubric. If there is no substantive failure, it should say so.
- **Defender:** asks for concrete reasons the under-review object passes the
  rubric, while acknowledging genuine ambiguities.

Both prompts include the same three sections and no review metadata:

```markdown
## Rubric

<rubric>

## Context

<context>

## Under Review

<under_review>
```

Neither prompt sees the other's output.

### 7.3 Basic CLI

The basic human/agent CLI accepts files for the three judge inputs:

```bash
neuromodels judge run \
  --rubric-file rubric.md \
  --context-file context.md \
  --under-review-file output.txt
```

It prints the judge result as JSON by default and supports markdown output.
Runner-specific and data-test-specific commands will be built later around
the same judge core. Writing `logs/review_queue/` files is caller
responsibility, not part of the basic judge CLI.

### 7.4 No autonomous judge decisions in v1

We do not have judge calibration data. Until we do, no automated path
treats a judge output as a decision. Building such a path is on the
deferred list.

---

## 8. Aggregated test log and stuck detection

### 8.1 Why git diff, not self-report

Self-reported "what I changed" from the agent is unreliable — agents
rationalize, summarize wrong, or omit. The aggregated log uses git diff as
the load-bearing signal. The agent's `agent_rationale` is logged for
*human* reading, not as input to the stuck classifier.

### 8.2 Diff features per attempt

Computed from the model repo git diff between the current attempt commit and
the attempt commit recorded on the last failing run of the same `test_id`:

- `diff_hash` — content hash of the diff.
- `lines_changed` — count.
- `files_touched` — set of file paths.
- `regions_jaccard_prior` — Jaccard similarity of changed line ranges
  against the union of changed line ranges in this debugging session for
  this test.

A "debugging session" is scoped per `test_id`: it begins at the first
failure and ends when the test passes, is relaxed, or the human clears it.

### 8.3 Trigger rules (initial; expected to iterate)

The stuck detector emits an unblock signal if, for any test in an active
debugging session:

- 2 consecutive identical `diff_hash` values → thrashing, no actual change.
- 4 attempts with `regions_jaccard_prior > 0.7` → oscillating in the same
  code regions.
- 6 attempts total → conservative cap regardless of progress shape.

Thresholds will be wrong; tune from real runs. The features are the
contract; the rules are policy.

### 8.4 What an unblock signal does

- Writes a `STUCK` file at the model root with the offending `test_id`,
  recent attempt summary, and the most recent failure's `issue_description`.
- The implementation agent, on next invocation, refuses to continue working
  on that test until the file is removed.
- The human investigates, takes one of: revise the spec, register a paper
  issue, relax the test, or clear the signal and tell the agent to keep
  trying.

### 8.5 Query patterns

The CSV is intentionally simple to start. Expected queries:

- "All currently failing tests, latest attempt only."
- "All tests relaxed because of paper issues."
- "Attempt history for a given `test_id`."
- "Tests in `pending_human_review` for current run."

These are achievable with pandas one-liners; we will not build a query
layer until the patterns are stable.

---

## 9. Citation/Assumption pattern

### 9.1 The rule

Every function in `implementation/src/` must have, in its docstring, either
a `Citation:` field or an `Assumption:` field. Both are allowed.

- `Citation:` references one or more citation IDs (`C-001`, `C-002`).
- `Assumption:` references one or more assumption IDs (`A-001`).

A function that wraps and composes other cited functions only needs
citations for the *additional* logic it introduces. The intent is that
small functions have small citation lists.

Example:

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

### 9.2 The static check

`framework/static_checks/` provides a check that scans
`implementation/src/` and asserts every function has at least one of
`Citation:` or `Assumption:` in its docstring. The check is run as part of
the test suite.

### 9.3 What this check does *not* do

It verifies *presence*, not *quality*. The cited paragraph might not
support the function's behavior. Periodic human audit is required;
automated quality auditing is on the deferred list.

---

## 10. Gates and lifecycle

### 10.1 Gates

- **APPROVED gate.** Phase B tooling refuses to start without
  `article_aware/APPROVED`. The human writes this file after reviewing
  Phase A outputs (spec, pseudocode, extracted data, reproduced figures).
- **STUCK gate.** When the stuck detector emits a signal, the implementation
  agent refuses to continue work on the affected test until the
  `STUCK` file is removed.
- **Pending review gate.** Tests in `pending_human_review` block any
  downstream work that depends on them. The agent may continue with
  unblocked work.

### 10.2 Spec edits invalidate prior passes

If the human edits any file in `article_aware/` after Phase B has started,
every prior test pass was validated against the *old* spec. The runner
records `spec_commit_hash` on every test row; queries that ask "what is
currently passing" filter to rows whose `spec_commit_hash` matches the
current head of `article_aware/`.

In v1 this is an advisory filter — the human or agent reads it and reruns
affected tests. Selective dependency-aware invalidation (re-running only
tests that depend on the changed spec components) is on the deferred list.

### 10.3 Per-model versioning

The framework lives in the parent monorepo. Each model directory is a nested
git repository tracked from the parent monorepo as a git submodule, so model
history is independent from framework history and from other models.

Model-repo commit points:

- Phase A artifacts complete (pre-approval).
- `APPROVED` written.
- Each test attempt created by the framework runner.
- Each implementation milestone (a passing component, a passing figure
  reproduction).
- Spec revisions during Phase B.

The framework records both the model commit hash and the parent framework
commit hash with every test row so any past run can be replayed against the
same code state. Framework changes are committed in the parent monorepo;
model attempts and milestones are committed inside the nested model repo.

---

## 11. Deferred decisions

These are explicitly punted to keep v1 scoped. Each appears here so we
do not re-litigate them when they come up; the answer is "deferred,
see DESIGN.md §11".

- **Spec schema specifics.** Pydantic models for `model_spec.yaml` will be
  pinned against the first real article. The shape is defined in §5; the
  fields are not.
- **Stochastic models.** Distributional comparison (KS test, percentile
  bounds over N runs), seed management, and noise-aware tolerances. Will
  add when the deterministic path is solid.
- **Citation/Assumption quality audit.** Static check verifies presence
  only. Sampling-based audit of whether cited passages actually support
  function behavior is for a later round.
- **Cache invalidation on spec change.** v1 is advisory: filter by
  `spec_commit_hash`. Selective dependency-aware invalidation is later.
- **Autonomous judge decisions.** No automated path treats judge output as
  a decision in v1. Calibration data needs to exist first.
- **Tolerance defaults.** Initial values in §6.2 will iterate from real
  runs. No principled derivation in v1.
- **Stuck-detector thresholds.** Initial values in §8.3 will iterate from
  real runs.
- **Multi-paper synthesis.** Out of scope. Enriching a spec from another
  paper is a human action that produces a new round of extraction.
- **UI for human review.** Human review may use files in `review_queue/`;
  no web UI is planned for v1.
- **Framework repository split.** The parent monorepo remains the framework
  repo throughout v1. Lifting the framework into a package-only repo is a
  future refactor.

---

## Appendix A — Suspected paper errors

Distinct from underspecification (which becomes an `Assumption`), suspected
paper errors are recorded by the human in `logs/paper_issues.md`:

```yaml
- id: PI-001
  test: test_figure_4b_attended_vs_unattended
  type: suspected_paper_error  # | paper_ambiguity | known_erratum
  description: "Figure 4B y-axis label appears inconsistent with text on p. 7."
  action: "assertion relaxed to qualitative ordering only"
  references:
    - "Erratum, Journal Vol X, p. Y"
```

Tests reference `PI-NNN` IDs in their `paper_issue` decorator argument and
report status `relaxed` rather than `pass`. The aggregated log can answer
"what is relaxed because of paper issues" separately from "what is stuck",
because the workflows for those are different.

---

## Appendix B — Glossary

- **Phase A** — article-aware steps (1–2): extraction and figure reproduction.
- **Phase B** — no-article steps (3–5): test suite, model, iteration.
- **Spec** — the structured artifact in `article_aware/spec/`.
- **Pseudocode** — protocol descriptions in `article_aware/pseudocode/`.
- **Extracted data** — numeric and qualitative data from paper figures.
- **Reproduced figures** — plots from extracted data, for human spot-check.
- **Citation** — referenceable pointer into the paper, identified `C-NNN`.
- **Assumption** — referenceable underspecification record, identified `A-NNN`.
- **Paper issue** — referenceable suspected paper error or ambiguity, `PI-NNN`.
- **Spec question** — write-only escalation from the implementation agent,
  `SQ-NNN`.
- **Compliance test** — test that asks judges whether code matches a spec
  section.
- **Qualitative test** — test that asks judges whether outputs satisfy a
  natural-language claim that resists deterministic reduction.
- **APPROVED gate** — sentinel file marking Phase A as human-reviewed.
- **STUCK gate** — sentinel file emitted by stuck detector blocking further
  work on a specific test.

---

## Appendix C — Open questions to revisit with first article

These are not deferred decisions — they need answers, but the answers
depend on seeing real article content first.

- Concrete Pydantic schema for `model_spec.yaml`.
- Whether one CSV per curve or one CSV per figure works better for
  `extracted_data/`.
- How fine-grained the `components` decomposition in the spec needs to be
  (one entry per equation? per logical block?).
- Whether the pseudocode files need a structured frontmatter (inputs,
  outputs, links to spec components).
- Initial tolerance values and whether per-figure overrides are common.
