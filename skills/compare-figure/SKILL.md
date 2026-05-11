# Skill: Compare Figure

## Purpose

Given a generated model figure and the article-aware artifacts for that figure,
produce a structured pass/fail verdict for each visual checklist item and identify
the most important discrepancies to guide the next implementation iteration.

---

## Inputs

The comparison packet — a JSON file produced by:

```bash
neuromodels compare-figure-packet <figure_number> \
  --model-dir <model_dir> \
  --output-file /tmp/<model>_figure_packets/figure_<N>.json
```

The packet contains paths to four artifacts:

- `original_figure` — the paper figure image (`.jpg`)
- `generated_figure` — the generated model output image (`.png`)
- `figure_description` — `article_aware/figures/figure_N.md`: expected behavior,
  simulation parameters, inter-panel relationships, grounded in model equations
- `figure_checklist` — `article_aware/figures/figure_N_visual_checklist.md`:
  per-item pass/fail criteria written by reading the original figure

---

## Process

### Step 1 — Generate the packet (parent agent)

The parent agent runs `neuromodels compare-figure-packet` and writes the packet
to a stable temp path. Then it spawns one or more comparison subagents, passing
only the packet path.

Spawn multiple subagents in parallel when comparing several figures. Multiple
independent subagents on the same figure also improve reliability — see
**Known failure modes** below.

### Step 2 — Subagent reads and evaluates (subagent)

**The subagent is the VLM.** It reads both images directly using its vision
capability. No external API calls or CLI commands are needed.

The subagent prompt should be minimal:

> "Read the packet at `<path>`. It contains paths to the original figure,
> generated figure, figure description, and visual checklist. Read all four
> files. Then evaluate every checklist item against the generated figure and
> report the result for each item (pass / fail / unsure) plus an overall
> verdict and the most important discrepancies."

The subagent reads:
1. The packet JSON to get the four paths
2. Both images
3. The figure description (for context on what the figure should show)
4. The visual checklist (the primary evaluation instrument)

It then works through each checkbox item and returns the full result verbatim —
do not summarize or truncate the checklist results.

### Step 3 — Parent agent synthesizes

The parent agent reads the subagent's verdict and:

- Groups failures by category (model bug vs. figure generation issue)
- Prioritizes: model equation errors before cosmetic/layout issues
- If a figure passes, notes any `unsure` items for human review
- If a figure fails, uses the specific failed items to guide the next fix

If a figure repeatedly fails and subagent feedback is insufficient to diagnose
the root cause, the parent agent inspects the generated figure directly before
continuing. Treat direct inspection as the exception, not the default.

---

## Known failure modes

VLM subagents make mistakes on figure comparison. These patterns have been
observed and should be kept in mind when interpreting verdicts:

**Hallucinating features that are absent.** A subagent may report PASS on a
structural item (e.g., "two distinct bands") when only one band is visible in the
generated figure. Always cross-check PASS verdicts on structural items against
your own reading of the image when something seems off.

**Inventing failures that don't exist.** A subagent may report FAIL on a feature
that is actually correct (e.g., claiming the attention field baseline is 0 when
it is visibly 1 in the slice plot). Check the colorbar and slice plots
explicitly before accepting a baseline-level failure.

**Equation-inferred vs. image-read claims.** Subagents sometimes reason from the
model equations about what the figure *should* show rather than reading what it
*does* show. A subagent that reports a peaked modulation curve when the figure
shows a monotonically decreasing one is making this error.

**Mitigation:** Spawn two or three independent subagents on the same figure.
Disagreements between them flag items that warrant direct inspection. Unanimous
FAIL across all subagents is a strong signal; a FAIL from one of three is weak.
When in doubt, read the image yourself.

---

## What to do with results

- **Model equation errors** (e.g., wrong floor value, wrong normalization):
  fix in `implementation/src/`, regenerate the figure, rerun figure tests,
  then rerun visual comparison.

- **Figure generation errors** (e.g., missing panel, missing operator labels):
  fix in the figure generation code, regenerate, rerun visual comparison only
  (no need to rerun model tests if the underlying computation is unchanged).

- **Checklist errors** (a checklist item is wrong or too coarse to catch a real
  failure): flag for the article-aware author. Do not edit `article_aware/` from
  Phase B to make a comparison pass — log a spec question instead.
