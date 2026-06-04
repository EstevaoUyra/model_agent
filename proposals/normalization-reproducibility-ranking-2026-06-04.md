# Normalization-attention corpus — reproduction-readiness, RE-VERIFIED

Date: 2026-06-04. Method: every label checked against the **actual paper source on
disk** (PDF title page read directly, or — for dirs holding no PDF — the extractor's
write-once `citations.yaml` header, cross-checked against the publisher record at the
DOI). Code provenance checked by **resolving each URL**, distinguishing "confirmed
downloadable" from "stated to exist." Skeptical posture throughout: we assume the
prior ranking's misattribution may not be the only one.

---

## STEP 1 — Label verification (dir vs. corpus label vs. ACTUAL paper on disk)

PDF on disk = title page read directly (page 1 unless noted). No-PDF dirs read from
`article_aware/spec/citations.yaml` header + DOI resolution (publisher page).

| dir | corpus label (PAPERS.md) | ACTUAL on disk (authors · title · year · DOI · venue) | source read | MATCH? | note |
|---|---|---|---|---|---|
| heeger_1992 | Heeger 1992, *Vis. Neurosci.* | **David J. Heeger** · "Normalization of cell responses in cat striate cortex" · 1992 · 9:181-197 · Cambridge UP | **PDF p.1** (scanned; rendered to image, read visually) | **yes** | correct |
| carandini_heeger_movshon_1997 | Carandini, Heeger & Movshon 1997, *J. Neurosci.* | **Carandini, Heeger & Movshon** · "Linearity and Normalization in Simple Cells of the Macaque Primary Visual Cortex" · 1997 · 17(21):8621-8644 · J Neurosci | no PDF on disk → citations.yaml + DOI resolved (jneurosci.org) | **yes** | exact title is "…Simple Cells of the Macaque Primary Visual Cortex" (PAPERS paraphrases as "…macaque V1 simple cells") — same paper |
| reynolds_heeger_2009 | Reynolds & Heeger 2009, *Neuron* | **Reynolds & Heeger** · "The Normalization Model of Attention" · 2009 · Neuron 61:168-185 | extracted_text.md + SOURCES.md | **yes** | HUB; own code (see STEP 2) |
| reynolds_chelazzi_desimone_1999 | Reynolds, Chelazzi & Desimone 1999, *J. Neurosci.* | **John H. Reynolds, Leonardo Chelazzi, Robert Desimone** · "Competitive Mechanisms Subserve Attention in Macaque Areas V2 and V4" · 1999 · 19(5):1736-1753 · J Neurosci | **PDF p.1** | **yes** | correct |
| hermann2010 | Herrmann, Montaser-Kouhsari, Carrasco & Heeger 2010, *Nat. Neurosci.* | **Katrin Herrmann, Leila Montaser-Kouhsari, Marisa Carrasco, David J Heeger** · "When size matters: attention affects performance by contrast or response gain" · 2010 · Nat Neurosci | **PDF p.1** | **yes** | dir spells "hermann", paper is "Herrmann" (two r's) — cosmetic only |
| carrasco2021 | Li, Pan & Carrasco 2021, *Nat. Hum. Behav.* | **Hsin-Hung Li, Jasmine Pan, Marisa Carrasco** · "Different computations underlie overt presaccadic and covert spatial attention" · 2021 · 10.1038/s41562-021-01099-4 · Nat Hum Behav | **PDF p.1** | **yes** | dir "carrasco2021" is last-author shorthand; content correct |
| lee_maunsell_2009 | Lee & Maunsell 2009, *PLoS ONE* | **Joonyeol Lee, John H. R. Maunsell** · "A Normalization Model of Attentional Modulation of Single Unit Responses" · 2009 · PLoS ONE 4(2):e4651 | **PDF p.1** | **yes** | correct |
| ni_ray_maunsell_2012 | Ni, Ray & Maunsell 2012, *Neuron* | **Ni, Ray & Maunsell** · "Tuned Normalization Explains the Size of Attention Modulations" · 2012 · Neuron 73(4):803-813 · 10.1016/j.neuron.2012.01.006 | no PDF → citations.yaml + DOI/PubMed 22365552 | **yes** | correct |
| ni_maunsell_2017 | Ni & Maunsell 2017, *J. Neurophysiol.* | **Amy M. Ni, John H. R. Maunsell** · "Spatially tuned normalization explains attention modulation variance within neurons" · 2017 · J Neurophysiol 118(3):1903-1913 · 10.1152/jn.00218.2017 | extracted_text.md (PMC) p.1 | **yes** | correct |
| ni_maunsell_2019 | Ni & Maunsell 2019, *J. Neurosci.* | **Amy M. Ni, John H.R. Maunsell** · "Neuronal Effects of Spatial and Feature Attention Differ Due to Normalization" · 2019 · J Neurosci 39(28):5493-5505 | **PDF p.1** | **yes** | PAPERS paraphrases title; same paper |
| ghose_maunsell_2008 | Ghose & Maunsell 2008, *J. Neurosci.* | **Geoffrey M. Ghose, John H. R. Maunsell** · "Spatial Summation Can Explain the Attentional Modulation of Neuronal Responses to Multiple Stimuli in Area V4" · 2008 · 28(19):5115-5126 | **PDF p.1** | **yes** | correct |
| boynton_2009 | Boynton 2009, *Vis. Res.* | **Geoffrey M. Boynton** · "A framework for describing the effects of attention on visual responses" · 2009 · Vis Res 49(10):1129-1143 · 10.1016/j.visres.2008.11.001 | no PDF → citations.yaml + DOI/PubMed 19038281 | **yes** | correct |
| pestilli_ling_carrasco_2009 | Pestilli, Ling & Carrasco 2009, *Vis. Res.* | **Franco Pestilli, Sam Ling, Marisa Carrasco** · "A population-coding model of attention's influence on contrast response: Estimating neural effects from psychophysical data" · 2009 · Vis Res 49:1144-1153 | **PDF p.1** | **yes** | correct |
| **hara_gardner_2016** | ⚠ already-flagged: Schwedhelm, Krishna & Treue 2016 (PAPERS row), but **dir name + Phase-A spec say "Hara/Pestilli/Gardner"** | **Philipp Schwedhelm, B. Suresh Krishna, Stefan Treue** · "An Extended Normalization Model of Attention Accounts for Feature-Based Attentional Enhancement of Both Response and Coherence Gain" · 2016 · PLoS Comput Biol 12(12):e1005225 · 10.1371/journal.pcbi.1005225 | **PDF p.1** | **MISATTRIBUTED** | CONFIRMED on the PDF. Dir name and the spec's citation author-label are WRONG; the DOI/title/figure-content are Schwedhelm. The *true* "Hara, Pestilli & Gardner" is a different 2014 *Front. Comput. Neurosci.* paper (10.3389/fncom.2014.00012) NOT in this repo. PAPERS.md already corrects the citation; the dir rename is still pending. |
| denison2021 | Denison, Carrasco & Heeger 2021, *Nat. Hum. Behav.* | **Rachel N. Denison, Marisa Carrasco, David J. Heeger** · "A dynamic normalization model of temporal attention" · 2021 · Nat Hum Behav 5:1674-1685 · 10.1038/s41562-021-01129-1 | no PDF → SOURCE.md + DOI (PMC8678377) | **yes** | correct |
| doostani_2023 | Doostani, Hossein-Zadeh, Vaziri-Pashkam & Carrasco 2023, *eLife* | **Narges Doostani, Gholam-Ali Hossein-Zadeh, Maryam Vaziri-Pashkam** · "The normalization model predicts responses in the human visual cortex during object-based attention" · 2023 · eLife · 10.7554/eLife.75726 | **PDF p.1** | **yes (author-list nuance)** | PDF byline is **three authors** (Doostani, Hossein-Zadeh, Vaziri-Pashkam); PAPERS.md adds **"& Carrasco"** as a 4th author — Marisa Carrasco is the **Reviewing Editor**, NOT an author. PAPERS.md author list is wrong; the paper itself is correctly the right paper. |
| verhoef_maunsell_2017 | Verhoef & Maunsell 2017, *eLife* e17256 | **Bram-Ernst Verhoef, John H. R. Maunsell** · "Attention operates uniformly throughout the classical receptive field and the surround" · eLife 5:e17256 · 10.7554/eLife.17256 | no PDF → SOURCE.md + DOI (elifesciences.org) | **yes** | DOI resolves; eLife lists online year **2016**, citable year 2017 (same article). See STEP-2 code caveat — the ModelDB code attributed here is for a *different* Verhoef&Maunsell-2017 paper. |
| cagly2012 | Coen-Cagli, Dayan & Schwartz 2012, *PLoS Comput. Biol.* | **Ruben Coen-Cagli, Peter Dayan, Odelia Schwartz** · "Cortical Surround Interactions and Perceptual Salience via Natural Scene Statistics" · 2012 · PLoS Comput Biol 8(3):e1002405 | **PDF p.1** | **yes** | correct |

### Verification verdict
- **1 hard misattribution** (the one already known): `hara_gardner_2016/` = **Schwedhelm, Krishna & Treue (2016)**, not Hara/Pestilli/Gardner. CONFIRMED against the PDF title page (p.1, byline reads "Philipp Schwedhelm, B. Suresh Krishna, Stefan Treue"). No additional hard misattribution found.
- **2 author-list errors in PAPERS.md** (not dir misattributions, but worth fixing): (a) **doostani_2023** lists "& Carrasco" — Carrasco is the *Reviewing Editor*, not an author; the paper has 3 authors. (b) cosmetic dir-name spellings: `hermann2010` vs paper "Herrmann"; `carrasco2021`/`cagly2012` are last-author shorthands (content correct).
- **1 code→paper cross-attribution** (STEP 2): the ModelDB #243534 code in `verhoef_maunsell_2017/` belongs to the authors' *other* 2017 paper (Nat Neurosci nn.4572), not the eLife e17256 reproduced here.

---

## STEP 2 — CODE → PAPERS map (artifact-first)

Each row is a **distinct code artifact**, who wrote it, what it implements, URL-resolution
status, and every corpus paper it is relevant to.

| Artifact (URL) | Author / who wrote it | Implements | URL resolves? | Corpus papers it is relevant to |
|---|---|---|---|---|
| **`attentionModel.zip`** — https://snl.salk.edu/~reynolds/Normalization_Model_of_Attention/attentionModel.zip (mirror: cns.nyu.edu/heegerlab) | **Heeger & Reynolds (2009)** | The R&H Normalization Model of Attention engine: `attentionModel.m` (`R=E./(I+sigma)+baseline`, separable 2D suppressive conv), `Figure{2A..7C}.m` reproductions, Simoncelli matlabPyrTools helpers | **YES — confirmed downloadable** (fetched live: 297.6 KB `application/zip`, PK archive with the `.m` files; sha256 0f4e114… recorded in hara SOURCES) | **OWN** for `reynolds_heeger_2009`. **SHARED engine** reused by: `hara_gardner_2016`/Schwedhelm (its sims are "custom MATLAB scripts based on the code of Reynolds & Heeger"); and the conceptual lineage all "reuses R&H" papers extend (`hermann2010`, `carrasco2021`, `doostani_2023`) — but those do NOT ship this zip themselves; they reimplement from the R&H spec. |
| **OSF `dkx7n`** — https://osf.io/dkx7n (API: api.osf.io/v2/nodes/dkx7n) | **Denison, Carrasco & Heeger** | "Model code and behavioral data for … A dynamic normalization model of temporal attention" (the paper's OWN dynamic-normalization model + behavioral data) | **YES — confirmed** (OSF API returns node title = exact paper title) | **OWN** for `denison2021` only. |
| **ModelDB #243534** — https://modeldb.science/citations/243534 | **Verhoef & Maunsell** | Code for **"Attention-related changes in correlated neuronal activity arise from normalization mechanisms"** (Nat Neurosci 2017, nn.4572) — a *different* Verhoef&Maunsell 2017 paper | **Entry page resolves; code download = HTTP 403** (not retrievable; "stated to exist, not confirmed downloadable") | Relevant to `verhoef_maunsell_2017`'s authors but is the **companion Nat Neurosci paper's code**, NOT the eLife e17256 "operates uniformly" model in the dir. Treat as adjacent, not this paper's own published code for the reproduced model. |
| **github.com/racheldenison/temporal-attention** | Rachel Denison | *Experiment* (task/stimulus) code for the temporal-attention psychophysics | not re-fetched this pass (stated in SOURCE.md) | `denison2021` — experiment code, not the model; the model code is the OSF artifact above. |

**No other code artifacts exist.** Every remaining Cluster-1 paper's own provenance.md
states verbatim **"No author code is published"** and the model is **"fully specified by
closed-form equations in the paper."** Verified for: heeger_1992, carandini_heeger_movshon_1997,
reynolds_chelazzi_desimone_1999, lee_maunsell_2009, ni_ray_maunsell_2012, ni_maunsell_2017,
ni_maunsell_2019, ghose_maunsell_2008, boynton_2009, pestilli_ling_carrasco_2009, cagly2012,
doostani_2023.

### Per-paper code classification (OWN / SHARED / NONE)

| Paper | Code class | Artifact named | Notes |
|---|---|---|---|
| reynolds_heeger_2009 | **OWN** | `attentionModel.zip` (Heeger&Reynolds) | Authoritative numeric source; confirmed downloadable. |
| denison2021 | **OWN** | OSF `dkx7n` (+ experiment code on GitHub) | Confirmed via OSF API. |
| hara_gardner_2016 (=Schwedhelm 2016) | **SHARED/REUSED** | R&H `attentionModel.zip` | Paper's sims are "custom scripts based on R&H code"; Schwedhelm's own scripts were never published. NOT its own code. |
| hermann2010 | **SHARED (spec-level)** | R&H NMoA (no zip shipped) | Reuses R&H model; reimplemented from spec. No own code. |
| carrasco2021 | **SHARED (spec-level)** | R&H NMoA | Reuses/extends R&H; no own code published. |
| doostani_2023 | **SHARED (spec-level)** | R&H divisive primitive | Reuses R&H normalization at scalar shape; no own code. |
| verhoef_maunsell_2017 | **NONE (for THIS paper's model)** | — (ModelDB 243534 is the *other* 2017 paper, and is 403) | The reproduced eLife e17256 model has no confirmed own code; the deposited ModelDB code is the companion Nat Neurosci paper and was not retrievable. |
| heeger_1992 | **NONE** | — | Closed-form (Eqs. 1-13). |
| carandini_heeger_movshon_1997 | **NONE** | — | Closed-form (Eqs. 5-7 + RC transfer fn). |
| reynolds_chelazzi_desimone_1999 | **NONE** | — | Closed-form (4 eqs in Fig 2). |
| lee_maunsell_2009 | **NONE** | — | Closed-form (Eqs. 3-5, 8, 10). |
| ni_ray_maunsell_2012 | **NONE** | — | Closed-form (Eqs. 1, 2, 3a/b). |
| ni_maunsell_2017 | **NONE** | — | Closed-form (Eqs. 1-9). |
| ni_maunsell_2019 | **NONE** | — | Closed-form. |
| ghose_maunsell_2008 | **NONE** | — | Closed-form (Eqs. 1-5). |
| boynton_2009 | **NONE** | — | Closed-form (Eqs. 1-5). |
| pestilli_ling_carrasco_2009 | **NONE** | — | Closed-form (Eqs. 1-10). |
| cagly2012 | **NONE** | — | MGSM closed-form / inference; no author code in provenance. |

**Reuse summary (explicit):** the single artifact `attentionModel.zip` is the OWN code of
**reynolds_heeger_2009** and is the engine the SHARED-class papers (Schwedhelm/hara,
hermann2010, carrasco2021, doostani_2023) build on — but only Schwedhelm/hara literally
derives from that code; the others reimplement from the R&H spec. A SHARED engine does
**not** count as a paper's own code.

---

## STEP 3 — Comparable model-output panels (curves/CRFs/tuning we can reproduce & overlay)

Counts are model-output panels (CRFs, tuning curves, modulation-index curves, d′ functions)
— excludes photos, schematics, and raw single-cell scatter that aren't model predictions.
"committed fig images" = digitized comparison images already in `article_aware/figures/`.

| Paper | Comparable model-output panels | Quant & digitizable | Qualitative only | committed fig images |
|---|---|---|---|---|
| reynolds_heeger_2009 | ~7 (Fig 2-7 CRFs + attention-field heatmaps) | high — CRFs, gain regimes | heatmaps semi-quant | 7 |
| boynton_2009 | ~8 (parametric attention CRFs across 7 re-fit studies) | high — many CRFs | — | 8 |
| pestilli_ling_carrasco_2009 | ~6-12 (population CRFs, contrast/response-gain) | high | some pop schematics | 6 |
| hermann2010 | ~4 (contrast-vs-response-gain psychometric/CRF, size dependence) | high | — | 2 |
| carandini_heeger_movshon_1997 | ~4-8 (contrast saturation, masking, plaids) | high — classic CRFs | — | 4 |
| lee_maunsell_2009 | ~4-6 (tuning-curve scaling, normalization vs attention) | high | — | 3 |
| ni_ray_maunsell_2012 | ~4-6 (tuned-normalization modulation-vs-strength) | high | — | 1 |
| ghose_maunsell_2008 | ~4-6 (summation-model fits to paired-stimulus responses) | mid-high | per-cell fits | 3 |
| heeger_1992 | ~6-10 (normalization fits to cat V1) | high | scanned figs harder to digitize | 5 |
| hara_gardner_2016 (=Schwedhelm) | ~3 (Fig7/8 narrow-vs-broad attention, coherence gain) | mid — fitted-curve overlays | partly qualitative | 3 |
| ni_maunsell_2017 | ~2-4 (within-neuron modulation/normalization covariance) | mid | scatter-heavy | 2 |
| ni_maunsell_2019 | ~1-4 (spatial vs feature modulation) | mid | scatter-heavy | 1 |
| denison2021 | ~2-4 (d′-vs-SOA dynamic curves) | mid — needs ODE sim + fitted params (some CODE-only) | — | 2 |
| reynolds_chelazzi_desimone_1999 | ~2 (model response-toward-attended curves) | mid | mostly raw V2/V4 data | 2 |
| carrasco2021 | ~1-2 (presaccadic response-gain vs model prediction) | low-mid — mostly psychophysics, model is a comparison | model is illustrative | 1 |
| doostani_2023 | ~5 (normalization vs weighted-sum fits to fMRI) | mid — fMRI, not neural CRFs | — | 5 |
| verhoef_maunsell_2017 | ~4-6 (spatially-tuned normalization fits across RF/surround) | mid-high (87% var explained) | per-location fits | 4 |
| cagly2012 | ~7-10 (surround suppression/facilitation, orientation tuning) | high but heavy (MGSM inference, natural-image fit) | — | 7 |

---

## STEP 4 — Re-ranked, best-to-reproduce on top

**Weighting (stated):** primarily (1) number of *comparable quantitative, digitizable
model-output panels*; then (2) *model-description completeness* (fully closed-form & all
params printed > params partly via code/fit > heavy inference machinery); then (3) *code*,
where **OWN code > SHARED engine > none**, and a SHARED engine is only a mild lift (you still
reimplement from the spec). Misattributed dir ranked as the **paper it actually contains**.

| Rank | dir (ACTUAL paper) | Comparable quant figs | Model completeness | Code | Why here |
|---|---|---|---|---|---|
| 1 | **reynolds_heeger_2009** (Reynolds & Heeger 2009) | ~7, high | full + Table 1 | **OWN** (`attentionModel.zip`, confirmed) | Only paper with confirmed-downloadable OWN engine AND many CRFs; the reference implementation everything else leans on. |
| 2 | **boynton_2009** (Boynton 2009) | ~8, high | fully closed-form (Eqs 1-5), all params printed | none | Most comparable CRFs of any closed-form paper; one parametric model re-fit to 7 studies — extremely reproducible from equations alone. |
| 3 | **carandini_heeger_movshon_1997** (CHM 1997) | ~4-8, high | fully closed-form, canonical | none | Foundational normalization; clean CRFs/masking/plaids, equations uniquely determine the model. |
| 4 | **pestilli_ling_carrasco_2009** (Pestilli/Ling/Carrasco 2009) | ~6-12, high | closed-form (Eqs 1-10), all FIXED params | none | Many population-CRF panels, contrast-vs-response-gain; fully specified. (PAPERS audit currently "illustrative" — upside.) |
| 5 | **lee_maunsell_2009** (Lee & Maunsell 2009) | ~4-6, high | closed-form (Eqs 3-5,8,10) | none | Clean tuning-scaling & normalization-vs-attention curves; canonical MT data fits. |
| 6 | **hermann2010** (Herrmann et al. 2010) | ~4, high | reuses R&H, equations given | SHARED (R&H, spec-level) | Crisp contrast-vs-response-gain predictions; reuses R&H so engine is known — but reimplement-from-spec. |
| 7 | **ni_ray_maunsell_2012** (Ni/Ray/Maunsell 2012) | ~4-6, high | closed-form (Eqs 1,2,3a/b) | none | Tuned-normalization modulation curves; well-specified. |
| 8 | **ghose_maunsell_2008** (Ghose & Maunsell 2008) | ~4-6, mid-high | closed-form (Eqs 1-5) | none | Summation-model fits; some per-cell fitting needed. |
| 9 | **heeger_1992** (Heeger 1992) | ~6-10, high | closed-form (Eqs 1-13) | none | Strong content, but the only **scanned** PDF — figures harder to digitize, OCR-less. |
| 10 | **cagly2012** (Coen-Cagli/Dayan/Schwartz 2012) | ~7-10, high | own MGSM, but heavy | none | Many surround panels, but reproduction needs natural-image inference machinery — high effort despite figure richness. |
| 11 | **verhoef_maunsell_2017** (Verhoef & Maunsell 2017, eLife e17256) | ~4-6, mid-high | own spatially-tuned norm; per-location FITS | NONE for this model (ModelDB code = companion paper, 403) | 87% var explained, good fits — but per-location fitting and no retrievable own code for THIS paper. |
| 12 | **doostani_2023** (Doostani et al. 2023) | ~5, mid | reuses R&H scalar primitive | SHARED (R&H, spec-level) | fMRI (not neural CRFs); normalization-vs-weighted-sum model comparison — reproducible but indirect. |
| 13 | **ni_maunsell_2017** (Ni & Maunsell 2017) | ~2-4, mid | closed-form (Eqs 1-9) | none | Within-neuron covariance; scatter-heavy, fewer overlayable curves. |
| 14 | **hara_gardner_2016** = **Schwedhelm, Krishna & Treue 2016** | ~3, mid | extends R&H; fit is stubbed (no optimizer published) | SHARED (R&H zip) | MISATTRIBUTED dir — ranked as Schwedhelm 2016. Fewer comparable panels; key fitted values only in legends; fit not reproducible without re-deriving the NLS optimizer. |
| 15 | **denison2021** (Denison/Carrasco/Heeger 2021) | ~2-4, mid | dynamic ODE; some params **CODE-only** (OSF) | **OWN** (OSF dkx7n, confirmed) | Has confirmed OWN code (lifts it), but the dynamic model needs ODE sim + several params only in the OSF code/figures, and few comparable panels. |
| 16 | **reynolds_chelazzi_desimone_1999** (RCD 1999) | ~2, mid | closed-form (4 eqs) | none | Mostly raw V2/V4 physiology; the model is a small curve set — few comparable model-output panels. |
| 17 | **ni_maunsell_2019** (Ni & Maunsell 2019) | ~1-4, mid | closed-form | none | Spatial-vs-feature; scatter-dominated, few overlayable model curves. |
| 18 | **carrasco2021** (Li/Pan/Carrasco 2021) | ~1-2, low-mid | model used as a *comparison*, response-gain only | SHARED (R&H, spec-level) | Mostly psychophysics; the normalization model is the foil being tested, not a rich set of model outputs. PAPERS audit "illustrative." Last for comparability. |

---

## Headline findings
1. **Misattribution CONFIRMED and bounded to one:** `hara_gardner_2016/` actually contains **Schwedhelm, Krishna & Treue (2016)** (PLoS Comput Biol 12(12):e1005225) — verified on the PDF title page. No second *hard* misattribution exists in the corpus.
2. **Two softer label defects** to fix in PAPERS.md: `doostani_2023` wrongly lists **"& Carrasco"** (she is the *Reviewing Editor*, the paper has 3 authors); and the `verhoef_maunsell_2017` "author code on ModelDB #243534" is the authors' **other** 2017 paper (Nat Neurosci nn.4572), not the eLife model reproduced here.
3. **Code reality:** exactly **2 papers have confirmed-downloadable OWN code** — `reynolds_heeger_2009` (`attentionModel.zip`, live) and `denison2021` (OSF `dkx7n`, live via API). The R&H zip is the **one shared engine**; Schwedhelm/hara derives from it, hermann/carrasco/doostani only reuse the R&H *spec*. **12 papers have NONE** (closed-form). `verhoef`'s deposited code is the companion paper's and is 403.
4. **Best reproduction targets** are the closed-form, CRF-rich papers — Boynton 2009, CHM 1997, Pestilli 2009, Lee & Maunsell 2009 — with R&H 2009 on top because it adds confirmed OWN code.
