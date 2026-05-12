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
- Prefer **comparative claims** over absolute ones where possible ("right stripe brighter
  than left" is more robust than "right stripe has value 0.8").
- Include a **coordinate convention section** at the top explaining how to interpret
  positional references.
- Structural absence claims are valid and important ("there is a clear dark gap between the
  two bands — they have not merged").

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
- [ ] Items where you had genuine visual uncertainty are tagged `<!-- UNSURE -->`.
