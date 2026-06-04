# Paper index — the reproduced corpus

Every paper currently reproduced in `models/`, grouped by cluster. The corpus and
its genealogy come from the deep-research synthesis in
[proposals/corpus-expansion-2026-06-02.md](proposals/corpus-expansion-2026-06-02.md)
(taxonomy · phylogeny · the three clusters and why they were chosen). This file is
the *what we hold*; that proposal is the *why and what next*.

> **Audit honesty — read this before trusting any status.** A `faithful` claim in a
> model's README is **not a certification**. Only the **hardened audit** —
> independent VLM figure-comparison (`logs/figure_comparisons/`) + the digitization
> gate — certifies, and **only 4 models have it**: `reynolds_heeger_2009`,
> `hermann2010`, `carrasco2021`, `hara_gardner_2016` — *all of which came back
> `partial` or `illustrative`, none `faithful`.* Three more have a partial
> **VLM-only** check. **The other 20 are `self-reported`** — the builder's own
> claim, not independently verified. Treat `self-reported` as *"implemented; not
> independently audited."*
>
> ⚠️ **`hara_gardner_2016` is misattributed.** The paper is **Schwedhelm, Krishna &
> Treue (2016)** (same DOI), not Hara/Pestilli/Gardner — a corpus-build labeling
> error. The submodule's own citations are corrected; the repo dir name and the
> corpus plan still carry the wrong label (dir rename pending).

**Audit column** — `hardened`: full independent pipeline (verdict shown) ·
`VLM`: independent figure-comparison only (partial) · `self-reported: X`: the
README's uncertified claim. **Model column** (Cluster 1) — `own`: the paper derives
its own forward model · `reuses R&H`: no new model; applies/extends Reynolds &
Heeger 2009 to compare with data.

## Phylogeny (from the corpus synthesis)

```
Heeger 1992 ─→ Carandini–Heeger–Movshon 1997 ─→ (Carandini & Heeger 2012, canonical computation)
   │
   └─→ Reynolds & Heeger 2009   ◀── HUB · Cluster 1 (attention via normalization)
          ├─ own-model descendants: Lee&Maunsell · Ni/Maunsell ×3 · Ghose · Boynton ·
          │  Pestilli · Denison · Verhoef
          └─ reuse-R&H (apply to data): Herrmann 2010 · Li/Pan/Carrasco 2021 ·
             Hara/Gardner 2016 · Doostani 2023
   Coen-Cagli 2012 (MGSM)  — own divisive-normalization model, separate branch

Olshausen & Field 1996/97 ─→ Bell–Sejnowski ICA · Rozell LCA → Zhu&Rozell · Karklin&Lewicki   ── Cluster 2 (sparse coding)
Rao & Ballard 1999 ─→ Spratling 2010/2012 · Bogacz 2017 (free-energy)                          ── Cluster 3 (predictive coding)
```

---

## Cluster 1 — Attention via normalization (R&H family) · flagship

| Paper | Citation | DOI | Model | Audit | Figs |
|---|---|---|---|---|---|
| [heeger_1992](models/heeger_1992) | Heeger (1992). Normalization of cell responses in cat striate cortex. *Vis. Neurosci.* | [10.1017/S0952523800009640](https://doi.org/10.1017/S0952523800009640) | own | self-reported: partial | 10 |
| [carandini_heeger_movshon_1997](models/carandini_heeger_movshon_1997) | Carandini, Heeger & Movshon (1997). Linearity and normalization in macaque V1 simple cells. *J. Neurosci.* | [10.1523/JNEUROSCI.17-21-08621.1997](https://doi.org/10.1523/JNEUROSCI.17-21-08621.1997) | own | self-reported: faithful | 8 |
| [reynolds_heeger_2009](models/reynolds_heeger_2009) | Reynolds & Heeger (2009). The Normalization Model of Attention. *Neuron* | [10.1016/j.neuron.2009.01.002](https://doi.org/10.1016/j.neuron.2009.01.002) | own (HUB) | **hardened: partial** · *mid-fix* | 14 |
| [reynolds_chelazzi_desimone_1999](models/reynolds_chelazzi_desimone_1999) | Reynolds, Chelazzi & Desimone (1999). Competitive mechanisms subserve attention in V2/V4. *J. Neurosci.* | [10.1523/JNEUROSCI.19-05-01736.1999](https://doi.org/10.1523/JNEUROSCI.19-05-01736.1999) | own | self-reported: faithful | 4 |
| [hermann2010](models/hermann2010) | Herrmann, Montaser-Kouhsari, Carrasco & Heeger (2010). When size matters: attention by contrast or response gain. *Nat. Neurosci.* | [10.1038/nn.2669](https://doi.org/10.1038/nn.2669) | reuses R&H | **hardened: partial** | 4 |
| [carrasco2021](models/carrasco2021) | Li, Pan & Carrasco (2021). Different computations underlie overt presaccadic and covert spatial attention. *Nat. Hum. Behav.* | [10.1038/s41562-021-01099-4](https://doi.org/10.1038/s41562-021-01099-4) | reuses R&H | **hardened: illustrative** | 2 |
| [lee_maunsell_2009](models/lee_maunsell_2009) | Lee & Maunsell (2009). A normalization model of attentional modulation of single-unit responses. *PLoS ONE* | [10.1371/journal.pone.0004651](https://doi.org/10.1371/journal.pone.0004651) | own | self-reported: faithful | 6 |
| [ni_ray_maunsell_2012](models/ni_ray_maunsell_2012) | Ni, Ray & Maunsell (2012). Tuned normalization explains the size of attention modulations. *Neuron* | [10.1016/j.neuron.2012.01.006](https://doi.org/10.1016/j.neuron.2012.01.006) | own | self-reported: faithful | 6 |
| [ni_maunsell_2017](models/ni_maunsell_2017) | Ni & Maunsell (2017). Spatially tuned normalization explains attention-modulation variance. *J. Neurophysiol.* | [10.1152/jn.00218.2017](https://doi.org/10.1152/jn.00218.2017) | own | self-reported: faithful | 4 |
| [ni_maunsell_2019](models/ni_maunsell_2019) | Ni & Maunsell (2019). Spatial and feature attention differ due to normalization. *J. Neurosci.* | [10.1523/JNEUROSCI.2106-18.2019](https://doi.org/10.1523/JNEUROSCI.2106-18.2019) | own | self-reported: illustrative | 4 |
| [ghose_maunsell_2008](models/ghose_maunsell_2008) | Ghose & Maunsell (2008). Spatial summation explains attentional modulation to multiple stimuli in V4. *J. Neurosci.* | [10.1523/JNEUROSCI.0138-08.2008](https://doi.org/10.1523/JNEUROSCI.0138-08.2008) | own | self-reported: faithful | 6 |
| [boynton_2009](models/boynton_2009) | Boynton (2009). A framework for describing the effects of attention on visual responses. *Vis. Res.* | [10.1016/j.visres.2008.11.001](https://doi.org/10.1016/j.visres.2008.11.001) | own | self-reported: faithful | 8 |
| [pestilli_ling_carrasco_2009](models/pestilli_ling_carrasco_2009) | Pestilli, Ling & Carrasco (2009). A population-coding model of attention's influence on contrast response. *Vis. Res.* | [10.1016/j.visres.2008.09.018](https://doi.org/10.1016/j.visres.2008.09.018) | own | self-reported: illustrative | 12 |
| [hara_gardner_2016](models/hara_gardner_2016) ⚠️ | Schwedhelm, Krishna & Treue (2016). An extended normalization model of attention accounts for feature-based attentional enhancement of both response and coherence gain. *PLoS Comput. Biol.* | [10.1371/journal.pcbi.1005225](https://doi.org/10.1371/journal.pcbi.1005225) | reuses R&H | **hardened: partial (6)** | 3 |
| [denison2021](models/denison2021) | Denison, Carrasco & Heeger (2021). A dynamic normalization model of temporal attention. *Nat. Hum. Behav.* | [10.1038/s41562-021-01129-1](https://doi.org/10.1038/s41562-021-01129-1) | own (dynamic) | self-reported: partial | 4 |
| [doostani_2023](models/doostani_2023) | Doostani, Hossein-Zadeh & Vaziri-Pashkam (2023). Normalization predicts human visual cortex in object-based attention. *eLife* | [10.7554/eLife.75726](https://doi.org/10.7554/eLife.75726) | reuses R&H | self-reported: illustrative | 9 |
| [verhoef_maunsell_2017](models/verhoef_maunsell_2017) | Verhoef & Maunsell (2017). Attention operates uniformly throughout the RF and surround. *eLife* | [10.7554/eLife.17256](https://doi.org/10.7554/eLife.17256) | own | VLM: faithful | 6 |
| [cagly2012](models/cagly2012) | Coen-Cagli, Dayan & Schwartz (2012). Cortical surround interactions and perceptual salience via natural scene statistics (MGSM). *PLoS Comput. Biol.* | [10.1371/journal.pcbi.1002405](https://doi.org/10.1371/journal.pcbi.1002405) | own (MGSM) | VLM: illustrative | 10 |

## Cluster 2 — Sparse / efficient coding (Olshausen–Field) · all own-model

| Paper | Citation | DOI | Audit | Figs |
|---|---|---|---|---|
| [olshausen_field_1996](models/olshausen_field_1996) | Olshausen & Field (1997). Sparse coding with an overcomplete basis set: a strategy employed by V1? *Vis. Res.* | [10.1016/S0042-6989(97)00169-7](https://doi.org/10.1016/S0042-6989(97)00169-7) | VLM: illustrative | 6 |
| [bell_sejnowski_1997](models/bell_sejnowski_1997) | Bell & Sejnowski (1997). The "independent components" of natural scenes are edge filters. *Vis. Res.* | [10.1016/S0042-6989(97)00121-1](https://doi.org/10.1016/S0042-6989(97)00121-1) | self-reported: faithful | 6 |
| [rozell2008](models/rozell2008) | Rozell, Johnson, Baraniuk & Olshausen (2008). Sparse coding via thresholding and local competition (LCA). *Neural Comput.* | [10.1162/neco.2008.03-07-486](https://doi.org/10.1162/neco.2008.03-07-486) | self-reported: faithful | 6 |
| [zhu_rozell_2013](models/zhu_rozell_2013) | Zhu & Rozell (2013). Visual nonclassical RF effects emerge from sparse coding in a dynamical system. *PLoS Comput. Biol.* | [10.1371/journal.pcbi.1003191](https://doi.org/10.1371/journal.pcbi.1003191) | self-reported: illustrative | 8 |
| [karklin_lewicki_2009](models/karklin_lewicki_2009) | Karklin & Lewicki (2009). Emergence of complex cell properties by learning to generalize in natural scenes. *Nature* | [10.1038/nature07481](https://doi.org/10.1038/nature07481) | self-reported: illustrative | 8 |

## Cluster 3 — Predictive coding (Rao–Ballard) · all own-model

| Paper | Citation | DOI | Audit | Figs |
|---|---|---|---|---|
| [rao_ballard_1999](models/rao_ballard_1999) | Rao & Ballard (1999). Predictive coding in the visual cortex. *Nat. Neurosci.* | [10.1038/4580](https://doi.org/10.1038/4580) | self-reported: illustrative | 8 |
| [spratling_2010](models/spratling_2010) | Spratling (2010). Predictive coding as a model of response properties in V1. *J. Neurosci.* | [10.1523/JNEUROSCI.4911-09.2010](https://doi.org/10.1523/JNEUROSCI.4911-09.2010) | self-reported: faithful | 8 |
| [spratling_2012](models/spratling_2012) | Spratling (2012). Predictive coding accounts for V1 response properties from reverse correlation. *Biol. Cybern.* | [10.1007/s00422-012-0477-7](https://doi.org/10.1007/s00422-012-0477-7) | self-reported: faithful | 8 |
| [bogacz2017](models/bogacz2017) | Bogacz (2017). A tutorial on the free-energy framework for modelling perception and learning. *J. Math. Psychol.* | [10.1016/j.jmp.2015.11.003](https://doi.org/10.1016/j.jmp.2015.11.003) | self-reported: faithful | 6 |

---

**Tally.** 27 papers — Cluster 1: 18 (14 own-model · 4 reuse R&H) · Cluster 2: 5 ·
Cluster 3: 4. **Independent audit:** 4 hardened (all `partial`/`illustrative`, none
faithful), 3 VLM-only; **20 self-reported.** No model is currently a
*certified-faithful* reproduction. Cross-cluster note: end-stopping &
surround-suppression are reproduced by all three motifs (R&H normalization ·
Zhu–Rozell LCA · Rao–Ballard predictive coding) — a natural cross-validation set.

*Next targets and the rationale for the corpus shape live in
[proposals/corpus-expansion-2026-06-02.md](proposals/corpus-expansion-2026-06-02.md). A
**due-diligence reproduction-readiness ranking** — every label re-checked against the
on-disk PDF, code provenance audited by resolving each URL — is in
[proposals/normalization-reproducibility-ranking-2026-06-04.md](proposals/normalization-reproducibility-ranking-2026-06-04.md).*

> **Code provenance (audited).** Only **2** papers have confirmed *own* downloadable
> code: `reynolds_heeger_2009` (`attentionModel.zip`) and `denison2021` (OSF `dkx7n`).
> The R&H `attentionModel.zip` is a **shared engine** (Schwedhelm reuses it; it is not
> any other paper's own code). `verhoef_maunsell_2017` has **no own code** — the
> ModelDB entry once attributed to it is a *different* Verhoef & Maunsell paper. All
> others are closed-form from the paper.
>
> *Dir-name note: `hermann2010` is the paper "Herr**mann**", and `hara_gardner_2016`
> is Schwedhelm et al. — both dir renames deferred; citations above are correct.*
