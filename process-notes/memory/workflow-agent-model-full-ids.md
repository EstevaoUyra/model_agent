---
name: workflow-agent-model-full-ids
description: "Workflow agent() model:'opus' only sets the tier; agents inherit the session's 1M window. Use explicit model IDs to control 1M."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

In the Workflow tool, `agent(..., { model: 'opus' })` sets only the **tier** (opus/sonnet/haiku). The context-window variant is **inherited from the session** — so when the session runs on `claude-opus-4-8[1m]`, every workflow agent gets the 1M window regardless of `model:'opus'`. Evidence: across a full run every agent transcript showed bare `claude-opus-4-8` and the user observed all agents on opus-1M (the `[1m]` suffix never appears in transcripts, so the window can't be read from there — only the user's live /workflows view shows it).

**Confirmed (2026-06-03): even explicit full IDs do NOT strip the 1M window.** `full-pass.js` sets `OPUS = 'claude-opus-4-8'` for the nine non-implementer roles and `IMPL = 'claude-opus-4-8[1m]'` for the implementer; the IDs are accepted (no error), but the user verified via /workflows that ALL agents still ran on opus-1M. The session's context-window setting dominates — workflow agents always inherit it. **The only real lever is the session model at session start**, not per-agent overrides. The user accepted all-1M for now and will set a non-1M session next time if they want the split. The explicit IDs in the script are harmless (correct intent) but a no-op on the 1M axis. See [[workflow-tool-invocation-gotchas]].
