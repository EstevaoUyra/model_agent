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
- **spratling_2010** → Phase B running.

**Phase-B lesson → guideline:** schematic figures must render the *specified
iconography* (the glyphs/panels the visual checklist names), not simplified
box/text placeholders — correct topology with wrong iconography still fails the
binding checklist. Added to WORKFLOW.md Phase B.

## Wave 2 — launched 2026-06-02 (6 in parallel)

Phase A for Denison 2021, Verhoef & Maunsell 2017 (C1); Rozell LCA 2008,
Bell & Sejnowski 1997 (C2); Rao & Ballard 1999, Bogacz 2017 (C3) — with the new
**content-only spec-review** (the organizer owns the git gate). Rozell-LCA and
Verhoef declare reuse of primitive stages (olshausen dictionary; R&H normalization
primitives) per the §1 reuse-surface rule. → outcome next entry.
