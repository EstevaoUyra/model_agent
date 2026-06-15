# Remediate figure artifacts to the canonical paths (one model)

Make every in-scope figure's three views exist at the canonical committed paths the README + coverage
gate read — or be **honestly marked absent**. Repo root: /Users/estevaouyra/dev/model_agent. You are
given one `models/<name>`. The corrected skills (`skills/digitize-figure/SKILL.md`,
`skills/implement/SKILL.md`) define the contract; `tools/check_figure_coverage.py` is the gate.

Canonical paths (committed, read via `git ls-files`):
- **paper**: `article_aware/figures/figure_<N>.{png,jpg}`
- **digitized**: `article_aware/figures/figure_<N>/overlay_<panel>.png` (filename contains `overlay`)
- **implementation**: `figures_reproduced/figure_<N>.{png,jpg}`

## Be efficient — RELOCATE/PROMOTE/MARK first; produce only when cheap

For each in-scope figure (see `logs/readme_meta.yaml` `figures:` + what renders on disk):

1. **Implementation** — if the render is committed under `figure_outputs/` (or
   `implementation/figure_outputs/`) but not at `figures_reproduced/figure_<N>.png`, **copy it there and
   commit** (promote). If several renders exist for one figure (e.g. `figure_6_weights.png` +
   `figure_6_activity.png`), pick the primary one as `figure_<N>.png` (or, if both are essential, the
   skill allows the generator to show multiple `figure_<N>_*.png` under figures_reproduced). If no render
   exists at all, leave it (an implement-pass concern, out of scope here) and note it.

2. **Paper** — if a paper crop exists only at a non-canonical path (`figure_<N>/figure_<N>_source.png`,
   `figure_<N>/panel_*_paper.png`), **copy/assemble the figure-level image to
   `article_aware/figures/figure_<N>.png`** and commit. If NO paper image exists anywhere but
   `paper/paper.pdf` (or page images) is committed, **crop figure N from it** (pymupdf render the page,
   crop the figure region, verify visually). If the paper source is genuinely absent (paywalled, never
   acquired), leave it and say so — do NOT fabricate.

3. **Digitized** — if overlays exist at a non-canonical path (`figure_outputs/figure_<N>/*overlay*`,
   `figure_<N>/panel_*_overlay.png`), **copy them to `article_aware/figures/figure_<N>/overlay_*.png`**
   and commit. If a `panel_*_digitized.json` exists but no overlay image, render the overlay
   (`neuromodels.framework.figures.overlay`) and commit at the canonical path. **If the figure is not a
   Mode-1 plot** (a learned-dictionary tile, an activity/heat map, a schematic, an illustrative
   constructed-stub render with no curve to trace), commit an empty
   `article_aware/figures/figure_<N>.nodigitize` marker — honest, not a fabricated overlay. Do NOT run a
   from-scratch full digitization of a never-digitized real plot here (that is a full digitize-pass); if
   one is genuinely warranted, note it and move on.

## Finish

- Run `python3 <repo-root>/tools/build_model_readme.py models/<name> --reuse-cost` to regenerate the
  README, then `--check` to confirm clean.
- Commit IN THE SUBMODULE only, on its **current branch (main for most)**. Stage the figure files +
  `README.md` (+ any `.nodigitize` markers). Never `git add -A`; never touch the parent repo.
- **Do NOT push** and do NOT open a PR — just commit locally on the current branch. The orchestrator
  batches all pushes centrally (a main-push guardrail makes per-agent pushes/PRs noisy). Report the sha.

## Report

`model | committed sha | pushed? | per-figure: what each view became (promoted/cropped/relocated/nodigitize/left-absent+why) | remaining genuine gaps (no paper source, render needed) | did the corrected skill suffice?`
