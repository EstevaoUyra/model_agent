# Digitization audit — hara_gardner_2016, Figure 4

- **Date:** 2026-06-04
- **Auditor role:** figure-digitization critic (independent; NOT the digitizer, NOT the organizer)
- **Paper:** Hara, Pestilli & Gardner (2016), PLOS Comput Biol, Fig. 4 (human behavioural d′ vs motion coherence, Naka-Rushton fits; valid vs invalid cue; Narrow Focus = A, Broad Focus = B).
- **Inputs read:** `figure_4.png`, `figure_4.md`, `panel_{A,B}_digitized.json` (incl. `provenance`), the shipped `panel_{A,B}_overlay.png`.
- **Fresh re-render:** rebuilt each panel's calibration from the JSON anchors and re-rendered the overlay myself (`.agent_tmp/fig4_audit/overlay_aligned.png`); it matches the committed overlays (not stale).
- **Adversarial crops** in `.agent_tmp/fig4_audit/`: paper-only and overlay crops of the mid-rise, the plateau, the feet, plus paper-vs-overlay side-by-side of the A-invalid plateau and the B-invalid kink.

## Scope note
Fig 4 is human behavioural data + Naka-Rushton fits, OUT OF SCOPE for the deterministic
model (A-006). No tier test asserts on it; it exists only to DEFINE the two diagnostic
effects (response gain, coherence gain) the in-scope Fig 7/8 curves are read through. This
bounds severity: a curve-shape defect here does not corrupt a graded ruler, but the file is
still presented as a faithful reference, so I judge it as one.

---

## Per-panel verdicts

### Panel A — Narrow Focus — `DIGITIZATION-DIVERGENT` (major, curve shape)

**Axis calibration: FAITHFUL.** Predicted tick pixels reproduce the labelled ticks
(x: 1.6/6.4/25.6/100% → 300.8/672.9/1045.0/1410.7 px, even log spacing; y: 0/1/2/3 →
1201/930/658/387 px). Feet land on d′=0, plateaus land on the paper ink. No calibration shift.

**valid (blue): minor.** Tracks the blue sigmoid well across foot, rise, and plateau
(≈3.3–3.4). Small non-monotone wiggles (≤~0.1 d′) where the tracer grazes the fused
subject-mean markers at ~13% and ~26%, and a +0.20 d′ step at 11→12% in the rise. Cosmetic.

**invalid (red dashed): MAJOR — spurious humps/trough the Naka-Rushton fit does not have.**
The paper's red dashed *fit* is a smooth, monotone, gently-saturating sigmoid (verified on a
paper-only crop, `A_invalid_top_PAPER.png`). The digitized "fitted" curve instead rides the
*subject-mean data markers* and carries excursions the fit cannot have
(`A_invalid_top_OVERLAY.png`):
- +0.249 d′ jump at 26→28% (0.958→1.207),
- +0.385 d′ near-vertical jump at 43→46% (1.766→2.151), overshooting ABOVE the red fit,
- then a **decrease** 53→61% (2.254→2.095, −0.16 over two steps) = a non-monotone trough,
- a second small hump approaching 100%.
Worst local gap from the ink ≈ 0.2–0.4 d′. This **contradicts the provenance's own claim**
that `curves` = the fitted line "NOT the markers," and far exceeds its stated
"<~0.05 d′ residual wiggle" caveat — the real excursions are 4–8× that.

### Panel B — Broad Focus — `DIGITIZATION-DIVERGENT` (minor→moderate, curve shape)

**Axis calibration: FAITHFUL** (x: 1.6/6.4/25.6/100% → 1964/2336.5/2709/3075.2 px; y shared
with A). Feet and plateaus land on the ink.

**valid (blue): minor.** Small dip below the blue fit at the ~13% marker; otherwise on-ink.

**invalid (red dashed): moderate.** A flat shelf/kink around the ~13% marker followed by a
+0.243 d′ step at 14→15% (0.358→0.601), where the paper's red fit rises smoothly
(`B_invalid_kink.png`). Same tracer-through-markers mechanism as A, smaller magnitude.

---

## Process lens — method is sound; NOT eyeballed; NOT tool-misuse

- **Provenance present and complete**: `figure_type`, `tools`, `tool_rationale`, two
  calibration anchors/axis (log-x), `per_curve` method, `normalization`, `caveats`.
- **Tool fit correct**: Mode-1 quantitative plot. `build_calibration` + colour-pre-separated
  `trace_darkest_in_band` + `resample_pchip` + `overlay`/`crop_region` is the right composable
  set for a two-condition sigmoid with a fused-marker scatter. No category error.
- **Not eyeballed**: 60 dense, non-round points per curve; calibration step recorded; overlay
  validation shipped. The "round-numbers / dozen-evenly-spaced-values" eyeball tell is absent.
- **Normalization correct**: native d′ scale (0..~3.4), shared across panels, NOT
  per-panel-normalized-to-1.0. The valid/invalid plateau-height difference (the response-gain
  claim) is preserved.

So this is **not** `TOOL-MISUSE`. The divergence is a **known limitation of the tracer**
(`trace_darkest_in_band` has no marker channel; where the fitted line and the fused
subject-mean markers/error-bars overlap, the band is pulled onto the marker and PCHIP carries
the excursion through). The digitizer acknowledged the mechanism in caveats but **understated
its magnitude**; the fix is to trace the *envelope/fit through* the markers (bridge across
them) rather than let the band graze them — a validation gap the digitizer's own
"trust your eye over the tool" step should have caught on the A-invalid plateau.

## Refute pass
- Could the humps be a real paper feature? No — the paper's red dashed line is a Naka-Rushton
  *fit* (smooth monotone by construction), and the paper-only crop shows no hump/trough. The
  excursions coincide exactly with subject-mean marker positions → tracer artifact. Survives.
- Could it be a normalization/calibration illusion? No — calibration verified against ticks;
  feet/plateaus land on the ink; the defect is local shape only. Survives.
- Do the diagnostics still hold? Yes — response gain (valid d′max > invalid: A 3.39>2.30,
  B 2.94>2.23) and coherence gain (valid c50 < invalid: A 11.4%<28.3%, B 20.0%<24.6%, larger
  separation in Narrow A than Broad B) all survive the wiggles. The figure's *qualitative*
  purpose is intact; its *curve shape* is not faithful.

---

## Figure verdict

**Figure 4: DIGITIZATION-DIVERGENT (major on A-invalid, moderate on B-invalid; calibration
and diagnostics faithful).** The reference is directionally faithful on the two effects it
exists to define, but both invalid curves carry spurious humps/kinks/troughs (0.15–0.4 d′)
that the paper's smooth Naka-Rushton fits do not have, from the tracer grazing fused
subject-mean markers. Method and provenance are otherwise sound (no eyeballing, no tool
misuse, calibration correct).

**Routing (organizer's call, not mine):** Because Fig 4 is out-of-scope reference-only and no
tier test grades against it, the divergence does not mis-calibrate any graded ruler — but the
panels should not be presented as a faithful curve reference until the A-invalid plateau
(43–61%) and B-invalid 13–15% kink are re-traced through the markers (envelope), or the file
is explicitly downgraded to "diagnostics-only, curve shape approximate." I do not edit the
JSON, the view, or any test, and I do not green the figure.
