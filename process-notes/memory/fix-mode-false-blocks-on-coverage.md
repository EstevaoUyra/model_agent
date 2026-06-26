---
name: fix-mode-false-blocks-on-coverage
description: "full-pass from=fix skips Phase A digitization, so any in-scope figure lacking committed original/digitized artifacts false-blocks at the finalize coverage gate even though the model is reproduction-sound"
metadata: 
  node_type: memory
  type: project
  originSessionId: a651000f-a156-41c6-b8cc-3db390b5524f
---

`full-pass from="fix"` skips Phase A (extract + digitization gate) and the finalize stale-sweep only re-renders the *implemented* view — so it can NEVER create a missing `original` (paper crop) or `digitized` (overlay/.nodigitize) artifact. Any in-scope figure that lacks those committed artifacts therefore **false-blocks** at the finalize coverage gate (`tools/check_figure_coverage.py`, exit→blocked), even when the model's reproduction state is sound. This hit **4 of 6** fix passes on 2026-06-15 (round 2). Three distinct flavors:

1. **Synthetic/derived panels** (itti_koch_niebur_1998 `dynamics`, ni_maunsell_2019 `mechanism`): a model-explanatory panel listed in `figures_in_scope` has NO paper figure, so `original` is unsatisfiable by nature (a `.nodigitize` marker only waives the *digitized* slot, not `original` — gate lines 47 vs 49-50). Passing such labels to the gate's `--figures` guarantees a block. **Lesson: don't pass derived/non-paper panels as coverage targets**; the gate's 3-view model (paper · digitized · render) doesn't fit them, and there is currently no "render-only, no paper source" marker.
2. **Never-digitized real figures** (rao_ballard_1999 figs 3,5,6 missing `digitized`): paper is available (fig 2 complete) but those figures were never digitized; fix mode can't digitize → needs a `from=extract` (or a standalone digitize) pass, not `fix`.
3. **Paywalled paper** (karklin_lewicki_2009 figs 1-4 missing `original`): genuinely no crop possible → real human/acquisition block, not a fix-mode artifact.

**How to apply:** before launching `from=fix`, run `check_figure_coverage.py <model> --figures <figs_in_scope>` first; if it's already incomplete, fix mode will exit blocked regardless of the work. Pass ONLY real paper figures with existing artifacts as the `figures` arg (drop `mechanism`/`dynamics`-type labels even when they appear in `figures_in_scope`). Route the three flavors differently: derived-panel → exclude or get a convention marker; never-digitized → `from=extract`; paywalled → human. Relates to [[rendered-output-panels-are-reproduction-targets]] (the derived panels ARE render targets, they just have no paper referent) and [[re-audit-after-every-model-change]].
