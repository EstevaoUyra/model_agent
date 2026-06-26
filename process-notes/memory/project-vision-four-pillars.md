---
name: project-vision-four-pillars
description: "The model-reproduction library's vision — four pillars + the current faithfulness-validation bottleneck; lives in repo VISION.md"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

Vision consolidated 2026-06-02 into the repo's new apex doc `VISION.md`. Four
pillars, **ordered and in tension** (the design lives in the conflicts):

1. **Faithful** — adamant, non-negotiable, wins every conflict; the output
   includes a *map of the paper's underspecification* (evidenced assumptions).
2. **Understandable** — readability is a real code-design constraint, not polish.
3. **Modifiable by scientific judgment** — a "piece" is what a *scientist* would
   swap (scientific ontology, not data-flow convenience); seams need an explicit
   rationale tagged natural / imposed / atomic. *(rationale artifact not built)*
4. **Process is part of the library** — the agent method for adding models is a
   co-equal deliverable; each model is also an *experiment on the process*; docs
   must not outrun validated evidence (STATUS.md is the corrective).

**Current bottleneck = the human's time to validate faithfulness.** Eventual
build: a **trust-triage report** sorted by confidence × impact, with
**evidence-grounded confidence** (author's original code > lineage >
sibling papers > mathematical necessity), a **researching faithfulness-auditor
agent** distinct from the isolated adversarial judge, and the **lineage used as
a cross-validation engine** (descendants corroborate ancestors).

**DIRECTION as of 2026-06-02 (user-set sequencing):** *Expand the corpus first;
the ontology crystallizes out of it later — 4 models is too few to build an
ontology that isn't guesswork.* Grow by **clusters, not singletons**: small
families of related papers reproduced as a batch → within-cluster literature
reduces uncertainty (goal 2), across-cluster motif diversity stresses/improves
the reproduction process (goal 1); each cluster is a proto-ontology. The one
process upgrade adopted now: **direct literature-grounding** as a step (research
each significant assumption against cited refs / lineage / follow-ups /
original code, record evidence + tier) — the manual precursor that also emits
the concept↔literature edges a future ontology needs. Other process gaps
(runner / stuck-detector / static-check / standing calibration audit) carried
as documented manual steps for now. Existing corpus = R&H normalization-of-
attention lineage + Coen-Cagli MGSM, so prioritize **complementary** clusters.

**Target corpus shape (user-set 2026-06-02):** ONE deep flagship cluster +
TWO complementary clusters. Cluster 1 = **attention normalization (R&H
family): exhaustive** — as many v1-reproducible papers in the
normalization-model-of-attention lineage as exist (already have R&H 2009,
hermann2010, carrasco2021). Clusters 2 & 3 = **3-4 papers each**, maximally
distinct motifs, internally dense, deterministic-forward-path-feasible. At
synthesis: run a dedicated *exhaustive enumeration* pass on cluster 1 (depth a
landscape survey won't give); pull clusters 2 & 3 from the deep-research
recommendations, trimmed to the 2 most distinct + dense + reproducible.

**Research DONE + committed (2026-06-02, `3b7afaf`):** full plan in
`proposals/corpus-expansion-2026-06-02.md`. Caveat: the `deep-research`
workflow's fan-out gathered good verified sources but its **auto-synthesis stage
returned a placeholder stub** — synthesis authored by hand from the source set +
2 scouts + 3 lineage-enumeration agents. Clusters now fully enumerated:
- **C1 attention-normalization (exhaustive):** ~18-22 papers, ~15 v1-reproducible.
  Top next targets: Lee & Maunsell 2009 (cheap competing formulation), Denison
  2021 (dynamic/ODE, OSF code), Verhoef & Maunsell 2017 (ModelDB code), Ni/Ray
  2012, Hara/Gardner 2016. R&H official code at Heeger/Salk.
- **C2 sparse coding:** O&F 1996/97 (anchor), Rozell 2008 LCA ⭐ (deterministic
  dynamical inference = purest forward target), Zhu & Rozell 2013 (NCRF), Bell &
  Sejnowski 1997. Code: rctn.org sparsenet + `IMAGES.mat`, `lanl/lca-pytorch`,
  scikit-learn. (plenoptic does NOT have sparse coding.)
- **C3 predictive coding:** Spratling 2010 PC/BC-DIM ⭐ (author code on Codeberg,
  densest V1 phenomenology), Rao & Ballard 1999 (anchor), Bogacz 2017 (reference
  solver+code), Spratling 2012 optional. PredNet = adjacent/excluded.

**Cross-cluster seed:** extra-classical RF effects (end-stopping / surround
suppression) reproduced by ALL three mechanisms → first cross-validation
benchmark + ontology edge. Scout findings on process/ontology also captured in
the plan (freeze-fit+hash, leaf-rubric faithfulness report, parameter-provenance
table = the literature-grounding step; reuse NeuroML/ModelDB/CNO, study
Brain-Score later).

**REPRODUCTION PROGRAM PLAN written + committed + pushed (2026-06-02, branch
`codex/compare-figures` @ `1947c0c`):**
`proposals/reproduction-program-plan-2026-06-02.md`. User direction: drive ALL
~21-23 models to reproduction via dynamic workflows, **mostly autonomously** —
**critique agents substitute for the human Phase-A/verdict gates** (a deliberate,
scoped override of DESIGN §1), and the human is **called only at the end** with
one consolidated confidence×impact triage report. Structure: **pilot (Lee &
Maunsell 2009) → waves of 3 (engines first) with revisits + a process retro
between waves**. Open-branch guardrails made mandatory under autonomy (esp. the
**hard parent-write guard** — an agent once `--amend`-ed the parent; multi-VLM
default; VLM-binding visual claims; falsification-trigger escalation). **Status =
AWAITING "GO" for the pilot; nothing reproduced yet.**

**PROGRAM STARTED 2026-06-02** (user set `/goal` "have all 21-23 models
reproduced" — a Stop hook keeps the loop running). Settled contract: autonomous
(critique agents replace human gates, one review at end); waves of ~3 engines-
first; improve guidelines EVERY iteration; re-run a group until solid; **a model
that won't reproduce is deferred to a later wave, never halts the program,
residual failures OK as learning**; uncapped; push discipline = work on a
`repro` branch per model repo, squash-PR to model `main` at the very end, parent
via history-preserving PR, commit ONLY inside model repos (parent-write guard),
`main`-push guard respected (use `gh pr merge`). Docs reconciled to reality
2026-06-02 (fictional machinery cut from DESIGN/WORKFLOW/REPO_STRUCTURE/AGENTS/
STATUS; VISION is the fixed anchor). Parent work on branch `codex/compare-figures`
(pushed); `origin/main` brought current once via PR #2.

**WAVE 1 COMPLETE — 3/3 GREEN** (`lee_maunsell_2009` C1, `olshausen_field_1996`
C2, `spratling_2010` C3): each reproduced end-to-end (Phase A → adversarial
spec-review → revise → organizer gate → paper-blind Phase B → 3-voter VLM),
organizer-verified, all on `repro` branches in their private repos. Three real
green-but-unfaithful defects caught+fixed by the critique/VLM layers (olshausen
confabulation; lee_maunsell contrast-units; spratling end-stopping — a loose
deterministic proxy + a stale figure render). **Corpus: 3 / ~22.**

**PROGRESS — 10 models GREEN.** Wave 1: lee_maunsell, olshausen, spratling. Wave
2: rozell2008, denison2021, verhoef_maunsell_2017, bogacz2017, bell_sejnowski_1997.
Wave 3: pestilli_ling_carrasco_2009 (6/6), heeger_1992 (5/5) — both first-pass
green; the deterministic render stage WORKED (no stale-figure false-alarms).
**Partial/fixes in flight:** rao_ballard_1999 3/4 (figure_3 r^td fix `w8kcqidxn`),
spratling_2012 3/4 (figure_3 Mexican-hat fix `wpx3quu0h`). **Wave-3 revised trio in
Phase B:** `w4j960brb` (zhu_rozell_2013, ni_ray_maunsell_2012, hara_gardner_2016).
**Final-triage caveats (lower confidence):** spratling_2012 paper figure IMAGES
unavailable (SQ-001) → VLM checklist-only; zhu_rozell exact tau/dt/M came from the
spec-review's paper reading (web-fetch digits were inconsistent). **After Wave 3
settles → final batch (~6-8 tail):** Boynton2009, Carandini-Heeger-Movshon1997,
Ni&Maunsell2017/2019, Doostani2023, Reynolds-Chelazzi-Desimone1999, Ghose2008,
Karklin&Lewicki2009. **Schedule now
3→6→6→rest** (user added a 3rd validation wave). **Wave 3 (6) Phase A running**
(`w7q9o2uux`: Zhu&Rozell2013, Spratling2012, Ni/Ray2012, Hara/Gardner2016,
Pestilli2009, Heeger1992; the first two reuse the rozell-LCA and spratling-DIM
primitives). Tail ~8 after Wave 3.

**Improvements assessment (mid-program): holding.** No-confabulation,
organizer-owns-git-gate, and fresh-figure-regen all held across Wave 2; added an
extraction threshold self-check + pinned repo names. Per-figure re-iterations
(spratling fig5 end-stopping [done green], bell fig4, rao_ballard fig3) are the
"re-run until solid" loop working — the independent 3-voter VLM backstop keeps
catching real model/stub defects deterministic tests miss. §1 cross-model
reuse-surface validated (rozell imported olshausen's dictionary primitive, no
leak).

**Process fixes locked this wave:** (1) the **organizer owns the git ground-truth
+ the APPROVED gate**; critique agents judge CONTENT only (a re-review agent
false-blocked an approvable model by reading git state from the PARENT repo). (2)
agents do git ops ONLY inside the model repo (`git -C models/<repo>`), never infer
nested-repo state from the parent. (3) extraction faithfulness rules (no
confabulation; thresholds in the ledger; one unit convention) now in WORKFLOW.md.
Retro ledger: `proposals/wave-retros.md`. Schedule widened to 3→6→rest (parallel).
See [[organizer-operating-model]].

**Why:** preserves a long vision discussion the user explicitly did not want to
lose. **How to apply:** treat VISION.md as apex for *intent* over
DESIGN/ARCHITECTURE; STATUS.md still wins on *reality*. User wants the repo
organized before building. See [[organizer-operating-model]].
