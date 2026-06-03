# Corpus-level Process Audit — final systemic-drift sweep (2026-06-03)

Auditor: Process Auditor (meta-critic, reasoning-trail only — did not open papers).
Scope: all reproduced models under `models/` (23 reproduced + 3 newly-landed untracked:
`cagly2012`, `carrasco2021`, `hermann2010` — swept too). Unit of analysis: the trail of
decisions (calibration ledgers, `spec_questions.md`, READMEs, git/commit trajectory), NOT
artifact-vs-paper correctness (that is the Faithfulness Auditor's handoff).

---

## (a) Corpus-level honesty verdict: **toward-faithfulness** (with two lingering ledger-flag defects)

The dominant, repeated pattern across the corpus is **self-correction toward the paper**,
much of it dated 2026-06-03 (this wave). The trail shows the project's own critics
actively *catching and reversing* the exact 2026-06-02 leniency signatures, naming them in
the log rather than burying them:

- **Laundered-contradiction reversal (rao_ballard_1999).** A prior guard `Q-505`
  ("feedback removal does not increase the count") was explicitly re-labelled in the log
  as *"itself a laundered contradiction — a guard that greens a paper-contradicting
  per-neuron count (27→24 vs paper 28→5) by asserting a trivially-satisfied direction"*
  and **routed** as `SQ-006` SUSPECTED-PAPER-ISSUE, with the figure marked ILLUSTRATIVE
  and the paper's convergence claim **restored** as `pytest.mark.xfail(strict=True)`
  (`SQ-007`, Q-304). This is the textbook *correct* route, applied to a real prior defect.
  (`models/rao_ballard_1999/logs/spec_questions.md:110-184`)
- **Synthesized-claim reversal (heeger_1992 SQ-005).** A prior fix that re-attributed a
  "60 deg" operator range to the plotted response (and widened V_e to 84.853 = 60·√2 to
  make the bell match the drawing) was reversed as *"a synthesized claim the paper
  directly contradicts"*; the verbatim text is honored and the text-vs-drawing gap routed
  as a paper defect, not silently closed.
  (`models/heeger_1992/logs/spec_questions.md:84-110`)
- **Fabricated-degree-of-freedom removal (ni_maunsell_2019 SQ-001).** A stub had given
  each unit-config a *second* fitted beta and pinned `panelC.beta_feature=1` to force
  `FMI=0` — "a fabricated degree of freedom that made the unreproducible panel-C magnitude
  constructible." It was **removed**; the binding test downgraded to the reproducible part;
  Fig.5 disclosed ILLUSTRATIVE-NOT-REPRODUCED. (`models/ni_maunsell_2019/logs/spec_questions.md:13-40`)
- **Overstated-disclosure reversal + self-satisfying-test flag (doostani_2023 SQ-009/010).**
  A round-1 disclosure ("Pat ≈ PatN within 0.1–0.2; PatN is the peak in V1/PPA") was found
  FALSE by re-audit (Pat strictly the peak in all five ROIs) and corrected; critically the
  log itself flags that the binding test `Q-4-asym-sum-largest` was "authored in the SAME
  step as the ledger change" and demands an **INDEPENDENT RE-AUDIT** for self-satisfaction.
  (`models/doostani_2023/logs/spec_questions.md:328-441`)
- **Process-audit-driven ledger downgrade (pestilli_ling_carrasco_2009).** `pcrf.normalization`
  was downgraded `audited:true → audited:false` with a `quote_note` explaining the caption
  fragment is verbatim but *which* curve is pinned to 1.0 is INFERRED — tagged
  "(Process-Audit wave1 2026-06-03)". (`.../pestilli_ling_carrasco_2009/article_aware/spec/calibration.yaml:55`)

**Check 2 (illustrative-honesty): PASS across all 11 named illustrative models.** Every one
carries an explicit `ILLUSTRATIVE-NOT-REPRODUCED` / "stubbed" / "frozen-fit" disclosure in
its README, and the result-bearing ones explicitly state the **headline magnitude is NOT
asserted** (ni_maunsell_2017 Table-1 "the paper's quantitative headline is not reproduced";
ni_maunsell_2019; rao_ballard; doostani; pestilli; zhu_rozell SQ-008). The one numeric test
that looks like a headline assert — `ni_maunsell_2017 test_stages.py:217 assert ev > 0.98` —
is honest: its name is `test_ems_spatial_fits_its_own_generated_data_near_perfectly` and the
docstring labels it the A-007 *circularity artifact*, not the paper's 92% claim. No
illustrative model quietly asserts a constructed result as reproduced.

**Check 3 (self-satisfying / laundered-contradiction): PASS.** The three models carrying
`SUSPECTED-*` tags (rao_ballard, heeger_1992, doostani_2023) are all HONEST routes — real
divergences logged for the human, several of them *corrections of prior laundering*. No test
was found asserting the opposite of a paper claim; where the model contradicts the paper, the
paper's claim is preserved as an `xfail(strict=True)` (rao_ballard) and the contradiction is
routed, not greened.

**Aggregate:** the trajectory consistently cites the paper, sharpens checks, and reverses its
own earlier lenient moves *in the log*. This is the instrument working. The corpus is
**toward-faithfulness**.

---

## (b) Lingering drift defects (named, with file:line)

Both are **drift-signature 8 (flag inflation / silent under-citation)**: `audited: true`
attached to **assumption-sourced** values, contradicting the ledger's own stated rule
(`audited:true → value directly cited from the paper`, e.g. denison2021 calibration header
lines 9, 19-23). These are the inverse of the denison correction (denison was tightened
true→false; these two were never tightened). Severity **moderate** — none is a result-bearing
magnitude — but each is exactly the flag-laundering the denison pass was meant to eradicate,
so it should be reconciled corpus-wide.

1. **reynolds_heeger_2009** — 4 underspecified globals marked `audited: true` while sourced to
   an **assumption** and noted only against `model_spec parameters` (no paper quote):
   - `model.sigma` (A-001) — `article_aware/spec/calibration.yaml:27-32`
   - `model.alpha` (A-002) — `:34-39`
   - `model.threshold_T` (A-003) — `:41-46`
   - `model.beta` (A-010) — `:48-53`
   Recommendation: downgrade to `audited: false` (assumption-resolved global), or supply a
   verbatim paper quote if one exists. Hand the value-vs-paper question to the Faithfulness
   Auditor; the *flag* is the process defect.

2. **verhoef_maunsell_2017** — 5 entries `audited: true` sourced to assumptions
   (`article_aware/spec/calibration.yaml`):
   - `model.sigma` (A-006, `:38-48`) — defensible: note admits it is "a median over a fitted
     distribution," a real paper number; borderline-acceptable but source is A-, not C-.
   - `protocol.distance_grid` (A-004, `:98-107`) — the note says "chosen to match the
     figure's tick spacing": this is an **extractor-chosen sampling grid**, not a paper-cited
     value, yet flagged `audited:true` ("Structural sampling ⇒ audited:true"). A human reading
     `audited:true` reads "verified against the paper"; this grid was picked by the extractor.
   - `protocol.L_sweep_n` (A-005, `:111-116`), `protocol.alpha_sweep_n` (A-005, `:125-130`),
     `protocol.heatmap_bins` (A-005, `:142-147`) — same: self-chosen sweep/plot counts flagged
     audited:true.
   Recommendation: these "structural sampling" knobs are assumptions and should be
   `audited:false` (or moved to implementation-side calibration, as denison/reynolds_heeger
   do for plotting/solver knobs). The model has redefined `audited` to mean "not-a-frozen-fit"
   rather than "paper-cited"; that local redefinition diverges from the corpus rule.

**Systemic schema split (lower-severity, route to organizer for a corpus convention, not a
per-model defect).** The corpus has two ledger styles for `audited:true` provenance:
- **`quote:`-field style** (the mature schema): `boynton_2009` (13), `zhu_rozell_2013` (8/6),
  `pestilli` (1), `denison2021` (the reference). These carry a verbatim string field and are
  the cleanest to audit.
- **`note:`-embedded-quote style**: most `audited:true` notes embed a verbatim single-quoted
  fragment with a locator — e.g. `ghose_maunsell_2008` `'slope, 0.578'` / `'exponent, 2.07'`
  (`:17-18`); `ni_maunsell_2017` `'we set beta for all neurons equal to 3.68 …'` (`:25`);
  `lee_maunsell_2009` "Fig. 3 caption: u=1 …" (`:14`); `carandini_heeger_movshon_1997`
  "Fig.3 caption: τ0 = 37 msec" (`:21`). These ARE verbatim-anchored — **not** synthesized.
- **bare-paraphrase note style** (the only mild concern): `rao_ballard_1999` "Paper: k1 = 0.5
  (rate of gradient descent in r)" (`:18`); `spratling_2010` "Paper: epsilon1 = 0.0001"
  (`:20`); `cagly2012` "Paper: RF diameter 9 px" (`:17`). These read as faithful
  *transcriptions* of plain numeric constants, not synthesized sentences, so they are NOT the
  denison defect (which was a numeric **table cell** dressed as a quotable sentence). No action
  required beyond noting that the corpus would be more auditable on the single `quote:`-field
  schema.
- **Confirmed:** spot-checking the `audited:true` quotes/notes across all models found **no
  other denison-style synthesized quote** — i.e. no `audited:true` whose "quote" is a
  fabricated sentence the paper does not contain. The recurring drift denison exhibited does
  not recur elsewhere.

---

## (c) Consolidated SUSPECTED-PAPER-ISSUE / underspecification ratification list

Items needing human ratification, grouped by urgency. (Routine "resolved-by-assumption,
pending periodic-panel sign-off" SQs — e.g. contrast-unit conventions, solver dt, grid sizes
— are omitted unless they bear on a paper claim; bracketed counts note how many such routine
pending SQs each model also carries.)

### Tier 1 — genuine paper contradictions / internal inconsistencies (routed, OPEN)
| Model | SQ | One-line |
|---|---|---|
| rao_ballard_1999 | SQ-006 | Fig.5 per-neuron endstopped count contradicts paper (27→24 vs 28→5); is the 28→5 collapse only reachable with the Eq.9-LEARNED basis (lift learning-stub scope)? |
| rao_ballard_1999 | SQ-007 | Fig.3 single-neuron r^td does NOT converge onto r at long bars over the constructed basis (gap WIDENS); same root as SQ-006/SQ-001. Restored as xfail(strict). |
| heeger_1992 | SQ-005 | Paper-internal inconsistency: verbatim "60 deg operator range" text vs the wider DRAWN Fig.5C panel (~56 deg ⇒ ~80 deg operator) — cannot both hold for a Gaussian. |

### Tier 2 — result-bearing illustrative divergences (disclosed; need human sign-off that ILLUSTRATIVE is the right disposition, not a fix path)
| Model | SQ | One-line |
|---|---|---|
| ni_maunsell_2017 | SQ-003 | Table-1 model-comparison headline (74–92% EV, ~14-pt EMS margin) NOT reproduced over EMS-generated reference (all forms ~0.94–1.00); partial-circularity contract boundary. |
| ni_maunsell_2019 | SQ-001 | Fig.5 panel index magnitudes not reproducible under the paper's single beta (FMI≥SMI generically); fabricated 2nd-beta DOF removed. |
| zhu_rozell_2013 | SQ-006 | Cross-orientation suppression (Fig 8F) single-cell-robust but does NOT generalize across the stub-dictionary population. |
| zhu_rozell_2013 | SQ-007 | Fig-7D half-width-vs-contrast slope single-cell-faithful but does NOT hold across the stub-dictionary population. |
| zhu_rozell_2013 | SQ-008 | Whole constructed-stub figure set is ILLUSTRATIVE-NOT-REPRODUCED (result-bearing stub), not plain-green-faithful; path to REPRODUCED = real `olshausen` dictionary. |
| doostani_2023 | SQ-002 | Figs 3/4/5 are constructed-comparison (the "data" IS the normalization forward) → standing ILLUSTRATIVE-NOT-REPRODUCED. |
| doostani_2023 | SQ-009/010 | Asymmetry inversion + isolated-Pat peak STRUCTURALLY IRREDUCIBLE under the binding clutter-suppression claim; binding test needs INDEPENDENT re-audit (authored with the ledger change). |
| doostani_2023 | SQ-006 | Noise-ceiling sub-claim (Q-3-noise-ceiling) DEFERRED / out of scope — confirm deferral, not a dodge. |
| carrasco2021 | SQ-001 | RG "invariance across uncertainty" is a fit artifact, not a forward-model property; forward-faithful signature substituted. |
| carrasco2021 | SQ-002 | NMA d′ amplitude is fit-scale-dependent; only the gain-type shift is a forward property. |
| hara_gardner_2016 | SQ-005 | Fig.8 "two extension curves NEARLY COINCIDE" (C-014) structurally unreachable with paper-fixed N_V/N_IV; figure_8 DEFERRED. |
| hara_gardner_2016 | SQ-006 | The Fig.8 "extensions coincide" deterministic tripwire is too LOOSE to bind the VLM claim (loose-test note for organizer). |
| ni_ray_maunsell_2012 | SQ-002/003 | beta held-fixed-vs-free choice for forward predictions; representative L_N for null driver — per-protocol, not paper-tabulated. |

### Tier 3 — underspecification frozen by assumption (need ledger ratification; non-blocking)
| Model | SQ(s) | One-line |
|---|---|---|
| denison2021 | SQ-005, SQ-008 | Orientation grid M / S1 tuning exponent m underspecified; voluntary no-limit allocation constant paper-underspecified (escalated). |
| bell_sejnowski_1997 | SQ-001/003 | No published W; original natural-scene images unavailable (stub frozen). |
| olshausen_field_1996 | (stub) | Learning out of scope; frozen-dictionary stub → SF-distribution panel ILLUSTRATIVE. |
| karklin_lewicki_2009 | (stub) | Second-layer B is a structured-stub stand-in for a learned B (disclosed). |
| spratling_2010 | SQ-001 | Fig.6a plaid combination: literal-sum vs mean-preserving additive. |
| spratling_2012 | SQ-001/002 | Paper figure images / full-text Methods could not be fetched; Mexican-hat magnitude threshold underspecified. |
| bogacz2017 | SQ-001/002 | Gradient-ascent vs error-network stage boundary; variance-learning stage scope. |
| cagly2012 | SQ-003/004 | No published MGSM parameters; GEM-stub cannot fix the SIGN of contrast/homogeneity-driven suppression. |
| hermann2010 | SQ-001/002/003 | Fig.1/3 regime sizes not in model units; R&H 1D suppressive calibration leak into ledger; flanker absolute-vs-multiplicative gain. |
| lee_maunsell_2009 | SQ-005/006 | Eq.13 "90 sp/s scaling": peak vs raw coefficient; Fig.2B equal-vs-unequal R_max (Methods vs figure). |

---

## What I traced (so the report's brevity reads as coverage, not a narrow search)

- All 25 `calibration.yaml` ledgers parsed (`audited:true` count, `source`, `quote:` presence,
  note-embedded-quote heuristic) — the basis for the (b) flag-inflation findings.
- All 27 `logs/spec_questions.md` enumerated; every `SUSPECTED-*` and `(pending)` entry read.
- All 11 named illustrative READMEs read for disclosure language; their tests grepped for
  headline-magnitude asserts (only the ni_maunsell_2017 circularity assert surfaced, and it
  is honest).
- Corpus git trajectory (waves 1→4 "faithfulness regime") scanned for threshold-loosening
  commit messages — none at corpus level (per-model history lives in submodules; hand specific
  ledger-value questions to the Faithfulness Auditor).

## Routing (separation of powers — I resolve nothing)
- **(b) defects → organizer + builder:** reconcile `audited:true` on assumption-sourced
  entries in `reynolds_heeger_2009` (4) and `verhoef_maunsell_2017` (5) to the corpus rule;
  consider adopting the `quote:`-field schema corpus-wide.
- **(c) Tier-1 + Tier-2 → human/spec-review panel:** these are paper-ratification calls, not
  agent closes. doostani SQ-009/010's binding test needs the independent re-audit it requests.
- **Value-vs-paper questions → Faithfulness Auditor** (handoffs, not mine to settle).

### Aggregate verdict: `toward-faithfulness`
The justification trajectory consistently cites the paper, sharpens checks, and — most
tellingly — reverses its own prior lenient moves in the open log (rao_ballard, heeger_1992,
ni_maunsell_2019, doostani, pestilli). The only standing drift is two ledgers' flag-inflation
(`audited:true` on assumptions), moderate severity, no result-bearing magnitude affected.
No model quietly asserts a constructed result as reproduced; no test asserts the opposite of a
paper claim. The denison synthesized-quote defect does **not** recur elsewhere.
