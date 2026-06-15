# Figure-artifact skill corrections — fixing the README issues at the source

_2026-06-15. The per-model README issues (missing paper crops, missing digitized overlays, renders in
the wrong dir, verbose status) are symptoms; the cause is that the skills that PRODUCE figure artifacts
don't pin the canonical paths the coverage gate + generator read. Each agent improvised, so every model
drifted. This fixes it per-skill._

## The single contract (already exists, under-referenced)

`tools/check_figure_coverage.py` defines what every in-scope figure N must commit:

| view | canonical committed path |
|---|---|
| **paper crop** (original) | `article_aware/figures/figure_<N>.{png,jpg,jpeg}` |
| **digitized** (overlay) | `article_aware/figures/figure_<N>/` with ≥1 `*overlay*`/`*digiti*` file — OR a `article_aware/figures/figure_<N>.nodigitize` marker |
| **implementation** (render) | `figures_reproduced/figure_<N>.{png,jpg}` (committed; `figure_outputs/` is gitignored scratch) |

The generator (`tools/build_model_readme.py`) and the gate both read these via `git ls-files`. The skills
must PRODUCE exactly these. Today they don't say so.

## Per-skill corrections

### digitize-figure — the biggest gap (causes issues 2, 3, 4)
- **Symptom:** zhu_rozell_2013 committed no overlays at all; zhang_1996/rozell2008 put overlays at
  ad-hoc paths (`figure_outputs/figure_6/A_overlay.png`, `figure_2/panel_a_overlay.png`); zhang fig 6 has
  no paper crop.
- **Cause:** the skill writes `panel_<X>_digitized.json` and renders an overlay only to *validate* it —
  it never mandates **committing** the shipping overlay at the canonical path, nor owns the figure-level
  paper crop, nor the `.nodigitize` marker.
- **Correction (implemented):** add a "Canonical committed artifacts" section — commit the shipping
  overlay at `article_aware/figures/figure_<N>/overlay_<panel>.png`, ensure the figure-level paper crop
  at `article_aware/figures/figure_<N>.png`, and write a `figure_<N>.nodigitize` marker for genuinely
  non-digitizable / illustrative panels (honest, not silently absent). Verify with
  `check_figure_coverage.py` before handoff.

### implement — renders land in gitignored scratch (causes the "Implementation —" stubs)
- **Symptom:** zhang/rozell/pfister committed renders under `figure_outputs/` (or left them only in the
  gitignored dir), so the README couldn't show them until the generator was taught the alt-path.
- **Cause:** the implement skill specifies no render destination; only the finalize stale-sweep does.
- **Correction (implemented):** the skill must render every in-scope figure to a **committed**
  `figures_reproduced/figure_<N>.png`, never only to `implementation/figure_outputs/` (gitignored scratch).

### extract-figure — assumes the paper crop "already exists"
- **Cause:** treats `article_aware/figures/figure_<N>.jpg` as a given input; nobody is accountable when
  it's missing or mis-pathed (zhang fig 6).
- **Correction (implemented):** note the canonical paper-crop requirement + cross-ref the contract;
  if the crop is absent, flag it (don't silently describe a figure with no committed image).

### update-state — verbose status (issue 5)
- **Cause:** the backfill/author step transcribed the prior README verbatim into `status_narrative`
  (zhu: 4384 chars).
- **Correction (implemented):** reinforce the caps — `status_narrative` ≤300 words, `model_summary`
  ≤200, figure `note`s tight; summarize, never paste the old README wholesale.

### audit-digitization — light
- **Correction (implemented):** verify the canonical artifacts exist at the contract paths (not just
  that *an* overlay looks right), so a mis-pathed/absent committed view is a finding.

## Validation
Spawn one agent running the corrected **digitize-figure** on **zhang_1996 figure 6** (missing paper crop
+ non-canonical overlays). Pass criterion: it commits `article_aware/figures/figure_6.png` (or flags the
source as genuinely unavailable) and the overlay at the canonical path / a `.nodigitize` marker, and
`check_figure_coverage.py models/zhang_1996 --figures 6` then reports figure 6 complete.
