# Cost baseline — pre-improvement measurement (2026-06-13)

The **measured token usage of the current (per-figure-parallel) `full-pass.js`**, captured
so we can A/B it against the de-parallelized + diff-scoped version (see
[cost-reduction-2026-06-13.md](cost-reduction-2026-06-13.md)). Numbers are the actual
per-turn billed usage parsed from the workflow agent transcripts (streaming deltas
de-duplicated by contiguous-run collapse).

## The batch — 15 workflow runs (2026-06-12/13)

| # | Model | agents | input | cache-write | cache-read | output | total tok |
|--:|---|--:|--:|--:|--:|--:|--:|
| 1 | pfister_gerstner_2006 | 39 | 206k | 2.99M | 105.7M | 777k | 109.7M |
| 2 | pfister_gerstner_2006 | 22 | 57k | 1.13M | 17.5M | 237k | 18.9M |
| 3 | bienenstock_cooper_munro_1982 | 46 | 186k | 3.51M | 108.1M | 796k | 112.6M |
| 4 | pfister_gerstner_2006 | 23 | 81k | 1.69M | 30.3M | 280k | 32.4M |
| 5 | bienenstock_cooper_munro_1982 | 14 | 45k | 816k | 10.8M | 107k | 11.8M |
| 6 | **flash_hogan_1985** (extract→faithful) | 54 | 187k | 3.79M | 137.2M | 857k | **142.0M** |
| 7 | roxin_ledberg_2008 | 40 | 167k | 2.87M | 98.6M | 687k | 102.3M |
| 8 | zhang_1996 | 57 | 179k | 3.74M | 98.6M | 718k | 103.2M |
| 9 | sutton_1988 | 47 | 156k | 2.70M | 57.3M | 459k | 60.6M |
| 10 | pfister_gerstner_2006 | 19 | 54k | 1.23M | 22.9M | 206k | 24.3M |
| 11 | zhang_1996 | 23 | 68k | 1.14M | 19.6M | 168k | 20.9M |
| 12 | pfister_gerstner_2006 | 17 | 52k | 1.21M | 23.6M | 190k | 25.1M |
| 13 | pfister_gerstner_2006 | 21 | 70k | 1.21M | 19.0M | 155k | 20.5M |
| 14 | roxin_ledberg_2008 | 22 | 95k | 2.68M | 53.1M | 309k | 56.2M |
| 15 | roxin_ledberg_2008 | 8 | 25k | 1.02M | 16.5M | 89k | 17.6M |
| | **TOTAL (15)** | **452** | **1.63M** | **31.7M** | **818.7M** | **6.03M** | **858.1M** |

**Cost-weighted** (Opus rates $5/$25 per M; cache write 1.25×, read 0.1×):
- cache-read 818.7M → **$409** · cache-write 31.7M → **$198** · output 6.03M → **$151** ·
  input 1.63M → **$8**. **Batch ≈ $767.**
- Caching is **already active** — cache-read is **95% of raw tokens**, so the raw-token
  total is dominated by cheap reads. Cost lives in cache-write + output.

## Per model (total across all its rounds)

| Model | runs | total tok | note |
|---|--:|--:|---|
| pfister_gerstner_2006 | 6 | 230.9M | recursion cost — the worst offender |
| roxin_ledberg_2008 | 3+ | 176.1M | (run 15 may be a still-in-flight cleanup) |
| flash_hogan_1985 | 1 | 142.0M | **dry-run A/B target** (faithful, 4 figures) |
| bienenstock_cooper_munro_1982 | 2 | 124.4M | |
| zhang_1996 | 2 | 124.1M | |
| sutton_1988 | 1 | 60.6M | cheapest extract (3 figures) |

## What the improvement should move (and what it won't)

- **Agent count.** Extract/build runs are **39–57 agents**, mostly the per-figure
  fan-out (describe → digitize → audit, ×N figures). De-parallelization collapses each
  role to one agent → the count should drop sharply (this is also what relieves the
  concurrency throttle).
- **Rounds per model.** Pfister 6 / Roxin 3 — the multiplier. The single cross-figure
  auditor + diff-scoping should cut rounds.
- **What it will NOT move much:** per-sweep token count. Caching already absorbs the
  reload (95% cache-read), and the consolidated sweep's O(N²) transcript can offset it on
  high-figure models — hence the fan-out cap. **So compare at the *model* level
  (total tokens + cost + rounds + agent-count), not per-pass.**

## Comparison metric (how to re-measure post-improvement)

The A/B target is **flash_hogan_1985** (baseline row 6: **142.0M tok, 54 agents,
extract→faithful**). Re-run `from='extract'` on the de-parallelized + diff-scoped
`full-pass.js` and compare:
1. **agents** (expect a large drop), **total tok** and **cost-weighted $** (expect ≤ baseline),
2. **outcome preserved** — still reaches `faithful` (correctness gate; de-parallelization
   must not change the verdict).

Re-measure with the same contiguous-run-collapse parse of the run's agent transcripts.

## Status

**Baseline of record, 2026-06-13.** Frozen for the A/B; supersede only with a fresh
measurement run.
