#!/usr/bin/env python3
"""Build the 200-paper candidate landscape and the top-100 reproduction ranking.

Data source: 8 parallel research scouts (OpenAlex/Semantic Scholar citation counts +
OA status, code availability, figure quality, compute flag, reproducibility fit,
traced lineage), run 2026-06-12. See corpus-candidates-200 / corpus-top100-ranking.

Composite score (balanced blend; user-chosen 2026-06-12). Weights sum to 1.0:
  repro_fit  0.30  - can we build+parametrize it from the paper? (core)
  importance 0.22  - log-scaled citation count (model influence)
  figures    0.12  - clear quantitative model-output panels to reproduce
  code       0.12  - author code available (faithfulness grounding)
  compute    0.12  - cheap to iterate (heavy ranked low, per user)
  phylogeny  0.12  - lineage richness + connection to the existing corpus

in_corpus papers are listed in the 200 (for phylogeny) but EXCLUDED from the
rankable top-100 (already reproduced).
"""
import math, os, json

# Cluster names
CLUSTERS = {
    "C1": "Normalization & attention (R&H family)",
    "C2": "Sparse / efficient coding",
    "C3": "Predictive coding / free-energy",
    "C4": "Motion-energy & MT models",
    "C5": "V1 receptive-field / LN / subunit models",
    "C6": "Bayesian / ideal-observer / cue combination",
    "C7": "Texture / mid-level / saliency / contour",
    "C8": "Decision-making / evidence accumulation",
    "C9": "Attractor networks / working memory / neural fields",
    "C10": "Hippocampal & spatial (place & grid cells)",
    "C11": "Population / probabilistic coding",
    "C12": "Motor control & cerebellum",
    "C13": "Reinforcement learning / reward / basal ganglia",
    "C14": "Synaptic plasticity / learning rules",
    "C15": "Single-neuron & network dynamics",
}
# Clusters anchored by a paper already in our corpus (cross-validation value)
CORPUS_CLUSTERS = {"C1", "C2", "C3"}

# Columns: key, label, venue, year, doi, cluster, cites, oa, link, code, fig, compute, repro, corpus, lineage
# oa: open|gold|green|bronze|hybrid = free full text exists; closed = paywalled
# code: yes|partial|unknown|no  | compute: light|freezable|heavy
ROWS = [
# ---------------- C1 Normalization & attention ----------------
("heeger_1992","Heeger 1992 — Normalization of cell responses in cat striate cortex","Vis. Neurosci.",1992,"10.1017/S0952523800009640","C1",1909,"closed","https://doi.org/10.1017/S0952523800009640","no",4,"light",4,True,"root of normalization; ->chm1997,ch2012,rh2009"),
("carandini_heeger_movshon_1997","Carandini, Heeger & Movshon 1997 — Linearity and normalization in macaque V1 simple cells","J. Neurosci.",1997,"10.1523/JNEUROSCI.17-21-08621.1997","C1",967,"bronze","https://www.jneurosci.org/content/jneuro/17/21/8621.full.pdf","no",4,"light",4,True,"parent heeger_1992; ->ch2012,rust2006"),
("carandini_heeger_2012","Carandini & Heeger 2012 — Normalization as a canonical neural computation","Nat. Rev. Neurosci.",2012,"10.1038/nrn3136","C1",2003,"closed","https://doi.org/10.1038/nrn3136","no",2,"light",3,False,"synthesis/review of the normalization trunk"),
("schwartz_simoncelli_2001","Schwartz & Simoncelli 2001 — Natural signal statistics and sensory gain control","Nat. Neurosci.",2001,"10.1038/90526","C1",872,"closed","https://doi.org/10.1038/90526","no",4,"freezable",3,False,"normalization from natural stats; ->coen_cagli_2012"),
("cavanaugh_bair_movshon_2002","Cavanaugh, Bair & Movshon 2002 — RF center-surround interaction in macaque V1","J. Neurophysiol.",2002,"10.1152/jn.00692.2001","C1",821,"closed","https://doi.org/10.1152/jn.00692.2001","no",4,"light",3,False,"ratio-of-Gaussians surround; ->coen_cagli_2012"),
("busse_wade_carandini_2009","Busse, Wade & Carandini 2009 — Representation of concurrent stimuli by population activity","Neuron",2009,"10.1016/j.neuron.2009.11.004","C1",270,"bronze","https://www.cell.com/article/S0896627309008861/pdf","no",4,"light",4,False,"weighted-average normalization; ->ni_ray_maunsell_2012"),
("brouwer_heeger_2011","Brouwer & Heeger 2011 — Cross-orientation suppression in human visual cortex","J. Neurophysiol.",2011,"10.1152/jn.00540.2011","C1",248,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/3214101","no",3,"light",3,False,"normalization on fMRI"),
("reynolds_chelazzi_desimone_1999","Reynolds, Chelazzi & Desimone 1999 — Competitive mechanisms subserve attention in V2/V4","J. Neurosci.",1999,"10.1523/JNEUROSCI.19-05-01736.1999","C1",1260,"bronze","https://www.jneurosci.org/content/jneuro/19/5/1736.full.pdf","no",3,"light",3,True,"biased-competition root; ->rh2009"),
("reynolds_pasternak_desimone_2000","Reynolds, Pasternak & Desimone 2000 — Attention increases sensitivity of V4 neurons","Neuron",2000,"10.1016/S0896-6273(00)81206-4","C1",1054,"bronze","https://www.cell.com/article/S0896627300812064/pdf","no",3,"light",3,False,"contrast-gain attention; ->rh2009"),
("treue_martinez_1999","Treue & Martinez-Trujillo 1999 — Feature-based attention influences motion processing gain","Nature",1999,"10.1038/21176","C1",1527,"green","https://doi.org/10.1038/21176","no",2,"light",2,False,"feature-gain root; ->martinez_treue_2004"),
("martinez_treue_2004","Martinez-Trujillo & Treue 2004 — Feature-based attention increases population selectivity","Curr. Biol.",2004,"10.1016/j.cub.2004.04.028","C1",735,"bronze","https://www.cell.com/article/S0960982204002684/pdf","no",3,"light",3,False,"feature-similarity-gain model"),
("williford_maunsell_2006","Williford & Maunsell 2006 — Effects of spatial attention on contrast response functions in V4","J. Neurophysiol.",2006,"10.1152/jn.01207.2005","C1",367,"closed","https://doi.org/10.1152/jn.01207.2005","no",3,"light",3,False,"contrast- vs response-gain; ->rh2009"),
("ghose_maunsell_2008","Ghose & Maunsell 2008 — Spatial summation explains attentional modulation in V4","J. Neurosci.",2008,"10.1523/JNEUROSCI.0138-08.2008","C1",88,"bronze","https://www.jneurosci.org/content/jneuro/28/19/5115.full.pdf","no",3,"light",3,True,"spatial-summation normalization"),
("boynton_2009","Boynton 2009 — A framework for describing the effects of attention on visual responses","Vis. Res.",2009,"10.1016/j.visres.2008.11.001","C1",138,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/2724072","no",4,"light",4,True,"normalization-attention synthesis"),
("reynolds_heeger_2009","Reynolds & Heeger 2009 — The Normalization Model of Attention","Neuron",2009,"10.1016/j.neuron.2009.01.002","C1",1553,"bronze","https://www.cell.com/article/S0896627309000038/pdf","no",5,"light",5,True,"HUB; parent of most of cluster"),
("lee_maunsell_2009","Lee & Maunsell 2009 — A normalization model of attentional modulation of single-unit responses","PLoS ONE",2009,"10.1371/journal.pone.0004651","C1",269,"gold","https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0004651&type=printable","no",4,"light",5,True,"child of rh2009"),
("ni_ray_maunsell_2012","Ni, Ray & Maunsell 2012 — Tuned normalization explains the size of attention modulations","Neuron",2012,"10.1016/j.neuron.2012.01.006","C1",123,"bronze","https://www.cell.com/article/S0896627312000487/pdf","no",4,"light",4,True,"tuned normalization"),
("ni_maunsell_2017","Ni & Maunsell 2017 — Spatially tuned normalization explains attention-modulation variance","J. Neurophysiol.",2017,"10.1152/jn.00218.2017","C1",50,"bronze","https://www.physiology.org/doi/pdf/10.1152/jn.00218.2017","no",4,"light",4,True,"spatially tuned normalization"),
("ni_maunsell_2019","Ni & Maunsell 2019 — Spatial and feature attention differ due to normalization","J. Neurosci.",2019,"10.1523/JNEUROSCI.2106-18.2019","C1",47,"bronze","https://www.jneurosci.org/content/jneuro/39/28/5493.full.pdf","no",4,"light",4,True,"spatial vs feature"),
("verhoef_maunsell_2017","Verhoef & Maunsell 2017 — Attention operates uniformly throughout RF and surround","eLife",2017,"10.7554/eLife.17256","C1",22,"gold","https://doi.org/10.7554/eLife.17256","no",3,"light",3,True,"RF-uniformity test"),
("pestilli_ling_carrasco_2009","Pestilli, Ling & Carrasco 2009 — Population-coding model of attention on contrast response","Vis. Res.",2009,"10.1016/j.visres.2008.09.018","C1",113,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/2743869","no",4,"light",4,True,"psychophysics-to-neural model"),
("herrmann_2010","Herrmann, Montaser-Kouhsari, Carrasco & Heeger 2010 — Attention by contrast or response gain","Nat. Neurosci.",2010,"10.1038/nn.2669","C1",375,"closed","https://doi.org/10.1038/nn.2669","no",4,"light",4,True,"contrast vs response gain via size"),
("schwedhelm_2016","Schwedhelm, Krishna & Treue 2016 — Extended normalization model (feature-based gain)","PLoS Comput. Biol.",2016,"10.1371/journal.pcbi.1005225","C1",60,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005225","no",4,"light",4,True,"reuses R&H (dir hara_gardner_2016)"),
("denison2021","Denison, Carrasco & Heeger 2021 — A dynamic normalization model of temporal attention","Nat. Hum. Behav.",2021,"10.1038/s41562-021-01129-1","C1",78,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/8678377","yes",5,"light",5,True,"dynamic/temporal; OSF code"),
("doostani_2023","Doostani, Hossein-Zadeh & Vaziri-Pashkam 2023 — Normalization in object-based attention","eLife",2023,"10.7554/eLife.75726","C1",9,"gold","https://doi.org/10.7554/eLife.75726","yes",4,"light",4,True,"reuses R&H; fMRI"),
("li_pan_carrasco_2021","Li, Pan & Carrasco 2021 — Presaccadic vs covert spatial attention","Nat. Hum. Behav.",2021,"10.1038/s41562-021-01099-4","C1",69,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/8552811","unknown",4,"light",4,True,"reuses R&H (dir carrasco2021)"),
("coen_cagli_2012","Coen-Cagli, Dayan & Schwartz 2012 — Surround interactions via natural scene statistics (MGSM)","PLoS Comput. Biol.",2012,"10.1371/journal.pcbi.1002405","C1",126,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002405","unknown",4,"freezable",3,True,"MGSM flexible normalization"),
("goris_movshon_simoncelli_2014","Goris, Movshon & Simoncelli 2014 — Partitioning neuronal variability","Nat. Neurosci.",2014,"10.1038/nn.3711","C1",621,"closed","https://doi.org/10.1038/nn.3711","no",3,"light",2,False,"modulated-Poisson; needs spike data to fit"),
("heeger_2017_organics","Heeger 2017 — Theory of cortical function (ORGaNICs)","PNAS",2017,"10.1073/pnas.1619788114","C1",240,"bronze","https://www.pnas.org/content/pnas/114/8/1773.full.pdf","no",4,"freezable",4,False,"recurrent dynamic normalization framework"),
("heeger_zemlianova_2020","Heeger & Zemlianova 2020 — A recurrent circuit implements normalization (V1 dynamics)","PNAS",2020,"10.1073/pnas.2005417117","C1",74,"bronze","https://www.pnas.org/content/pnas/117/36/22494.full.pdf","yes",4,"freezable",4,False,"ORGaNICs concrete; NYU archive code"),
# ---------------- C2 Sparse / efficient coding ----------------
("barlow_1961","Barlow 1961 — Possible principles underlying transformations of sensory messages","Sensory Communication",1961,"","C2",6500,"closed","https://www.cnbc.cmu.edu/~tai/readings/tai_share/barlow.pdf","no",1,"light",1,False,"efficient-coding conceptual root"),
("laughlin_1981","Laughlin 1981 — A simple coding procedure enhances a neuron's information capacity","Z. Naturforsch. C",1981,"10.1515/znc-1981-9-1040","C2",1041,"hybrid","https://www.degruyter.com/document/doi/10.1515/znc-1981-9-1040/pdf","no",4,"light",3,False,"histogram-equalization in fly"),
("srinivasan_laughlin_dubs_1982","Srinivasan, Laughlin & Dubs 1982 — Predictive coding: a fresh view of inhibition in the retina","Proc. R. Soc. B",1982,"10.1098/rspb.1982.0085","C2",1079,"closed","https://doi.org/10.1098/rspb.1982.0085","no",3,"light",3,False,"coins predictive coding; ->rao_ballard_1999"),
("atick_redlich_1990","Atick & Redlich 1990 — Towards a theory of early visual processing","Neural Comput.",1990,"10.1162/neco.1990.2.3.308","C2",590,"closed","https://doi.org/10.1162/neco.1990.2.3.308","no",3,"light",3,False,"retinal whitening/decorrelation"),
("olshausen_field_1996","Olshausen & Field 1996 — Emergence of simple-cell RFs by learning a sparse code","Nature",1996,"10.1038/381607a0","C2",5834,"closed","https://www.rctn.org/bruno/papers/sparse-coding.pdf","yes",5,"light",5,True,"sparse-coding HUB; sparsenet code"),
("olshausen_field_1997","Olshausen & Field 1997 — Sparse coding with an overcomplete basis set","Vis. Res.",1997,"10.1016/S0042-6989(97)00169-7","C2",3720,"closed","https://www.rctn.org/bruno/papers/VR.pdf","yes",4,"light",5,False,"overcomplete extension; sparsenet code"),
("bell_sejnowski_1997","Bell & Sejnowski 1997 — The 'independent components' of natural scenes are edge filters","Vis. Res.",1997,"10.1016/S0042-6989(97)00121-1","C2",2269,"green","https://www.cnl.salk.edu/~tony/ptrs.html","yes",4,"light",4,True,"infomax ICA"),
("van_hateren_van_der_schaaf_1998","van Hateren & van der Schaaf 1998 — ICA filters of natural images vs simple cells","Proc. R. Soc. B",1998,"10.1098/rspb.1998.0303","C2",1163,"green","https://research.rug.nl/files/3200279/1998ProcRSocLondBvHateren1.pdf","yes",5,"light",4,False,"quantitative RF-stat match"),
("van_hateren_ruderman_1998","van Hateren & Ruderman 1998 — ICA of natural image sequences -> spatiotemporal filters","Proc. R. Soc. B",1998,"10.1098/rspb.1998.0577","C2",429,"green","https://pure.rug.nl/ws/files/3197234/1998ProcRSocLondBvHateren2.pdf","no",4,"light",4,False,"space-time ICA"),
("hyvarinen_hoyer_2001","Hyvarinen & Hoyer 2001 — Two-layer sparse coding -> simple/complex cells + topography","Vis. Res.",2001,"10.1016/S0042-6989(01)00114-6","C2",272,"closed","https://www.cs.helsinki.fi/u/ahyvarin/papers/VR01.pdf","yes",5,"light",5,False,"topographic ICA; imageica code"),
("hyvarinen_hoyer_2000","Hyvarinen & Hoyer 2000 — Phase/shift-invariant features via feature subspaces (ISA)","Neural Comput.",2000,"10.1162/089976600300015312","C2",546,"closed","https://www.cs.helsinki.fi/u/ahyvarin/papers/NC00.pdf","yes",4,"light",5,False,"complex-cell pooling root; imageica code"),
("lewicki_sejnowski_2000","Lewicki & Sejnowski 2000 — Learning overcomplete representations","Neural Comput.",2000,"10.1162/089976600300015826","C2",1142,"closed","https://papers.cnl.salk.edu/PDFs/Learning%20Overcomplete%20Representations_2000_3917.pdf","unknown",3,"light",3,False,"overcomplete ICA"),
("smith_lewicki_2006","Smith & Lewicki 2006 — Efficient auditory coding","Nature",2006,"10.1038/nature04485","C2",653,"closed","https://www.cs.cmu.edu/~lewicki/papers/smith-lewicki-nature06.pdf","no",5,"light",3,False,"sparse coding of sound (needs corpus)"),
("karklin_lewicki_2005","Karklin & Lewicki 2005 — Hierarchical Bayesian model of nonlinear regularities","Neural Comput.",2005,"10.1162/0899766053011474","C2",160,"closed","https://doi.org/10.1162/0899766053011474","unknown",3,"light",3,False,"density-component hierarchy; ->kl2009"),
("karklin_lewicki_2009","Karklin & Lewicki 2009 — Emergence of complex cell properties by learning to generalize","Nature",2009,"10.1038/nature07481","C2",225,"closed","https://www.cs.cmu.edu/~lewicki/papers/karklin-lewicki-nature09.pdf","unknown",5,"light",4,True,"hierarchical variance model"),
("rozell2008","Rozell, Johnson, Baraniuk & Olshausen 2008 — Sparse coding via local competition (LCA)","Neural Comput.",2008,"10.1162/neco.2008.03-07-486","C2",475,"closed","https://www.rctn.org/bruno/papers/lca.pdf","yes",4,"light",5,True,"dynamical-systems sparse coding"),
("zhu_rozell_2013","Zhu & Rozell 2013 — Nonclassical RF effects emerge from sparse coding","PLoS Comput. Biol.",2013,"10.1371/journal.pcbi.1003191","C2",190,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003191","unknown",5,"light",4,True,"LCA -> nCRF/surround"),
("vinje_gallant_2000","Vinje & Gallant 2000 — Sparse coding and decorrelation in V1 during natural vision","Science",2000,"10.1126/science.287.5456.1273","C2",1345,"closed","https://doi.org/10.1126/science.287.5456.1273","no",4,"light",1,False,"data paper (comparison target)"),
("simoncelli_olshausen_2001","Simoncelli & Olshausen 2001 — Natural image statistics and neural representation","Annu. Rev. Neurosci.",2001,"10.1146/annurev.neuro.24.1.1193","C2",2532,"closed","https://www.cns.nyu.edu/pub/eero/simoncelli01-reprint.pdf","no",2,"light",1,False,"review"),
# ---------------- C3 Predictive coding ----------------
("rao_ballard_1999","Rao & Ballard 1999 — Predictive coding in the visual cortex (extra-classical RF)","Nat. Neurosci.",1999,"10.1038/4580","C3",5718,"closed","https://www.cs.utexas.edu/~dana/nn.pdf","yes",4,"light",4,True,"predictive-coding HUB"),
("spratling_2008","Spratling 2008 — Reconciling predictive coding and biased competition","Front. Comput. Neurosci.",2008,"10.3389/neuro.10.004.2008","C3",155,"gold","https://www.frontiersin.org/articles/10.3389/neuro.10.004.2008/full","no",3,"light",4,False,"PC/BC-DIM unification; links to C1"),
("spratling_2010","Spratling 2010 — Predictive coding as a model of response properties in V1","J. Neurosci.",2010,"10.1523/JNEUROSCI.4911-09.2010","C3",216,"bronze","https://www.jneurosci.org/content/30/9/3531","yes",5,"light",5,True,"PC/BC-DIM V1; author code"),
("spratling_2012","Spratling 2012 — Predictive coding accounts for V1 response from reverse correlation","Biol. Cybern.",2012,"10.1007/s00422-012-0477-7","C3",67,"closed","https://nms.kcl.ac.uk/michael.spratling/Doc/dim_learning.pdf","yes",4,"light",5,True,"adds learning to PC/BC-DIM"),
("friston_2005","Friston 2005 — A theory of cortical responses","Phil. Trans. R. Soc. B",2005,"10.1098/rstb.2005.1622","C3",4759,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/1569488","partial",2,"light",2,False,"free-energy/hierarchical-PC theory"),
("friston_kiebel_2009","Friston & Kiebel 2009 — Predictive coding under the free-energy principle","Phil. Trans. R. Soc. B",2009,"10.1098/rstb.2008.0300","C3",1641,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/2666703","partial",3,"light",3,False,"DEM hierarchical-dynamic-model"),
("bogacz2017","Bogacz 2017 — A tutorial on the free-energy framework for perception and learning","J. Math. Psychol.",2017,"10.1016/j.jmp.2015.11.003","C3",309,"hybrid","https://www.mrcbndu.ox.ac.uk/papers/tutorial-free-energy-framework-modelling-perception-and-learning","yes",4,"light",5,True,"concrete PC eqns + embedded code"),
("jehee_ballard_2009","Jehee & Ballard 2009 — Predictive feedback accounts for biphasic LGN responses","PLoS Comput. Biol.",2009,"10.1371/journal.pcbi.1000373","C3",76,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000373","unknown",4,"light",4,False,"Rao-Ballard-style PC of LGN"),
("huang_rao_2011","Huang & Rao 2011 — Predictive coding (review)","WIREs Cogn. Sci.",2011,"10.1002/wcs.142","C3",428,"closed","https://doi.org/10.1002/wcs.142","no",2,"light",1,False,"review"),
("bastos_2012","Bastos et al. 2012 — Canonical microcircuits for predictive coding","Neuron",2012,"10.1016/j.neuron.2012.10.038","C3",2588,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/3777738","no",2,"light",2,False,"laminar/microcircuit PC mapping"),
("lotter_kreiman_cox_2017","Lotter, Kreiman & Cox 2017 — PredNet: deep predictive coding for video","ICLR",2017,"10.48550/arXiv.1605.08104","C3",418,"green","https://arxiv.org/pdf/1605.08104","yes",4,"freezable",3,False,"deep-net PC; released weights freezable"),
("wen_2018","Wen et al. 2018 — Deep predictive coding network for object recognition","ICML",2018,"10.48550/arXiv.1802.04762","C3",41,"green","https://arxiv.org/pdf/1802.04762","yes",3,"heavy",2,False,"training-heavy CNN"),
# ---------------- C4 Motion-energy & MT ----------------
("hassenstein_reichardt_1956","Hassenstein & Reichardt 1956 — Correlation-type motion detector (beetle)","Z. Naturforsch. B",1956,"10.1515/zna-1956-9-1004","C4",1900,"closed","https://doi.org/10.1515/zna-1956-9-1004","no",2,"light",2,False,"correlation-detector root"),
("reichardt_1961","Reichardt 1961 — Autocorrelation & sensory information processing","Sensory Communication",1961,"","C4",2600,"closed","https://mitpress.mit.edu/sensory-communication","no",2,"light",2,False,"Reichardt correlator"),
("adelson_bergen_1985","Adelson & Bergen 1985 — Spatiotemporal energy model of motion","JOSA A",1985,"10.1364/JOSAA.2.000284","C4",3507,"closed","https://doi.org/10.1364/JOSAA.2.000284","unknown",5,"light",5,False,"motion-energy = complex-cell energy"),
("van_santen_sperling_1985","van Santen & Sperling 1985 — Elaborated Reichardt detectors","JOSA A",1985,"10.1364/JOSAA.2.000300","C4",892,"closed","https://doi.org/10.1364/JOSAA.2.000300","unknown",4,"light",4,False,"ERD; equivalent to energy model"),
("watson_ahumada_1985","Watson & Ahumada 1985 — Model of human visual-motion sensing","JOSA A",1985,"10.1364/JOSAA.2.000322","C4",1180,"closed","https://doi.org/10.1364/JOSAA.2.000322","unknown",4,"light",4,False,"linear motion sensor"),
("heeger_1987","Heeger 1987 — Model for extraction of image flow","JOSA A",1987,"10.1364/JOSAA.4.001455","C4",570,"closed","https://doi.org/10.1364/JOSAA.4.001455","unknown",4,"light",4,False,"energy + least-squares flow"),
("simoncelli_heeger_1998","Simoncelli & Heeger 1998 — A model of neuronal responses in area MT","Vis. Res.",1998,"10.1016/S0042-6989(97)00183-1","C4",963,"hybrid","https://www.cns.nyu.edu/~lcv/MTmodel/","yes",5,"freezable",5,False,"V1->MT two-stage; LCV MATLAB"),
("rust_mante_simoncelli_movshon_2006","Rust, Mante, Simoncelli & Movshon 2006 — How MT cells analyze motion of patterns","Nat. Neurosci.",2006,"10.1038/nn1786","C4",534,"closed","https://doi.org/10.1038/nn1786","yes",5,"freezable",4,False,"LN on V1 population; MTmodel code"),
("nishimoto_gallant_2011","Nishimoto & Gallant 2011 — 3D spatiotemporal RF model of MT to natural movies","J. Neurosci.",2011,"10.1523/JNEUROSCI.6801-10.2011","C4",143,"bronze","https://www.jneurosci.org/content/jneuro/31/41/14551.full.pdf","unknown",4,"freezable",3,False,"energy RF fit to movies"),
("borst_egelhaaf_1989","Borst & Egelhaaf 1989 — Principles of visual motion detection (fly)","Trends Neurosci.",1989,"10.1016/0166-2236(89)90010-6","C4",527,"green","https://pub.uni-bielefeld.de/record/1774131","no",3,"light",2,False,"fly motion review"),
# ---------------- C5 V1 RF / LN / subunit ----------------
("hubel_wiesel_1962","Hubel & Wiesel 1962 — RFs, binocular interaction, cat visual cortex","J. Physiol.",1962,"10.1113/jphysiol.1962.sp006837","C5",13819,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1359523","no",4,"light",1,False,"simple/complex RF conceptual root"),
("jones_palmer_1987","Jones & Palmer 1987 — 2D Gabor filter model of simple-cell RFs","J. Neurophysiol.",1987,"10.1152/jn.1987.58.6.1233","C5",2400,"closed","https://doi.org/10.1152/jn.1987.58.6.1233","unknown",5,"light",5,False,"explicit 2D Gabor; directly fittable"),
("movshon_thompson_tolhurst_1978","Movshon, Thompson & Tolhurst 1978 — Spatial summation in simple cells of cat striate","J. Physiol.",1978,"10.1113/jphysiol.1978.sp012281","C5",1500,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1282847","no",4,"light",3,False,"simple-cell linearity test"),
("chichilnisky_2001","Chichilnisky 2001 — A simple white-noise analysis of neuronal light responses (LNP)","Network",2001,"10.1080/net.12.2.199.213","C5",851,"closed","https://doi.org/10.1080/net.12.2.199.213","unknown",3,"light",4,False,"LNP/STA method root"),
("rust_schwartz_movshon_simoncelli_2005","Rust, Schwartz, Movshon & Simoncelli 2005 — Spatiotemporal elements of macaque V1 RFs (STC)","Neuron",2005,"10.1016/j.neuron.2005.05.021","C5",482,"bronze","https://www.cell.com/article/S089662730500468X/pdf","unknown",5,"freezable",3,False,"STC subunits; needs spike data to fit"),
("schwartz_pillow_rust_simoncelli_2006","Schwartz, Pillow, Rust & Simoncelli 2006 — Spike-triggered neural characterization","J. Vision",2006,"10.1167/6.4.13","C5",463,"gold","https://doi.org/10.1167/6.4.13","unknown",4,"light",3,False,"STA/STC methods review"),
("touryan_felsen_dan_2005","Touryan, Felsen & Dan 2005 — Complex-cell RF subunits from natural images","Neuron",2005,"10.1016/j.neuron.2005.01.029","C5",209,"bronze","https://www.cell.com/article/S0896627305000619/pdf","unknown",4,"freezable",3,False,"subunit energy model"),
("vintch_movshon_simoncelli_2015","Vintch, Movshon & Simoncelli 2015 — A convolutional subunit model of macaque V1","J. Neurosci.",2015,"10.1523/JNEUROSCI.2815-13.2015","C5",127,"bronze","https://www.jneurosci.org/content/jneuro/35/44/14829.full.pdf","unknown",5,"freezable",4,False,"convolutional subunit (simple+complex)"),
("mcfarland_cui_butts_2013","McFarland, Cui & Butts 2013 — Inferring nonlinear neuronal computation (NIM)","PLoS Comput. Biol.",2013,"10.1371/journal.pcbi.1003143","C5",192,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003143","yes",4,"freezable",4,False,"LNLN max-likelihood; author toolbox"),
("pillow_etal_2008","Pillow et al. 2008 — Spatio-temporal correlations & coding in a neural population (GLM)","Nature",2008,"10.1038/nature07140","C5",1445,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2684455","yes",5,"freezable",3,False,"coupled GLM; needs RGC spike trains"),
("carandini_etal_2005","Carandini et al. 2005 — Do we know what the early visual system does?","J. Neurosci.",2005,"10.1523/JNEUROSCI.3726-05.2005","C5",651,"bronze","https://www.jneurosci.org/content/jneuro/25/46/10577.full.pdf","no",3,"light",1,False,"standard-model review"),
# ---------------- C6 Bayesian / ideal-observer / cue combination ----------------
("knill_richards_1996","Knill & Richards 1996 — Perception as Bayesian Inference","Cambridge UP",1996,"10.1017/CBO9780511984037","C6",462,"closed","https://doi.org/10.1017/CBO9780511984037","no",2,"light",2,False,"Bayesian-perception conceptual root"),
("weiss_simoncelli_adelson_2002","Weiss, Simoncelli & Adelson 2002 — Motion illusions as optimal percepts","Nat. Neurosci.",2002,"10.1038/nn858","C6",1023,"closed","https://doi.org/10.1038/nn858","unknown",4,"light",5,False,"slow-prior Bayesian estimator"),
("stocker_simoncelli_2006","Stocker & Simoncelli 2006 — Noise characteristics and prior expectations in speed perception","Nat. Neurosci.",2006,"10.1038/nn1669","C6",858,"closed","https://doi.org/10.1038/nn1669","yes",4,"light",4,False,"speed prior; EfficientCoding code"),
("ernst_banks_2002","Ernst & Banks 2002 — Humans integrate visual and haptic information optimally","Nature",2002,"10.1038/415429a","C6",4920,"closed","https://doi.org/10.1038/415429a","no",4,"light",5,False,"optimal cue combination (MLE)"),
("kording_wolpert_2004","Kording & Wolpert 2004 — Bayesian integration in sensorimotor learning","Nature",2004,"10.1038/nature02169","C6",2077,"closed","https://doi.org/10.1038/nature02169","no",4,"light",4,False,"Bayesian sensorimotor estimator"),
("geisler_1989","Geisler 1989 — Sequential ideal-observer analysis of visual discriminations","Psychol. Rev.",1989,"10.1037/0033-295X.96.2.267","C6",411,"open","https://doi.org/10.1037/0033-295X.96.2.267","no",3,"light",4,False,"ideal-observer root"),
("geisler_2008","Geisler 2008 — Visual perception and the statistical properties of natural scenes","Annu. Rev. Psychol.",2008,"10.1146/annurev.psych.58.110405.085632","C6",716,"open","https://doi.org/10.1146/annurev.psych.58.110405.085632","no",3,"light",2,False,"review"),
("najemnik_geisler_2005","Najemnik & Geisler 2005 — Optimal eye movement strategies in visual search","Nature",2005,"10.1038/nature03390","C6",861,"closed","https://doi.org/10.1038/nature03390","yes",4,"heavy",4,False,"ideal searcher; needs visibility map"),
("najemnik_geisler_2008","Najemnik & Geisler 2008 — Eye movement statistics in an optimal search model","J. Vision",2008,"10.1167/8.3.4","C6",218,"open","https://doi.org/10.1167/8.3.4","yes",4,"heavy",4,False,"optimal-search procedural detail"),
("burge_geisler_2015","Burge & Geisler 2015 — Optimal speed estimation in natural image movies (AMA)","Nat. Commun.",2015,"10.1038/ncomms8900","C6",73,"open","https://doi.org/10.1038/ncomms8900","unknown",4,"freezable",4,False,"AMA pipeline; needs movie stims"),
("girshick_landy_simoncelli_2011","Girshick, Landy & Simoncelli 2011 — Cardinal rules: visual orientation perception priors","Nat. Neurosci.",2011,"10.1038/nn.2831","C6",687,"closed","https://doi.org/10.1038/nn.2831","unknown",4,"light",4,False,"orientation prior; ->wei_stocker"),
("wei_stocker_2015","Wei & Stocker 2015 — A Bayesian observer model constrained by efficient coding","Nat. Neurosci.",2015,"10.1038/nn.4105","C6",452,"closed","https://doi.org/10.1038/nn.4105","yes",4,"light",5,False,"efficient-coding Bayesian observer"),
# ---------------- C7 Texture / mid-level / saliency / contour ----------------
("heeger_bergen_1995","Heeger & Bergen 1995 — Pyramid-based texture analysis/synthesis","SIGGRAPH",1995,"10.1145/218380.218446","C7",1103,"open","https://www.ipol.im/pub/art/2014/79/","yes",4,"freezable",5,False,"histogram-matched pyramid; IPOL ref"),
("portilla_simoncelli_2000","Portilla & Simoncelli 2000 — A parametric texture model based on joint statistics","Int. J. Comput. Vis.",2000,"10.1023/A:1026553619983","C7",1834,"closed","https://github.com/LabForComputationalVision/textureSynth","yes",5,"freezable",5,False,"P-S texture; MATLAB+plenoptic. unlocks subtree"),
("freeman_simoncelli_2011","Freeman & Simoncelli 2011 — Metamers of the ventral stream","Nat. Neurosci.",2011,"10.1038/nn.2889","C7",694,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/3164938","yes",5,"heavy",4,False,"P-S stats in log-polar pooling"),
("balas_nakano_rosenholtz_2009","Balas, Nakano & Rosenholtz 2009 — A summary-statistic representation explains crowding","J. Vision",2009,"10.1167/9.12.13","C7",299,"gold","https://doi.org/10.1167/9.12.13","yes",4,"freezable",4,False,"crowding via P-S stats (mongrels)"),
("freeman_ziemba_2013","Freeman, Ziemba et al. 2013 — A functional and perceptual signature of the second visual area","Nat. Neurosci.",2013,"10.1038/nn.3402","C7",365,"green","https://doi.org/10.1038/nn.3402","unknown",4,"freezable",4,False,"V2 reads P-S texture stats"),
("koch_ullman_1985","Koch & Ullman 1985 — Shifts in selective visual attention (saliency/WTA)","Hum. Neurobiol.",1985,"10.1007/978-94-009-3833-5_5","C7",4226,"open","https://doi.org/10.1007/978-94-009-3833-5_5","no",2,"light",2,False,"saliency-map conceptual root"),
("itti_koch_niebur_1998","Itti, Koch & Niebur 1998 — A model of saliency-based visual attention","IEEE TPAMI",1998,"10.1109/34.730558","C7",11301,"closed","https://doi.org/10.1109/34.730558","yes",4,"freezable",5,False,"saliency model; Saliency Toolbox"),
("itti_koch_2001","Itti & Koch 2001 — Computational modelling of visual attention (review)","Nat. Rev. Neurosci.",2001,"10.1038/35058500","C7",4752,"closed","https://doi.org/10.1038/35058500","yes",3,"freezable",3,False,"review of saliency model"),
("li_zhaoping_2002","Li (Zhaoping) 2002 — A saliency map in primary visual cortex","Trends Cogn. Sci.",2002,"10.1016/S1364-6613(00)01817-9","C7",701,"open","https://doi.org/10.1016/S1364-6613(00)01817-9","unknown",3,"freezable",3,False,"V1 recurrent saliency hypothesis"),
("field_hayes_hess_1993","Field, Hayes & Hess 1993 — Contour integration by the visual system (association field)","Vis. Res.",1993,"10.1016/0042-6989(93)90156-Q","C7",2400,"closed","https://doi.org/10.1016/0042-6989(93)90156-Q","no",4,"light",3,False,"association field; ->geisler_2001"),
("geisler_2001","Geisler, Perry, Super & Gallogly 2001 — Edge co-occurrence predicts grouping performance","Vis. Res.",2001,"10.1016/S0042-6989(00)00277-7","C7",708,"open","https://doi.org/10.1016/S0042-6989(00)00277-7","unknown",4,"freezable",4,False,"edge-stat grouping; needs image DB"),
# ---------------- C8 Decision-making / evidence accumulation ----------------
("ratcliff_1978","Ratcliff 1978 — A theory of memory retrieval (the diffusion model)","Psychol. Rev.",1978,"10.1037/0033-295X.85.2.59","C8",4207,"closed","https://doi.org/10.1037/0033-295X.85.2.59","yes",2,"light",5,False,"DDM root"),
("ratcliff_rouder_1998","Ratcliff & Rouder 1998 — Modeling response times for two-choice decisions","Psychol. Sci.",1998,"10.1111/1467-9280.00067","C8",1562,"closed","https://doi.org/10.1111/1467-9280.00067","yes",3,"light",5,False,"DDM with across-trial variability"),
("ratcliff_mckoon_2008","Ratcliff & McKoon 2008 — The diffusion decision model: theory and data","Neural Comput.",2008,"10.1162/neco.2008.12-06-420","C8",3235,"closed","https://doi.org/10.1162/neco.2008.12-06-420","yes",3,"light",5,False,"canonical DDM reference"),
("ratcliff_smith_2004","Ratcliff & Smith 2004 — A comparison of sequential sampling models","Psychol. Rev.",2004,"10.1037/0033-295X.111.2.333","C8",1283,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/1440925","no",3,"light",4,False,"DDM/LCA/Poisson comparison"),
("usher_mcclelland_2001","Usher & McClelland 2001 — The time course of perceptual choice (leaky competing accumulator)","Psychol. Rev.",2001,"10.1037/0033-295X.108.3.550","C8",2173,"closed","https://doi.org/10.1037/0033-295X.108.3.550","unknown",3,"light",5,False,"LCA; biologically-flavored"),
("bogacz_2006","Bogacz et al. 2006 — The physics of optimal decision making (DDM/LCA/race vs SPRT)","Psychol. Rev.",2006,"10.1037/0033-295X.113.4.700","C8",1989,"closed","https://doi.org/10.1037/0033-295X.113.4.700","unknown",4,"light",5,False,"analytic unifier of accumulators"),
("brown_heathcote_2008","Brown & Heathcote 2008 — The simplest complete model of choice RT (LBA)","Cogn. Psychol.",2008,"10.1016/j.cogpsych.2007.12.002","C8",1202,"green","https://figshare.com/articles/journal_contribution/22923626","yes",3,"light",5,False,"linear ballistic accumulator; closed-form"),
("gold_shadlen_2007","Gold & Shadlen 2007 — The neural basis of decision making (review)","Annu. Rev. Neurosci.",2007,"10.1146/annurev.neuro.29.051605.113038","C8",3985,"closed","https://doi.org/10.1146/annurev.neuro.29.051605.113038","no",4,"light",1,False,"review"),
("wang_2002","Wang 2002 — Probabilistic decision making by slow reverberation in cortical circuits","Neuron",2002,"10.1016/S0896-6273(02)01092-9","C8",987,"bronze","https://www.cell.com/article/S0896627302010929/pdf","yes",4,"heavy",4,False,"spiking attractor decision circuit"),
("wong_wang_2006","Wong & Wang 2006 — A recurrent network mechanism of time integration (reduced 2-var)","J. Neurosci.",2006,"10.1523/JNEUROSCI.3733-05.2006","C8",1111,"green","https://www.jneurosci.org/content/26/4/1314","yes",4,"light",5,False,"mean-field reduction; community code"),
("roxin_ledberg_2008","Roxin & Ledberg 2008 — Neurobiological models of two-choice decisions reduce to 1D","PLoS Comput. Biol.",2008,"10.1371/journal.pcbi.1000046","C8",152,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000046","unknown",4,"light",5,False,"1D reduction; bridges spiking<->DDM"),
("churchland_kiani_shadlen_2008","Churchland, Kiani & Shadlen 2008 — Decision-making with multiple alternatives","Nat. Neurosci.",2008,"10.1038/nn.2123","C8",738,"closed","https://doi.org/10.1038/nn.2123","unknown",4,"light",3,False,"multi-alternative diffusion; data-anchored"),
("brunton_botvinick_brody_2013","Brunton, Botvinick & Brody 2013 — Rats and humans optimally accumulate evidence","Science",2013,"10.1126/science.1233912","C8",701,"closed","https://doi.org/10.1126/science.1233912","yes",4,"light",4,False,"click accumulator; fit needs their data"),
("drugowitsch_2012","Drugowitsch et al. 2012 — The cost of accumulating evidence in perceptual decisions","J. Neurosci.",2012,"10.1523/JNEUROSCI.4010-11.2012","C8",625,"bronze","https://www.jneurosci.org/content/jneuro/32/11/3612.full.pdf","unknown",4,"light",4,False,"normative collapsing bounds"),
("machens_romo_brody_2005","Machens, Romo & Brody 2005 — Flexible control of mutual inhibition (parametric WM)","Science",2005,"10.1126/science.1104171","C8",568,"closed","https://doi.org/10.1126/science.1104171","unknown",4,"light",4,False,"line-attractor 2-interval discrimination"),
# ---------------- C9 Attractor networks / WM / neural fields ----------------
("hopfield_1982","Hopfield 1982 — Neural networks and physical systems with emergent collective computation","PNAS",1982,"10.1073/pnas.79.8.2554","C9",19319,"closed","https://doi.org/10.1073/pnas.79.8.2554","yes",3,"light",5,False,"associative-memory root"),
("hopfield_1984","Hopfield 1984 — Neurons with graded response have collective computational properties","PNAS",1984,"10.1073/pnas.81.10.3088","C9",6946,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/345226","yes",3,"light",5,False,"continuous Hopfield"),
("amit_gutfreund_sompolinsky_1985","Amit, Gutfreund & Sompolinsky 1985 — Spin-glass models of neural networks","Phys. Rev. A",1985,"10.1103/PhysRevA.32.1007","C9",1220,"closed","https://doi.org/10.1103/PhysRevA.32.1007","unknown",3,"freezable",3,False,"statistical-mechanics capacity"),
("ben_yishai_1995","Ben-Yishai, Bar-Or & Sompolinsky 1995 — Theory of orientation tuning in visual cortex (ring)","PNAS",1995,"10.1073/pnas.92.9.3844","C9",1128,"green","https://doi.org/10.1073/pnas.92.9.3844","unknown",4,"light",5,False,"ring attractor; ->compte_2000"),
("amari_1977","Amari 1977 — Dynamics of pattern formation in lateral-inhibition neural fields","Biol. Cybern.",1977,"10.1007/BF00337259","C9",2084,"closed","https://doi.org/10.1007/BF00337259","unknown",3,"light",4,False,"neural-field bump root"),
("compte_2000","Compte, Brunel, Goldman-Rakic & Wang 2000 — Synaptic mechanisms of spatial working memory","Cereb. Cortex",2000,"10.1093/cercor/10.9.910","C9",1221,"bronze","https://academic.oup.com/cercor/article-pdf/10/9/910/9751089/100910.pdf","yes",4,"heavy",4,False,"spiking bump attractor; ModelDB"),
("wimmer_2014","Wimmer, Nykamp, Constantinidis & Compte 2014 — Bump attractor dynamics and WM precision","Nat. Neurosci.",2014,"10.1038/nn.3645","C9",533,"closed","https://doi.org/10.1038/nn.3645","yes",4,"heavy",4,False,"bump drift -> WM errors"),
# ---------------- C10 Hippocampal & spatial ----------------
("okeefe_dostrovsky_1971","O'Keefe & Dostrovsky 1971 — The hippocampus as a spatial map (place cells)","Brain Res.",1971,"10.1016/0006-8993(71)90358-1","C10",6292,"closed","https://doi.org/10.1016/0006-8993(71)90358-1","no",2,"light",1,False,"place-cell discovery (data)"),
("zhang_1996","Zhang 1996 — Representation of spatial orientation by attractor dynamics (head direction)","J. Neurosci.",1996,"10.1523/JNEUROSCI.16-06-02112.1996","C10",1050,"bronze","https://www.jneurosci.org/content/jneuro/16/6/2112.full.pdf","no",4,"light",5,False,"canonical 1D ring attractor"),
("tsodyks_sejnowski_1995","Tsodyks & Sejnowski 1995 — Associative memory and hippocampal place cells","Int. J. Neural Syst.",1995,"","C10",300,"closed","https://www.semanticscholar.org/paper/d108512969b971b927b5b01f965c607205e022f0","no",2,"light",3,False,"continuous attractor for place cells"),
("samsonovich_mcnaughton_1997","Samsonovich & McNaughton 1997 — Path integration in a continuous attractor map","J. Neurosci.",1997,"10.1523/JNEUROSCI.17-15-05900.1997","C10",1023,"bronze","https://www.jneurosci.org/content/jneuro/17/15/5900.full.pdf","no",4,"freezable",4,False,"2D charting attractor; ->burak_fiete"),
("tsodyks_1999","Tsodyks 1999 — Attractor neural network models of spatial maps in hippocampus","Hippocampus",1999,"10.1002/(SICI)1098-1063(1999)9:4<481::AID-HIPO14>3.0.CO;2-S","C10",156,"closed","https://doi.org/10.1002/(SICI)1098-1063(1999)9:4<481::AID-HIPO14>3.0.CO;2-S","no",3,"light",4,False,"standard CANN"),
("hartley_2000","Hartley, Burgess, Lever, Cacucci & O'Keefe 2000 — Boundary vector cell model of place fields","Hippocampus",2000,"10.1002/1098-1063(2000)10:4<369::AID-HIPO3>3.0.CO;2-0","C10",396,"bronze","https://doi.org/10.1002/1098-1063(2000)10:4<369::AID-HIPO3>3.0.CO;2-0","no",4,"light",5,False,"BVC; thresholded Gaussian sum"),
("hafting_2005","Hafting, Fyhn, Molden, Moser & Moser 2005 — Microstructure of a spatial map (grid cells)","Nature",2005,"10.1038/nature03721","C10",4201,"closed","https://doi.org/10.1038/nature03721","no",4,"light",1,False,"grid-cell discovery (data)"),
("mcnaughton_2006","McNaughton, Battaglia, Jensen, Moser & Moser 2006 — Path integration & cognitive map (review)","Nat. Rev. Neurosci.",2006,"10.1038/nrn1932","C10",2088,"closed","https://doi.org/10.1038/nrn1932","no",3,"light",2,False,"review"),
("fuhs_touretzky_2006","Fuhs & Touretzky 2006 — A spin-glass model of path integration in MEC (grid)","J. Neurosci.",2006,"10.1523/JNEUROSCI.4353-05.2006","C10",662,"bronze","https://www.jneurosci.org/content/jneuro/26/16/4266.full.pdf","no",4,"freezable",4,False,"2D grid attractor"),
("solstad_2006","Solstad, Moser & Einevoll 2006 — From grid cells to place cells (Fourier)","Hippocampus",2006,"10.1002/hipo.20244","C10",495,"closed","https://doi.org/10.1002/hipo.20244","no",4,"light",5,False,"weighted-sum of grids; closed-form"),
("guanella_2007","Guanella, Kiper & Verschure 2007 — A model of grid cells based on a twisted torus","Int. J. Neural Syst.",2007,"10.1142/S0129065707001093","C10",231,"closed","https://doi.org/10.1142/S0129065707001093","unknown",4,"light",5,False,"toroidal grid attractor; explicit updates"),
("burgess_2007","Burgess, Barry & O'Keefe 2007 — An oscillatory interference model of grid cell firing","Hippocampus",2007,"10.1002/hipo.20327","C10",720,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/2678278","no",4,"light",5,False,"oscillatory-interference grid"),
("hasselmo_2007","Hasselmo, Giocomo & Zilli 2007 — Grid cell firing may arise from interference of oscillations","Hippocampus",2007,"10.1002/hipo.20374","C10",261,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2678279","no",4,"light",5,False,"VCO/interference in single neurons"),
("burak_fiete_2009","Burak & Fiete 2009 — Accurate path integration in continuous attractor network models of grid cells","PLoS Comput. Biol.",2009,"10.1371/journal.pcbi.1000291","C10",835,"gold","https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000291","yes",5,"freezable",5,False,"CANN grid; author code; standout candidate"),
("sreenivasan_fiete_2011","Sreenivasan & Fiete 2011 — Grid cells generate an analog error-correcting code","Nat. Neurosci.",2011,"10.1038/nn.2901","C10",240,"closed","https://doi.org/10.1038/nn.2901","no",3,"light",4,False,"coding-capacity theory"),
# ---------------- C11 Population / probabilistic coding ----------------
("georgopoulos_1986","Georgopoulos, Schwartz & Kettner 1986 — Neuronal population coding of movement direction","Science",1986,"10.1126/science.3749885","C11",3210,"closed","https://doi.org/10.1126/science.3749885","no",3,"light",3,False,"population vector root"),
("seung_sompolinsky_1993","Seung & Sompolinsky 1993 — Simple models for reading neuronal population codes","PNAS",1993,"10.1073/pnas.90.22.10749","C11",646,"green","https://www.pnas.org/doi/10.1073/pnas.90.22.10749","no",3,"light",5,False,"Fisher-info/MLE readout; analytic"),
("zemel_1998","Zemel, Dayan & Pouget 1998 — Probabilistic interpretation of population codes","Neural Comput.",1998,"10.1162/089976698300017214","C11",771,"closed","https://doi.org/10.1162/089976698300017214","no",3,"light",4,False,"distributional population codes"),
("pouget_2000","Pouget, Dayan & Zemel 2000 — Information processing with population codes (review)","Nat. Rev. Neurosci.",2000,"10.1038/35039062","C11",782,"closed","https://doi.org/10.1038/35039062","no",3,"light",2,False,"review"),
("pouget_2003","Pouget, Dayan & Zemel 2003 — Inference and computation with population codes","Annu. Rev. Neurosci.",2003,"10.1146/annurev.neuro.26.041002.131112","C11",444,"closed","https://www.gatsby.ucl.ac.uk/~dayan/papers/pdz03.pdf","no",3,"light",2,False,"review"),
("ma_2006","Ma, Beck, Latham & Pouget 2006 — Bayesian inference with probabilistic population codes","Nat. Neurosci.",2006,"10.1038/nn1790","C11",1542,"closed","https://doi.org/10.1038/nn1790","no",4,"light",5,False,"Poisson PPC; linear combination"),
("jazayeri_movshon_2006","Jazayeri & Movshon 2006 — Optimal representation of sensory information by neural populations","Nat. Neurosci.",2006,"10.1038/nn1691","C11",582,"closed","https://doi.org/10.1038/nn1691","no",4,"light",5,False,"log-likelihood pooling readout"),
("beck_2008","Beck et al. 2008 — Probabilistic population codes for Bayesian decision making","Neuron",2008,"10.1016/j.neuron.2008.09.021","C11",691,"bronze","https://www.cell.com/article/S0896627308008039/pdf","no",4,"freezable",4,False,"line-attractor PPC integrator"),
# ---------------- C12 Motor control & cerebellum ----------------
("flash_hogan_1985","Flash & Hogan 1985 — The coordination of arm movements (minimum-jerk)","J. Neurosci.",1985,"10.1523/JNEUROSCI.05-07-01688.1985","C12",4360,"hybrid","https://www.jneurosci.org/content/jneuro/5/7/1688.full.pdf","no",4,"light",5,False,"minimum-jerk; closed-form optimum"),
("uno_kawato_suzuki_1989","Uno, Kawato & Suzuki 1989 — Minimum torque-change model of arm trajectory","Biol. Cybern.",1989,"10.1007/BF00204593","C12",1701,"closed","https://doi.org/10.1007/BF00204593","no",4,"light",4,False,"minimum-torque-change"),
("harris_wolpert_1998","Harris & Wolpert 1998 — Signal-dependent noise determines motor planning","Nature",1998,"10.1038/29528","C12",2515,"closed","https://doi.org/10.1038/29528","no",4,"light",4,False,"minimum-variance planning"),
("todorov_jordan_2002","Todorov & Jordan 2002 — Optimal feedback control as a theory of motor coordination","Nat. Neurosci.",2002,"10.1038/nn963","C12",3123,"closed","https://doi.org/10.1038/nn963","unknown",4,"freezable",3,False,"OFC hub; LQG; many task params"),
("todorov_2004","Todorov 2004 — Optimality principles in sensorimotor control","Nat. Neurosci.",2004,"10.1038/nn1309","C12",1781,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/1488877","unknown",3,"freezable",3,False,"stochastic OFC review/framework"),
("scott_2004","Scott 2004 — Optimal feedback control and the neural basis of volitional motor control","Nat. Rev. Neurosci.",2004,"10.1038/nrn1427","C12",1094,"closed","https://doi.org/10.1038/nrn1427","no",2,"light",2,False,"review"),
("shadmehr_mussaivaldi_1994","Shadmehr & Mussa-Ivaldi 1994 — Adaptive representation of dynamics during learning","J. Neurosci.",1994,"10.1523/JNEUROSCI.14-05-03208.1994","C12",2667,"bronze","https://www.jneurosci.org/content/jneuro/14/5/3208.full.pdf","no",5,"light",4,False,"force-field internal model"),
("wolpert_ghahramani_jordan_1995","Wolpert, Ghahramani & Jordan 1995 — An internal model for sensorimotor integration","Science",1995,"10.1126/science.7569931","C12",3558,"closed","https://doi.org/10.1126/science.7569931","no",4,"light",4,False,"Kalman forward model"),
("marr_1969","Marr 1969 — A theory of cerebellar cortex","J. Physiol.",1969,"10.1113/jphysiol.1969.sp008820","C12",3331,"green","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1351593","no",2,"light",2,False,"cerebellar theory root"),
("albus_1971","Albus 1971 — A theory of cerebellar function (CMAC)","Math. Biosci.",1971,"10.1016/0025-5564(71)90051-4","C12",2591,"closed","https://doi.org/10.1016/0025-5564(71)90051-4","no",2,"light",3,False,"CMAC associative learner"),
("fujita_1982","Fujita 1982 — Adaptive filter model of the cerebellum","Biol. Cybern.",1982,"10.1007/BF00336192","C12",532,"closed","https://doi.org/10.1007/BF00336192","no",3,"light",4,False,"LMS adaptive filter"),
("dean_porrill_2010","Dean, Porrill, Ekerot & Jorntell 2010 — The cerebellar microcircuit as an adaptive filter","Nat. Rev. Neurosci.",2010,"10.1038/nrn2756","C12",407,"closed","https://doi.org/10.1038/nrn2756","unknown",3,"light",3,False,"adaptive-filter review"),
("medina_mauk_2000","Medina & Mauk 2000 — Computer simulation of cerebellar information processing","Nat. Neurosci.",2000,"10.1038/81486","C12",343,"closed","https://doi.org/10.1038/81486","unknown",3,"heavy",2,False,"large spiking cerebellar sim"),
# ---------------- C13 RL / reward / basal ganglia ----------------
("sutton_1988","Sutton 1988 — Learning to predict by the methods of temporal differences","Mach. Learn.",1988,"10.1007/BF00115009","C13",2795,"bronze","https://doi.org/10.1007/BF00115009","no",3,"light",5,False,"TD-learning root"),
("montague_dayan_sejnowski_1996","Montague, Dayan & Sejnowski 1996 — A framework for mesencephalic dopamine (predictive Hebbian)","J. Neurosci.",1996,"10.1523/JNEUROSCI.16-05-01936.1996","C13",2107,"bronze","https://www.jneurosci.org/content/jneuro/16/5/1936.full.pdf","no",4,"light",4,False,"TD + dopamine framework"),
("schultz_dayan_montague_1997","Schultz, Dayan & Montague 1997 — A neural substrate of prediction and reward","Science",1997,"10.1126/science.275.5306.1593","C13",9589,"closed","https://doi.org/10.1126/science.275.5306.1593","no",4,"light",4,False,"dopamine-RPE hub"),
("houk_adams_barto_1995","Houk, Adams & Barto 1995 — A model of how the basal ganglia generate reinforcement signals","MIT Press",1995,"10.7551/mitpress/4708.003.0020","C13",550,"closed","https://doi.org/10.7551/mitpress/4708.003.0020","no",3,"light",3,False,"actor-critic basal ganglia"),
("suri_schultz_1999","Suri & Schultz 1999 — A neural network learns a delayed-response task with a dopamine signal","Neuroscience",1999,"10.1016/S0306-4522(98)00697-6","C13",297,"closed","https://doi.org/10.1016/S0306-4522(98)00697-6","unknown",3,"freezable",3,False,"TD actor-critic net"),
("suri_schultz_2001","Suri & Schultz 2001 — Temporal difference model reproduces anticipatory neural activity","Neural Comput.",2001,"10.1162/089976601300014376","C13",169,"closed","https://doi.org/10.1162/089976601300014376","unknown",3,"light",4,False,"TD with serial-compound stimulus"),
("frank_2005","Frank 2005 — Dynamic dopamine modulation in the basal ganglia (Go/NoGo)","J. Cogn. Neurosci.",2005,"10.1162/0898929052880093","C13",950,"closed","https://doi.org/10.1162/0898929052880093","yes",3,"heavy",2,False,"Leabra spiking net; Emergent-specific"),
("frank_2006","Frank 2006 — Hold your horses: STN in decision making","Neural Netw.",2006,"10.1016/j.neunet.2006.03.006","C13",715,"closed","https://doi.org/10.1016/j.neunet.2006.03.006","yes",3,"heavy",2,False,"Leabra net + STN"),
("oreilly_frank_2006","O'Reilly & Frank 2006 — Making working memory work (PBWM gating)","Neural Comput.",2006,"10.1162/089976606775093909","C13",1102,"closed","https://doi.org/10.1162/089976606775093909","yes",3,"heavy",2,False,"PBWM Leabra net"),
("daw_niv_dayan_2005","Daw, Niv & Dayan 2005 — Uncertainty-based competition between prefrontal and dorsolateral striatal systems","Nat. Neurosci.",2005,"10.1038/nn1560","C13",2641,"closed","https://doi.org/10.1038/nn1560","unknown",3,"light",4,False,"model-based vs model-free arbitration"),
("doya_2002","Doya 2002 — Metalearning and neuromodulation","Neural Netw.",2002,"10.1016/S0893-6080(02)00044-8","C13",699,"closed","https://doi.org/10.1016/S0893-6080(02)00044-8","no",2,"light",3,False,"RL meta-params <-> neuromodulators"),
("bayer_glimcher_2005","Bayer & Glimcher 2005 — Midbrain dopamine neurons encode a quantitative RPE","Neuron",2005,"10.1016/j.neuron.2005.05.020","C13",1334,"bronze","https://doi.org/10.1016/j.neuron.2005.05.020","no",4,"light",2,False,"RPE regression (data)"),
# ---------------- C14 Synaptic plasticity / learning rules ----------------
("oja_1982","Oja 1982 — A simplified neuron model as a principal component analyzer","J. Math. Biol.",1982,"10.1007/BF00275687","C14",2667,"closed","https://doi.org/10.1007/BF00275687","yes",3,"light",5,False,"Oja's rule (PCA); ->BCM"),
("bienenstock_cooper_munro_1982","Bienenstock, Cooper & Munro 1982 — Theory for the development of neuron selectivity (BCM)","J. Neurosci.",1982,"10.1523/JNEUROSCI.02-01-00032.1982","C14",2947,"bronze","https://www.jneurosci.org/content/jneuro/2/1/32.full.pdf","yes",3,"light",5,False,"BCM sliding threshold"),
("miller_keller_stryker_1989","Miller, Keller & Stryker 1989 — Ocular dominance column development","Science",1989,"10.1126/science.2762813","C14",666,"closed","https://doi.org/10.1126/science.2762813","unknown",3,"freezable",3,False,"correlation-based plasticity"),
("song_miller_abbott_2000","Song, Miller & Abbott 2000 — Competitive Hebbian learning through STDP","Nat. Neurosci.",2000,"10.1038/78829","C14",2892,"closed","https://doi.org/10.1038/78829","yes",4,"freezable",5,False,"additive STDP + LIF"),
("van_rossum_bi_turrigiano_2000","van Rossum, Bi & Turrigiano 2000 — Stable Hebbian learning from STDP","J. Neurosci.",2000,"10.1523/JNEUROSCI.20-23-08812.2000","C14",740,"bronze","https://www.jneurosci.org/content/jneuro/20/23/8812.full.pdf","yes",4,"freezable",5,False,"multiplicative STDP"),
("pfister_gerstner_2006","Pfister & Gerstner 2006 — Triplets of spikes in a model of STDP","J. Neurosci.",2006,"10.1523/JNEUROSCI.1425-06.2006","C14",662,"bronze","https://www.jneurosci.org/content/jneuro/26/38/9673.full.pdf","yes",4,"light",5,False,"triplet STDP; recovers BCM"),
("gutig_sompolinsky_2006","Gutig & Sompolinsky 2006 — The tempotron: a neuron that learns spike-timing decisions","Nat. Neurosci.",2006,"10.1038/nn1643","C14",845,"closed","https://doi.org/10.1038/nn1643","yes",4,"light",5,False,"supervised spike-timing classifier"),
("clopath_2010","Clopath, Busing, Vasilaki & Gerstner 2010 — Connectivity reflects coding: voltage-based STDP","Nat. Neurosci.",2010,"10.1038/nn.2479","C14",634,"green","https://infoscience.epfl.ch/record/144104","yes",4,"freezable",4,False,"voltage-based STDP; ModelDB"),
("toyoizumi_2005","Toyoizumi, Pfister, Aihara & Gerstner 2005 — Generalized BCM rule maximizing information","PNAS",2005,"10.1073/pnas.0500495102","C14",125,"green","https://infoscience.epfl.ch/record/97821","unknown",3,"freezable",3,False,"infomax spiking BCM"),
("wilson_cowan_1972","Wilson & Cowan 1972 — Excitatory and inhibitory interactions in localized neuron populations","Biophys. J.",1972,"10.1016/S0006-3495(72)86068-5","C15",3741,"bronze","https://doi.org/10.1016/S0006-3495(72)86068-5","yes",4,"light",5,False,"E/I population dynamics; canonical"),
("fitzhugh_1961","FitzHugh 1961 — Impulses and physiological states in models of nerve membrane","Biophys. J.",1961,"10.1016/S0006-3495(61)86902-6","C15",6257,"green","https://doi.org/10.1016/S0006-3495(61)86902-6","yes",4,"light",5,False,"FitzHugh-Nagumo; 2D reduced HH"),
("morris_lecar_1981","Morris & Lecar 1981 — Voltage oscillations in the barnacle giant muscle fiber","Biophys. J.",1981,"10.1016/S0006-3495(81)84782-0","C15",2324,"bronze","https://doi.org/10.1016/S0006-3495(81)84782-0","yes",4,"light",5,False,"2-conductance spiking model"),
("izhikevich_2003","Izhikevich 2003 — Simple model of spiking neurons","IEEE Trans. Neural Netw.",2003,"10.1109/TNN.2003.820440","C15",4826,"closed","https://doi.org/10.1109/TNN.2003.820440","yes",5,"light",5,False,"2-ODE + reset; 20 firing patterns"),
("brette_gerstner_2005","Brette & Gerstner 2005 — Adaptive exponential integrate-and-fire model (AdEx)","J. Neurophysiol.",2005,"10.1152/jn.00686.2005","C15",1313,"green","https://infoscience.epfl.ch/record/97829/files/3637.pdf","yes",4,"light",5,False,"AdEx; params tabulated"),
("van_vreeswijk_sompolinsky_1996","van Vreeswijk & Sompolinsky 1996 — Chaos in neuronal networks with balanced excitation/inhibition","Science",1996,"10.1126/science.274.5293.1724","C15",1970,"closed","https://doi.org/10.1126/science.274.5293.1724","unknown",3,"heavy",3,False,"balanced E/I chaos"),
("brunel_2000","Brunel 2000 — Dynamics of sparsely connected networks of excitatory and inhibitory spiking neurons","J. Comput. Neurosci.",2000,"10.1023/A:1008925309027","C15",1857,"closed","https://doi.org/10.1023/A:1008925309027","yes",4,"heavy",5,False,"sparse balanced LIF; phase diagram; Brian2 ref"),
("mainen_sejnowski_1995","Mainen & Sejnowski 1995 — Reliability of spike timing in neocortical neurons","Science",1995,"10.1126/science.7770778","C15",2000,"closed","https://doi.org/10.1126/science.7770778","yes",4,"light",4,False,"single HH neuron reliability; ModelDB"),
("vogels_abbott_2005","Vogels & Abbott 2005 — Signal propagation and logic gating in networks of I&F neurons","J. Neurosci.",2005,"10.1523/JNEUROSCI.3508-05.2005","C15",490,"bronze","https://www.jneurosci.org/content/jneuro/25/46/10786.full.pdf","yes",4,"heavy",5,False,"balanced LIF propagation; Brian2 ref"),
("sompolinsky_crisanti_sommers_1988","Sompolinsky, Crisanti & Sommers 1988 — Chaos in random neural networks","Phys. Rev. Lett.",1988,"10.1103/PhysRevLett.61.259","C15",1042,"closed","https://doi.org/10.1103/PhysRevLett.61.259","unknown",3,"light",4,False,"random rate net; g-gain transition; ->sussillo_abbott_2009"),
("nagumo_1962","Nagumo, Arimoto & Yoshizawa 1962 — An active pulse transmission line simulating nerve axon","Proc. IRE",1962,"10.1109/JRPROC.1962.288235","C15",4199,"closed","https://doi.org/10.1109/JRPROC.1962.288235","no",3,"light",5,False,"FitzHugh-Nagumo circuit realization"),
("sussillo_abbott_2009","Sussillo & Abbott 2009 — Generating coherent patterns of activity from chaotic neural networks (FORCE)","Neuron",2009,"10.1016/j.neuron.2009.07.018","C15",1146,"bronze","https://www.cell.com/article/S0896627309005479/pdf","unknown",4,"freezable",4,False,"FORCE learning in rate RNN; ->mante_2013"),
("ermentrout_cowan_1979","Ermentrout & Cowan 1979 — A mathematical theory of visual hallucination patterns","Biol. Cybern.",1979,"10.1007/BF00336965","C15",605,"closed","https://doi.org/10.1007/BF00336965","no",3,"light",4,False,"cortical pattern formation; descends from wilson_cowan_1972"),
# ---------------- C9 additions (attractor / integrator) ----------------
("seung_1996","Seung 1996 — How the brain keeps the eyes still (line attractor / neural integrator)","PNAS",1996,"10.1073/pnas.93.23.13339","C9",569,"green","https://www.pnas.org/doi/10.1073/pnas.93.23.13339","no",4,"light",5,False,"oculomotor line-attractor integrator"),
("amit_brunel_1997","Amit & Brunel 1997 — Model of global spontaneous and local structured delay activity","Cereb. Cortex",1997,"10.1093/cercor/7.3.237","C9",1137,"closed","https://doi.org/10.1093/cercor/7.3.237","unknown",3,"heavy",4,False,"attractor WM spiking; ->compte_2000,brunel_2000"),
# ---------------- C14 addition (PCA/Hebbian) ----------------
("sanger_1989","Sanger 1989 — Optimal unsupervised learning in a single-layer linear feedforward network (GHA)","Neural Netw.",1989,"10.1016/0893-6080(89)90044-0","C14",1530,"closed","https://doi.org/10.1016/0893-6080(89)90044-0","no",3,"light",5,False,"Generalized Hebbian Algorithm; extends oja_1982"),
]

# ---- validate columns ----
COLS = ["key","label","venue","year","doi","cluster","cites","oa","link","code","fig","compute","repro","corpus","lineage"]
data = [dict(zip(COLS, r)) for r in ROWS]
assert len({d["key"] for d in data}) == len(data), "duplicate keys!"

# ---- scoring ----
CODE_S = {"yes":1.0, "partial":0.6, "unknown":0.3, "no":0.0}
COMPUTE_S = {"light":1.0, "freezable":0.6, "heavy":0.15}
def oa_is_open(oa): return oa.lower() != "closed"

# importance: log-scaled citations across the set
cmin = math.log10(10); cmax = math.log10(20000)
def imp(c): return max(0.0, min(1.0, (math.log10(max(c,1)+1)-cmin)/(cmax-cmin)))

# phylogeny: cluster richness (count of rankable candidates) + corpus-anchor bonus
cand = [d for d in data if not d["corpus"]]
clust_count = {}
for d in cand:
    clust_count[d["cluster"]] = clust_count.get(d["cluster"],0)+1
maxc = max(clust_count.values())
def phylo(d):
    rich = clust_count.get(d["cluster"],0)/maxc
    anchor = 1.0 if d["cluster"] in CORPUS_CLUSTERS else 0.5
    return 0.6*rich + 0.4*anchor

W = {"repro":0.30,"imp":0.22,"fig":0.12,"code":0.12,"compute":0.12,"phylo":0.12}
def score(d):
    s = (W["repro"]*(d["repro"]/5.0) + W["imp"]*imp(d["cites"]) + W["fig"]*(d["fig"]/5.0)
         + W["code"]*CODE_S[d["code"]] + W["compute"]*COMPUTE_S[d["compute"]] + W["phylo"]*phylo(d))
    return round(100*s,1)
for d in data: d["score"] = score(d)

ranked = sorted([d for d in data if not d["corpus"]], key=lambda d:(-d["score"], -d["cites"]))
top100 = ranked[:100]

# ---- write the 200 landscape ----
def oa_cell(d):
    return ("**closed**" if not oa_is_open(d["oa"]) else d["oa"])
def link_cell(d):
    return f"[link]({d['link']})" if d["link"] else "-"

with open("proposals/corpus-candidates-200.md","w") as f:
    f.write("# Candidate corpus — 200 mechanistic models for reproduction\n\n")
    f.write(f"Auto-generated by `proposals/corpus-ranking/build_ranking.py` from 8 research scouts (2026-06-12). "
            f"**{len(data)} papers**, {len(cand)} not-yet-reproduced + {len(data)-len(cand)} already in corpus. "
            "Grouped by lineage cluster. See `corpus-top100-ranking.md` for the ranked reproduction list.\n\n")
    f.write("**Columns** — Cites: OpenAlex/S2 citation count (~2026-06, approximate). "
            "Access: free full-text type, or **closed** (paywalled — note the link so you only fetch via your institution). "
            "Code: author code available. Fig: quantitative-model-output figure quality (1-5). "
            "Compute: light / freezable / heavy. Repro: reproducibility-from-paper fit (1-5). "
            "Corpus: already reproduced here.\n\n")
    f.write("> Access types: open/gold/green/bronze/hybrid all mean a free legal full-text exists; **closed** = paywalled.\n\n")
    for ck, cname in CLUSTERS.items():
        rows = [d for d in data if d["cluster"]==ck]
        if not rows: continue
        rows.sort(key=lambda d:-d["cites"])
        f.write(f"## {ck} — {cname}  ({len(rows)})\n\n")
        f.write("| Paper | Year | Cites | Access | Link | Code | Fig | Compute | Repro | Corpus |\n")
        f.write("|---|--:|--:|---|---|---|--:|---|--:|---|\n")
        for d in rows:
            f.write(f"| {d['label']} | {d['year']} | {d['cites']} | {oa_cell(d)} | {link_cell(d)} | "
                    f"{d['code']} | {d['fig']} | {d['compute']} | {d['repro']} | {'YES' if d['corpus'] else '-'} |\n")
        f.write("\n")

# ---- write the top-100 ranking ----
with open("proposals/corpus-top100-ranking.md","w") as f:
    f.write("# Top 100 — ranked reproduction targets\n\n")
    f.write(f"Auto-generated by `proposals/corpus-ranking/build_ranking.py` (2026-06-12). Drawn from the "
            f"{len(cand)} not-yet-reproduced candidates in `corpus-candidates-200.md` (the 27 already-reproduced "
            "papers are excluded — they appear in the 200 for lineage only).\n\n")
    f.write("## Scoring (balanced blend)\n\n")
    f.write("Composite = weighted sum, 0-100. Weights: "
            "**repro-fit 0.30** (buildable from paper) · **importance 0.22** (log-citations) · "
            "**figures 0.12** · **code 0.12** · **compute 0.12** (heavy ranked low) · "
            "**phylogeny 0.12** (lineage richness + connection to existing corpus). "
            "Heavy-compute models are included but down-weighted, per the corpus criteria.\n\n")
    n_saved = sum(1 for i,d in enumerate(top100,1) if os.path.exists(f"paper_candidates/{i:03d}_{d['key']}.pdf"))
    f.write(f"**Download note** — the **PDF** column: `saved` = already in the gitignored `paper_candidates/` "
            f"folder as `NNN_<key>.pdf` (matching Rank) — **don't re-download these** ({n_saved} saved). "
            "`OA-todo` = open-access but the publisher bot-blocked the automated fetch (Nature/Cell/Wiley/PNAS/PMC "
            "serve challenge pages to scripts) — grab from the Link in a browser or via Unpaywall. "
            "`get@inst` = paywalled (**closed**) — fetch via your institution using the Link.\n\n")
    CMP = {"light":"light","freezable":"frzbl","heavy":"HEAVY"}
    def pdf_cell(i,d):
        if os.path.exists(f"paper_candidates/{i:03d}_{d['key']}.pdf"): return "saved"
        if not oa_is_open(d["oa"]): return "**get@inst**"
        return "OA-todo"
    f.write("| Rank | Score | Paper | Cluster | Cites | Access | Link | Code | Compute | Repro | PDF |\n")
    f.write("|--:|--:|---|---|--:|---|---|---|---|--:|---|\n")
    for i,d in enumerate(top100,1):
        f.write(f"| {i} | {d['score']} | {d['label']} | {CLUSTERS[d['cluster']]} | {d['cites']} | {oa_cell(d)} | "
                f"{link_cell(d)} | {d['code']} | {CMP[d['compute']]} | {d['repro']} | {pdf_cell(i,d)} |\n")
    f.write("\n## Ranks 101+ (candidates not making the cut)\n\n")
    f.write("| Rank | Score | Paper | Cluster | Access | Repro |\n|--:|--:|---|---|---|--:|\n")
    for i,d in enumerate(ranked[100:],101):
        f.write(f"| {i} | {d['score']} | {d['label']} | {CLUSTERS[d['cluster']]} | {oa_cell(d)} | {d['repro']} |\n")

# ---- emit JSON of all 200 papers (key, url, doi + useful fields) ----
rank_of = {d["key"]: i for i, d in enumerate(top100, 1)}
# Canonical PDF filename (relative to the gitignored paper_candidates/ folder):
# top-100 papers -> "NNN_<key>.pdf" (NNN = zero-padded rank, matches the 18 already saved);
# unranked (rank 101+) papers -> "<key>.pdf".
def pdf_filename(d):
    r = rank_of.get(d["key"])
    return f"{r:03d}_{d['key']}.pdf" if r else f"{d['key']}.pdf"
records = []
for d in sorted(data, key=lambda d: (int(d["cluster"][1:]), -d["cites"])):
    doi = d["doi"] or None
    records.append({
        "key": d["key"],
        "citation": d["label"],
        "year": d["year"],
        "venue": d["venue"],
        "cluster": d["cluster"],
        "cluster_name": CLUSTERS[d["cluster"]],
        "doi": doi,
        "doi_url": (f"https://doi.org/{doi}" if doi else None),
        "url": d["link"] or None,
        "open_access": d["oa"],
        "is_open_access": oa_is_open(d["oa"]),
        "code": d["code"],
        "citations": d["cites"],
        "in_corpus": d["corpus"],
        "top100_rank": rank_of.get(d["key"]),
        "pdf_filename": pdf_filename(d),
        "pdf_saved": os.path.exists(f"paper_candidates/{pdf_filename(d)}"),
    })
with open("proposals/corpus-candidates-200.json", "w") as f:
    json.dump({
        "generated": "2026-06-12",
        "source": "proposals/corpus-ranking/build_ranking.py",
        "note": ("Citation counts are OpenAlex/S2 reads (~2026-06), approximate. doi may be null for "
                 "pre-DOI works; use url. Save each downloaded PDF as pdf_filename inside the gitignored "
                 "paper_candidates/ folder (top-100 = 'NNN_<key>.pdf', NNN = rank; others = '<key>.pdf'). "
                 "pdf_saved=true means it is already on disk."),
        "count": len(records),
        "papers": records,
    }, f, indent=2, ensure_ascii=False)

# ---- emit download manifest for OA top-100 ----
with open("proposals/corpus-ranking/downloads.tsv","w") as f:
    for i,d in enumerate(top100,1):
        if oa_is_open(d["oa"]) and d["link"]:
            f.write(f"{i:03d}\t{d['key']}\t{d['link']}\n")

n_oa = sum(1 for d in top100 if oa_is_open(d["oa"]) and d["link"])
print(f"total papers: {len(data)}  | rankable (non-corpus): {len(cand)}  | in-corpus: {len(data)-len(cand)}")
print(f"top100 written. OA in top100 to download: {n_oa}  | closed (institution): {100-n_oa}")
print("\nTop 20 preview:")
for i,d in enumerate(top100[:20],1):
    print(f"{i:3d}. {d['score']:5.1f}  {d['cluster']:4s} {d['oa']:7s} {'CODE' if d['code']=='yes' else '    '}  {d['key']}")
print("\nCluster counts (rankable):")
for ck in CLUSTERS:
    print(f"  {ck}: {clust_count.get(ck,0)}")
