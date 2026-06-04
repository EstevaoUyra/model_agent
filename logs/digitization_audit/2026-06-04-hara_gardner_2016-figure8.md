# Digitization audit — hara_gardner_2016 Figure 8

Date: 2026-06-04
Auditor role: figure-digitization critic (audit-digitization skill). NOT the digitizer.
Branch: audit/figure5-digitization

Figure 8: two d′-vs-Motion-Coherence panels (log-x, linear-y 0..3.5) for the extended
normalization models NMoA+ciN (solid) / NMoA+cdN (dashed), blue=valid green=invalid.
- Panel A "Narrow Focus" (κ=15)
- Panel B "Broad Focus" (κ=0.5)

Source image: `article_aware/figures/figure_8.png` (3300×1628).
Digitized refs: `figure_8/panel_A_digitized.json`, `panel_B_digitized.json`.

## What I checked and how

- **Re-rendered my own overlay** (independent script, contrasting magenta=blue/orange=green
  + ×-markers for data points), each panel drawn with its OWN calibration on the full
  paper image, frame-matched to 3300×1628 so the JSON pixel calibration applies.
  (`.agent_tmp/audit/audit_ov_full.png`)
- **Calibration anchors verified on the paper pixels**: drew the y-anchor rows
  (1378/1072/762/454 → d′ 0/1/2/3) and x-anchor cols (panel A 311/702/1096/1482, panel B
  2043/2434/2828/3215 → 1.6/6.4/25.6/100%) onto the paper. All land exactly on the
  gridlines/tick labels (`axis_marked.png`). Round-trip error <0.2% in x, <0.01 d′ in y.
  Log-x / linear-y scales correct.
- **crop_region zooms** at the binding features: green plateau, blue plateau, green rise
  (the prior-audit defect region), and the foot — both panels.
- **Independent re-trace** of the green line via my own RGB color-mask + per-column
  thin-run analysis (marker blobs excluded), at 25.6/51.2/80/88-96%, to re-measure the
  solid/dashed midline from scratch.
- **Process / provenance**: read the provenance block + the digitizer's trace artifacts
  (`.agent_tmp/digit8/traces.npz` = 547–814-column dense pixel traces per curve;
  `knots.json` matches the JSON knots).

## Panel A (Narrow Focus) — FAITHFUL-DIGITIZATION

- Blue (valid) midline tracks the blue solid/dashed bundle through the whole range;
  endpoint ~3.31 at 100%, plateau hugs the bundle (crop `c2_A_bluetop.png`). Foot:
  blue marker ~0.16 above the curve, as in paper.
- Green (invalid) midline runs centrally between green solid (UPPER) and dashed (LOWER)
  on the plateau — orientation matches the JSON's "solid upper / dashed lower" claim.
  My independent retrace confirms the split: 80% solid≈2.30 / dashed≈2.12 → mid≈2.21
  (digitized 80%≈2.225); 92–96% solid≈2.37 / dashed≈2.03 → mid≈2.20 (digitized
  endpoint 2.23). Green rise (10–40%) rides the curve centre, NOT low — the prior
  audit's "green sits 0.15–0.33 low" defect is fixed (crop `crop_A_greenrise.png`).
- Completeness: 2 colours present; line-style split documented as a deliberate
  per-column midline; data points recorded separately; error bars explicitly excluded.

Minor note (not a finding): at the 25.6% marker column my fringe retrace read ≈1.18 vs
the digitized PCHIP-bridge value 1.15 (a 0.03 d′ difference at a marker-occluded column;
within line width, and the caveat already flags 25.6% as a bridge). Both sit far above
the prior-defect ≈0.84.

## Panel B (Broad Focus) — FAITHFUL-DIGITIZATION

- Blue midline tracks the bundle; endpoint ~2.90 (crop `c2_B_bluetop.png`).
- Green midline central between dashed (UPPER) and solid (LOWER) — OPPOSITE orientation
  to panel A, exactly as the JSON states. My retrace confirms: 80% lines at 2.19 / 2.35
  → mid 2.27 (digitized 80%≈2.274); 88–92% upper line ≈2.40–2.41 (matches the JSON's
  "dashed reaches ~2.41 near 90%"), digitized endpoint 2.32. Green rise tracks centre.
- Response gain (blue 2.90 > green 2.32) and the small broad-focus coherence gain both
  read true on the overlay.

## Process — FAITHFUL (not eyeballed)

- provenance block complete on both panels: figure_type, tools
  (color_mask → per-column run/midline → build_calibration → trace → resample_pchip →
  overlay → crop_region), tool_rationale (monochrome tracer can't split blue/green nor
  solid/dashed → RGB mask + per-column run grouping with marker/error-bar rejection),
  calibration anchors, per_curve method, normalization, caveats.
- Tool fit correct: a colour figure with two line styles + markers needs exactly this
  composite (mask + run-split + tracer + pchip + overlay), and it was used.
- NOT eyeballed: dense pixel traces (547–814 cols/curve) exist in the digitizer's
  tmp; knots match the JSON; point values are non-round (0.054, 0.403, 2.379…).
- Normalization honest: native d′, shared 0..3.5 y-axis across panels, identical
  y-calibration — NOT per-panel auto-normalized to 1.0. Asymptotes read at their real
  heights (blue 3.31/2.90; green-mid 2.23/2.32), which is the figure's response-gain claim.

## Refute pass

- The 25.6%-A 0.03 d′ gap → marker-column fringe vs PCHIP bridge; within line width;
  downgraded to non-finding.
- "Every panel peaks at 1.0" auto-normalization tell → absent; heights are native and
  differ across panels/colours. No finding.
- Split-orientation flip between panels (solid-upper in A, dashed-upper in B) could look
  like an inconsistency, but my from-scratch retrace reproduces exactly this flip on the
  paper pixels — it is a real paper feature, not a digitization error.

## Verdict

**FAITHFUL-DIGITIZATION** for both panels (8A, 8B). Calibration anchors correct on the
paper; curve shapes, plateaus, rises, and feet track the paper bundle midline; the
solid/dashed split magnitude and per-panel orientation match an independent retrace;
native shared-scale normalization preserves the response-gain heights; produced by a
recorded color-mask + per-column-midline + PCHIP pipeline with real dense traces, not by
eye. No DIGITIZATION-DIVERGENT / TOOL-MISUSE / BLOCKED findings.

(Per the skill I do not green the figure or mark the reference "trusted" — that routing
is the organizer's. This report states the reference is faithful on the binding
dimensions I checked.)

Artifacts: `.agent_tmp/audit/` (audit_ov_full.png, axis_marked.png, c2_*_*.png,
crop_*_greenrise.png, crop_A_foot.png, retrace scripts).
