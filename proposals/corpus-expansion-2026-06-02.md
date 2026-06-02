# Corpus expansion plan — 2026-06-02

Pillar-4 process-knowledge (see [VISION.md](../VISION.md)). This is the plan for
growing the model library from 4 reproductions to a structured corpus, and the
process upgrade we adopt alongside it. Not canon; an input to canon.

## Target shape (user-set)

**One deep flagship cluster + two complementary clusters.** Grow by *clusters,
not singletons*: within a cluster the papers' shared literature reduces each
other's uncertainty; across clusters, different computational motifs stress and
improve the reproduction process. Each cluster is also a proto-ontology — but
the ontology itself is **deferred**: 4 models is too few to distil one that
isn't guesswork. Build the corpus first; let the ontology crystallise out of it.

- **Cluster 1 — Attention via normalization (R&H family): exhaustive.** As many
  v1-reproducible members of the lineage as exist. (Already hold 3.)
- **Cluster 2 — Sparse / efficient coding (Olshausen–Field): 3–4 papers.**
- **Cluster 3 — Predictive coding (Rao–Ballard): 3–4 papers.**

Clusters 2 and 3 were chosen to leave the normalization trunk entirely — both
existing clusters (R&H attention, Coen-Cagli MGSM) sit *on* divisive
normalization, the field's unifying hub, so genuine process diversity requires
different motifs.

## Provenance of this synthesis (honesty note)

Authored from: the verified **source set** of the `deep-research` workflow (27
sources / 24 confirmed claims across 6 angles) — **its automated synthesis stage
returned placeholder output and was discarded**; two background scouts
(comp-neuro ontology landscape; model-reproduction practice); a dedicated
exhaustive enumeration of cluster 1; and domain knowledge. **Cluster 1 is
complete; clusters 2 & 3 below are preliminary**, pending dedicated enumeration
agents (running at time of writing).

---

## 1. Taxonomy of mechanistic vision models

Scope = the mechanistic/biological computational-neuroscience tradition (DNN
goal-driven ventral-stream models named as an adjacent branch, not detailed).

- **Linear–nonlinear / energy & Gabor models** — oriented linear RFs + static
  nonlinearity; complex-cell energy model (Adelson & Bergen).
- **Divisive normalization** — response divided by a pooled normalization
  signal; framed as a *canonical neural computation* (Carandini & Heeger 2012,
  [doi:10.1038/nrn3136](https://doi.org/10.1038/nrn3136)). The field's hub.
- **Efficient / sparse coding & natural-image statistics** — represent images
  with a sparse, statistically efficient code (Olshausen & Field; Simoncelli &
  Olshausen 2001).
- **Predictive coding** — hierarchical generative model + prediction-error
  propagation (Rao & Ballard 1999; Friston).
- **Bayesian / ideal-observer** — optimal inference under a generative model and
  noise (Geisler).
- **Probabilistic / population codes** — neural populations represent
  distributions / uncertainty (Ma, Beck, Pouget 2006; Fiser et al. 2010).
- **Texture / mid-level summary statistics** — pooled higher-order statistics
  (Portilla & Simoncelli 2000; Freeman & Simoncelli 2011 metamers).
- *(Adjacent, named not detailed)* goal-driven deep-network ventral-stream
  models (HMAX → CNN → task-optimized).

## 2. Phylogeny — the lineage graph

```
Heeger 1992 ──→ Carandini–Heeger–Movshon 1997 ──→ Carandini & Heeger 2012 (canonical computation) ──→ ORGaNICs
   │                                                         ▲
   └─→ Reynolds & Heeger 2009  (normalization model of ATTENTION)  ◀── HUB / CLUSTER 1
          ├─ Herrmann 2010              ✓ in corpus
          ├─ Li/Pan/Carrasco 2021      ✓ in corpus
          └─ Lee&Maunsell, Ni/Maunsell, Boynton, Pestilli, Hara/Gardner, Denison, Verhoef …

Schwartz & Simoncelli 2001 ──→ Coen-Cagli 2012 (MGSM)   ✓ in corpus   (also a normalization branch)

── separate trunks (clusters 2 & 3) ──
Olshausen & Field 1996/97 ──→ Bell–Sejnowski ICA, Rozell LCA (deterministic solver), Vinje–Gallant
Rao & Ballard 1999 ──→ Spratling 2010/2008, Friston/Bogacz, (PredNet — adjacent)
```

**Structural fact:** divisive normalization is the unifying hub; the existing
corpus is concentrated there. Clusters 2 & 3 deliberately sit on independent
trunks.

---

## 3. Cluster 1 — Attention via normalization (FLAGSHIP, exhaustive)

Hub: **Reynolds & Heeger 2009**, *Neuron* 61:168–185
([doi:10.1016/j.neuron.2009.01.002](https://doi.org/10.1016/j.neuron.2009.01.002)).
Official MATLAB: Heeger Lab / Salk
([attentionModel.zip](https://snl.salk.edu/~reynolds/Normalization_Model_of_Attention/)).
**Already in corpus:** R&H 2009; Herrmann et al. 2010; Li/Pan/Carrasco 2021.

Lineage is **dense and well-bounded: ~18–22 papers, ~15 with a simulatable
deterministic forward model.** Three lab clusters (Heeger/Carrasco, Maunsell/Ni,
Gardner/Pestilli) plus Spratling & Bundesen as outside-family comparisons.
Original code is concentrated in a few places (R&H official; Denison 2021 on
[OSF dkx7n](https://osf.io/dkx7n); Verhoef & Maunsell 2017 on
[ModelDB #243534](https://modeldb.science/citations/243534)); most others ship
**no code but full in-paper equations** → reimplement-from-spec, with
parameter-fitting separable & stubbable (the property we want).

**Ranked next targets within cluster 1:**

1. **Denison, Carrasco & Heeger 2021** — *dynamic* (ODE) normalization, temporal
   attention; OSF code; fitting separable.
   [doi:10.1038/s41562-021-01129-1](https://doi.org/10.1038/s41562-021-01129-1)
2. **Lee & Maunsell 2009** — the canonical *competing* normalization-of-attention
   formulation; tiny, fully-specified deterministic model; ideal contrast piece.
   [doi:10.1371/journal.pone.0004651](https://doi.org/10.1371/journal.pone.0004651)
3. **Verhoef & Maunsell 2017 (eLife)** — RF/surround spatial-profile extension;
   deterministic + **original code on ModelDB**.
   [doi:10.7554/eLife.17256](https://doi.org/10.7554/eLife.17256)
4. **Ni, Ray & Maunsell 2012** — *tuned* normalization; sharp distinct prediction
   (modulation-size variance, pref/null asymmetry).
   [doi:10.1016/j.neuron.2012.01.006](https://doi.org/10.1016/j.neuron.2012.01.006)
5. **Hara, Pestilli & Gardner 2016** — feature-attention extension; response +
   coherence gain; open-access.
   [doi:10.1371/journal.pcbi.1005225](https://doi.org/10.1371/journal.pcbi.1005225)
6. **Pestilli, Ling & Carrasco 2009** — population-coding CRF; endogenous→contrast
   vs exogenous→response gain.
   [doi:10.1016/j.visres.2008.09.018](https://doi.org/10.1016/j.visres.2008.09.018)
7. **Boynton 2009** — compact parametric attention-on-CRF framework unifying the
   gain taxonomy. [doi:10.1016/j.visres.2008.11.001](https://doi.org/10.1016/j.visres.2008.11.001)
8. **Spratling 2008** — strongest *different-mechanism* comparison (predictive
   coding / biased competition); deterministic iterative forward, no training
   stage; bridges to Cluster 3.
   [doi:10.1016/j.visres.2008.03.009](https://doi.org/10.1016/j.visres.2008.03.009)

Precursors worth a cheap reproduction for completeness: **Heeger 1992**
([doi:10.1017/S0952523800009640](https://doi.org/10.1017/S0952523800009640)),
**Carandini–Heeger–Movshon 1997**
([doi:10.1523/JNEUROSCI.17-21-08621.1997](https://doi.org/10.1523/JNEUROSCI.17-21-08621.1997)).

---

## 4. Cluster 2 — Sparse / efficient coding (Olshausen–Field)

**Motif:** learn an overcomplete dictionary; represent an image by sparse
inference over it. Maximally unlike normalization.

**Why it's a strong process test:** the textbook *freeze-the-fit* case. The
lineage factorizes cleanly into **(A) dictionary learning** (slow, stochastic,
iterative → stub/freeze it; the canonical `IMAGES.mat` whitened dataset + a
pre-trained basis can be shipped as the frozen artifact) and **(B) sparse
inference** (the per-image deterministic forward pass). The LCA sub-trunk is
special: there the **inference *is* a deterministic dynamical system**, the
purest "deterministic forward" target in the whole corpus, and a direct
exercise of ARCHITECTURE's "the solver is its own swappable stage" rule.

**Members (verified):**
- **Olshausen & Field 1996/1997** *(anchor; treat as one target)* — emergent
  localized/oriented/bandpass (Gabor-like) basis from natural-image patches (the
  iconic dictionary montage); sparseness/kurtosis stats; reconstruction.
  [doi:10.1038/381607a0](https://doi.org/10.1038/381607a0) ·
  [doi:10.1016/S0042-6989(97)00169-7](https://doi.org/10.1016/S0042-6989(97)00169-7)
- **Rozell, Johnson, Baraniuk & Olshausen 2008 — LCA** ⭐ — recurrent
  leaky-integrator + lateral-inhibition + thresholding network that converges to
  the sparse code; reproduce convergence, sparsity-vs-λ, ISTA equivalence.
  Inference-only (fixed dictionary) → zero training.
  [doi:10.1162/neco.2008.03-07-486](https://doi.org/10.1162/neco.2008.03-07-486)
- **Zhu & Rozell 2013** — **nonclassical-RF effects (end-stopping, surround
  suppression) emerge from the LCA dynamics**; reuses the LCA engine, so low
  marginal cost, distinct neuroscience claim. **Cross-links to Cluster 3** (same
  phenomena predictive coding explains — a built-in cross-validation pair).
  [doi:10.1371/journal.pcbi.1003191](https://doi.org/10.1371/journal.pcbi.1003191)
- **Bell & Sejnowski 1997** — ICA → oriented edge-filter basis (infomax); a
  methodologically independent route to the same emergent-RF result; near-zero
  reproduction risk (one-line `FastICA`).
  [doi:10.1016/S0042-6989(97)00121-1](https://doi.org/10.1016/S0042-6989(97)00121-1)
- *(deferred)* **Karklin & Lewicki 2009** ([doi:10.1038/nature07481](https://doi.org/10.1038/nature07481))
  — emergent complex-cell invariances; scientifically richest but nested
  two-stage learning is least separable and has no maintained code. High cost.

**Ranked targets:** (1) O&F 1996/97 (safest, iconic, author MATLAB + many
MIT-licensed PyTorch reimpls with ISTA inference split from learning); (2) LCA
(best fit for the deterministic-forward mandate); (3) Zhu & Rozell 2013 (near-
free LCA extension, distinct claim, pairs with Vinje & Gallant 2000 as empirical
sparseness benchmark); (4) Bell & Sejnowski (cheap independent cross-check).

**Code (corrected):** Olshausen `sparsenet` ([rctn.org/bruno/sparsenet](http://www.rctn.org/bruno/sparsenet/))
— canonical MATLAB **+ the shared `IMAGES.mat` whitened dataset** every
downstream reimpl reuses; **`lanl/lca-pytorch`** (BSD-3, maintained, explicit
Rozell-2008 variable mapping) for the whole LCA sub-trunk; **scikit-learn**
(`SparseCoder` / `MiniBatchDictionaryLearning` / `FastICA`) for the generative +
ICA trunk. *Note:* `plenoptic` does **not** ship sparse coding (texture/metamers
only). A single frozen-dictionary artifact feeds O&F, LCA, and Zhu & Rozell.

## 5. Cluster 3 — Predictive coding (Rao–Ballard)

**Motif:** hierarchical generative model + prediction-error propagation;
recurrent, multi-level, top-down. Distinct again.

**Why it stresses the process differently:** reproduces **qualitative
extra-classical RF effects** (end-stopping, surround/cross-orientation
suppression, flanker facilitation as emergent predictions) — strong VLM
targets — via deterministic iterative inference (a recurrent ODE / DIM update to
a fixed point, again a solver-as-stage); generative-weight learning is separable
& stubbable. Exercises hierarchy/recurrence the algebraic normalization models
never touch.

**Members (verified):**
- **Rao & Ballard 1999**, *Nat. Neurosci.* 2:79–87
  ([doi:10.1038/4580](https://doi.org/10.1038/4580)) — anchor; end-stopping
  (their Fig 5), emergent Gabor RFs, contextual suppression. Clean two-phase
  split (Hebbian weight learning vs MAP inference dynamics). No author release
  but fully specified in-paper.
- **Spratling 2010 (PC/BC-DIM)**, *J. Neurosci.* 30:3531–3543
  ([doi:10.1523/JNEUROSCI.4911-09.2010](https://doi.org/10.1523/JNEUROSCI.4911-09.2010))
  — **densest phenomenology in one model** (orientation/SF/TF tuning,
  cross-orientation suppression, surround suppression, flanker facilitation,
  end-stopping); deterministic DIM solver, frozen dictionary. **Author MATLAB on
  Codeberg.**
- **Bogacz 2017** tutorial, *J. Math. Psychol.* 76B:198–211
  ([doi:10.1016/j.jmp.2015.11.003](https://doi.org/10.1016/j.jmp.2015.11.003))
  — cleanest minimal deterministic PC inference network with **author code**; the
  "solver-is-its-own-stage" exemplar + a validation harness for the others.
- *(optional 4th)* **Spratling 2012**, *Biol. Cybern.* 106:37–49
  ([doi:10.1007/s00422-012-0477-7](https://doi.org/10.1007/s00422-012-0477-7))
  — reverse-correlation V1 RFs; same DIM engine + author code; cheap add.
- *(adjacent — flagged out-of-cluster)* Lotter, Kreiman & Cox 2017 **PredNet**
  ([code](https://github.com/coxlab/prednet)) — a trained DNN with a single
  feedforward pass, *not* a frozen-generative-model + iterative-solver; excluded
  from the mechanistic cluster, named for completeness.

**Ranked targets:** (1) Spratling 2010 (best reproducibility-per-effort, author
code, densest claims); (2) Rao & Ballard 1999 (non-negotiable historical anchor,
cleanest learning/inference split); (3) Bogacz 2017 (reference solver +
harness); (4) Spratling 2012 if a 4th slot is wanted.

**Code:** Spratling's Codeberg ([mwspratling](https://codeberg.org/mwspratling)
— `V1_ResponseProperties`, `V1_ReverseCorrelation`, `DivisiveInputModulation`,
…) covers the whole PC/BC-DIM trunk on one DIM kernel; Bogacz tutorial on
[GitHub](https://github.com/Fivetuple/free_energy_tutorial). RB99 reimplement-
from-paper. *Note:* Spratling's mechanism is **divisive-input-modulation** —
divisive normalization reaching into predictive coding, reinforcing it as the
field hub.

## 5a. Cross-cluster convergence (a built-in cross-validation + ontology seed)

**One phenomenon, three mechanisms.** Extra-classical RF effects (end-stopping,
surround suppression) are reproduced by **all three clusters**: R&H-style
normalization (Cluster 1 precursors), sparse-coding LCA (Zhu & Rozell 2013,
Cluster 2), and predictive coding (Rao & Ballard / Spratling, Cluster 3). This is
exactly the cross-mechanism edge the deferred ontology (§7) will want — and a
concrete near-term opportunity: once two of these are reproduced, the shared
phenomenon becomes a *cross-validation target* (do independent mechanisms predict
the same measured effect?), not just three isolated figures. Flag end-stopping /
surround suppression as the first cross-cluster benchmark to wire up.

---

## 6. Process upgrade adopted now — direct literature-grounding

The one process change we make before scaling (other gaps — runner /
stuck-detector / static-check / standing calibration audit — carried as
documented manual steps). Grounded in the model-reproduction-practice scout:

- **Per-model parameter-provenance / discrepancy table** — *the* highest-leverage
  artifact. For each significant parameter/choice: `value | stated-in-paper |
  relative-only | inferred/assumed | evidence (cited ref / lineage / follow-up /
  original code) | sensitivity interval`. Underspecification is empirically the
  top reproduction blocker (NEST replication, PMC10310927; SciReplicate-Bench).
  This *is* the direct-literature-leverage step — and every row is a
  concept↔literature edge the future ontology will reuse.
- **Freeze-the-fit, hashed & provenanced.** Persist fitted/learned parameters as
  a hashed, versioned artifact (producing run/seed/commit); stub the stochastic
  fit; reproduction target = `forward(frozen_params) → output`. (Freeze the
  *output*, not the process — seed-fixing can't make training bit-deterministic.)
  Extends the existing stub convention (DESIGN §1, ARCHITECTURE §1).
- **Faithfulness rubric + confidence tiers (the trust-triage report, concrete).**
  PaperBench-style leaves — *code-present / executes / result-matches* as three
  separate gates — weighted roll-up; confidence tiered by *objectivity*
  (IDMRC κ: "env reproduces / code runs" high-confidence; "matches the figure"
  low). LLM first-pass triage, human-confirm low-confidence leaves. **Keep
  "it runs" strictly separate from "result matches"** — silent runs-but-wrong is
  the dominant failure across every benchmark.
- **Metamorphic + distributional gates above golden-file** — symmetry / scaling /
  monotonicity invariances (oracle-free, via Hypothesis); KS two-sample +
  seed-percentile bounds for any stochastic forward path.
- **Vocabulary** — label deliverables as *Replication* (ACM badging terms); emit
  a ReScience-style per-model report ("what was reproduced / diverged /
  underspecified / confidence per claim").

## 7. Ontology — deferred, but seed it now (from the ontology scout)

- **The phylogeny we want is genuine white space** — no existing resource curates
  cross-model *derives-from / extends / reuses-component* edges (BioModels &
  Physiome study, PMC5898004). This is ours to own.
- **Reuse, don't rebuild:** NeuroML 2 + LEMS (component/equation decomposition);
  ModelDB API + `model_concept` annotations (papers↔models↔concepts corpus);
  CNO / NIF / Cognitive Atlas (controlled vocabularies); SED-ML/OMEX (the
  standard for "a paper's figure as a runnable spec").
- **Study as the structural template:** **Brain-Score (vision)** — a
  benchmark/region node (paper-derived) with many model realizations + literature
  attached, MIT-licensed and queryable. **SciUnit** — capability/test↔model, so
  concept nodes can carry executable validation.
- The §6 literature-grounding tables are the raw material; the ontology
  formalises them once the corpus is dense enough.

## 8. Next actions

1. **[running]** Enumerate clusters 2 & 3 (seed + 3–4 each, code + reproducibility
   verified); fold results into §§4–5.
2. **Draft the literature-grounding step** (§6 provenance table) as a skill /
   WORKFLOW addition so it runs for every new model.
3. **Pick the first new reproduction target.** Candidates: within cluster 1,
   *Lee & Maunsell 2009* (cheap, fully-specified contrast to R&H) or
   *Denison 2021* (distinct dynamic claim, has code); to seed a new trunk,
   *Olshausen & Field 1996* (cluster 2).
