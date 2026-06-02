# Wave retros — the reproduction program's running improvement ledger

Pillar-4 process-knowledge ([VISION.md](../VISION.md)): the program improves its
guidelines **every iteration**. Each entry = what ran, what was learned, and the
concrete guideline/skill/canon edit it produced. Newest first.

---

## Wave 1 — Phase A (setup + extraction + spec-review) — 2026-06-02

**Ran:** workflow `wss72q6ay` — 3 extraction agents + 3 adversarial spec-review
panels for `lee_maunsell_2009` (C1), `olshausen_field_1996` (C2),
`spratling_2010` (C3). Each repo created (private), scaffolded from the
cagly2012 template, Phase A authored on a `repro` branch, pushed.

**Verdicts:** spratling_2010 **approved**; lee_maunsell_2009 + olshausen_field_1996
**revise**. Revision round: workflow `woukyc13z`.

**Headline — the autonomous gate substitution works.** The critique panels caught
genuine *green-but-unfaithful* defects a human gate would have had to catch:
- **olshausen_field_1996:** the extractor **invented a false mechanism** ("pixel
  basis ⇒ b == a"; mathematically wrong — an identity dictionary still applies
  soft-threshold shrinkage) **and a fabricated quantitative claim** (Q-905,
  learned-more-kurtotic-than-pixel) cited to a real reference. Both killed before
  they reached Phase B.
- **lee_maunsell_2009:** an internal contradiction on the load-bearing
  contrast-units convention (provenance/calibration notes said "percent" while
  the verified rule is "fraction" — percent silently zeroes the attention
  effect).

**Failure mode → guideline fix (applied):** extraction agents can confabulate
mechanisms/claims and bury binding thresholds in test code. Added the
**"Faithfulness rules (extraction)"** block to [WORKFLOW.md](../WORKFLOW.md)
Phase A — *never confabulate (cite the passage or mark an A-NNN); thresholds live
in the ledger; one unit convention everywhere; verify internal consistency with a
throwaway reference impl.* Wave-2 extractors inherit it.

**Process notes:**
- Reviewers tended to mislabel `article_aware/` corrections as "Phase B should…".
  `article_aware/` is Phase-A-owned (Phase B is paper-blind) — the revision round
  applies those in Phase A. (Folded into the revise briefs.)
- Cost visibility (uncapped per user): Wave-1 Phase A ≈ 818k subagent tokens / 6
  agents. Each extraction agent read the full paper and wrote a throwaway
  reference impl to self-check — expensive but it is what caught the defects.

**After revision (round 2):**
- **lee_maunsell_2009 + olshausen_field_1996 → APPROVED** (organizer-gated).
  lee_maunsell was content-approved by the panel; olshausen needed one more fix —
  a false pixel-control claim ("identity bases give no sparsity gain") still
  lurking in the Fig-9 *visual checklist* after the revision removed it
  everywhere else — applied by the organizer.
- **spratling_2010 → one more pass.** Real catch: the Fig.6a iso-point relaxation
  landed in the test + ledger but three figure/protocol docs still asserted strict
  suppression at all orientations, and the cited paper text (C-011) says "all mask
  orientations" — so whether the relaxation is even faithful needs the figure/
  paper. A focused reconciliation agent is resolving it against `figure_6.jpg`.

**Process lessons → fixes (applied going forward):**
- **Git-context confusion (cost a cycle).** The re-review agents inferred each
  model's git state from the **parent** repo — where the model is a *nested,
  untracked* repo — and falsely concluded "the work doesn't exist", a phantom
  blocker that nearly failed an approvable model. *Fix:* any agent doing git
  ops/verification operates INSIDE the model repo (`git -C models/<repo>`);
  model-repo state is never inferred from the parent.
- **Organizer owns the git gate.** Critique / spec-review / re-review agents judge
  **content faithfulness only** — they do not verify push state or write
  `APPROVED`. The organizer verifies git ground-truth in each repo and writes the
  gate. (Removes the brittle agent-git-verification that caused the above.)

**Phase B (paper-blind impl + 3-voter VLM backstop):**
- **lee_maunsell_2009 → GREEN.** Deterministic 20/20 + VLM-green on all 3 figures
  + modification smoke test passing; stage decomposition a *natural* fit (no
  `boundary: imposed`). Flag for final triage: figure_1 (schematic) passed by VLM
  majority but a voter flagged simplified iconography (plain boxes/text vs the
  specified sigmoid+arrow pools and the Gabor-in-RF-ellipse inset) — topology
  correct, low scientific impact.
- **olshausen_field_1996 → GREEN.** Deterministic 13/13 + VLM-green on all 3.
- **spratling_2010 → GREEN (4/4).** figure_6/9/11 green from Phase B; figure_5
  resolved — the model already produced genuine end-stopping (interior peak @ d=11,
  suppression index 0.674); the original Phase-B VLM had read a STALE render.
  Tightened the 5b test (SI≥0.30, ledger A-012; a monotonic/plateau curve now
  fails), regenerated, VLM 2/2 pass, **organizer-verified** (pytest 5a+5b 8/8 at
  HEAD `dac5283`). (Open: SQ-001 — Fig.6a plaid rendered mean-preserving to satisfy
  A-011; human resolution pending.)

**Phase-B lesson #2 → guideline:** the 5b deterministic test PASSED 22/22 on a
curve with NO end-stopping — a **loose visual proxy** (it accepted a plateau as a
"peak"), and the impl agent's *self*-assessment falsely claimed an interior peak.
The **independent 3-voter VLM backstop caught the det/VLM disagreement** the
measurement-record was supposed to prevent. *Fixes:* shape claims (turnover /
end-stopping / saturation / peak) need STRICT structural assertions (interior
argmax that exceeds both endpoints by a ledger margin), so a monotonic/plateau
curve fails; and never trust an impl agent's self-figure-assessment — the
independent VLM is the binding backstop. (Reinforced in WORKFLOW.md.)

**Phase-B lesson #3 → guideline:** the figure the first VLM judged was STALE — the
impl agent's pre-VLM regeneration was unreliable, so the VLM scored an out-of-date
render (monotonic) while the committed model actually produced the turnover.
*Fix:* the VLM step regenerates every figure from the committed model immediately
before reading it — never judge a possibly-stale render. (Added to WORKFLOW.md.)

### ✅ Wave 1 COMPLETE — 3/3 green

**lee_maunsell_2009, olshausen_field_1996, spratling_2010** — all three motifs
(attention-normalization · sparse coding · predictive coding) reproduced
end-to-end through the autonomous pipeline, each organizer-verified. The machinery
and the four-pillar discipline held; three real *green-but-unfaithful* defects were
caught and fixed by the critique/VLM layers (olshausen confabulation, lee_maunsell
contrast-units, spratling end-stopping). **Corpus: 3 / ~22.**

**Phase-B lesson → guideline:** schematic figures must render the *specified
iconography* (the glyphs/panels the visual checklist names), not simplified
box/text placeholders — correct topology with wrong iconography still fails the
binding checklist. Added to WORKFLOW.md Phase B.

## Wave 2 — launched 2026-06-02 (6 in parallel)

Phase A for Denison 2021, Verhoef & Maunsell 2017 (C1); Rozell LCA 2008,
Bell & Sejnowski 1997 (C2); Rao & Ballard 1999, Bogacz 2017 (C3) — with the new
**content-only spec-review** (the organizer owns the git gate).

**Phase A outcome:** 4 approved (denison2021, verhoef_maunsell_2017,
rao_ballard_1999, bogacz2017) + 2 **minor**-revise (rozell2008, bell — both ONLY
the rule-(b) threshold-in-ledger slip; gate caught them, revised → approved).

**Are the improvements holding? (mid-program check)**
- ✅ **No-confabulation held** — the olshausen-class defect did not recur;
  denison even adjudicated an OCR divisive-vs-multiplicative Eq.1 ambiguity
  *without* confabulating.
- ✅ **Organizer-owns-git-gate held** — zero false git-blocks in Wave 2.
- ⚠️ **Thresholds-in-ledger** caught by the gate but still slipped at extraction
  (2/6) → added an explicit **extraction self-check** to WORKFLOW.md (grep tests
  for hard-coded numbers before finishing).
- 🆕 **Repo-naming drift** (`denison2021` vs `denison_2021`) → pinned exact names
  in the Wave-3 brief.

**Phase B outcome (so far):** **rozell2008 GREEN** (3/3; the olshausen
dictionary-PRIMITIVE reuse ran clean with no calibrated-protocol leak — §1
reuse-surface validated across models; honest SQ-004 on a convergence-criterion
inconsistency; the fresh-figure-regen produced first-pass green). **bell → GREEN (organizer-verified).** figure_4 noise was a **STALE PNG
artifact, NOT a model defect**: the committed model's filters are localized=0.951
/ oriented=0.993 (verified by metric AND a fresh organizer re-render showing clean
Gabors). My "noise-inverse stub" hypothesis was wrong — the reconcile agent
correctly found the basis is oriented-but-NOT-localized (the paper's filter-vs-
basis distinction) and usefully ADDED a spectral-concentration floor that rejects
a noise basis. **4-model Phase B done:** denison2021, verhoef_maunsell_2017,
bogacz2017 GREEN; rao_ballard_1999 3/4 (figure_3 `r^td` overlap fix `w8kcqidxn`).
**8 models GREEN total.**

**Phase-B lesson #3 STRENGTHENED (stale figures recurred: spratling fig5, bell
fig4).** The impl/fix agents' "regenerate before VLM" step is unreliable — a stale
PNG wasted a whole bell-fig4 fix cycle (the model was already correct). *Robust
fix:* the VLM-backstop must render figures **deterministically** (a verifier/
organizer render step), not trust an agent's claim; the **measurement record is
the source of truth** — a det-green / VLM-red split means "re-render and re-check
first" (stale figures cause false-NEEDS-WORK, never false-GREEN).

**Decision (user-offered): a 3rd validation wave** — Wave 3 (6) Phase A launched
(`w7q9o2uux`: Zhu&Rozell, Spratling2012, Ni/Ray2012, Hara/Gardner2016,
Pestilli2009, Heeger1992); after it + the Phase-B evidence, the final batch
(remaining ~8) goes out. So the schedule is now **3 → 6 → 6 → rest**.
