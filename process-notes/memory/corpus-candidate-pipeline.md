---
name: corpus-candidate-pipeline
description: "Where the 200-paper candidate landscape + top-100 reproduction ranking live and how they're regenerated"
metadata: 
  node_type: memory
  type: project
  originSessionId: a6fd7e82-9088-4e49-8e88-9c0c3e990d90
---

A 200-paper candidate landscape and a ranked top-100 reproduction list exist (built 2026-06-12):
`proposals/corpus-candidates-200.md` (200 models in 15 lineage clusters C1–C15, vision-weighted but
deliberately broad across neuroscience — decision-making, hippocampal/spatial, motor, RL, plasticity,
single-neuron dynamics) and `proposals/corpus-top100-ranking.md` (top 100 of the 173 not-yet-reproduced,
ranked by a transparent composite). Both are **regenerated** from one source of truth:
`proposals/corpus-ranking/build_ranking.py` (edit the `ROWS` data, rerun `python3 …/build_ranking.py`).

Composite weights (user-chosen, "balanced blend"): repro-fit 0.30 · importance/log-citations 0.22 ·
figures 0.12 · code 0.12 · compute 0.12 (heavy ranked low) · phylogeny 0.12.

Selection follows VISION.md "What enters the library" (reproducible-from-paper; unavailable data OK if
only a comparison target; cheap to iterate; heavy-compute included-but-flagged). Data came from 8 parallel
scout subagents using OpenAlex for citation counts + OA status.

Open-access PDFs for top-100 are in gitignored `paper_candidates/` named `NNN_<key>.pdf` (NNN = rank).
Only 18 fetched — Nature/Cell/Wiley/PNAS/PMC bot-block scripted downloads; the rest are `OA-todo`
(browser/Unpaywall) or `get@inst` (paywalled, fetch via institution). The PDF column in the ranking doc
says which is which — don't re-fetch `saved` ones. Use these lists to pick next reproduction targets
instead of re-researching. Related: [[project-vision-four-pillars]], [[keep-main-current-branch-promptly]].
