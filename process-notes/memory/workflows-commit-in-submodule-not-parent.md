---
name: workflows-commit-in-submodule-not-parent
description: "Full-pass workflow agents must commit INSIDE their model submodule, never on the parent model_agent — agents run from the parent root, so relative skill paths silently target the parent unless pinned"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e8552c97-c722-4643-9557-00815e47fc70
---

A reproduction run operates on ONE model = ONE submodule (`models/<m>/`). Every
workflow agent must read/write/**commit inside that submodule**, NEVER in the parent
`model_agent` repo (AGENTS.md: "commit only inside the model repo, never the parent").

**Why it silently breaks (I got this wrong twice, 2026-06-04):** workflow agents run
with cwd = the parent root, but skills use *model-relative* paths (`logs/`,
`article_aware/`, `implementation/`, `figure_outputs/`) and say "commit your output."
So an agent that doesn't `cd` into the model writes + commits into `model_agent/`
instead — e.g. the figure-audit lane dumped every digitization report into
`model_agent/logs/digitization_audit/`. And a finalize step I designed *bumped the
parent submodule pointer + opened model_agent PRs* — committing on the parent, exactly
forbidden.

**The fixes now in place (so check before re-introducing):**
- `full-pass.js` `SK()` pins every skill-based agent to its model repo (cd in; paths
  relative to it; commit inside, never the parent).
- finalize lands the result in the **model's own repo** — a PR onto the *submodule's*
  main (`gh pr create`+`gh pr merge` in the submodule) — and never touches model_agent.
  Parent submodule-pointer bumps are a SEPARATE, deliberate step, not part of a run.
- Parent `.gitignore` ignores per-model artifact paths (`logs/digitization_audit|
  faithfulness_audit|figure_comparisons|spec_audit`, `test_runs.jsonl`) so a stray write
  can't pollute model_agent. `logs/process_audit/` (corpus-level) stays tracked.

**How to apply:** model results land on the *submodule's* main (the submodule has its
own GitHub remote; the submodule's main was going stale on feature branches — see the
RH2009 case where the parent pointed at a fix-branch commit and the submodule main was
24 commits behind). Process/skill/workflow-definition changes go on model_agent via PR
(those ARE parent artifacts). Never auto-commit reproduction *results* on model_agent.
