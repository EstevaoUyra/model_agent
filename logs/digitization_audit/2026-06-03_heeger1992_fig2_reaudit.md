# Digitization Audit (RE-AUDIT) — Heeger 1992, Figure 2

- **Date:** 2026-06-03
- **Auditor role:** figure-digitization critic (audit-digitization). NOT the digitizer.
- **Target:** `models/heeger_1992` — Figure 2, **panel B** (model contrast-response
  family, one curve per sigma). Panel A is empirical (Ohzawa 1985), out of scope as a
  reproduction target.
- **Why a re-audit:** the prior audit (`2026-06-03_heeger1992_fig2.md`) flagged panel 2B
  **DIGITIZATION-DIVERGENT (major)** — the five same-colour curves had been traced
  per-column and `trace_darkest_in_band` MERGED them through the plateau, leaving
  byte-identical y across curves and 4-of-5 non-monotone curves; the shipping overlay's
  red line sagged off the top markers. The digitization was then revised (see the
  `PRIOR-DEFECT FIX` caveat in `panel_b_digitized.json`). This re-audit checks the fix.
- **Inputs read:** paper figure `article_aware/figures/figure_2.png` + `figure_2.md`;
  revised digitized JSON `figure_2/panel_b_digitized.json` (incl. `provenance`); paper
  panel crop `panel_b_crop.png`; shipping overlay `panel_b_overlay.png`.
- **What I did myself (not trusting committed renders):** rebuilt the calibration from the
  JSON anchors; re-rendered a fresh overlay of the JSON points on the paper crop;
  independently traced the top curve's plateau ink; zoomed the paper crop and the overlay
  at the feet and the plateau with `crop_region` (upscale 3-4); recomputed every digitized
  point against the analytic Naka-Rushton.

## Verdict

**Panel 2B: FAITHFUL-DIGITIZATION.** The prior merge/non-monotonicity defect is fixed. The
reference is the analytic Naka-Rushton family reconstructed from image-pinned anchors
(calibration + R_max + half-max=sigma), it is strictly monotone, the five curves stay
separated through the plateau, and every colored line sits on its own marker series in the
zoomed overlay. Tooling/process is the composition the skill prescribes for an
analytic-family panel.

## Faithfulness checks (paper vs reference)

- **Axis calibration — sound.** Rebuilt from JSON anchors: x ticks 1/10/100% map back to
  0.999 / 10.03 / 99.86; y ticks 1 / .1 / .01 map back exactly; corner sanity (col150,
  row200) -> (2.985%, 0.148) matches the JSON's stated (2.98%, 0.148). Independent
  half-max cross-check (curve crosses R_max/2 at c=sigma): digitized half-max contrasts =
  3.10 / 6.25 / 12.50 / 25.00 / 50.02% for sigma = 0.031 / 0.0625 / 0.125 / 0.25 / 0.5 —
  exact. This confirms BOTH the calibration and the c=%/100 fraction convention,
  independently of the curve fit.
- **Normalization — correct, and the right trap avoided.** Recorded **as drawn**: top
  curve plateaus at R_max≈0.6955, NOT 1.0; single shared y-scale across all five curves;
  no per-panel auto-normalization to 1.0. My independent trace of the top curve's plateau
  ink (sigma=0.031, x=20-90%) reads median y≈0.666, top edge≈0.698 — i.e. the paper ink
  saturates at ~0.67-0.70, matching R_max=0.6955 and contradicting any read of 1.0. This is
  the R&H-Fig-2-style trap the skill names, and it is avoided.
- **Curve shape across the full range — faithful, strictly monotone.** Every one of the 81
  digitized points equals R_max·c²/(σ²+c²) (c=%/100) to within max|resid| ≤ 1e-4 — the
  reference IS the analytic family. No plateau rounding, no pointy apex, no interior wiggle.
- **Plateau separation (the prior defect) — fixed.** Zoomed overlay at the plateau
  (x 18-100%, y 0.55-1.0): red (σ=0.031) on the filled-square top series, green (0.0625) on
  the open-square series just below it, blue (0.125) on filled triangles, orange (0.25) on
  open circles, purple (0.5) on filled circles still rising at 100%. Five distinct lines on
  five distinct marker series — no merge, no byte-identical y, no non-monotone dip.
- **Feet / low-contrast / off-scale handling — faithful.** Zoomed overlay at the feet
  (x 1.5-12%, y 0.01-0.35): each colored line tracks its marker series down the c²/σ²
  log-log straight-line regime. σ=0.25 and σ=0.5 enter from the 0.01 floor near ~3.3% and
  ~6.8%; points below the floor are OMITTED (off-scale, as the paper draws them), not
  clamped to 0.01. Correct.
- **Completeness & mapping — complete.** All 5 curves present; correct count; smaller σ =
  leftmost/highest, larger σ = rightmost/lowest; lateral-translate family intact.
- **x-range — reasonable.** Digitized data span 1.6-95%: leftmost = the y-axis box at
  ~1.6% contrast (not the x=1 tick), rightmost = last plotted marker ~95% (paper markers
  reach ~100%; a ~5% right-edge truncation, immaterial to the saturating shape). Minor,
  not a divergence.

## Process / tooling

- **Tool fit — correct composition.** `detect_plot_box` + `build_calibration` +
  `trace_darkest_in_band` (to ANCHOR R_max and half-max) + analytic reconstruction (to
  REPRESENT) + `crop_region`/`overlay` (to VALIDATE). For an analytic-family panel whose
  curves are the SAME colour and bunch at the shared plateau (the documented monochrome
  limitation of the tracer), this trace-anchor → reconstruct → overlay-validate composition
  is exactly what the skill prescribes. It is NOT eyeballing: the three free quantities the
  image determines (calibration, R_max, half-max=σ) are pinned to ink, and the result is
  validated back on the paper.
- **No eyeball tell.** Points are dense, log-spaced, strictly monotone, and exactly on an
  analytic curve — the opposite of the round-number, dozen-evenly-spaced eyeball signature.
- **Provenance — present and honest.** `figure_type`, `tools`, `tool_rationale`,
  `calibration` (with independent half-max cross-check), `model_params` (R_max fit method +
  residuals), `per_curve`, `normalization`, and `caveats` including an explicit, accurate
  account of the prior defect and how it was fixed. Auditable.

## Refute pass

- *Is analytic reconstruction a shortcut around the data?* No — the skill explicitly
  endorses reconstruct-to-represent for an analytic family, and it is validated on the
  paper ink (overlay sits on the markers; independent plateau trace ≈0.70; half-max=σ).
- *Could R_max be wrong (e.g. should be 1.0)?* No — independent plateau trace tops at
  ≈0.698 and the paper top curve sits well below the y=1 gridline; 0.6955 is right.
- *Could the curves still be subtly merged?* No — the zoomed plateau overlay shows five
  separated lines on five distinct marker series; the data are strictly monotone and not
  byte-identical between curves.
- The one residual (x-range truncated at 95% vs ~100%) survives only as a **minor** note,
  not a divergence.

## Disposition

Panel 2B carries **no** unresolved DIGITIZATION-DIVERGENT / TOOL-MISUSE / BLOCKED finding.
The prior major divergence is resolved by the revision. Routing/gating is the organizer's;
this report does not green the figure or mark the reference "trusted."
