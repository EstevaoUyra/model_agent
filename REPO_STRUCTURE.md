# Repository structure

This document is the reference for **what lives where**. For *how* to do
work, see [WORKFLOW.md](WORKFLOW.md). For *why* the design is shaped this
way, see [DESIGN.md](DESIGN.md).

## Layout

The framework is a Python package, installed in editable mode (`pip install
-e .` from the repo root). Models are nested git repositories under
`models/`, tracked from this monorepo as git submodules. Each model
directory imports from the framework but has its own history.

```
model_agent/                            # repo root (this monorepo)
  pyproject.toml                        # framework package config + extras
  pytest.ini                            # custom pytest markers
  AGENTS.md                             # thin entry point for agent sessions
  REPO_STRUCTURE.md                     # this document
  WORKFLOW.md                           # how to reproduce a model end-to-end
  DESIGN.md                             # rationale for the system

  neuromodels/                          # the framework
    framework/
      testing/                          # pytest decorators, runner, tolerance types
      llm/                              # shared LLM provider access
      judge/                            # adversarial judge orchestration
      logging/                          # aggregated test log + queries
      stuck_detector/                   # diff-based stuck signal computation
      static_checks/                    # citation/assumption docstring check
      review/                           # review-queue file format and apply
      explore/                          # helpers for sanity-check scripts
    cli/                                # `neuromodels` CLI entry points
    tests/                              # framework tests

  models/
    reynolds_heeger_2009/               # git submodule; one repo per model
      paper/                            # source of truth (raw input)
      article_aware/                    # PROTECTED — Phase A artifacts
      implementation/                   # Phase B code, tests, sanity checks
      logs/                             # per-model test/escalation logs
```

## Per-model layout (inside `models/<model_name>/`)

```
paper/
  paper.pdf                             # raw source
  extracted_text.md                     # OCR/text extraction (optional)

article_aware/                          # PROTECTED — see "Boundaries"
  spec/
    model_spec.yaml                     # state vars, params, equations, components,
                                        #   pipeline, simulation_protocols
    citations.yaml                      # numbered C-NNN references into the paper
    assumptions.yaml                    # named A-NNN underspecification records
  pseudocode/
    figure_<N>_protocol.md              # per-protocol procedure descriptions
  extracted_data/
    figure_<N>.csv                      # numeric data digitized from paper figures
    figure_<N>_qualitative.yaml         # claims with deterministic-reducible flag
  reproduced_figures/
    figure_<N>.png                      # plotted from extracted_data; human spot-check
  APPROVED                              # empty sentinel file; presence = human gate ok

implementation/
  src/<package>/                        # the model implementation
    __init__.py
    model.py                            # pipeline functions
    protocols.py                        # per-figure runners
    helpers.py                          # numerical utilities
  tests/
    conftest.py
    test_*.py                           # tests written from spec + qualitative claims
  sanity_checks/                        # exploratory scripts (not tests)
    check_<topic>.py                    # one file per topic; multiple checks inside
    check_<topic>_outputs/              # GITIGNORED — PNG + text per check

logs/
  test_runs.csv                         # aggregated test log (one row per test execution)
  spec_questions.md                     # Phase B agent: append-only, no read-back
  paper_issues.md                       # human-only, structured PI-NNN entries
  review_queue/                         # one file per pending human verdict
```

## Who writes / reads what

| Directory                            | Writers                          | Readers                          |
|--------------------------------------|----------------------------------|----------------------------------|
| `paper/`                             | human (one-time)                 | extractor only                   |
| `article_aware/spec/`                | extractor                        | extractor, impl agent, framework |
| `article_aware/pseudocode/`          | extractor                        | extractor, impl agent            |
| `article_aware/extracted_data/`      | extractor                        | extractor, impl agent            |
| `article_aware/reproduced_figures/`  | extractor                        | human (review)                   |
| `article_aware/APPROVED`             | human                            | framework gate                   |
| `implementation/src/`                | impl agent                       | impl agent, framework, judges    |
| `implementation/tests/`              | impl agent                       | impl agent, framework            |
| `implementation/sanity_checks/`      | impl agent                       | impl agent, human                |
| `implementation/sanity_checks/*_outputs/` | impl agent (auto-generated) | impl agent, human                |
| `logs/test_runs.csv`                 | framework runner                 | impl agent, human, framework     |
| `logs/spec_questions.md`             | impl agent (append-only)         | human                            |
| `logs/paper_issues.md`               | human                            | impl agent, framework            |
| `logs/review_queue/`                 | framework runner / impl agent    | human                            |

## Boundaries (enforced by tooling, not just prompts)

| Agent role     | Reads paper | Reads article_aware | Writes article_aware | Reads spec_questions | Writes spec_questions |
|----------------|-------------|---------------------|----------------------|----------------------|-----------------------|
| Extractor      | yes         | yes                 | yes                  | n/a                  | n/a                   |
| Implementation | **no**      | yes (read-only)     | **no**               | **no**               | append-only           |
| Judges         | no          | scoped section only | no                   | no                   | no                    |

Boundaries are enforced by Claude Code permission config / working
directory scope, not by prompt instructions. Prompts are a hint; tool
config is a guarantee.

## Defenses for layout choices

- **`article_aware/` as a single directory** makes the protection boundary
  one path prefix. Easy to enforce; obvious to humans inspecting the repo.
- **`paper/` separate from `article_aware/`** because the PDF is raw input
  with a different lifecycle from derived artifacts. Extractor reads both;
  implementation reads neither.
- **`APPROVED` sentinel file** is a cheap, version-controllable gate. Phase
  B tooling refuses to start without it.
- **Per-model submodules** give each reproduced model an independent
  history while keeping the framework and model collection discoverable
  from one parent repo.
- **`logs/` per model rather than central** because logs are inherently
  per-model and we want `git log` on one model directory to tell the full
  story.
- **`sanity_checks/` separate from `tests/`** because sanity checks are
  exploratory diagnostics with no assertions; mixing them with assertion
  tests would conflate "this is a contract" with "let me look at this."
  Generated `_outputs/` directories are gitignored — only the scripts are
  version-controlled.
- **`framework/explore/` shared across models** so sanity-check scripts
  use a consistent style (stat printing, heatmap saving) rather than
  reimplementing helpers per model.

## Glossary

- **Phase A** — article-aware steps: extraction and figure reproduction.
- **Phase B** — no-article steps: test suite, model, iteration.
- **Spec** — the structured artifact in `article_aware/spec/`.
- **Pseudocode** — protocol descriptions in `article_aware/pseudocode/`.
- **Extracted data** — numeric and qualitative data from paper figures.
- **Reproduced figures** — plots from extracted data, for human spot-check.
- **Citation** — referenceable pointer into the paper, identified `C-NNN`.
- **Assumption** — referenceable underspecification record, identified `A-NNN`.
- **Paper issue** — referenceable suspected paper error or ambiguity, `PI-NNN`.
- **Spec question** — write-only escalation from the impl agent, `SQ-NNN`.
- **Sanity check** — exploratory script under `sanity_checks/`; no asserts.
- **APPROVED gate** — sentinel file marking Phase A as human-reviewed.
- **STUCK gate** — sentinel file emitted by stuck detector blocking further
  work on a specific test.
