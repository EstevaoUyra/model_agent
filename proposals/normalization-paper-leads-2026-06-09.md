# Normalization paper leads — download list (university trip 2026-06-10)

**Purpose.** Additional papers to leverage against the *reproduction difficulty* we
diagnosed in the normalization corpus (none of the 4 hardened models reached
`faithful`; the deepest blocker — where CRF saturation comes from — was only cracked
by the original R&H MATLAB). These candidates attack that difficulty in three ways:
**(A) code-bearing worked implementations**, **(B) canonical methods/review papers that
pin down the conventions the primary papers leave implicit** (semi-saturation constant,
Naka-Rushton CRF form, normalization-pool extent, attention-field shape), and
**(C) lineage / cross-validation neighbors** that let one model corroborate another.

Verified 2026-06-09 (DOIs, access, code links checked via web). **Code claims are only
listed where an actual repo/ModelDB/OSF/lab page was found; everything else is "none
found".**

> Already in the corpus (don't re-acquire): `heeger_1992`,
> `carandini_heeger_movshon_1997`, `ni_maunsell_2017`, `ni_maunsell_2019`,
> `denison2021`, `carrasco2021` (Li/Pan/Carrasco), `doostani_2023` (eLife 75726).
> The official **R&H 2009 `attentionModel.zip`** is already acquired — it's the
> reference implementation; verify against it first.

---

## Tier A — highest leverage (code-bearing / convention-pinning). Get these first.

| # | Paper | DOI | Access | Code | Why it helps |
|---|---|---|---|---|---|
| A1 | **Carandini & Heeger (2012). Normalization as a canonical neural computation.** *Nat. Rev. Neurosci.* 13(1):51–62. (Erratum 10.1038/nrn3424) | 10.1038/nrn3136 | 🔒 paywall | — (review) | The canonical normalization equation + parameter vocabulary (semi-saturation σ, the pool) that R&H inherits. The reference for what the divisive denominator "should" be. |
| A2 | **Simoncelli & Heeger (1998). A model of neuronal responses in area MT.** *Vision Res.* 38(5):743–761. | 10.1016/S0042-6989(97)00183-1 | 🔒 paywall | ✅ NYU **MTmodel** MATLAB: cns.nyu.edu/~lcv/MTmodel/ | Worked two-stage rectify→divisively-normalize implementation by Heeger himself — a second reference for *how* the normalization denominator is instantiated in code. |
| A3 | **Busse, Wade & Carandini (2009). Representation of concurrent stimuli by population activity in V1.** *Neuron* 64(6):931–942. | 10.1016/j.neuron.2009.11.004 | 🔒 paywall (free PMC2807406) | none found | The **two-stimulus** normalization regime (weighted-average / WTA) — exactly the colocated/competing-stimulus case where our 4C/4E geometry kept breaking. Empirical constraint on the pool's two-stimulus behavior. |
| A4 | **Martinez-Trujillo & Treue (2004). Feature-based attention increases selectivity of population responses in primate visual cortex.** *Curr. Biol.* 14(9):744–751. | 10.1016/j.cub.2004.04.028 | 🔒 paywall | none (empirical) | The **feature-similarity-gain** shape of the attention field — constrains how the R&H attention gain spreads over the *feature* axis, the thing SQ-006 (R&H) and the 4C sign error turned on. |

## Tier B — convention-pinning for CRF / pool extent / variability

| # | Paper | DOI | Access | Code | Why it helps |
|---|---|---|---|---|---|
| B1 | **Albrecht & Hamilton (1982). Striate cortex of monkey and cat: contrast response function.** *J. Neurophysiol.* 48(1):217–237. | 10.1152/jn.1982.48.1.217 | 🔒 paywall (old) | none | Origin of the hyperbolic-ratio (Naka-Rushton) CRF form + exponent/semi-saturation values — grounds the sigmoidal CRF shape our models must hit (the saturation we struggled to produce). |
| B2 | **Schwartz & Simoncelli (2001). Natural signal statistics and sensory gain control.** *Nat. Neurosci.* 4(8):819–825. | 10.1038/90526 | 🔒 paywall (author PDF cns.nyu.edu) | none found | Principled basis for **which units belong in the normalization pool** (the denominator weights) — informs the suppressive-field extent left underspecified in R&H. |
| B3 | **Brouwer & Heeger (2011). Cross-orientation suppression in human visual cortex.** *J. Neurophysiol.* 106(5):2108–2119. | 10.1152/jn.00540.2011 | 🔒 paywall (free PMC3214101) | none found | Evidence the pool sums **across orientations** → supports a broad/untuned θ-pool. This is precisely the `IthetaWidth=360` (near-flat orientation pool) that turned out to drive R&H saturation. |
| B4 | **Goris, Movshon & Simoncelli (2014). Partitioning neuronal variability.** *Nat. Neurosci.* 17(6):858–865. | 10.1038/nn.3711 | 🔒 paywall (free PMC4135707) | none found | Separates normalization-driven response changes from gain/excitability noise — tells a reproduction what variance it should *not* attribute to the deterministic model. |
| B5 | **Rust, Mante, Simoncelli & Movshon (2006). How MT cells analyze the motion of visual patterns.** *Nat. Neurosci.* 9(11):1421–1431. | 10.1038/nn1786 | 🔒 paywall | ✅ shared NYU **MTmodel** code (cns.nyu.edu/~lcv/MTmodel/) | The **tuned + untuned normalization** decomposition in MT — directly informs whether the R&H denominator needs a tuned component (relevant to Ni/Ray/Maunsell tuned-normalization too). |

## Tier C — lineage / cross-validation neighbors

| # | Paper | DOI | Access | Code | Why it helps |
|---|---|---|---|---|---|
| C1 | **Coen-Cagli, Kohn & Schwartz (2015). Flexible gating of contextual influences in natural vision.** *Nat. Neurosci.* 18(11):1648–1655. | 10.1038/nn.4128 | 🔒 paywall (free PMC4624479) | data on CRCNS; code none found | Direct descendant of our `cagly2012` (MGSM) — **gating** of normalization (when it's on/off). Cross-validates the MGSM branch. |
| C2 | **Reynolds & Chelazzi (2004). Attentional modulation of visual processing.** *Annu. Rev. Neurosci.* 27:611–647. | 10.1146/annurev.neuro.26.041002.131039 | 🔒 paywall | — (review) | Empirical grounding for contrast-gain vs response-gain attention effects — the phenomena the R&H attention-field shape must produce. Good orientation doc. |
| C3 | **Burg, Cadena, Denfield, Walker, Tolias, Bethge & Ecker (2021). Learning divisive normalization in primary visual cortex.** *PLoS Comput. Biol.* 17(6):e1009028. | 10.1371/journal.pcbi.1009028 | 🟢 **open access** | ✅ eckerlab.org/code/burg2021_learning_divisive_normalization; data G-Node GIN 10.12751/g-node.2e31e3 | OA code+data reference for a *learned* normalization denominator — a modern, fully-open worked example of the DN pool to compare conventions against. (Download is free; listed so you have the link.) |
| C4 | **Li, Pan & Carrasco (2021)** — *adaptation of R&H code* | repo: github.com/hsinhungli/overt-covert-attention | 🟢 code | ✅ MATLAB, explicitly adapted from R&H 2009 (needs matlabPyrTools) | A second, modernized worked implementation of the *same* attention model — a cross-check for our `carrasco2021`. (Free; grab the repo, not a PDF.) |

---

## Data-quality flags (caught during verification — don't propagate the errors)

- **Busse, Wade & Carandini 2009** pages are **931–942** (PubMed-verified); a circulating
  snippet says "778–780" — wrong.
- **Martinez-Trujillo & Treue 2004** title is "…in **primate visual cortex**", *not* "in V4".

## Suggested download order for tomorrow

1. **A1, A2** (Carandini & Heeger 2012 review; Simoncelli & Heeger 1998 + grab the
   MTmodel zip from cns.nyu.edu/~lcv/MTmodel/) — convention + a second code reference.
2. **A3, A4, B1, B3** — the four that directly target the two pain points that blocked us:
   two-stimulus geometry (A3), feature-attention-field shape (A4), the Naka-Rushton CRF
   form (B1), and the broad orientation pool behind saturation (B3).
3. **B2, B4, B5, C1, C2** — deeper convention/lineage support.
4. **C3, C4** are free downloads (no paywall) — grab the repos any time, no university needed.

> Acquisition note: when any of these is adopted as a model or a lineage/spec source,
> route it through Phase 0 (`skills/acquire-sources`) so `paper/SOURCES.md` +
> `code_refs.yaml`/`lineage_refs.yaml` stay the provenance record — same discipline that
> let the R&H author code settle SQ-005.
