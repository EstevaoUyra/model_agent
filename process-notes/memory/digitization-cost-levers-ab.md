---
name: digitization-cost-levers-ab
description: Digitization-cost experiment REVERTED from main — merged/batched tools don't help; don't rebuild them
metadata: 
  node_type: memory
  type: project
  originSessionId: 5fff61cd-8924-45f9-97f9-c6c40428d091
---

**Disposition (2026-06-14): the whole experiment was REVERTED from main (PR #59)** — it had leaked
inadvertently via PR #57. The "merged tool" (batched helpers) gave no benefit, so the ORIGINAL
primitives are kept (overlay, crop_region, trace_darkest_in_band, build_calibration, resample_pchip,
detect_plot_box). Do NOT rebuild overlay_with_crops / trace_bands. Code preserved on
`experiment/dig-cost-levers-v2` for reference only. Even Lever 2 (which tested well) was rolled back,
not landed. The leak/branch-collision is the case that motivated the worktree git-discipline rule
([[branch-bumps-from-origin-main]]).

Validated A/B (2026-06-14, branch `experiment/dig-cost-levers-v2`) of two figure-digitization
cost levers, run blind via a new `from='digitize'` harness in full-pass.js (runs only
describe→digitize→audit, no implement/finalize) on **paper-only clones** (`tools/dig_bench.py`
clone whitelists paper materials, strips every answer artifact incl. paper/code; a snoop-check
aborts on leakage — the first itti clone was leaky and that result is void).

**Lever 2 (diff-scoped audit: rounds ≥2 re-audit only re-digitized figures) WORKS.** Clean
isolation on hyvarinen (both arms ran identical 3-round structure over the same 3 figures):
audit cost **−36% ($9.37→$6.03)**, total digit+audit **−12%**, and treatment was *higher* quality
(3/3 FAITHFUL vs baseline's 2 minor-DIVERGENT). Land it (default-on).

**Lever 1 (batched helpers overlay_with_crops / trace_bands) does ~nothing for cost.** hyvarinen
digitize flat (−2%) despite 89 batched-helper calls — **per-turn cache size dominates, not tool-call
count**, so collapsing round-trips doesn't move the bill. Harmless to quality; not worth relying on.

**Round count is the dominant cost driver, and the levers don't control it.** flash didn't isolate
the levers: baseline judged the scale-bar-only figures uncalibratable and BLOCKED them → 1 round,
$8.88; treatment attempted them → 3 rounds, $38.11, + a fig-10 TOOL_MISUSE the auditor caught. The
**block-vs-attempt decision on hard figures** swings cost ~4×. Next lever to test is convergence
speed / early-block heuristics (Lever 3), not more batching.

**Tooling lesson:** the numeric point-set comparator (`dig_bench compare`) is unusable across blind
re-digitizations — panel DECOMPOSITION itself varies run-to-run (different file/panel/curve names,
per-cell vs aggregate splits). Quality must rest on the independent Opus auditor verdict (it held —
caught the TOOL_MISUSE blind), not file diffs. Relates to [[faithfulness-critics-want-to-find-issues]],
[[saturation-is-the-genealogy-blocker]] (run-to-run digitization variance is large).
