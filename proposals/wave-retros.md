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

**Still open after revision:** → next entry.
