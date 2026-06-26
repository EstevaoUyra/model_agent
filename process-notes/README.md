# process-notes/

Versioned process knowledge that previously lived **only** in the orchestrator's
local memory store (`~/.claude/projects/<this-project>/memory/`), which is
machine-local and not backed up with the repo. Snapshotting it here makes the
hard-won operational knowledge portable, reviewable, and recoverable.

## `memory/` — orchestrator memory snapshot

A **verbatim point-in-time copy** of the orchestrator's memory files as of the
snapshot date below. Each file is one fact with frontmatter (`name`,
`description`, `type`); the bodies cross-link with `[[name]]`. `MEMORY.md` is the
index.

**This is a snapshot, not a live mirror.** The live store keeps evolving; these
files reflect what was true when copied and may name files / flags / line numbers
that have since moved. Treat them the way `WORKFLOW.md` asks you to treat any
recalled memory: **verify against current code before asserting as fact.** The
canonical, current process docs remain `VISION.md` > `STATUS.md` > `WORKFLOW.md` >
`AGENTS.md`; where a snapshot note and those docs disagree, the docs win.

What's here is operational lore in three rough buckets:
- **Workflow-tool sharp edges** — invocation gotchas, concurrency cap, model-ID
  pinning, commit-in-submodule-not-parent, sandbox venv.
- **Operating model** — delegate-and-synthesize, don't-implement-trust-the-process,
  re-audit-after-every-change, escalation policy.
- **Faithfulness lessons** — why critics must want to find issues, rendered-panels
  are targets, saturation is a shared human decision, drift-vs-STUCK.

### Refreshing the snapshot

Re-copy from the live store (overwrites; the snapshot is intentionally a clean
mirror, not a hand-edited fork):

```sh
cp ~/.claude/projects/-Users-estevaouyra-dev-model-agent/memory/*.md process-notes/memory/
```

Snapshot date: 2026-06-26.

### Long-term intent

The principled home for durable, repo-relevant lessons is the canonical docs and
the skill docstrings *at the point of use* (per the `capture-discovered-knowledge`
and `process-outran-its-docs` notes themselves). This snapshot is the safety net;
distilling its durable items into `AGENTS.md` / `WORKFLOW.md` / `skills/*/SKILL.md`
and pruning the snapshot is follow-up work.
