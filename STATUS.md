# STATUS — what is actually built

This file is the **canonical map of reality**. [WORKFLOW.md](WORKFLOW.md) (the single
consolidated process/structure doc) and [VISION.md](VISION.md) describe the *target*;
parts are not built. **On any conflict, STATUS.md wins.** If you are an agent:
navigate by this file, not by machinery the other docs describe in the present tense.

Last reconciled: 2026-06-02 (fictional machinery removed from the process docs); docs
consolidated 2026-06-03 (DESIGN / ARCHITECTURE / REPO_STRUCTURE / ARCHITECTURE_WATCHLIST
folded into WORKFLOW.md and deleted — older `§DESIGN`/`§REPO_STRUCTURE` cross-references
below now live in WORKFLOW). This file records what remains genuinely deferred.

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
| Skills (operational layer) | `skills/` | acquire-sources, extract-spec, extract-figure, digitize-figure, compare-figure, implement, author-tests, run-tests, write-sanity-check, update-state (+ audit-{spec,tests,reuse,digitization,faithfulness,process}; scripts: failing_tests, log_freshness, persist_verdict, verdict_status). **The skills, not a runner, are how work actually gets done.** |
| Source acquisition (Phase 0) | `skills/acquire-sources/SKILL.md` | gathers paper materials + SI + original code into `paper/`, writes `paper/SOURCES.md` manifest (obtained / exists-but-not-obtained / confirmed-absent). `paper/code/` (original author code) is **gitignored** — not redistributed; existence+source stay traceable via the versioned `SOURCES.md` + `code_refs.yaml`. Wired as Phase 0 of the full-pass workflow (`from="extract"` only); run by an agent, no standalone tooling. |
| Phase-A contract auditor + SQ-blocking workflow | `skills/audit-spec/SKILL.md`, `.claude/workflows/full-pass.js` | **wired, partially exercised.** `audit-spec` independently audits the *contract* (the safeguard missing till now: only figures were audited); full-pass wires it as a Phase-A gate + the paper-fix verify step, with SQ-as-blocking-circuit-breaker (never implement with an open SQ), CONTRACT_BUG/PAPER_ISSUE auto-routed to a ground-truth→lineage→human paper-fix ladder (≤MAX_PAPERFIX, then the WHOLE workflow exits BLOCKED), and a `finalize()` that runs on EVERY exit (try/finally) → README human-entrypoint + commit + push + PR. `audit-spec` prototyped once on RH2009 (FAITHFUL); the SQ-blocking/paper-fix/finalize loop is **not yet run end-to-end**. Design: `proposals/sq-blocking-gate-and-paper-fix-2026-06-04.md`. |
| Per-model submodule | `models/<m>/` nested git repo | real; parent bumps the pointer. |
| Citation/Assumption/Code/**Lineage** presence check | `neuromodels/framework/static_checks/check_citations.py` | presence+**resolution** — every `C-NNN`/`A-NNN`/`CODE-NNN`/`LINEAGE-NNN` tag resolves to its ledger (`citations.yaml`/`assumptions.yaml`/`code_refs.yaml`/`lineage_refs.yaml`). For lineage it **additionally** validates cross-model: the named ancestor `model:` exists and `ref:` resolves to a real ledger ID or calibration key there, so a genealogy link is always traceable. Run **manually**, no CI; not a quality/semantic check. |
| Provenance taxonomy report | `neuromodels/framework/provenance.py`, CLI `neuromodels provenance` | buckets calibrated values by source (paper / paper+code / **code-alone** / **lineage** / assumption / unsourced). Surfaces the code-alone set (specified by authors' code, absent from the paper) and **traces lineage values through to the ancestor's ultimate ground** (paper/code/assumption in the genealogy ancestor). Four first-class provenance ledgers: `citations.yaml` (`C-`), `assumptions.yaml` (`A-`), `code_refs.yaml` (`CODE-`), `lineage_refs.yaml` (`LINEAGE-`). |

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
  **Central to the VLM / faithfulness flow** (WORKFLOW.md §3 + §8).
- `models/<m>/implementation/figure_outputs/figure_<N>.png` — generated
  figures the VLM compares (gitignored).
- `models/<m>/logs/figure_comparisons/` — the persistent VLM verdict home.
- The `update-state` skill + its `scripts/` — the reviewable state report
  (`models/<m>/README.md`) and the verdict/freshness tooling.
- `models/<m>/figures_reproduced/figure_<N>.png` — the **committed** implemented
  render (the README's "implemented" view + the coverage gate's render artifact).
  As of 2026-06-14 the `full-pass` finalize **stale-sweep refreshes it from the
  current model on every run**, so it is fresh-at-finalize (earlier it was a
  hand-added snapshot with no freshness guarantee). The gitignored
  `implementation/figure_outputs/` remains the scratch render; a faithfulness audit
  still re-renders fresh rather than trusting any committed snapshot.
- `models/<m>/article_aware/figures/figure_<N>.png` — the **committed** original
  paper-figure crop (the README's "paper" view + the digitization/faithfulness
  referent). A genuine schematic carries a `figure_<N>.nodigitize` marker instead of
  a digitized overlay. Both are required by the coverage gate.

---

## The orchestrated workflow (`full-pass.js`) — the real loop as of 2026-06-14

The reproduction loop is now driven by **`.claude/workflows/full-pass.js`** (the `full-pass`
workflow), NOT the hand-run skill loop the older text below described. Its loop is:
acquire → extract-spec + digitization gate (digitize → separate-critic audit, **per-panel**,
commits the paper crop) → audit-spec gate → implement → verify (`audit-faithfulness` +
`audit-process`, loop-until-dry) → **exit reconciliation** → finalize (stale-sweep that commits
`figures_reproduced/` + **modification smoke test** + **coverage gate** → README → PR).

Figure faithfulness is established by **`audit-faithfulness`** (re-render vs the digitized
reference + paper), **not** by `compare-figure-packet` + VLM subagents — that VLM-checklist path
(rows in "Built and in use") still *exists* as tooling but is **superseded** and no longer in the
loop. The `test-table` VLM column will therefore be empty for `full-pass`-built models; that is
expected, not a regression.

**Gates added 2026-06-14** (`proposals/process-drift-register-2026-06-14.md`): the exit can no
longer be `faithful` while a digitization is unverified, a `GENUINE_DIVERGENCE`/`BLOCKED` figure
is open, the process trajectory is `drifting`, or the verify loop has reached its cap with
actionable findings that would require an unaudited final-round mutation. A **coverage gate**
(`tools/check_figure_coverage.py`) blocks any exit whose target figures lack their committed three
views (paper crop · digitized · `figures_reproduced/` render) or a committed faithfulness audit.
That gate is deterministic artifact-presence checking; semantic/VLM judgment remains with the
audit agents. There is still **no runner and no stuck gate**; `check_citations.py` is
presence-only, run
manually. New tooling: `tools/check_figure_coverage.py` (coverage), `tools/repro_cost.py`
(per-model API cost in each README).
