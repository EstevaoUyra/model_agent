# STATUS — what is actually built

This file is the **canonical map of reality**. DESIGN.md, WORKFLOW.md, and
REPO_STRUCTURE.md describe the *target* design; parts of it are not built.
**On any conflict, STATUS.md wins.** If you are an agent: navigate by this
file, not by machinery the other docs describe in the present tense.

Last reconciled: 2026-06-02. The fictional machinery below was **removed** from
DESIGN/WORKFLOW/REPO_STRUCTURE (not merely flagged), so those docs now describe
reality; this file records what remains genuinely deferred.

---

## Built and in use

| Capability | Where | Notes |
|---|---|---|
| Per-test logging | `neuromodels/framework/testing/plugin.py` | pytest plugin; appends one row per test to `models/<m>/logs/test_runs.jsonl`. Records `run_id, session_id, timestamp, test_id, figure, status, commit_hash, spec_commit_hash, failure_message`. Statuses are pytest-native (pass/fail/skip), **not** the `relaxed`/`pending_human_review` vocabulary in WORKFLOW.md. |
| `figure(N)` test marker | same plugin | associates a test with a figure for the table. |
| Test status table | `neuromodels/framework/test_table.py`, CLI `neuromodels test-table` | reads `test_runs.jsonl` + `logs/figure_comparisons/`; emits the per-figure Deterministic + VLM columns. |
| Figure comparison packet | `neuromodels/framework/compare_figures.py`, CLI `neuromodels compare-figure-packet` | path-only JSON; the subagent IS the VLM (reads images directly). |
| Direct VLM compare | CLI `neuromodels compare-figure` | calls an external VLM provider; the packet+subagent path is what the skills actually use. |
| Adversarial judge | `neuromodels/framework/judge/`, CLI `neuromodels judge` | attacker/defender; human decides. |
| LLM provider access | `neuromodels/framework/llm/` | shared. |
| VLM verdict home | `models/<m>/logs/figure_comparisons/figure_<N>_<stamp>.json` | append-only; provenance-wrapped (model commit, evaluated_at, n_subagents, parent_adjudication). |
| Skills (operational layer) | `skills/` | extract-spec, extract-figure, compare-figure, run-tests, write-sanity-check, update-state (+ scripts: failing_tests, log_freshness, persist_verdict, verdict_status). **The skills, not a runner, are how work actually gets done.** |
| Per-model submodule | `models/<m>/` nested git repo | real; parent bumps the pointer. |
| Citation/Assumption presence check | `neuromodels/framework/static_checks/check_citations.py` | presence+**resolution** only (tags resolve to a ledger entry); run **manually**, no CI; not a quality/semantic check. See the deferred-table row below. |

## Partial / advisory only

| Thing | Reality |
|---|---|
| `spec_commit_hash` | The plugin **records** it (git tree hash of `article_aware/`). There is **no tooling** that filters "currently passing" by it — it is advisory, by manual query only. |
| Conflict rule (det vs VLM) | Lives in the **update-state skill** and the README it writes, not in code. `test-table` reports the two signals separately. |
| Spec questions | `logs/spec_questions.md` is a hand-maintained markdown ledger (SQ-NNN; `chosen_assumption` and, since SQ-003, `human_resolution`). No tooling. |

## Removed from the docs (2026-06-02) / still deferred

These were described as if built; the mentions are now **removed** from
DESIGN/WORKFLOW/REPO_STRUCTURE. They remain genuinely deferred — named here, not
pretended built (the autonomous program realizes the runner as its workflow, the
stuck-detector as the iteration cap, and a presence-only citation check):

| Claimed in docs | Reality |
|---|---|
| "framework runner (not raw pytest)", attempt commits | **Does not exist.** Tests run via plain `pytest` (the plugin logs them). No automatic attempt commits. |
| Stuck detector + `STUCK` gate (DESIGN §4, WORKFLOW) | **Not built.** No diff-based detector, no `STUCK` file emission. |
| `neuromodels/framework/logging/`, `stuck_detector/`, `review/` | **No such modules.** |
| `review_queue/` as the human-review mechanism (was: DESIGN §9) | **Never built.** Human review is the per-model `README.md` state report + (autonomous program) the final triage report. The DESIGN mention is now marked never-built, not present-tense. |
| Citation/Assumption static check (DESIGN §8, WORKFLOW Step 4) | **Now built** (2026-06-02): `neuromodels/framework/static_checks/check_citations.py` — a *presence+resolution* check (every `C-NNN`/`A-NNN` tag in `src/` resolves to a ledger entry). Run **manually** (`python -m neuromodels.framework.static_checks.check_citations`); **no CI is wired**. It does **not** check the tag is on the right function or that the cited passage supports the behavior — that quality audit stays a periodic human task. Passes on all 27 models as of 2026-06-02. |
| `logs/test_runs.csv` | It is `test_runs.jsonl` (JSONL via the plugin). |
| `logs/paper_issues.md`, `relaxed`/`pending_human_review` statuses, `CurveTolerance` machinery | **Not present / not built.** |
| `article_aware/reproduced_figures/` auto-plotted from extracted data | Directory exists but the auto-plot path is not built; treat as manual/optional. |

## Real but under-documented (exists; the layout docs omit it)

- `models/<m>/article_aware/figures/` — `figure_<N>.md` (overpowered caption),
  `figure_<N>_visual_checklist.md`, and the original paper figure images.
  **Central to the VLM flow**; REPO_STRUCTURE.md does not list it.
- `models/<m>/implementation/figure_outputs/figure_<N>.png` — generated
  figures the VLM compares (gitignored).
- `models/<m>/logs/figure_comparisons/` — the persistent VLM verdict home.
- The `update-state` skill + its `scripts/` — the reviewable state report
  (`models/<m>/README.md`) and the verdict/freshness tooling.
- `models/<m>/figures_reproduced/` — a **committed** snapshot of paper-vs-
  reproduced comparison PNGs (added by the docs/README pass; now in
  REPO_STRUCTURE.md). It is **not** produced by the render pipeline and its
  freshness is **not** guaranteed: the authoritative render is the gitignored
  `implementation/figure_outputs/`. A faithfulness audit reading
  `figures_reproduced/` could see a stale image — render fresh + read the
  persisted `logs/figure_comparisons/` verdicts for the binding check.

---

## Implication for agents

The real loop is: edit `implementation/` → `pytest` (plugin logs to
`test_runs.jsonl`) → `neuromodels test-table` → `compare-figure-packet` +
VLM subagents → persist verdict → `update-state` rewrites the model README.
There is **no runner and no stuck gate** catching you. One static check exists
(`check_citations.py`, run manually — citation/assumption tags resolve to a
ledger), but it is presence-only and not wired to CI. Self-discipline (and the
skills) carry what the docs imply tooling enforces.
