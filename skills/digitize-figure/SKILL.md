# Skill: Digitize Figure

## Purpose

Produce the **digitized reference** for a figure panel — the curve/point data read off
the paper image that the three-tier figure tests (WORKFLOW §3b) grade the implementation
against. You are paper-aware (Phase A). You use the digitization tools to remove the
metric guesswork of eyeballing; you do **not** grade your own work — a separate critic
(`skills/audit-digitization`) audits it. Your job is the best tool-grounded digitization
**plus an honest, auditable record of how you made it.**

The reference is a **ruler**: every tier test measures against it, so a wrong reference
silently mis-calibrates the whole figure's verification. Digitize for correctness, record
your method, and hand it off — do not certify it yourself.

## Step 1 — classify the figure (capabilities, not slots)

Decide what the panel *is*, because it decides which tools apply and what "faithful"
means (see `proposals/figure-digitization-design-2026-06-03.md` for the full taxonomy):

- **Mode 1 — quantitative plot** (line/curve, scatter+regression, bar, histogram, polar):
  recoverable (x, y). The tools below apply.
- **Mode 2 — image/structure** (learned-filter dictionary, heatmap, RF map, image patches):
  there is **no curve to extract** — faithfulness is *emergent statistics* (e.g. Gabor-ness,
  orientation/frequency coverage), and a stochastic output must **never** be pixel-matched.
  These tools do NOT apply. If no Mode-2 tool exists yet → **BLOCKED**, do not force a curve.
- **Mode 3 — schematic** (circuit/architecture diagram, stimulus layout): no data — use the
  structural checklist, no digitization.

A panel often needs a **set** of Mode-1 capabilities, not one — e.g. data points (a point
detector) *and* a fitted curve (a tracer). Compose them. **Never** route content to a
wrong-but-available tool (a dictionary through a curve tracer is a category error) — a
missing capability is **BLOCKED**, surfaced explicitly.

## Step 2 — digitize (Mode 1) with the tools

`from neuromodels.framework.figures import build_calibration, detect_plot_box, trace_darkest_in_band, overlay, resample_pchip`
Read each tool's docstring first.

1. **Calibrate.** `detect_plot_box` gives a starting hint; **verify it** (its top is often
   open on scans, and a neighbouring-panel sliver can fool the left edge). VIEW the panel,
   read the tick DATA values at their pixel positions, and `build_calibration` (linear or
   log per axis; build a separate calibration for a right-hand axis). Sanity-check on a
   known point.
2. **Trace.** `trace_darkest_in_band`, one row-band per curve. **Respect its documented
   limitation**: it has no colour/style channel, so it cannot split two same-colour curves
   where they overlap — trace the **envelope** there and split only where they visibly
   separate; isolate a dashed curve by its own region. If two curves cannot be separated
   anywhere, say so — do **not** invent a confident split.
3. **Normalization — match the paper's scale** (binding; see `skills/extract-figure`
   "Normalization convention"). Read the curves' ACTUAL heights. If the paper's curves do
   not reach 1.0, **yours must not either**; never per-panel normalize to max where the
   paper uses a shared scale across panels.
4. **Represent smoothly.** Sample peaks/turns densely and use `resample_pchip` (monotone
   cubic) so bells render rounded and plateaus stay flat — not the pointy apex linear
   interpolation gives.
5. **Validate** with `overlay`: render your curves on the paper panel, VIEW it, confirm
   they track. (One validation pass — not an iteration loop, unless the brief says so.)

## Step 3 — write the digitized JSON **with a provenance block**

Write `article_aware/figures/figure_<N>/panel_<X>_digitized.json` with the data **and** a
`provenance` block — this is what makes your method auditable; **an absent provenance block
is itself an audit finding.** Schema:

```json
{
  "panel": "2A", "figure": 2, "description": "...",
  "x_variable": "...", "x_scale": "log", "x_range": [0.01, 1.0],
  "curves": { "<name>": { "axis": "left|right", "y_range": [..], "points": [[x,y], ...] } },
  "provenance": {
    "figure_type": "line/curve CRF, log-x",
    "tools": ["build_calibration", "trace_darkest_in_band", "overlay", "resample_pchip"],
    "tool_rationale": "why this set for this panel type",
    "calibration": { "x": [[col, val], ...], "y_left": [[row, val], ...],
                     "y_right": [[row, val], ...], "x_scale": "log" },
    "per_curve": { "<name>": "traced | enveloped where coincident (x<0.025) | interpolated through crossover" },
    "normalization": "paper shared sub-1.0 scale; attended plateau ~0.94, NOT pinned to 1.0",
    "caveats": ["no numeric x ticks — x_range from frame", "..."]
  }
}
```

Be honest in `per_curve` and `caveats`: where you traced the envelope, interpolated through
an occlusion, or could not separate curves, **say so**. The critic will check these against
the pixels; an understated caveat is worse than an admitted limit.

## What this skill is NOT — and the handoff

- **You never grade your own digitization faithful**, never write APPROVED, never mark the
  reference "trusted" or binding. Produce it, record how, hand to `audit-digitization`. (An
  agent that draws *and* blesses its own reference is back to grading its own homework — the
  failure this split exists to break.)
- Not the model implementer, not the figure-description writer (`extract-figure`), not the
  Mode-2/Mode-3 path. If the panel is not a Mode-1 plot, stop and route it, don't force it.
