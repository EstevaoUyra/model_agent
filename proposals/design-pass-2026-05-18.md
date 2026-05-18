# Design pass — 2026-05-18

A single reviewable artifact consolidating one empirical design cycle.
Method (your call): commit the best scaffold version, run real agents
against it, iterate from what breaks, consolidate when the validation loop
closes. The loop is now closed. This document is the input for deciding
v2; it does not itself change canon (STATUS.md / ARCHITECTURE.md /
DESIGN.md remain the living docs).

---

## 1. What was run

| Agent run | Kind | Outcome |
|---|---|---|
| hermann2010 | reproduction (R&H extension) | Figs 1,3 green det+VLM; smoke clean; exposed the calibrated-protocol leak |
| cagly2012 | reproduction (from-scratch MGSM) | Figs 6,8 green; 7 fails = one honest v1-scope limit (stubbed GEM); smoke clean |
| carrasco2021 | reproduction (R&H extension, 5 variants) | Fig 7 green; 5-variant config swap clean; clean R&H reuse (no leak) |
| reynolds_heeger_2009 | ARCHITECTURE migration | behavior bit/pixel-identical; built the `run_crf` reuse entry point |
| hermann2010 → run_crf | dependent refactor (the proof) | carried R&H knobs **3→0**, bit-identical; §1 proven end-to-end |

Plus 5 lateral-research/paper-analysis subagents (kept off the main
context by design).

## 2. Thesis verdict — validated

The reframed goal (a substrate a scientist can **verify** and **modify**,
not just faithful figures) held under contact with three very different
model classes:

- **Modification smoke test: 5/5 clean** — incl. carrasco's 5-variant
  attention modulation, cagly's full→diagonal covariance, and the
  migration/refactor config-only swaps. "Swap a component, re-verify, zero
  unrelated edits" is real.
- **measurement-record-as-single-truth: validated** — *zero*
  deterministic-vs-VLM disagreement in any run. The Figure-1 class
  (det-green / visually-broken) is structurally eliminated, not merely
  patched.
- **stub→real-fit artifact contract: validated** — cagly's 7 failures are
  a clean, contained v1-scope limit; a real-GEM stage honoring the same
  artifact would lift them with zero inference edits.
- **§1 reuse-surface rule: proven end-to-end** — not argued: a real
  dependent (hermann) was refactored and the leak provably dissolved
  (3→0, bit-identical).

## 3. Scaffold-change ledger

| # | Defect | Evidence | Fix | Commit | Status |
|---|---|---|---|---|---|
| 1 | Docs described unbuilt machinery (runner, stuck-detector, static-check, CSV) | all runs would mis-navigate | STATUS.md as canonical reality map | `af27252` | fixed |
| 2 | Calibration ledger filed under Phase-A-protected `article_aware/` but written by Phase B | hermann SQ-002 + cagly SQ-003 (convergent) | §3 split: paper-derived (Phase A) vs implementation-side (Phase B) | `ebc86e8` | fixed |
| 3 | Dependents leaked a depended-on model's implementation calibration | hermann (leak) vs carrasco (clean) contrast | §1 reuse-surface rule: depend on primitives, not calibrated protocols | `14323db` | **proven end-to-end** (`a727439`) |
| 4 | `test_table._sort_key` crashed on mixed int/str figure keys | carrasco | uniformly-typed key + regression test | `14323db` | fixed |
| 5 | Stage manifest filed under Phase-A protection (2nd instance of #2's root cause) | R&H migration forced it impl-side | §1: stage manifest is Phase-B-owned | `26d13f2` | fixed |
| 6 | Coupled-math stages have no natural boundary; static pipeline vs data-dependent topology | cagly SQ-001/002 | recorded as ARCHITECTURE §1 known limitations (workarounds held) | `ebc86e8` | recorded |
| 7 | Evidence record overstated the leak ("22" vs true 3+conditional) | hermann refactor | corrected §1 + watchlist | `a727439` | fixed |

## 4. The single most important v2 insight

**Every defect was at a Phase-ownership or reuse-surface seam.** Items
2 and 5 are the *same root cause* surfacing twice: ARCHITECTURE mis-filed
Phase-B-owned artifacts (calibration, the stage manifest) under Phase-A
protection. v2 should state the principle **once, globally**, instead of
rediscovering it per artifact:

> Phase A owns the *paper-derived contract* (spec, claims, pipeline
> dataflow order, paper-stated parameters). Phase B owns *implementation
> structure and implementation-side calibration* (stage decomposition &
> manifest, discretization knobs, stub magnitudes, carried-dependency
> calibration). An artifact's directory is its owner's; never file a
> Phase-B artifact under `article_aware/`.

Recommended v2 action: refactor ARCHITECTURE around this principle stated
up front, with the per-section rules derived from it.

## 5. Contract status per ARCHITECTURE section

| Section | Status | Note |
|---|---|---|
| §1 stages + reuse-surface | **validated end-to-end** | open refinement SQ-004: how much *scientific* parameterization (regime geometry) a reuse entry point should encapsulate vs expose |
| §2 protocol→measurement→view | **validated** | zero det/VLM disagreement in 5 runs; Figure-1 class eliminated |
| §3 two-ledger calibration | **validated** | "contained not eliminated" is the honest steady state — audit the *ledger*, not the code |
| §4 closed loop | **lightly tested** | extensions converged fast; cagly was the only hard loop and hit the v1 GEM limit, not a loop failure. The 12-iter cap / stuck detector is still an unbuilt manual convention (STATUS.md) — **v2 open decision** |
| §5 acceptance + modification smoke test | **validated 5/5** | the operational definition of "modifiable" held every time |

## 6. Open process-improvement proposals (consolidated)

From `proposals/process-improvements-2026-05-18.md` plus this cycle:

1. **Parent-write guard** — a reproduction agent accidentally `--amend`-ed
   the parent; I applied an explicit prohibition ad-hoc in the hermann
   refactor brief. Make it a standing brief-template clause **and** a
   pre-commit guard (refuse commits whose cwd-repo ≠ the model repo).
2. **Brief template / skill** — I hand-wrote 5 briefs (AGENT/MIGRATION/
   REFACTOR) sharing ~80% content. Promote to a `spawn-model-agent` skill
   with the doc-anchor list, git-safety clause, and report contract.
3. **Tiered multi-subagent VLM** as default for contested/changed figures
   (caught a hermann hallucination + a latent 4E issue earlier).
4. **Deterministic layout guards** for schematic figures (Figure-1 class)
   — now partly addressed by the measurement-record carrying layout
   positions; make it a Phase-A authoring rule.
5. **Calibration audit checkpoint** — ~5 SQs / many `audited:false` across
   models; needs a scheduled human pass before it compounds.
6. **`calibrate-figure` skill** — the sweep→apply→confirm loop recurred.
7. **Structured issue categories** in verdicts (model | figure_gen |
   spec_scope) to auto-route the next correction.
8. **test-log commit-hash ordering footgun** — log rows tagged with the
   pre-commit hash; add a dirty-tree flag or a refresh-state macro.
9. **NEW — named-regime-geometry preset** (SQ-004): decide whether reuse
   entry points should encapsulate scientific regime geometry too.
10. **NEW — vaporware decision**: DESIGN/WORKFLOW/REPO_STRUCTURE still
    describe a runner / stuck-detector / static-check beyond STATUS.md's
    patch. v2 must **build or cut** them, not carry them as documented
    fiction.

## 7. Open spec questions across models (for human adjudication)

| Model | SQ | Gist | Status |
|---|---|---|---|
| reynolds_heeger | SQ-001 | suppressive_drive_gain calibration | chosen_assumption, unaudited |
| reynolds_heeger | SQ-002 | Fig 2/3 baseline calibration | chosen_assumption, unaudited |
| reynolds_heeger | SQ-003 | Fig 7 = Panel C only | **human-resolved** |
| reynolds_heeger | SQ-004 | Fig 4C suppressive tuning width vs C-011 | chosen_assumption, unaudited |
| hermann2010 | SQ-001..003 | regime sizes / R&H boundary / response-gain measure | resolved in-run |
| hermann2010 | SQ-004 | run_crf scientific-geometry encapsulation nuance | open (refinement) |
| cagly2012 | SQ-001..003 | coupled-λ / data-dependent pool / no published params | flagged |
| cagly2012 | SQ-004 | stubbed GEM can't fix a learned-covariance sign | **open, needs Phase A** |
| carrasco2021 | SQ-001..003 | RG fit-artifact / NMA amplitude / (framework sort bug) | flagged; sort bug fixed framework-side |

These want a single human adjudication pass — the "where do things stand"
review the project's reviewability goal is for.

## 8. Recommended v2 decisions (yours to make)

1. **Adopt the global Phase-ownership principle (§4)** and refactor
   ARCHITECTURE to lead with it.
2. **Build-or-cut** the runner / stuck-detector / citation static-check.
   They are the largest remaining gap between documented and real.
3. **Promote** the brief template and the closed loop into skills (they
   are now proven patterns, not experiments).
4. **Schedule the calibration audit** and the cross-model SQ adjudication
   (§7) — these are the soft blockers under every "provisional green".
5. **Decide cagly2012's path**: leave at the v1 frozen-GEM boundary, or
   stand up the real-GEM stage against the (validated) stub artifact
   contract.

Nothing here is acted on unilaterally — this is the decision surface.
