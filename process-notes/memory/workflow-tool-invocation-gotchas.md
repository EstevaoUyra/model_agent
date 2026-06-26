---
name: workflow-tool-invocation-gotchas
description: Workflow-tool gotchas — name-cache ignores edits; args can arrive as a string; model arg must be models/<name> (now canonicalized) — and that agents run the PARENT's tools/
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

Running the full-pass dynamic workflow (2026-06-03) hit two non-obvious Workflow-tool behaviors:

1. **Invoking by `name:` reads a STALE snapshot.** A named workflow (`.claude/workflows/*.js`) is registered at session start; later edits to that file are IGNORED when you invoke by name — it ran the pre-edit script. **Fix:** invoke via `scriptPath: '<abs path to the canonical file>'` so it reads the live file. The generated per-run script copies under the session dir confirm which version ran (read line ~14).

2. **`args` can arrive as a JSON-encoded STRING, not a parsed object** (despite passing an object in the tool call). `args.figures` was undefined → `pipeline() expects an array`. **Fix in-script:** `const A = typeof args === 'string' ? JSON.parse(args) : (args||{})` then read `A.model` / `A.figures`. The full-pass.js already carries this guard.

3. **`model` arg must resolve to `models/<name>`** — passing a bare `fitzhugh_1961` (2026-06-15 run) silently broke TWO things while the run otherwise SUCCEEDED (resilient agents still built in the real `models/<name>`): the coverage gate ran `check_figure_coverage.py <name>`, looked under `<name>/article_aware/`, found nothing, and emitted a FALSE `model:figure-coverage` block; and `repro_cost.py` (which attributes a run by grepping prompts for `models/<name>`) found no match, so the finisher omitted the README cost section. **Now FIXED** in full-pass.js — `MODEL` is canonicalized so bare `<name>` and `models/<name>` both work — and repro_cost attribution was hardened to search the whole transcript (recovers past bad-arg runs). These fixes live on branch `scidekick-full-pass-hardening` (commit 322ecd3); they reach the live tool path only once that branch merges to main, because **agents always invoke the PARENT's `${ROOT}/tools/*.py` (ROOT=`/Users/estevaouyra/dev/model_agent`), not the scriptPath worktree's copies.**

**How to launch full-pass now:** `Workflow({ scriptPath: '/Users/estevaouyra/dev/model_agent/.claude/workflows/full-pass.js', args: { model: '<name>'|'models/<name>', figures: [...] } })`. Each run re-derives a built paper end-to-end, so check out a fresh branch in the model repo FIRST (agents commit per [[keep-main-current-branch-promptly]]; main stays safe).
