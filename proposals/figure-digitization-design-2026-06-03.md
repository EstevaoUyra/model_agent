# Figure digitization — design notes (2026-06-03)

Status: **design-only, not built.** This records the shape of the figure-digitization
system we converged on while hardening the reynolds_heeger_2009 worked example, before
building tools. STATUS.md remains canonical on what exists; nothing here is built yet
except the reynolds_heeger Mode-1 prototype (digitized references + three-tier tests +
Phase-A view) and the `audit-digitization` skill prompt.

## The problem this addresses

The worked example proved the three-tier design works for line plots, but surfaced two
weaknesses the human caught (the agents did not):

1. **The digitization itself is eyeballed and self-graded.** The agent *looks* at the
   paper panel (Read tool = VLM) and hand-types ~a dozen `[x,y]` points; there is **no
   pixel extraction, no axis calibration, no tracing** — and the same agent then grades
   its own digitization "matches the paper well." Result: references that are "close but
   not as good as we want" (Figs 2/3/4 plateaus too soft; 5/6/7 peaks too pointy — the
   latter compounded by linear interpolation between sparse points).
2. **A line-plot pipeline does not cover the corpus.** A curve tracer is the right tool
   for ~70% of figures and the *wrong* tool — or a category error — for the rest.

## Figure-type taxonomy (corpus survey, 27 models)

Three comparison **modes**; within them ~11 types. The mode decides what "faithful"
even means.

| Mode | Types | ~Prevalence | What "faithful" means | Example models |
|---|---|---|---|---|
| **1 · Quantitative plot** (recoverable x,y) | line/curve (CRF, tuning, psychometric, time-series, density); **bar**; **histogram/distribution**; **scatter+regression**; **polar** | ~70% | type-specific (see contract) | nearly all; hara, hermann, heeger, pestilli, boynton, doostani, spratling_2010 |
| **2 · Image / structure** (no curve to extract) | **filter/basis dictionary**; **heatmap / 2-D matrix**; single RF / spatial map; natural-image patches / reconstructions | ~20% | structural / **emergent statistics** | olshausen, bell_sejnowski, rao_ballard, zhu_rozell, verhoef, spratling_2012, karklin |
| **3 · Schematic** (no data) | circuit / architecture diagram; stimulus layout; trial timeline | ~5–10% | topology + iconography only | R&H fig1, heeger fig1, karklin fig1, reynolds_chelazzi, ni_ray, denison, carrasco |

Notes that matter for design:
- **Three models have no figure image at all** (karklin_lewicki_2009, rozell2008,
  spratling_2012) → BLOCKED under the missing-image hard-blocker rule; record, don't skip.
- **Mode-2 stochastic outputs** (learned dictionaries) must be compared by *emergent
  statistics* (Gabor-ness, orientation/frequency coverage), **never pixel- or
  point-matched** — the dictionary is order-arbitrary, so a faithful reproduction has
  *different* filters with the *same* statistics. A pointwise shape-check here would fail
  a correct reproduction and could be "fixed" by overfitting. This is the biggest blind
  spot if we generalize from R&H.

## Tools are composable capabilities, not slots

Figures do not map to one tool each. A single panel routinely needs a **set** of tools
— data points (a point detector) **plus** a fitted curve (a tracer) is the most common
figure in the corpus. So:

- The agent **classifies the panel's content and picks the *set* of capabilities** it
  needs, composing their outputs. The taxonomy names capabilities, not mutually-
  exclusive buckets.
- **Tool selection is a recorded, auditable decision:** *figure type → tools chosen →
  why* travels with the digitization. A reviewer challenges the *choice*, not just the
  result.
- **No tool ⇒ BLOCKED, never silent fallback.** The failure mode to design out is the
  agent reaching for the curve tracer on a filter dictionary because that is the tool it
  has. A missing capability surfaces as an explicit gap, exactly like a missing paper
  image — it must not quietly route to the wrong tool or back to eyeballing.
- The toolbox grows incrementally (curve capabilities first — highest coverage), but the
  **taxonomy is registered up front** so each type is a named slot and the empty slots
  are visible holes.

### Candidate Mode-1 capabilities (highest-leverage first)
- **Axis calibration** — VLM supplies pixel coords of known ticks; tool builds the
  pixel→data transform (affine / log-linear / polar). Removes the largest eyeball error.
- **Curve tracer** (`trace_darkest_in_band`) — VLM gives a row-band to isolate a curve;
  tool returns the precise per-column pixel (PIL+numpy; no new deps). **Limitation, by
  design:** it separates only by position + darkness — no colour/style channel — so on a
  grayscale scan it **cannot split two same-colour curves where they overlap** (a
  contrast-gain pair sits ~coincident). Reliable for single/well-separated curves,
  envelopes, plateaus, and style-distinct (dashed) curves; degrades to "trace the
  envelope" on monochrome overlap. The limitation + how-to-use is documented in the
  function docstring (point of use) and the `audit-digitization` critic's process check.
- **Point / scatter detector** — blob detection → cloud; report slope + R, not points.
- **Bar / histogram reader** — rectangle edges → per-category heights / bin counts.
- **Smooth / parametric representation** — PCHIP (monotone, rounds peaks, fixes
  pointiness) or fit the known family (Naka-Rushton CRF, Gaussian/von-Mises tuning) → a
  smooth reference with a correct plateau, recovering the paper's few generating params.
- **Overlay validator** — render the candidate on the paper image for the critic.

### Mode-2 capabilities (different tool, do not reuse Mode-1)
- Dictionary statistics (Gabor-fit; orientation/frequency/size distributions);
  heatmap structural/gradient similarity; RF-profile comparison. **Statistical, not
  pointwise; tolerant of permuted/stochastic output.**

### Mode-3
- Structural checklist only (the existing VLM-checklist approach is correct here — R&H
  fig1 is Mode 3, and keeping it a checklist was the right call). No digitization.

## Per-mode comparison contract (what the tier tests grade)

| Type | Faithful quantity (the tier tests' target) |
|---|---|
| line/curve | pointwise shape within tolerance across the range (+ plateau, peak, interior features) |
| scatter+regression | regression **slope / R / intercept** — not individual points |
| histogram/distribution | median / spread / shape (e.g. kurtosis, sparsity) |
| bar | per-category heights |
| polar | radius–angle profile |
| heatmap / 2-D matrix | iso-contour shape / gradient structure |
| filter/basis dictionary | emergent **population statistics**; explicitly NOT pointwise |
| schematic | element presence + arrangement (checklist) |

The "dozen-point shape check" we built is **one** Mode-1 metric (the line/curve row),
not the universal one. Each row needs its own test generator; the soft/hard/qualitative
tiering wraps whichever metric the type calls for.

## The separate critic — never self-grade

The digitization must be checked by a **separate critic, incentivized to find errors** —
not the digitizer, not the organizer (both invested). Skill: **`skills/audit-
digitization`**. It is a *merge* of the Faithfulness and Process Auditors, justified by
the small scope (only the digitization of original figures), doing both jobs at once:

1. **Faithfulness** — digitized reference + rendered overlay vs the paper image, panel
   and figure level (axis calibration, curve shape, plateau, peak, completeness, frame;
   right *kind* of comparison for the type).
2. **Process** — did the digitizer use the right *tool set* for the type, or eyeball it?
   Is the tool-choice rationale recorded? Content with no tool → BLOCKED, not faked.

It guards the **ruler** before anyone measures with it: a wrong digitized reference
silently mis-calibrates every tier test graded against it, so this check is *prior* to
the model Faithfulness Auditor. It is report-only and never greens a figure; a panel
with an unresolved finding holds its reference **not-yet-binding**. See the skill for
the prime directive, statuses (`FAITHFUL-DIGITIZATION` / `DIGITIZATION-DIVERGENT` /
`TOOL-MISUSE` / `BLOCKED` / `UNVERIFIED`), and phase.

## Open items before building

- Register the taxonomy + per-mode contract into WORKFLOW §3b (currently §3b is Mode-1
  shaped — generalize it to "classify → pick capability set → type-specific tiers").
- Decide the v1 toolbox scope. Pragmatic v1 = Mode-1 axis-calibration + tracer +
  PCHIP/parametric + overlay validator (unblocks ~70%); Mode-2 dictionary-statistics is
  a distinct second build; Mode-3 reuses the checklist.
- Wire `audit-digitization` into the figure flow as the precondition gate for the tier
  tests, and stop the digitizer from running its own "self-check."
- The dozen-point shape check is the comparison granularity for line/curve, **not** the
  digitization density — digitization can be as dense/smooth as the tool produces.
- **Fix the view's normalization.** The R&H view's `norm_pair` rescales each panel to its
  own max (→ 1.0), which violates the paper's **shared** scale — R&H Fig 2 plateaus at
  ~0.58 / ~0.67 on one axis, and that height difference *is* the contrast-gain-vs-
  response-gain claim. The digitization inherited this and pinned both panels to 1.0; the
  tracer + overlay caught it, the self-check did not. The rule was already explicit
  (`extract-figure`: "must match the paper"); the case sharpened it to "reproduce the
  paper's scale; if the paper's curves don't reach 1.0, yours must not either; never
  per-panel auto-normalize." The view (Phase-A-owned) must carry the paper's scale.
