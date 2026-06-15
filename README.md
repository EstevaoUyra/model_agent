# model_agent — reproduction roadmap

An agentic pipeline that reproduces computational-neuroscience models from their
papers, one git submodule per model under [`models/`](models/). See
[VISION.md](VISION.md) for the why, [WORKFLOW.md](WORKFLOW.md) for the full-pass
process, [AGENTS.md](AGENTS.md) for agent instructions, and
[PAPERS.md](PAPERS.md) for the clustered index + phylogeny.

## Reproduction status

The table below is **auto-generated** — do not edit it by hand. A pre-commit hook
(`tools/hooks/pre-commit`, activated with `git config core.hooksPath tools/hooks`)
refreshes it on every commit; run `python3 tools/build_readme.py` to refresh it
manually. It lists the
**top-100 ranked reproduction targets plus every paper already started**
(38 of 112 rows have a submodule), interleaved by composite score
(same scoring as [`proposals/corpus-top100-ranking.md`](proposals/corpus-top100-ranking.md)).

**Columns.** *Rank/Score/Cluster/Cites/Access/Code* describe the paper (from the
corpus data). *State* is the submodule's own self-reported exit
(`reproduced` › `faithful` › `partial` › `blocked` › `not started`); *Traj* its
trajectory; *Figs* committed reproduced figures; *Flags* open dispositions a human
must confirm.

> **Audit honesty.** `State` is the *builder's claim*, not a certification. The
> **Audit** column is the real trust signal: `hardened` = independent figure +
> digitization audit with build/audit roles separated · `VLM` = independent
> figure-comparison only · `self-reported` = implemented, not independently
> audited. Treat `self-reported` as *"not yet verified."*

<!-- BEGIN AUTOGEN: reproduction-table (tools/build_readme.py) -->
| Rank | Score | Paper | Cluster | Cites | Access | Code | State | Traj | Figs | Flags | Audit |
|--:|--:|---|---|--:|---|---|---|---|--:|--:|---|
| 1 | 96.0 | [Olshausen & Field 1996 — Emergence of simple-cell RFs by learning a sparse code](https://www.rctn.org/bruno/papers/sparse-coding.pdf) | Sparse / efficient coding | 5834 | closed | yes | reproduced | — | 3 | 0 | VLM |
| 2 | 92.5 | [Izhikevich 2003 — Simple model of spiking neurons](https://doi.org/10.1109/TNN.2003.820440) | Single-neuron & network dynamics | 4826 | closed | yes | partial | toward | 3 | 3 | hardened |
| 3 | 92.3 | [Olshausen & Field 1997 — Sparse coding with an overcomplete basis set](https://www.rctn.org/bruno/papers/VR.pdf) | Sparse / efficient coding | 3720 | closed | yes | not started | — | — | — | — |
| 4 | 90.9 | [FitzHugh 1961 — Impulses and physiological states in models of nerve membrane](https://doi.org/10.1016/S0006-3495(61)86902-6) | Single-neuron & network dynamics | 6257 | green | yes | blocked | toward | 3 | 2 | self-reported |
| 5 | 89.8 | [Hopfield 1982 — Neural networks and physical systems with emergent collective computation](https://doi.org/10.1073/pnas.79.8.2554) | Attractor networks / working memory / neural fields | 19319 | closed | yes | not started | — | — | — | — |
| 6 | 89.4 | [Wilson & Cowan 1972 — Excitatory and inhibitory interactions in localized neuron populations](https://doi.org/10.1016/S0006-3495(72)86068-5) | Single-neuron & network dynamics | 3741 | bronze | yes | not started | — | — | — | — |
| 7 | 88.0 | [Morris & Lecar 1981 — Voltage oscillations in the barnacle giant muscle fiber](https://doi.org/10.1016/S0006-3495(81)84782-0) | Single-neuron & network dynamics | 2324 | bronze | yes | not started | — | — | — | — |
| 8 | 87.5 | [Ratcliff & McKoon 2008 — The diffusion decision model: theory and data](https://doi.org/10.1162/neco.2008.12-06-420) | Decision-making / evidence accumulation | 3235 | closed | yes | blocked | toward | 7 | 0 | hardened |
| 9 | 87.1 | [Hyvarinen & Hoyer 2001 — Two-layer sparse coding -> simple/complex cells + topography](https://www.cs.helsinki.fi/u/ahyvarin/papers/VR01.pdf) | Sparse / efficient coding | 272 | closed | yes | not started | — | — | — | — |
| 10 | 86.9 | [Hopfield 1984 — Neurons with graded response have collective computational properties](https://www.ncbi.nlm.nih.gov/pmc/articles/345226) | Attractor networks / working memory / neural fields | 6946 | green | yes | not started | — | — | — | — |
| 11 | 86.8 | [Itti, Koch & Niebur 1998 — A model of saliency-based visual attention](https://doi.org/10.1109/34.730558) | Texture / mid-level / saliency / contour | 11301 | closed | yes | partial | toward | 7 | 2 | hardened |
| 12 | 86.8 | [Wong & Wang 2006 — A recurrent network mechanism of time integration (reduced 2-var)](https://www.jneurosci.org/content/26/4/1314) | Decision-making / evidence accumulation | 1111 | green | yes | not started | — | — | — | — |
| 13 | 86.7 | [Hyvarinen & Hoyer 2000 — Phase/shift-invariant features via feature subspaces (ISA)](https://www.cs.helsinki.fi/u/ahyvarin/papers/NC00.pdf) | Sparse / efficient coding | 546 | closed | yes | partial | toward | 4 | 4 | hardened |
| 14 | 86.4 | [Brette & Gerstner 2005 — Adaptive exponential integrate-and-fire model (AdEx)](https://infoscience.epfl.ch/record/97829/files/3637.pdf) | Single-neuron & network dynamics | 1313 | green | yes | not started | — | — | — | — |
| 15 | 86.3 | [Rozell, Johnson, Baraniuk & Olshausen 2008 — Sparse coding via local competition (LCA)](https://www.rctn.org/bruno/papers/lca.pdf) | Sparse / efficient coding | 475 | closed | yes | partial | toward | 3 | 3 | self-reported |
| 16 | 85.9 | [Ratcliff 1978 — A theory of memory retrieval (the diffusion model)](https://doi.org/10.1037/0033-295X.85.2.59) | Decision-making / evidence accumulation | 4207 | closed | yes | not started | — | — | — | — |
| 17 | 85.4 | [Ratcliff & Rouder 1998 — Modeling response times for two-choice decisions](https://doi.org/10.1111/1467-9280.00067) | Decision-making / evidence accumulation | 1562 | closed | yes | not started | — | — | — | — |
| 18 | 85.3 | [van Hateren & van der Schaaf 1998 — ICA filters of natural images vs simple cells](https://research.rug.nl/files/3200279/1998ProcRSocLondBvHateren1.pdf) | Sparse / efficient coding | 1163 | green | yes | not started | — | — | — | — |
| 19 | 84.9 | [Bienenstock, Cooper & Munro 1982 — Theory for the development of neuron selectivity (BCM)](https://www.jneurosci.org/content/jneuro/2/1/32.full.pdf) | Synaptic plasticity / learning rules | 2947 | bronze | yes | partial | toward | 0 | 6 | VLM |
| 20 | 84.8 | [Bell & Sejnowski 1997 — The 'independent components' of natural scenes are edge filters](https://www.cnl.salk.edu/~tony/ptrs.html) | Sparse / efficient coding | 2269 | green | yes | faithful | toward | 3 | 0 | self-reported |
| 21 | 84.7 | [Brown & Heathcote 2008 — The simplest complete model of choice RT (LBA)](https://figshare.com/articles/journal_contribution/22923626) | Decision-making / evidence accumulation | 1202 | green | yes | not started | — | — | — | — |
| 22 | 84.6 | [Rao & Ballard 1999 — Predictive coding in the visual cortex (extra-classical RF)](https://www.cs.utexas.edu/~dana/nn.pdf) | Predictive coding / free-energy | 5718 | closed | yes | partial | toward | 4 | 2 | hardened |
| 23 | 84.6 | [Oja 1982 — A simplified neuron model as a principal component analyzer](https://doi.org/10.1007/BF00275687) | Synaptic plasticity / learning rules | 2667 | closed | yes | not started | — | — | — | — |
| 24 | 84.0 | [Portilla & Simoncelli 2000 — A parametric texture model based on joint statistics](https://github.com/LabForComputationalVision/textureSynth) | Texture / mid-level / saliency / contour | 1834 | closed | yes | not started | — | — | — | — |
| 25 | 83.6 | [Gutig & Sompolinsky 2006 — The tempotron: a neuron that learns spike-timing decisions](https://doi.org/10.1038/nn1643) | Synaptic plasticity / learning rules | 845 | closed | yes | not started | — | — | — | — |
| 26 | 83.6 | [Burak & Fiete 2009 — Accurate path integration in continuous attractor network models of grid cells](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000291) | Hippocampal & spatial (place & grid cells) | 835 | gold | yes | not started | — | — | — | — |
| 27 | 83.5 | [Spratling 2010 — Predictive coding as a model of response properties in V1](https://www.jneurosci.org/content/30/9/3531) | Predictive coding / free-energy | 216 | bronze | yes | partial | toward | 4 | 4 | hardened |
| 28 | 82.9 | [Pfister & Gerstner 2006 — Triplets of spikes in a model of STDP](https://www.jneurosci.org/content/jneuro/26/38/9673.full.pdf) | Synaptic plasticity / learning rules | 662 | bronze | yes | partial | toward | 0 | 4 | hardened |
| 29 | 82.8 | [Wei & Stocker 2015 — A Bayesian observer model constrained by efficient coding](https://doi.org/10.1038/nn.4105) | Bayesian / ideal-observer / cue combination | 452 | closed | yes | not started | — | — | — | — |
| 30 | 82.5 | [Denison, Carrasco & Heeger 2021 — A dynamic normalization model of temporal attention](https://www.ncbi.nlm.nih.gov/pmc/articles/8678377) | Normalization & attention (R&H family) | 78 | green | yes | partial | toward | 2 | 1 | hardened |
| 31 | 82.4 | [Song, Miller & Abbott 2000 — Competitive Hebbian learning through STDP](https://doi.org/10.1038/78829) | Synaptic plasticity / learning rules | 2892 | closed | yes | not started | — | — | — | — |
| 32 | 82.2 | [Bogacz 2017 — A tutorial on the free-energy framework for perception and learning](https://www.mrcbndu.ox.ac.uk/papers/tutorial-free-energy-framework-modelling-perception-and-learning) | Predictive coding / free-energy | 309 | hybrid | yes | faithful | toward | 3 | 1 | hardened |
| 33 | 81.8 | [Adelson & Bergen 1985 — Spatiotemporal energy model of motion](https://doi.org/10.1364/JOSAA.2.000284) | Motion-energy & MT models | 3507 | closed | unknown | not started | — | — | — | — |
| 34 | 81.6 | [Mainen & Sejnowski 1995 — Reliability of spike timing in neocortical neurons](https://doi.org/10.1126/science.7770778) | Single-neuron & network dynamics | 2000 | closed | yes | not started | — | — | — | — |
| 35 | 81.6 | [Simoncelli & Heeger 1998 — A model of neuronal responses in area MT](https://www.cns.nyu.edu/~lcv/MTmodel/) | Motion-energy & MT models | 963 | hybrid | yes | not started | — | — | — | — |
| 36 | 81.1 | [Jones & Palmer 1987 — 2D Gabor filter model of simple-cell RFs](https://doi.org/10.1152/jn.1987.58.6.1233) | V1 receptive-field / LN / subunit models | 2400 | closed | unknown | not started | — | — | — | — |
| 37 | 80.1 | [Bogacz et al. 2006 — The physics of optimal decision making (DDM/LCA/race vs SPRT)](https://doi.org/10.1037/0033-295X.113.4.700) | Decision-making / evidence accumulation | 1989 | closed | unknown | not started | — | — | — | — |
| 38 | 80.1 | [Heeger & Bergen 1995 — Pyramid-based texture analysis/synthesis](https://www.ipol.im/pub/art/2014/79/) | Texture / mid-level / saliency / contour | 1103 | open | yes | not started | — | — | — | — |
| 39 | 79.5 | [Brunton, Botvinick & Brody 2013 — Rats and humans optimally accumulate evidence](https://doi.org/10.1126/science.1233912) | Decision-making / evidence accumulation | 701 | closed | yes | not started | — | — | — | — |
| 40 | 79.2 | [Reynolds & Heeger 2009 — The Normalization Model of Attention](https://www.cell.com/article/S0896627309000038/pdf) | Normalization & attention (R&H family) | 1553 | bronze | no | reproduced | toward | 13 | 0 | hardened |
| 41 | 78.6 | [Stocker & Simoncelli 2006 — Noise characteristics and prior expectations in speed perception](https://doi.org/10.1038/nn1669) | Bayesian / ideal-observer / cue combination | 858 | closed | yes | not started | — | — | — | — |
| 42 | 78.5 | [van Rossum, Bi & Turrigiano 2000 — Stable Hebbian learning from STDP](https://www.jneurosci.org/content/jneuro/20/23/8812.full.pdf) | Synaptic plasticity / learning rules | 740 | bronze | yes | not started | — | — | — | — |
| 43 | 78.0 | [Usher & McClelland 2001 — The time course of perceptual choice (leaky competing accumulator)](https://doi.org/10.1037/0033-295X.108.3.550) | Decision-making / evidence accumulation | 2173 | closed | unknown | not started | — | — | — | — |
| 44 | 77.8 | [Flash & Hogan 1985 — The coordination of arm movements (minimum-jerk)](https://www.jneurosci.org/content/jneuro/5/7/1688.full.pdf) | Motor control & cerebellum | 4360 | hybrid | no | faithful | toward | 0 | 1 | VLM |
| 45 | 77.8 | [Spratling 2012 — Predictive coding accounts for V1 response from reverse correlation](https://nms.kcl.ac.uk/michael.spratling/Doc/dim_learning.pdf) | Predictive coding / free-energy | 67 | closed | yes | faithful | toward | 4 | 3 | hardened |
| 46 | 77.7 | [Ernst & Banks 2002 — Humans integrate visual and haptic information optimally](https://doi.org/10.1038/415429a) | Bayesian / ideal-observer / cue combination | 4920 | closed | no | not started | — | — | — | — |
| 47 | 77.2 | [Brunel 2000 — Dynamics of sparsely connected networks of excitatory and inhibitory spiking neurons](https://doi.org/10.1023/A:1008925309027) | Single-neuron & network dynamics | 1857 | closed | yes | not started | — | — | — | — |
| 48 | 76.8 | [Weiss, Simoncelli & Adelson 2002 — Motion illusions as optimal percepts](https://doi.org/10.1038/nn858) | Bayesian / ideal-observer / cue combination | 1023 | closed | unknown | not started | — | — | — | — |
| 49 | 75.6 | [Ben-Yishai, Bar-Or & Sompolinsky 1995 — Theory of orientation tuning in visual cortex (ring)](https://doi.org/10.1073/pnas.92.9.3844) | Attractor networks / working memory / neural fields | 1128 | green | unknown | not started | — | — | — | — |
| 50 | 75.3 | [Nagumo, Arimoto & Yoshizawa 1962 — An active pulse transmission line simulating nerve axon](https://doi.org/10.1109/JRPROC.1962.288235) | Single-neuron & network dynamics | 4199 | closed | no | not started | — | — | — | — |
| 51 | 74.7 | [Zhang 1996 — Representation of spatial orientation by attractor dynamics (head direction)](https://www.jneurosci.org/content/jneuro/16/6/2112.full.pdf) | Hippocampal & spatial (place & grid cells) | 1050 | bronze | no | partial | toward | 0 | 0 | self-reported |
| 52 | 73.9 | [Rust, Mante, Simoncelli & Movshon 2006 — How MT cells analyze motion of patterns](https://doi.org/10.1038/nn1786) | Motion-energy & MT models | 534 | closed | yes | not started | — | — | — | — |
| 53 | 73.9 | [Guanella, Kiper & Verschure 2007 — A model of grid cells based on a twisted torus](https://doi.org/10.1142/S0129065707001093) | Hippocampal & spatial (place & grid cells) | 231 | closed | unknown | not started | — | — | — | — |
| 54 | 73.7 | [Sutton 1988 — Learning to predict by the methods of temporal differences](https://doi.org/10.1007/BF00115009) | Reinforcement learning / reward / basal ganglia | 2795 | bronze | no | partial | toward | 3 | 4 | hardened |
| 55 | 73.6 | [Schultz, Dayan & Montague 1997 — A neural substrate of prediction and reward](https://doi.org/10.1126/science.275.5306.1593) | Reinforcement learning / reward / basal ganglia | 9589 | closed | no | not started | — | — | — | — |
| 56 | 73.6 | [Burgess, Barry & O'Keefe 2007 — An oscillatory interference model of grid cell firing](https://www.ncbi.nlm.nih.gov/pmc/articles/2678278) | Hippocampal & spatial (place & grid cells) | 720 | green | no | not started | — | — | — | — |
| 57 | 73.3 | [Vogels & Abbott 2005 — Signal propagation and logic gating in networks of I&F neurons](https://www.jneurosci.org/content/jneuro/25/46/10786.full.pdf) | Single-neuron & network dynamics | 490 | bronze | yes | not started | — | — | — | — |
| 58 | 72.8 | [Shadmehr & Mussa-Ivaldi 1994 — Adaptive representation of dynamics during learning](https://www.jneurosci.org/content/jneuro/14/5/3208.full.pdf) | Motor control & cerebellum | 2667 | bronze | no | not started | — | — | — | — |
| 59 | 72.7 | [Roxin & Ledberg 2008 — Neurobiological models of two-choice decisions reduce to 1D](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000046) | Decision-making / evidence accumulation | 152 | gold | unknown | blocked | mixed | 0 | 5 | VLM |
| 60 | 72.5 | [Solstad, Moser & Einevoll 2006 — From grid cells to place cells (Fourier)](https://doi.org/10.1002/hipo.20244) | Hippocampal & spatial (place & grid cells) | 495 | closed | no | not started | — | — | — | — |
| 61 | 72.4 | [Ma, Beck, Latham & Pouget 2006 — Bayesian inference with probabilistic population codes](https://doi.org/10.1038/nn1790) | Population / probabilistic coding | 1542 | closed | no | not started | — | — | — | — |
| 62 | 72.1 | [Karklin & Lewicki 2009 — Emergence of complex cell properties by learning to generalize](https://www.cs.cmu.edu/~lewicki/papers/karklin-lewicki-nature09.pdf) | Sparse / efficient coding | 225 | closed | unknown | partial | toward | 4 | 1 | hardened |
| 63 | 72.0 | [Clopath, Busing, Vasilaki & Gerstner 2010 — Connectivity reflects coding: voltage-based STDP](https://infoscience.epfl.ch/record/144104) | Synaptic plasticity / learning rules | 634 | green | yes | not started | — | — | — | — |
| 64 | 71.9 | [Hartley, Burgess, Lever, Cacucci & O'Keefe 2000 — Boundary vector cell model of place fields](https://doi.org/10.1002/1098-1063(2000)10:4<369::AID-HIPO3>3.0.CO;2-0) | Hippocampal & spatial (place & grid cells) | 396 | bronze | no | not started | — | — | — | — |
| 65 | 71.7 | [Lee & Maunsell 2009 — A normalization model of attentional modulation of single-unit responses](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0004651&type=printable) | Normalization & attention (R&H family) | 269 | gold | no | blocked | — | 3 | 0 | hardened |
| 66 | 71.7 | [Zhu & Rozell 2013 — Nonclassical RF effects emerge from sparse coding](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003191) | Sparse / efficient coding | 190 | gold | unknown | partial | toward | 4 | 4 | VLM |
| 67 | 71.4 | [Heeger 1992 — Normalization of cell responses in cat striate cortex](https://doi.org/10.1017/S0952523800009640) | Normalization & attention (R&H family) | 1909 | closed | no | partial | drifting | 5 | 3 | hardened |
| 68 | 71.3 | [Pillow et al. 2008 — Spatio-temporal correlations & coding in a neural population (GLM)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2684455) | V1 receptive-field / LN / subunit models | 1445 | green | yes | not started | — | — | — | — |
| 69 | 71.2 | [Wolpert, Ghahramani & Jordan 1995 — An internal model for sensorimotor integration](https://doi.org/10.1126/science.7569931) | Motor control & cerebellum | 3558 | closed | no | not started | — | — | — | — |
| 70 | 71.1 | [Daw, Niv & Dayan 2005 — Uncertainty-based competition between prefrontal and dorsolateral striatal systems](https://doi.org/10.1038/nn1560) | Reinforcement learning / reward / basal ganglia | 2641 | closed | unknown | not started | — | — | — | — |
| 71 | 71.0 | [Sanger 1989 — Optimal unsupervised learning in a single-layer linear feedforward network (GHA)](https://doi.org/10.1016/0893-6080(89)90044-0) | Synaptic plasticity / learning rules | 1530 | closed | no | not started | — | — | — | — |
| 72 | 70.8 | [Drugowitsch et al. 2012 — The cost of accumulating evidence in perceptual decisions](https://www.jneurosci.org/content/jneuro/32/11/3612.full.pdf) | Decision-making / evidence accumulation | 625 | bronze | unknown | not started | — | — | — | — |
| 73 | 70.7 | [Hasselmo, Giocomo & Zilli 2007 — Grid cell firing may arise from interference of oscillations](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2678279) | Hippocampal & spatial (place & grid cells) | 261 | green | no | not started | — | — | — | — |
| 74 | 70.5 | [Machens, Romo & Brody 2005 — Flexible control of mutual inhibition (parametric WM)](https://doi.org/10.1126/science.1104171) | Decision-making / evidence accumulation | 568 | closed | unknown | not started | — | — | — | — |
| 75 | 70.3 | [Wang 2002 — Probabilistic decision making by slow reverberation in cortical circuits](https://www.cell.com/article/S0896627302010929/pdf) | Decision-making / evidence accumulation | 987 | bronze | yes | not started | — | — | — | — |
| 76 | 70.3 | [Balas, Nakano & Rosenholtz 2009 — A summary-statistic representation explains crowding](https://doi.org/10.1167/9.12.13) | Texture / mid-level / saliency / contour | 299 | gold | yes | not started | — | — | — | — |
| 77 | 70.2 | [Harris & Wolpert 1998 — Signal-dependent noise determines motor planning](https://doi.org/10.1038/29528) | Motor control & cerebellum | 2515 | closed | no | not started | — | — | — | — |
| 78 | 70.2 | [Watson & Ahumada 1985 — Model of human visual-motion sensing](https://doi.org/10.1364/JOSAA.2.000322) | Motion-energy & MT models | 1180 | closed | unknown | not started | — | — | — | — |
| 79 | 70.0 | [Seung 1996 — How the brain keeps the eyes still (line attractor / neural integrator)](https://www.pnas.org/doi/10.1073/pnas.93.23.13339) | Attractor networks / working memory / neural fields | 569 | green | no | not started | — | — | — | — |
| 80 | 69.9 | [Itti & Koch 2001 — Computational modelling of visual attention (review)](https://doi.org/10.1038/35058500) | Texture / mid-level / saliency / contour | 4752 | closed | yes | not started | — | — | — | — |
| 81 | 69.8 | [Freeman & Simoncelli 2011 — Metamers of the ventral stream](https://www.ncbi.nlm.nih.gov/pmc/articles/3164938) | Texture / mid-level / saliency / contour | 694 | green | yes | not started | — | — | — | — |
| 82 | 69.6 | [Girshick, Landy & Simoncelli 2011 — Cardinal rules: visual orientation perception priors](https://doi.org/10.1038/nn.2831) | Bayesian / ideal-observer / cue combination | 687 | closed | unknown | not started | — | — | — | — |
| 83 | 69.6 | [Jazayeri & Movshon 2006 — Optimal representation of sensory information by neural populations](https://doi.org/10.1038/nn1691) | Population / probabilistic coding | 582 | closed | no | not started | — | — | — | — |
| 84 | 69.4 | [Carandini, Heeger & Movshon 1997 — Linearity and normalization in macaque V1 simple cells](https://www.jneurosci.org/content/jneuro/17/21/8621.full.pdf) | Normalization & attention (R&H family) | 967 | bronze | no | blocked | toward | 4 | 4 | hardened |
| 85 | 69.4 | [van Santen & Sperling 1985 — Elaborated Reichardt detectors](https://doi.org/10.1364/JOSAA.2.000300) | Motion-energy & MT models | 892 | closed | unknown | not started | — | — | — | — |
| 86 | 69.2 | [Montague, Dayan & Sejnowski 1996 — A framework for mesencephalic dopamine (predictive Hebbian)](https://www.jneurosci.org/content/jneuro/16/5/1936.full.pdf) | Reinforcement learning / reward / basal ganglia | 2107 | bronze | no | not started | — | — | — | — |
| 87 | 69.2 | [Kording & Wolpert 2004 — Bayesian integration in sensorimotor learning](https://doi.org/10.1038/nature02169) | Bayesian / ideal-observer / cue combination | 2077 | closed | no | not started | — | — | — | — |
| 88 | 69.2 | [Heeger & Zemlianova 2020 — A recurrent circuit implements normalization (V1 dynamics)](https://www.pnas.org/content/pnas/117/36/22494.full.pdf) | Normalization & attention (R&H family) | 74 | bronze | yes | not started | — | — | — | — |
| 89 | 69.1 | [Uno, Kawato & Suzuki 1989 — Minimum torque-change model of arm trajectory](https://doi.org/10.1007/BF00204593) | Motor control & cerebellum | 1701 | closed | no | not started | — | — | — | — |
| 90 | 69.0 | [Amari 1977 — Dynamics of pattern formation in lateral-inhibition neural fields](https://doi.org/10.1007/BF00337259) | Attractor networks / working memory / neural fields | 2084 | closed | unknown | not started | — | — | — | — |
| 91 | 69.0 | [McFarland, Cui & Butts 2013 — Inferring nonlinear neuronal computation (NIM)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003143) | V1 receptive-field / LN / subunit models | 192 | gold | yes | not started | — | — | — | — |
| 92 | 68.9 | [Sompolinsky, Crisanti & Sommers 1988 — Chaos in random neural networks](https://doi.org/10.1103/PhysRevLett.61.259) | Single-neuron & network dynamics | 1042 | closed | unknown | not started | — | — | — | — |
| 93 | 68.5 | [Najemnik & Geisler 2005 — Optimal eye movement strategies in visual search](https://doi.org/10.1038/nature03390) | Bayesian / ideal-observer / cue combination | 861 | closed | yes | not started | — | — | — | — |
| 94 | 68.2 | [Doostani, Hossein-Zadeh & Vaziri-Pashkam 2023 — Normalization in object-based attention](https://doi.org/10.7554/eLife.75726) | Normalization & attention (R&H family) | 9 | gold | yes | faithful | toward | 4 | 2 | hardened |
| 95 | 68.1 | [Heeger 1987 — Model for extraction of image flow](https://doi.org/10.1364/JOSAA.4.001455) | Motion-energy & MT models | 570 | closed | unknown | not started | — | — | — | — |
| 96 | 68.0 | [Compte, Brunel, Goldman-Rakic & Wang 2000 — Synaptic mechanisms of spatial working memory](https://academic.oup.com/cercor/article-pdf/10/9/910/9751089/100910.pdf) | Attractor networks / working memory / neural fields | 1221 | bronze | yes | not started | — | — | — | — |
| 97 | 68.0 | [van Hateren & Ruderman 1998 — ICA of natural image sequences -> spatiotemporal filters](https://pure.rug.nl/ws/files/3197234/1998ProcRSocLondBvHateren2.pdf) | Sparse / efficient coding | 429 | green | no | not started | — | — | — | — |
| 98 | 67.8 | [Friston & Kiebel 2009 — Predictive coding under the free-energy principle](https://www.ncbi.nlm.nih.gov/pmc/articles/2666703) | Predictive coding / free-energy | 1641 | green | partial | not started | — | — | — | — |
| 99 | 67.5 | [Seung & Sompolinsky 1993 — Simple models for reading neuronal population codes](https://www.pnas.org/doi/10.1073/pnas.90.22.10749) | Population / probabilistic coding | 646 | green | no | not started | — | — | — | — |
| 100 | 67.3 | [Chichilnisky 2001 — A simple white-noise analysis of neuronal light responses (LNP)](https://doi.org/10.1080/net.12.2.199.213) | V1 receptive-field / LN / subunit models | 851 | closed | unknown | not started | — | — | — | — |
| 103 | 66.7 | [Herrmann, Montaser-Kouhsari, Carrasco & Heeger 2010 — Attention by contrast or response gain](https://doi.org/10.1038/nn.2669) | Normalization & attention (R&H family) | 375 | closed | no | partial | toward | 2 | 3 | self-reported |
| 109 | 65.4 | [Li, Pan & Carrasco 2021 — Presaccadic vs covert spatial attention](https://www.ncbi.nlm.nih.gov/pmc/articles/8552811) | Normalization & attention (R&H family) | 69 | green | unknown | partial | toward | 4 | 2 | hardened |
| 115 | 63.8 | [Boynton 2009 — A framework for describing the effects of attention on visual responses](https://www.ncbi.nlm.nih.gov/pmc/articles/2724072) | Normalization & attention (R&H family) | 138 | green | no | partial | toward | 4 | 2 | self-reported |
| 119 | 63.4 | [Ni, Ray & Maunsell 2012 — Tuned normalization explains the size of attention modulations](https://www.cell.com/article/S0896627312000487/pdf) | Normalization & attention (R&H family) | 123 | bronze | no | faithful | toward | 3 | 0 | VLM |
| 122 | 63.2 | [Pestilli, Ling & Carrasco 2009 — Population-coding model of attention on contrast response](https://www.ncbi.nlm.nih.gov/pmc/articles/2743869) | Normalization & attention (R&H family) | 113 | green | no | partial | toward | 6 | 7 | hardened |
| 135 | 61.8 | [Reynolds, Chelazzi & Desimone 1999 — Competitive mechanisms subserve attention in V2/V4](https://www.jneurosci.org/content/jneuro/19/5/1736.full.pdf) | Normalization & attention (R&H family) | 1260 | bronze | no | faithful | toward | 2 | 0 | hardened |
| 136 | 61.4 | [Schwedhelm, Krishna & Treue 2016 — Extended normalization model (feature-based gain)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005225) | Normalization & attention (R&H family) | 60 | gold | no | partial | toward | 2 | 6 | self-reported |
| 138 | 60.9 | [Ni & Maunsell 2017 — Spatially tuned normalization explains attention-modulation variance](https://www.physiology.org/doi/pdf/10.1152/jn.00218.2017) | Normalization & attention (R&H family) | 50 | bronze | no | faithful | toward | 2 | 1 | hardened |
| 141 | 60.7 | [Ni & Maunsell 2019 — Spatial and feature attention differ due to normalization](https://www.jneurosci.org/content/jneuro/39/28/5493.full.pdf) | Normalization & attention (R&H family) | 47 | bronze | no | partial | toward | 2 | 0 | hardened |
| 161 | 56.3 | [Coen-Cagli, Dayan & Schwartz 2012 — Surround interactions via natural scene statistics (MGSM)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002405) | Normalization & attention (R&H family) | 126 | gold | unknown | blocked | — | 5 | 0 | hardened |
| 175 | 54.1 | [Ghose & Maunsell 2008 — Spatial summation explains attentional modulation in V4](https://www.jneurosci.org/content/jneuro/28/19/5115.full.pdf) | Normalization & attention (R&H family) | 88 | bronze | no | partial | toward | 3 | 2 | VLM |
| 192 | 50.2 | [Verhoef & Maunsell 2017 — Attention operates uniformly throughout RF and surround](https://doi.org/10.7554/eLife.17256) | Normalization & attention (R&H family) | 22 | gold | no | faithful | toward | 3 | 0 | self-reported |
<!-- END AUTOGEN: reproduction-table -->
