# Repository structure

What lives where. *What the project is for*: [VISION.md](VISION.md). *How to
reproduce a model*: [WORKFLOW.md](WORKFLOW.md). *Why the design*:
[DESIGN.md](DESIGN.md). *The shape each model must take*:
[ARCHITECTURE.md](ARCHITECTURE.md). *What is actually built*:
[STATUS.md](STATUS.md).

## Root

```
model_agent/                       # parent monorepo (also the framework repo)
  VISION.md                        # what the project is for (four pillars; apex)
  STATUS.md                        # what is actually built (canonical on reality)
  DESIGN.md                        # rationale for the mechanisms
  ARCHITECTURE.md                  # the contract shape every model must take
  ARCHITECTURE_WATCHLIST.md        # what would falsify the structural bets
  WORKFLOW.md                      # how to reproduce a model end-to-end
  REPO_STRUCTURE.md                # this document
  AGENTS.md                        # thin entry point for agent sessions
  pyproject.toml  pytest.ini
  neuromodels/                     # the framework (pip install -e .)
  models/                          # one git submodule per reproduced model
  proposals/                       # process-knowledge (Pillar 4): plans, retros, design passes
  skills/                          # the operational layer — how work actually gets done
```

## The framework — `neuromodels/`

```
neuromodels/
  framework/
    testing/         # pytest plugin → logs/test_runs.jsonl; figure(N) marker; deterministic_test
    test_table.py    # per-figure Deterministic + VLM status table   (CLI: neuromodels test-table)
    compare_figures.py  # figure-comparison packet builder           (CLI: neuromodels compare-figure[-packet])
    judge/           # adversarial judge, attacker/defender           (CLI: neuromodels judge)
    llm/             # shared LLM provider access
    explore/         # helpers for sanity-check scripts
    static_checks/   # check_citations.py — manual presence+resolution of C-NNN/A-NNN tags
  cli/               # `neuromodels` CLI entry points
  tests/             # framework tests
```

Earlier drafts listed `logging/`, `stuck_detector/`, `review/`, and a "runner" —
**none ever existed**; they have been removed here (STATUS.md). `static_checks/`
now holds one real check — `check_citations.py`, a manually-run, presence-only
citation/assumption resolver (STATUS.md). The real operational layer is `skills/`
+ the pytest plugin.

## Per-model — `models/<model>/`

Each model is a **private git submodule** with its own history; the parent bumps
the pointer. The required *internal* shape (stage modules + `manifest.yaml`,
`measurements.py`, `views.py`, the two calibration ledgers, `artifacts/`,
`logs/figure_comparisons/`, `logs/figure_diagnoses/`) is defined in
**[ARCHITECTURE.md → Per-model layout]** — the authoritative source. In brief:

```
models/<model>/
  paper/             # raw PDF — extractor (Phase A) only
  article_aware/     # PROTECTED — Phase A contract: spec/ (model_spec, calibration,
                     #   citations, assumptions), pseudocode/, figures/, extracted_data/, APPROVED
  implementation/    # Phase B: src/<pkg>/{stages,measurements,views,protocols}, calibration.yaml,
                     #   artifacts/, tests/, sanity_checks/, figure_outputs/ (gitignored)
  logs/              # test_runs.jsonl, figure_comparisons/, figure_diagnoses/, spec_questions.md
  figures_reproduced/ # COMMITTED snapshot of paper-vs-reproduced comparison PNGs (see below)
  README.md          # the reviewable state report (update-state skill)
```

**`figures_reproduced/` (committed snapshot — freshness NOT guaranteed).**
A per-model directory of paper-vs-reproduced comparison PNGs, committed by the
docs/README pass (not produced by the render pipeline). The **authoritative**
render is the gitignored `implementation/figure_outputs/figure_<N>.png` that the
VLM compares; `figures_reproduced/` is a hand-committed copy for at-a-glance
review. **Its freshness is not enforced** — a later code change can move
`figure_outputs/` without anyone re-committing `figures_reproduced/`. **Open
risk:** a faithfulness audit that reads `figures_reproduced/` may be looking at a
stale image; for the binding visual check, render `figure_outputs/` fresh and use
the persisted `logs/figure_comparisons/` verdicts.

## Boundaries (enforced by tooling, not just prompts)

| Agent role | Reads `paper/` | Reads `article_aware/` | Writes `article_aware/` | Writes `spec_questions` |
|---|---|---|---|---|
| Extractor (Phase A) | yes | yes | yes | n/a |
| Implementation (Phase B) | **no** | yes (read-only) | **no** | append-only |
| Judges / critique | no | scoped section only | no | no |

Enforced by working-directory scope, not prompt text — prompts are a hint, tool
config is the guarantee. The Phase-A `APPROVED` and faithfulness-verdict **human
gates** are, in the autonomous reproduction program, substituted by adversarial
critique agents (program plan §1); the directory boundary itself is unchanged.

## Who writes / reads what

| Path | Writers | Readers |
|---|---|---|
| `paper/` | human (once) | extractor only |
| `article_aware/**` | extractor | extractor, impl agent |
| `article_aware/APPROVED` | human / spec-review panel | Phase-B gate |
| `implementation/**` | impl agent | impl agent, judges |
| `logs/test_runs.jsonl` | pytest plugin | impl agent, organizer, human |
| `logs/figure_comparisons/` | compare-figure flow | organizer, human |
| `logs/spec_questions.md` | impl agent (append-only) | human / organizer |

## Layout rationale (still true)

- **`article_aware/` as one directory** = the protection boundary is one path
  prefix; obvious to enforce and to inspect.
- **`paper/` separate from `article_aware/`** — the PDF is raw input with a
  different lifecycle; the extractor reads both, the implementation reads neither.
- **`APPROVED` sentinel** — a cheap, version-controllable gate.
- **Per-model submodules** — independent history per model, discoverable from one
  parent (DESIGN §6).
- **Per-model `logs/`** — `git log` on one model tells its full story.
- **`sanity_checks/` separate from `tests/`** — exploratory (no asserts) vs
  contract; generated `_outputs/` are gitignored.
