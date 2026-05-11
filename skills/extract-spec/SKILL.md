# Skill: Extract Spec

## Purpose

Given a paper describing a computational model, produce the article-aware
specification: the structured artifacts a downstream implementation agent
needs to reproduce the model **without re-reading the paper**.

Anything the implementation agent cannot find in these artifacts is by
definition an underspecification, and must be recorded as an `Assumption`.
This is the property that makes the Phase A / Phase B split work; protect it.

---

## Inputs

- `paper/` — the paper PDF and `extracted_text.md` (verbatim text, equations,
  table data, figure captions)

---

## Outputs

Four artifacts under `article_aware/spec/` and `article_aware/pseudocode/`:

- `spec/citations.yaml`
- `spec/assumptions.yaml`
- `spec/model_spec.yaml`
- `pseudocode/<figure>_protocol.md` (one per simulation protocol)

---

## Process

### Step 1 — Citations (`spec/citations.yaml`)

Numbered `C-NNN` references into the paper. Cite each equation, each parameter
table, each qualitative claim source, and each figure caption you'll rely on.
Citations are **write-once** and referenced from the spec, code docstrings,
and tests.

```yaml
- id: C-001
  source: "Author Year"
  location: "Eq. 3, p. 4"
  text: "<short verbatim quote or close paraphrase>"
  notes: "<optional>"
```

Cite generously — every fact you derive from the paper should have a citation
that a reader can verify. Untraceable claims become silent assumptions later.

### Step 2 — Assumptions (`spec/assumptions.yaml`)

Named `A-NNN` records for every underspecification. Lead with what was assumed,
then *why*, alternatives considered, and what scope is affected. Knowing why
later lets a reader judge edge cases.

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

If the paper is silent on a value, type, or convention you need, that's an
assumption — record it. If you want to validate later that an assumption was
load-bearing, the `affects` field tells you which tests to rerun under
alternative choices.

### Step 3 — Model spec (`spec/model_spec.yaml`)

Structured Pydantic-validated YAML with these required top-level fields:

- **`state_variables`** — names, dimensions, units, initial conditions.
- **`parameters`** — names, values (or `value: null` plus `underspecified_by:
  A-NNN`), units, source citation IDs.
- **`equations`** — symbolic form or natural-language description with
  citation. Each has a stable ID (`EQ-NNN`).
- **`components`** — named building blocks with parameter and equation refs.
- **`pipeline`** — **ordered** computation steps from input to recorded
  response. Each step references an equation and lists its inputs/outputs.
  Steps may be `optional: true` with an `applies_when` condition.
- **`simulation_protocols`** — one per pseudocode file. Per-protocol parameter
  overrides, link to the pseudocode document, `expected_outputs` returned by
  `implementation/src/<package>/protocols.py::run_<id>()`, and references to
  expected data / claim files.

**Why `pipeline` is non-negotiable.** The pipeline is what makes the spec
*executable*. Without an ordered dataflow, the implementation agent has to
reverse-engineer the pipeline from equations and prose alone — which it
cannot do without re-reading the paper. The pipeline is the contract that
keeps Phase A and Phase B separable.

### Step 4 — Pseudocode (`pseudocode/<figure>_protocol.md`)

Plain markdown, one per simulation protocol. Each file has:

- **Inputs** — what stimulus or condition drives this protocol
- **Parameter sweeps** — what varies across runs
- **Procedure** — step-by-step computation
- **Outputs** — named variables (these names are the runner output contract;
  they must match `simulation_protocols[*].expected_outputs` in
  `model_spec.yaml`)
- **Expected behavior** — qualitative claims with citation refs

The output variable names are load-bearing: tests in
`extracted_data/test_<figure>.py` will assert against exactly these keys.

---

## Quality checks before finishing

- [ ] Every equation in the paper that the model uses has a `C-NNN` citation
- [ ] Every parameter in `model_spec.yaml` has either a value with a citation
      or `value: null` with `underspecified_by: A-NNN`
- [ ] Every assumption has `affects:` populated so its blast radius is traceable
- [ ] The `pipeline` field lists steps in execution order, each referencing
      an equation; no implicit ordering
- [ ] `simulation_protocols[*].expected_outputs` keys match the variables named
      in the corresponding `pseudocode/<figure>_protocol.md`
- [ ] An implementation agent reading only `article_aware/` can produce the
      model without ambiguity — if not, find the gap and either cite or
      record an assumption

---

## What NOT to do

- **Do not paraphrase equations into your own form.** Use the paper's notation;
  cite the equation; let the implementation derive the closed form.
- **Do not silently choose values.** If the paper is ambiguous, write an
  assumption — don't pick a number and move on.
- **Do not leave `pipeline` empty or unordered** even if the paper presents
  equations as a flat list. Decide the dataflow order yourself, and cite the
  reasoning in the spec.

---

## Approval gate

When the human is satisfied with the spec + pseudocode + extracted figure
data + reproduced figures, they write `article_aware/APPROVED` (an empty file
is fine). Phase B tooling refuses to start without it.
