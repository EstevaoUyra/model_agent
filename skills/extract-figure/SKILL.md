# Skill: Extract Figure

## Purpose

Given a figure from a computational neuroscience paper, produce two artifacts:

1. `article_aware/figures/figure_N.md` — a citation-grounded description of the figure's
   purpose, simulation parameters, per-panel expected behavior, and key inter-panel
   relationships. Think of it as an overpowered figure caption.

2. `article_aware/figures/figure_N_visual_checklist.md` — a panel-by-panel checklist of
   structural features that a reviewer (who has NOT read the paper) can use to verify that
   the generated **model simulation output** matches the paper's intended model result.

These two files are complementary: the `figure_N.md` explains *why* each model-generated
panel looks the way it does (grounded in model equations and citations); the checklist
specifies *what* to look for when doing a visual comparison of generated simulation output.

---

## Inputs

- `article_aware/figures/figure_N.jpg` — the paper figure image
- `paper/extracted_text.md` — the full extracted paper text, including verbatim figure
  captions, equations, Table 1 parameters, and qualitative claims
- `article_aware/spec/citations.yaml` — citation IDs to reference from the figure.md
- `article_aware/spec/model_spec.yaml` — simulation parameters and equations for cross-reference

---

## Process

### Step 1 — Read the verbatim caption before looking at the image

Find the figure's verbatim caption in `paper/extracted_text.md`. Read it carefully before
examining the image. Captions often contain encoding information that is not derivable from
the image alone — for example, "midgray indicates a value of 1" for an attention field
colormap. Missing this step leads to misinterpreting what you see.

Also read the per-figure simulation protocol entry in `extracted_text.md` and the relevant
row(s) in Table 1 for the parameter values.

### Step 2 — Establish coordinate and encoding conventions explicitly

Before describing anything, write down:

- **Axes**: what do the x and y axes represent?
- **Coordinate reference**: if the figure has no axis tick marks, establish a reference
  using the protocol values (e.g., "left stimulus at x = −10, right at x = +10 per the
  figure protocol"). State that the figure has no labels and you are using protocol values.
- **Colormap encoding**: does zero map to black? Is the baseline a non-zero value encoded
  as midgray? Is the scale normalized? Derive this from the caption, not from assumption.

### Step 3 — Read the figure image panel by panel

Look at each panel carefully. For each one:

- Describe what you **literally see**, not what you expect from the model equations.
- Note both **presence** (bright regions, peaks, bands) and **absence** (dark regions,
  gaps, separations).
- Use **intra-figure comparisons** where possible — these are more robust than absolute
  claims. Examples: "stripes in R are narrow, comparable to E, not as broad as S";
  "right band in S is brighter than left band".
- **Quantify extent concretely** when you can read it from the image — "approximately
  50% of the vertical extent" is more useful than "a substantial portion." A reviewer
  needs something to check against.
- Be explicit about uncertainty. If a feature is ambiguous in the image, say so rather
  than resolving it by assumption.

**For schematic/inset panels:** treat them as encoding the simulation parameters, not as
decorative art. Grating orientations reflect the stimulus orientation parameter; grating
or stimulus positions reflect the position parameters; circle sizes reflect RF, attention
field, and stimulus size parameters. If those parameters changed, the schematic would
change. Write checklist items that verify the schematic is consistent with the parameters.

**For sigmoid / contrast-response curves:** always describe the **inflection point**
explicitly — it carries the most diagnostic information.
- Contrast gain = inflection point shifts **left** (lower contrast at half-max).
- Response gain = inflection point shifts **up in y** at the same x position; the
  saturation level is higher, not the contrast at half-max.
Describe changes in these terms rather than vague "shift."

**Distinguish monotonically decreasing from peaked:** if a curve starts high and ends
low, verify whether it has a local maximum in the middle or simply decreases throughout.
These are different shapes with different implications — do not assume a peak exists.

**Do not infer curve shape from model equations — read the figure directly.** A formula
may have its theoretical maximum at c=0, but if the plot's x-axis starts at a nonzero
contrast, the curve may already be at or near its maximum at the left edge of the plot
and decrease monotonically throughout the visible range. In this case the "peak" is at the
left edge, not in the interior — do not describe it as a bell or inverted-U peak. Look at
where the curve is *at the leftmost visible point*, and whether it goes up then down
(interior peak) or only down (monotonically decreasing from left edge). This error is
especially common for percent modulation curves under contrast gain conditions.

**Convergence is a strong claim:** only say two curves "converge" if they literally reach
the same endpoint value. If they both saturate but at different y-values, state the
endpoint separation explicitly — that is a different and important claim.

### Step 4 — Identify the figure's role in the paper's argument

Ask: why does this figure exist? Is it illustrating the pipeline (schematic), demonstrating
a qualitative regime (contrast gain vs response gain), or reproducing a specific experimental
result? The answer shapes what belongs in `figure_N.md` and what counts as a meaningful
discrepancy in the checklist.

Before writing the visual checklist, identify which panels are actually expected to be
generated by the implementation. Many paper figures include empirical reference panels
alongside model simulation panels. If the implementation protocol does not generate the
empirical data panel, do not write a deep visual checklist for that empirical panel. Treat it
as context in `figure_N.md`, not as a reproduction target.

**Pin each figure slug to the PAPER's actual figure content** — the plotted object the
paper's Figure N shows. Rendering an **engine/convergence DIAGNOSTIC in place of the
paper's figure** is a COVERAGE divergence and must be flagged (a RED tripwire / honest
disposition), never passed silently as the figure. rozell2008 rendered engine diagnostics
(convergence traces, LCA-vs-ISTA equivalence) under the figure slugs while the paper's
actual Fig 2 (the thresholding nonlinearities) — trivially reproducible — went unrendered:
a silent coverage gap. The slug must target what the paper plots; a diagnostic substitute is
an explicit gap to surface, not the figure.

### Step 5 — Write figure_N_visual_checklist.md

Structure: one section per panel. Each item is a checkbox `- [ ]` that a reviewer can
evaluate as binary pass/fail by looking at the generated figure.

Scope the checklist to generated model artifacts:
- For **model simulation panels**, write detailed visual checks for curve shapes, endpoint
  relationships, schematic/inset structure, colormap encoding, and inter-panel relationships.
- For **simulation schematics or insets** that the implementation is expected to draw,
  checklist the visual encodings of model parameters (stimulus size/location/orientation,
  RF, attention field, etc.).
- For **empirical-data panels that are included only as paper context and are not generated
  from the model**, do not checklist detailed data geometry, point locations, error bars,
  source labels, or empirical curve shapes. Either omit those panels from the checklist or
  include a short note such as "Panel B is empirical reference data and is not a generated
  model output." The reviewer should not fail a generated figure for not reproducing
  empirical data that the implementation does not have access to.
- If a generated figure is expected to include a coarse placeholder or context panel for
  empirical data, checklist only that coarse requirement, not detailed empirical values.

Rules for writing checklist items:
- Written for someone who has **not read the paper** — all necessary context is in the item.
- Each item is a **single, unambiguous visual claim**. Do not bundle two claims in one item.
- Comparative phrasing ("right stripe brighter than left") is fine where it captures the
  real claim and is robust to render style. But **comparative phrasing must NEVER be used to
  excuse a discriminating quantitative dimension** (see "Binding the discriminating
  dimensions" below). "More robust" previously meant "tolerant of quantitative divergence" —
  that tolerance is exactly what passed 49% of figures that don't look like the paper
  (2026-06-02 post-mortem). A claim must fail when the figure stops matching the paper.
- Include a **coordinate convention section** at the top explaining how to interpret
  positional references.
- Structural absence claims are valid and important ("there is a clear dark gap between the
  two bands — they have not merged").

**Binding the discriminating dimensions (2026-06-02 — non-negotiable).** The first run's
checklists marked as "NOT binding" exactly the dimensions that distinguish a faithful figure
from an unfaithful one — and so passed figures with the wrong tuning width, no baseline, the
inverted normalization, and spurious extra panels. For every **model** panel (this does NOT
apply to non-generated empirical panels, which stay out of scope per the model-panels-only
ruling), these are **binding** and must each be a checklist item judged against the paper
image:

- **Normalization convention** — reproduce the paper's **actual scale**, not a convenient one.
  State explicitly what the response is normalized *to* (which curve/quantity, or a shared
  reference), and it must match the paper. Two failure modes, both binding:
  - *Wrong referent* — pinning the wrong curve to 1.0 (the corpus-wide inversion: neutral
    pinned to 1.0 so attended overshoots). "Y = normalized response" with no stated referent
    is the underspecification that caused it.
  - *Per-panel auto-normalization* — rescaling **each panel/curve to its own max (→ 1.0)**.
    This is wrong whenever the paper uses a **shared scale across panels** so the panels are
    **directly comparable**: e.g. R&H Fig 2, where the contrast-gain panel plateaus at ~0.58
    and the response-gain panel at ~0.67 *on the same axis* — that height **difference is the
    figure's claim**. Re-normalizing each panel to 1.0 erases it and inflates the level. If the
    paper's curves do not reach 1.0, **yours must not either.** Never `max`-normalize a panel
    just because the view code makes it easy; the view must carry the paper's scale.
  Use **one convention across the corpus** and record it in the spec, not just the checklist.
- **Curve shape AND width/bandwidth** — a tuning curve 2× too broad fails. Width is binding,
  not an "exact tuning width — non-binding" excuse.
- **Baseline / floor / asymptote** — the offset a curve sits on is binding.
- **Panel layout** — enumerate the panels the paper's figure has; **forbid panels it does
  not** (do not write "the difference curve, if plotted" — that pre-blesses a spurious panel).
  A model panel the paper has and the figure drops is also a failure.
- **Axes** — range, scale (log/linear), sign convention, labels, tick values.
- **Pinned axis limits (absolute magnitude)** — the Phase-A view MUST pin each panel's
  axis limits to the **paper's published limits**, exactly as R&H's `PAPER_PANEL_LIMITS`
  does — never auto-scale a meaningful magnitude axis. Rationale: pinning makes a magnitude
  divergence **OVERFLOW the panel** so the VLM/eye catches it for free, and the limits are
  paper-derived so the builder cannot game them. The antipattern is `ax.set_ylim(bottom=0)`
  (or any auto-scaling of the top) on a data/fit-scaled axis: denison2021 Fig 5 did exactly
  this, so a 4×-too-high d′ merely relabeled the axis 0–10 instead of overflowing the paper's
  0–3, and the builder waved the magnitude off as a "degenerate scale" — only an adversarial
  audit caught it. If the paper's axis is a meaningful or fit-to-data scale, the view carries
  the paper's limits and a wrong-magnitude curve must visibly overflow or undershoot.

**Validate the checklist for SUFFICIENCY, not just necessity.** Before the spec is approved,
show that a *deliberately-wrong* figure (wrong width, inverted normalization, an extra panel,
a degenerate monotone/plateau curve where the paper turns over) **fails** the checklist. A
checklist a known-bad figure passes is too loose by construction and is a hard reject. "The
right figure passes" is necessary but not sufficient — the gap between them is where the
leniency lived.

**Tagging uncertain items:** If you are not confident about a checklist item — because the
image is ambiguous, because you are inferring from equations rather than clearly seeing the
feature, or because reasonable interpretations differ — append `<!-- UNSURE: one-line reason -->`
to that item on the same line. Example:

```
- [ ] The two bands are separated by a dark gap. <!-- UNSURE: hard to tell if gap is present or bands fully merge -->
```

Tag generously: it is better to flag too many items than to miss a misinterpretation. The
human reviewer will pay extra attention to tagged items.

### Step 6 — Write figure_N.md

Structure:
- **Role in the paper**: one paragraph explaining why this figure exists and what it shows.
- **Verbatim caption**: copy the exact caption text from `paper/extracted_text.md`, formatted
  as a blockquote. Do not paraphrase. This is the primary source and must be preserved exactly
  so readers can verify interpretation claims against the original wording.
- **Simulation parameters**: table of values with citation IDs from `citations.yaml`.
- **Coordinate convention**: same reference frame as the checklist.
- **Pipeline and expected behavior**: one subsection per panel, with the relevant equation
  references and citation IDs. Explain *why* the panel looks the way it does from first
  principles — not just what it shows, but how the model equations produce that structure.
- **Key inter-panel relationships**: a numbered list of claims that relate two or more
  panels to each other. These should follow directly from the model equations and hold in
  any correct implementation. They are the highest-value items for test generation.

Citation IDs (`C-NNN`) must exist in `citations.yaml`. Do not invent IDs.

### Step 7 — Commit and request review

Once both files are written:

1. Stage and commit both files:
   ```bash
   git add article_aware/figures/figure_N.md article_aware/figures/figure_N_visual_checklist.md
   git commit -m "Extract figure N: initial extraction pending review"
   ```

2. Report to the human:
   - Which items in the checklist are tagged `UNSURE` and why.
   - Any aspects of the figure that were genuinely ambiguous or that required inferring
     from equations rather than direct visual observation.
   - A one-line summary of the figure's role and what makes it non-trivial to check.

3. Ask the human to review both files and leave inline comments where needed (see Review
   Protocol below).

---

## Review protocol

After the agent commits the files, the human reviews by **writing comments inline in the
markdown file, on the same line as the item being reviewed**. No special syntax is required
— just append your comment to the line. Example:

```
- [ ] The two bands are separated by a dark gap. <!-- UNSURE: hard to tell --> they clearly merge in the paper figure
```

When the human asks the agent to incorporate the review, the agent runs:

```bash
git diff HEAD -- article_aware/figures/figure_N_visual_checklist.md
git diff HEAD -- article_aware/figures/figure_N.md
```

The diff shows exactly which lines were touched, with the original and the human's addition
in full context. The agent reads each changed line, understands the comment, and updates the
item accordingly. After updating, the agent commits again:

```bash
git commit -m "Extract figure N: incorporate human review"
```

---

## Output file locations

```
article_aware/figures/
  figure_N.jpg                   ← already exists (input)
  figure_N.md                    ← produce this
  figure_N_visual_checklist.md   ← produce this
```

---

## Quality checks before finishing

- [ ] Every claim in `figure_N.md` has a citation ID or is explicitly labeled as derived
      from the model equations.
- [ ] The coordinate convention is stated in both files and is consistent between them.
- [ ] Each checklist item is self-contained — a reviewer with no paper access can evaluate it.
- [ ] The checklist focuses on panels and features generated by the implementation; empirical
      reference panels are omitted or marked as non-reproduction context unless the protocol
      explicitly says to generate them.
- [ ] The inter-panel relationships in `figure_N.md` are grounded in equations, not just
      visual observation.
- [ ] No checklist item contradicts a claim in `figure_N.md`.
- [ ] The colormap encoding convention (if non-standard) is stated in the checklist.
- [ ] For every model panel, the discriminating dimensions are binding items: normalization
      convention (which curve = 1.0, stated), curve shape + width, baseline/floor, panel
      layout (panels the paper lacks are forbidden), and axes.
- [ ] **Sufficiency demonstrated**: a deliberately-wrong figure (wrong width / inverted
      normalization / extra panel / degenerate curve) has been shown to FAIL this checklist.
      A known-bad figure that passes = reject.
- [ ] Items where you had genuine visual uncertainty are tagged `<!-- UNSURE -->`.

## Commit when done

When your work is complete, **commit your output** on the working branch — your changes, or (for a report-only role) your report — with a message that matches the diff. The process-auditor reads commit messages against diffs, so every agent must leave an atomic, honestly-described commit.
