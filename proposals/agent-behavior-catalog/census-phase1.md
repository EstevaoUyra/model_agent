# Phase-1 census — precision-adjusted denominators + the post-fix-corpus finding

**What we did (2026-06-29).** Phase 0 scanned all 2062 workflow-agent transcripts deterministically
for each behavior's high-recall signature → candidate counts (`evidence/census-phase0.md`). Phase 1
had 5 LLM adjudication agents label a stratified 30-sample per behavior (half from the parallel-batch
days) true/false-positive, giving **precision**; true-count estimate = candidate × precision, with a
Wilson 95% CI (n=30, so the CIs are wide — these are order-of-magnitude, not point estimates). 46
new examples were harvested and verified verbatim (`*.census.quotes.jsonl`).

## The headline finding (answers "are there lots of un-referenced instances?")

**Mostly no — and the reason is structural.** The `wf_` corpus *starts 2026-06-02*, the day of the
faithfulness redesign (#5). It is the **post-fix regime**. So for the grader-side fidelity behaviors,
the originating failures predate this window; what the corpus contains is the system *catching* them.
Across the 19 censused behaviors, **~93–100% of candidate matches are the agent doing the right thing**
(naming a divergence and keeping the tripwire RED, preserving the shared scale, re-rendering before
judging, refusing to fabricate). That honest-handling majority **is the `P#` positive baseline the
catalog was missing** — the denominator, not missed failures.

**The exception is the Generation family and the active-tuning/routing behaviors** — things you can't
fully *gate*, so they persist into the corpus and leave real un-referenced instances.

## Precision-adjusted estimates (true instances in the post-fix corpus)

| Behavior | candidates | precision (TRUE/30) | est. true | 95% CI | read |
|---|--:|--:|--:|--|---|
| T2 substrate (matplotlib) | 294 | 27% | ~78 | 42–131 | real, but *blameless substrate* (Kind: env), not a bias |
| **G2 result-bearing stub** | 234 | 27% | **~62** | 33–104 | **real gap — generation-side** |
| E11 magnitude-in-test-code | 517 | 10% | ~52 | 18–132 | weak signature (`audited:false` broad); real core small |
| **X1 over-route to human** | 256 | 17% | **~43** | 19–86 | real |
| E10 false paper-attribution | 484 | 7% | ~32 | 9–103 | mostly one contested incident (rao) |
| **G1 confabulate/fabricate** | 167 | 17% | **~28** | 12–56 | **real gap — and all 5 TRUE were parallel-batch** |
| E1a leniency-acquit | 402 | 7% | ~27 | 7–86 | real but uncommon |
| **X3 tune per-figure knob** | 51 | 23% | ~12 | 6–21 | real but *single-model* (RH/hermann gain) |
| E1b, T5, X2, E9 | — | 3–7% | <20 | wide | rare / signature near-unusable |
| E2, E3, E5, E6, E7, E8, E12 | — | **0%** | ~0 | 0–(wide) | **not found in this corpus — post-fix window** |

## How to read the zeros (important honesty point)

`0/30` does **not** mean "never happened." It means **not text-detectable in the post-fix corpus**:
- **E2** (same-actor reversal) — the heeger smoking gun *exists* (it's in the entry) but isn't reachable
  by keyword sampling; needs same-actor disposition-flip detection.
- **E6/E8** — the originating failures (3/3 agents; the digitizer self-grade) **predate the snapshot**.
- **E12** — lives in retro proposals, not role-tagged narration.
- **E3/E5** — the slice is saturated with the *guards' vocabulary* (`adversarial`, `audited:false`,
  `all tests pass`) used in the corrected behavior; the real instances (RH hidden gains, heeger
  laundered sign-off) are the documented entry smoking guns, not a corpus rate.

So these threads stay **anecdote-bounded with their curated smoking gun** — which, given the window, is
about as complete as this evidence allows. The references in those entries are *not* missing a large pile.

## Concurrency note (your parallel-passes intuition)

The TRUE n's are too small for a firm rate, but the one clean signal: **G1's 5 TRUE fabrications are
all on parallel-batch days (5/5)**, and G2 splits 4/4. Consistent with "fabrication recurs under
concurrent load," but n is small — flagged `[to-verify]`, not asserted. The candidate-level
parallel concentration (46–76%) is real but inflated by the honest-handling majority.

## What changed in the catalog from this

- **46 verified census examples** appended to `*.census.quotes.jsonl` for the censusable threads —
  extra references beyond each entry's curated smoking gun, weighted to the early/parallel windows.
- **Denominators** for the censusable threads are the estimates above (this doc is the record;
  entries point here rather than each restating it).
- **The `P#` baseline is now evidenced**: ~93–100% of candidates per behavior are correct handling.
- **Two reusable instruments committed**: `census_detect.py` (Phase 0) + `build_samples.py` (Phase 1a).

## What remains genuinely open (and why it's diminishing returns)
- Real failure-*rates* (not just "≥ exists") for E2/E6/E8/E12 need a **different evidence window** —
  the pre-#5 era in the 23 orchestrator/top-level sessions (barely mined) + the post-mortems' own
  counts ("49% wrong figures"). That is the one place more digging would change a number.
- Everything else is precision-bounded here; sweeping harder in the post-fix `wf_` corpus mostly
  harvests more positive baseline.
