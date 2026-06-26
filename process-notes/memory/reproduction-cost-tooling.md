---
name: reproduction-cost-tooling
description: tools/repro_cost.py measures per-model API cost from full-pass transcripts; cache-read dominates token count but not cost
metadata: 
  node_type: memory
  type: project
  originSessionId: a6fd7e82-9088-4e49-8e88-9c0c3e990d90
---

`tools/repro_cost.py` recovers a model's full-pass workflow agent transcripts (under
`~/.claude/projects/.../subagents/workflows/wf_*/agent-*.jsonl`), sums billed tokens per agent and
per token type, and prices at **standard Opus 4.8 rates** ($5/$25; cache read $0.50/1M = 0.1×, cache
write 5m $6.25/1M = 1.25×). De-dups streaming by API `message.id` (max cumulative output), agents by
`agentId` (cache-replayed resumes not double-counted). `--markdown <model>` emits the README section.

- **`--markdown` is wired into the finisher** (`full-pass.js` update-state agent) → every reproduced
  model carries a `## Reproduction cost` section, refreshed each run. 25 already-built models were
  backfilled (2026-06-13). `tools/backfill_cost_readme.py` is the one-off splicer.
- **Key finding:** token *counts* look enormous (flash_hogan one pass = 142M tokens) but ~**95% is
  cache-read**, billed at 10× discount — so 142M tokens ≈ **$115**, not thousands. Cost lives in
  cache-write + output, not the raw count. Whole recoverable corpus ≈ **$2,965** (a lower bound;
  older transcripts have rotated out of local history, so old-model numbers undercount).
- Caveat the section states: it's a **lower bound** (only transcripts still in local history), most
  reliable for recently-built models. Related: [[full-pass-concurrency-limit]].
