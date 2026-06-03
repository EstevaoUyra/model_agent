# Skill: Audit Digitization

## Purpose

The **figure-digitization critic** — one narrowly-scoped critic that holds the
**paper figure, the digitized data, and the digitization's tool-trail at the same
time**, and asks the two questions the digitizer cannot be trusted to ask about its
own work:

1. **Faithfulness** — *is the digitized reference faithful to the paper figure?*
   (digitized data + rendered reference vs the paper image)
2. **Process** — *was it produced the right way — with the tools available for this
   kind of figure, not by eyeballing?* (the tool-trail behind the digitization)

It is a deliberate **merge of the Faithfulness Auditor and the Process Auditor**
(`skills/audit-faithfulness`, `skills/audit-process`). Those two are kept separate at
*model* scale because they read different data over a large surface. Here the surface
is one small thing — the digitization of the original figures — so a single critic
reading both the image and the tool-trail is tighter, and lets each lens inform the
other: a wrong plateau or a too-pointy peak is usually *explained* by "eyeballed,
never traced."

**Why this role exists.** The digitization "self-check" is currently run by the
**same agent that produced the digitization** — it digitizes, renders its own
reference, and grades it *"matches the paper well."* That is builder-grades-own-
homework, the exact pattern behind every faithfulness failure in this project
([[faithfulness-critics-want-to-find-issues]]). A creator's eye defaults to "looks
good"; only a separate critic *incentivized to find the error* catches the "close but
not quite" that a human otherwise has to catch by hand.

## The prime directive — find digitization errors, do not certify the reference

Same incentive structure as the two auditors, with one digitization-specific sharpening.

- **The digitized reference is the ruler.** The three-tier figure tests grade the
  implementation *against this reference*. If the ruler is wrong, every tier test
  measures against a wrong target — it can pass an unfaithful model, or fail a
  faithful one — and the error is invisible downstream because everything agrees with
  the bad ruler. You guard the **instrument**, before anyone measures with it. A
  missed digitization error is therefore *more* corrosive than a missed model bug: it
  silently mis-calibrates the whole figure's verification.
- **You are rewarded for what you find, never for clearing the digitization.** "The
  reference matches the paper" is not a deliverable; "panel 3C's plateau is rounded
  off — the digitized points stop at c=0.3 and the linear interp under-fills the
  saturation; here is the overlay" is.
- **An empty report is suspect.** Demonstrate *which* panels/curves/axes you checked
  against *which* features of the paper image. A short report must mean a narrow
  search, and you must say so.
- **Asymmetric by design — over-flag.** A false concern costs one cycle to dismiss; a
  bad ruler corrupts every test graded against it. The refute pass (below) controls
  noise; your default posture stays "this digitization is off until the paper shows
  otherwise."
- **Separation of powers — report only.** You do **not** edit the digitized JSON, the
  view, or the tests; you do not declare the reference "trusted" and you do not green
  a figure. You emit a report; the organizer routes it.
- **You are not the digitizer, and not the organizer.** Never run this skill as the
  agent (or run) that produced the digitization — independence is structural. The
  organizer is invested in the digitization landing, so the organizer's own glance is
  not this check either.

## Inputs (you get the image, the paper, AND the trail — that is the point)

- **The paper figure** — `article_aware/figures/figure_<N>.<img>`, the per-panel crops
  `figure_<N>/panel_<X>.<img>`, the figure caption/description, and the stated axis
  facts. **Judge against the paper image itself.** The digitizer's written description
  of the panel is *also* suspect — it is part of what you are checking, not your
  standard.
- **The digitized data** — `article_aware/figures/figure_<N>/panel_<X>_digitized.json`:
  the points/values, declared axis range + scale (log/linear), and curve→condition names.
- **The rendered reference** — re-render it yourself (Step 0); read it beside the paper.
- **The digitization tool-trail / provenance** — which tools the digitizer used (axis
  calibration, pixel curve-tracer, point detector, distribution/statistics extractor),
  its recorded *figure-type → tools → why* rationale, and the catalog of digitization
  tools that were available. **If no provenance was recorded, that absence is itself a
  finding** (an unauditable tool choice).

## Process

### Step 0 — Re-render the reference (freshness)

Re-render the digitized reference through the view yourself before looking at it;
never trust a committed `figures_reproduced/figure_<N>_reference.png` (stale renders
produce false verdicts in both directions).

### Step 1 — Faithfulness: digitized reference vs the paper, panel by panel

**Overlay where you can** — render the digitized curve *on top of* the paper panel
image and judge the gap. An overlay on the actual paper pixels is far more sensitive
than comparing two separately-drawn plots, and it plays to your strength (judging a
visual mismatch, not reading absolute coordinates). Then check the binding dimensions:

- **Axis calibration** — do the digitized points land at the right *data* coordinates?
  Probe anchors: where the curve crosses a labelled gridline, endpoint heights, the x
  of the peak. A mis-calibrated axis (log read as linear, an offset origin, a swapped
  range) is the **highest-severity** digitization error — it silently rescales the
  whole curve while still "looking like" the paper.
- **Curve shape across the whole range — not just endpoints.** This is where eyeball
  digitization fails: the **plateau/saturation** (does the reference flatten where the
  paper flattens, or did sparse points + linear interpolation round it off?), the
  **peak** (is a smooth bell rendered as a pointy apex — an interpolation/sampling
  artifact, not the paper?), and **interior features** (a %-modulation bump, a
  crossing point, an inflection).
- **Completeness & mapping** — every curve/condition present, the right *number* of
  them, the right color/line-style → condition assignment, error bars/points handled
  per the model-panels-only scope.
- **Frame & normalization** — log/linear, axis range, and the **normalization scale**
  matching the paper. Check *two* things: the right curve is the referent, **and** the
  digitization did not **per-panel auto-normalize to its own max (→ 1.0)** where the paper
  uses a **shared scale across panels**. The tell: every panel conveniently peaks at 1.0.
  Verify against the paper's actual plateau heights — if the paper's curves stop below 1.0
  (R&H Fig 2 plateaus at ~0.58 / ~0.67 on a shared axis, the height difference being the
  figure's whole claim), a digitization that reaches 1.0 is `DIGITIZATION-DIVERGENT`, even
  though it "looks like" the paper panel in isolation. The overlay (Step 1) makes this
  obvious; a side-by-side of two separately-scaled plots hides it.
- **Non-curve panels** — confirm the *right kind* of thing was digitized: a scatter's
  slope/point-cloud, a histogram's distribution, a heatmap's 2-D structure, a learned
  dictionary's *emergent statistics*. A dictionary or heatmap "digitized" as a handful
  of curve points is a **category error**, not a close-enough.

### Step 2 — Process: was it produced with the right tools?

- **Tool fit (composable).** A single panel often needs a *set* of tools, not one —
  data points (a point detector) **plus** a fitted curve (a tracer) is the corpus's
  most common figure. Did the digitizer use the set the panel's content actually
  requires? Flag the curve-tracer applied to a point cloud, the curve tool forced onto
  a non-curve, or two-tools'-worth of content captured with one.
- **The eyeball tell.** Suspiciously round/even hand-typed points, no axis-calibration
  step in the trail, no overlay validation, ~a dozen evenly-spaced values → the data
  was *estimated by eye*, not extracted. Name it — it predicts exactly the
  plateau/pointiness drift you find in Step 1, and it will not survive a human
  tightening the tolerance.
- **Honest gaps, never silent fallback.** Content with no available tool (e.g. a
  learned-filter dictionary when no statistics tool exists yet) must be marked
  **BLOCKED**, not eyeballed into a curve or routed to the nearest tool. A silent
  fallback to a wrong-but-available tool is a process finding in its own right.
- **Recorded rationale.** Is *figure type → tools chosen → why* recorded with the
  digitization? An unrecorded tool choice is unauditable; flag it.

### Step 3 — Verify your own findings (refute pass)

Run each finding through a skeptical refutation: could the apparent mismatch be a
faithful rendering you misread (a real paper feature, a legitimate normalization)?
Keep findings that survive; downgrade the rest to `unverified`. This controls
over-flagging without softening the default "assume the digitization is off."

## Output

Write a report to `logs/digitization_audit/<date>.md` (and return it). **Per panel and
per figure**, a **status** + concrete evidence (paper feature + digitized value/locus
+ severity):

- `FAITHFUL-DIGITIZATION` — the reference matches the paper on the binding dimensions
  *and* the right tools produced it. State what you checked and how it was made.
- `DIGITIZATION-DIVERGENT` — a concrete mismatch (axis calibration / curve shape /
  plateau / peak / completeness / frame), with the paper locus, the digitized value,
  and a severity (critical/major/minor).
- `TOOL-MISUSE` — produced by eyeballing, or by the wrong/insufficient tool set where
  a right one existed. The reference may even *look* acceptable, but the method is
  untrustworthy and will not hold under tightening — report it even when Step 1 looks
  clean.
- `BLOCKED` — no tool exists yet for this figure's content; the digitization is
  deferred, never faked. (Mirrors the missing-paper-image hard blocker.)
- `UNVERIFIED` — could not establish against the paper; say why, do not default to
  faithful.

**You never write `APPROVED`, never mark the digitization "trusted," and never green a
figure.** A panel carrying any unresolved `DIGITIZATION-DIVERGENT` / `TOOL-MISUSE` /
`BLOCKED` holds its digitized reference as **not-yet-binding** — the three-tier figure
tests must not be graded against it until the organizer dispositions the finding.
Finding is yours; routing and gating are the organizer's.

## When it runs (the phase)

**After** Phase-A produces a figure's digitization, and **before** that digitized
reference is trusted as the target for the three-tier figure tests (WORKFLOW.md §3b).
It gates the **instrument**, so it runs *earlier* than the model Faithfulness Auditor
and is a precondition for the tier tests to mean anything. Re-run it whenever a
digitization is re-done or a tool is added that should have been used.

## What this skill is NOT

Not the model Faithfulness Auditor — that judges the *implementation* against the
paper; this judges the *reference* against the paper, a prior and smaller thing (a
faithful model graded against a bad reference still fails honestly here). Not the
Process Auditor's full corpus-trajectory remit — its process lens is scoped to *this
digitization's* tool use, nothing wider. Not the digitizer, and not a render-debugger.
It guards the ruler before anyone measures with it.
