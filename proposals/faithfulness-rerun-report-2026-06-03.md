# Faithfulness re-run — consolidated report (2026-06-03)

The whole corpus (23 models) was re-run under the new faithfulness regime
(`skills/audit-faithfulness` + `skills/audit-process`, the gates rewired per
[faithfulness-enforcement-2026-06-02.md](faithfulness-enforcement-2026-06-02.md)),
in four waves + targeted closeouts, **all landed on `main`** (23/23 submodule
pointers consistent). Per-model loop: Faithfulness Auditor → remediation → fresh
independent re-audit, looped until faithful or honestly-dispositioned, then a
Process Audit on the trail. **Nothing was forced green.**

## The headline finding: the faithful / illustrative split

The single most important output of the new regime is a split the **old gate
completely hid** (it called all 23 "green"):

- **~12 models reproduce faithfully** — the analytically-specified ones (divisive
  normalization, attention gains, CRFs). Their figures, equations, and parameters
  match the paper.
- **~11 models are honestly `ILLUSTRATIVE-NOT-REPRODUCED`** — their *headline result
  is a learned or fitted component that is stubbed* (sparse-coding dictionaries,
  per-observer fits, second-layer pooling). The forward model is faithful, but the
  figure that demonstrates the paper's claim shows a *constructed* answer, not a
  reproduced one. The old gate shipped these as green; the new regime discloses them.

This split is the real deliverable: it tells a scientist, per model, *what is
actually reproduced* vs *what is illustrated pending the learning/fitting being
implemented*.

## Verification tiers — what each verdict actually rests on (READ THIS)

A `faithful` / `dispositioned` verdict is only as strong as the paper material that
was available to compare against. Surfaced by a user audit of this report (2026-06-03):
**not every figure was compared to a paper figure, because for some there is no paper
figure image — and in a few cases no paper at all.** Where there is no paper image,
the *entire* chain is self-referential: the Phase-A extractor wrote the
`figure_N.md` + checklist **paper-blind** (from the model's intended behavior +
literature), the figure is produced by that model, and the VLM / Faithfulness Auditor
check the figure against that checklist. Such a loop can confirm *"the model does what
we designed it to do"* — it **cannot** confirm *"the model matches the paper."* The
audits flagged these `UNVERIFIED-vs-paper`, but the summary verdicts conflated them
with genuinely paper-compared models. Three tiers, made explicit:

| Tier | What it rests on | Figures / models |
|---|---|---|
| **paper-verified** | rendered figure compared to the paper's figure **image** | the ~78 in-scope figures (≈20 models) that have a `figure_N.jpg/png` |
| **paper-text-verified, no figure image** | equations/values checked vs the paper **text/PDF**, but the figure itself has no paper image | carrasco2021 `supp_figure_4`; ni_ray_maunsell_2012 `figure_A/B`; ni_maunsell_2019 `figure_mechanism` (the model's other figures *are* paper-verified) |
| **self-referential — NO paper anchor** | checklist authored paper-blind; nothing in the pipeline ever saw the paper | **karklin_lewicki_2009** (all 4 figs — paper paywalled, `PAPER_IMAGES_NOTE.md`), **rozell2008** (all 3), **spratling_2012** (all 4) |

**The three self-referential models (karklin, rozell, spratling_2012) are NOT
paper-verified** — their "faithful/dispositioned" status reflects only that the model
reproduces the behavior the checklist (derived from the paper's *prose* + general
literature) describes. Lifting them to paper-verified requires the paper itself:
rozell (2008) and spratling (2012) PDFs are obtainable and should be re-audited
against real figures; karklin (KL2009, *Nature*) is paywalled and blocked. This is the
post-mortem's core defect (internal consistency standing in for paper fidelity) in its
*total* form for these figures — and the regime cannot repair it without the paper.

## Per-model ledger

### Faithful (12)
| Model | Notes |
|---|---|
| boynton_2009 | normalization convention fixed (attended→1.0), spurious diff-panels removed, all 4 figs faithful |
| lee_maunsell_2009 | Methods four-location averaging restored (round-1 green-tuning self-corrected); minor Fig2B paper-issue |
| carandini_heeger_movshon_1997 | **Fig.11 vectorial-polar recovered** — original repro had laundered the paper's vectorial claim into an always-true scalar substitute |
| heeger_1992 | FWHM reverted to the paper's verbatim 60° (a fix-agent had laundered it to 85°); 60-vs-drawn-80 inconsistency → SQ-005 |
| reynolds_chelazzi_desimone_1999 | indices/protocol corrections |
| bogacz2017 | faithful, 0 fixes |
| ghose_maunsell_2008 | faithful model panels, 0 fixes |
| ni_ray_maunsell_2012 | faithful, 0 fixes |
| rozell2008 | LCA dynamics; model-generated figures, checklist-faithful (no paper image) |
| spratling_2010 | faithful, 0 fixes |
| spratling_2012 | model-generated, checklist-faithful |
| verhoef_maunsell_2017 | faithful model panels, 0 fixes |

### Honestly-dispositioned — ILLUSTRATIVE result-bearing stub (11)
| Model | Stubbed result-bearing component |
|---|---|
| pestilli_ling_carrasco_2009 | per-observer attention-gain fit → figs 3/5/6/7 illustrative (forward model faithful; provenance drift corrected) |
| zhu_rozell_2013 | learned sparse dictionary → figs 2/3/8 illustrative |
| hara_gardner_2016 | NMoA fitted params → figs 7/8 illustrative; Fig.8 coincidence → SQ-005 |
| doostani_2023 | model-comparison is circular (synthetic data from the model) → figs 3/4/5 illustrative; peak-ordering → paper-issue |
| olshausen_field_1996 | the learned Gabor dictionary (the headline result) is a constructed stub → figs 7/8/9 illustrative |
| ni_maunsell_2017 | Table-1 EV comparison circular (reference responses EMS-generated) → Table-1 illustrative |
| bell_sejnowski_1997 | learned ICA unmixing W → figs 4/5 illustrative |
| karklin_lewicki_2009 | second-layer pooling structured-stub → illustrative |
| ni_maunsell_2019 | Fig5C's FMI=0/large-SMI needs an extra-DOF per-block fit → Fig5C illustrative; NMI equation corrected |
| rao_ballard_1999 | learned basis stubbed → figs 2/3/5/6 illustrative; endstopped-count + r^td → SQ-006/007 |
| denison2021 | absolute-d′ readout_gain illustrative; no-limit allocation → SQ-008; synthesized-quote provenance corrected |

## SUSPECTED-PAPER-ISSUE ratification list (needs your judgment)

These are cases where the *faithful* build contradicts or cannot satisfy the paper as
stated — surfaced honestly rather than papered over. A human (you) decides whether
each is a genuine paper problem, an acceptable scope boundary, or warrants more work:

1. **heeger_1992 (SQ-005)** — filter orientation width: text states "60°" but the
   *drawn* Fig.5C implies ~80°; no single Gaussian operator satisfies both. The build
   now honors the verbatim 60°.
2. **hara_gardner_2016 (SQ-005)** — Fig.8: the ciN/cdN curves do not coincide as the
   published panel shows, under the faithful N(θ) two-scalar operationalization.
3. **doostani_2023** — Fig.2/3 peak-ordering: the paper's text says paired-PatN is the
   curve peak, but the equations (and a 200k-draw search + closed-form argument) give
   isolated-Pat as the peak.
4. **rao_ballard_1999 (SQ-006/007)** — Fig.5 per-neuron endstopped count 27→24 vs the
   paper's 28→5; Fig.3 r^td non-convergence vs the paper's residual→0 mechanism (both
   artifacts of the constructed, non-Eq.9 basis).
5. **denison2021 (SQ-008)** — the no-limit un-cued allocation constant is
   underspecified by the paper.

## What the regime caught that the old gate shipped

- **Real model bugs:** carandini's Fig.11 (laundered vectorial→scalar), ni_2019's NMI
  equation (dropped a term), boynton's normalization inversion, heeger's operator width.
- **Real drift introduced by the fix agents themselves**, caught by the independent
  re-audit / Process Auditor: pestilli's fabricated `audited:true` quote, denison's
  systematically synthesized quotes, heeger's laundered FWHM, lee_maunsell's
  green-tuning — each reversed before landing.
- **Constructed-result honesty:** every result-bearing stub now discloses
  `ILLUSTRATIVE-NOT-REPRODUCED` instead of shipping a hand-built answer as green.

## The 4 original (pre-regime) models — also run

After the 23, the 4 pre-existing models that never went through the program were
brought through the same loop (entire corpus now = 27):

- **reynolds_heeger_2009** — **FAITHFUL.** The foundational R&H normalization model
  (hermann2010 + carrasco2021 depend on its primitives). The audit caught that the
  original repro had **dropped the paper-present Fig.4 %-modulation curve, with a code
  comment mislabeling it "a spurious analysis panel the paper figure does not
  contain"** — factually wrong; the paper's Fig.4C/4E both draw it. Restored (full
  81-test suite passes, untouched). Its `audited:true`-on-assumption-sourced flags were
  also corrected.
- **cagly2012** — honestly-dispositioned (GEM-learned params stubbed → figs 5/7/8/11
  `ILLUSTRATIVE`).
- **carrasco2021** — honestly-dispositioned (frozen-stub simulations → figs 7/supp-4
  `ILLUSTRATIVE`; RG asymptote-invariance + NMA amplitude → SQ-001/002 paper-issues).
- **hermann2010** — honestly-dispositioned (frozen result-bearing params → fig 3
  `ILLUSTRATIVE`).

**Corpus total: 13 faithful / 14 honestly-dispositioned, all 27 landed on `main`.**

## Final corpus Process-Audit sign-off

The cross-model honesty sweep (`logs/process_audit/corpus-final-2026-06-03.md`)
returned **toward-faithfulness**: illustrative-honesty **PASS** (all 11 stubs
disclosed; no headline magnitude asserted), laundered-contradiction **PASS** (no test
asserts a paper's opposite; the `SUSPECTED-*` routes are honest, several *correcting*
prior laundering), and the denison synthesized-quote defect confirmed **not recurring**
elsewhere. It found exactly two moderate flag-inflation defects (the *inverse* defect:
`audited:true` on assumption-sourced values) — **verhoef_maunsell_2017** and
**reynolds_heeger_2009** — both **now downgraded to `audited:false` and landed**. The
corpus is clean.

## Process learnings (the recipe evolved across waves)

- **MAX_ROUNDS 3→2; render-only verification** (don't re-run slow full pytest suites);
  **`perl`-timeout** on every render (no `timeout`/`gtimeout` on macOS) — Wave 2 ran
  ~3× faster than Wave 1.
- **ILLUSTRATIVE / SUSPECTED-PAPER-ISSUE terminate the loop** (don't waste rounds
  "fixing" honest dispositions).
- **Plain-text agents** (verdict-block parsing) replaced schema-forced output — the
  StructuredOutput call kept getting dropped by heavy agents, losing verdicts.
- **Two recurring agent defects requiring organizer recovery:** agents that do the fix
  but don't commit it; agents that re-introduce synthesized quotes. The independent
  re-audit caught the consequences; the organizer committed/cleaned. Both are candidates
  for the next recipe hardening (a commit-gate; a ledger-quote linter).
- **The two-auditor design proved itself repeatedly:** the artifact auditor caught
  wrong science; the process auditor caught reasoning drift the artifact auditor missed
  (pestilli, denison). Orthogonal data, complementary catches — as designed.
