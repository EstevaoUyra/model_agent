---
name: keep-main-current-branch-promptly
description: Land work on main promptly via branch→PR→squash-merge; never accumulate uncommitted work on an inherited/stale branch
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

The user wants **everything landed on `main`**, and has said so more than once
(first during the reproduction program: "Bring origin main current with everything,
via a PR"; again on 2026-06-02 when I'd accumulated the whole faithfulness redesign
uncommitted on a stale, already-merged branch). This is a firm standing expectation,
not a per-task ask.

**Why:** main is the source of truth. Work that sits uncommitted on an inherited
branch is invisible, un-reviewable, and at risk — and it violated a repeated explicit
instruction. The lapse had the same shape as the leniency bug we'd just diagnosed:
optimize the visible task (make edits), let an unwatched default (the checked-out
branch) ride, because no gate forced the choice.

**How to apply:**
- At the START of a coherent body of work, create a properly-named branch for it
  (e.g. `redesign/faithfulness-enforcement`) — don't defer the branch decision to
  commit-time and don't pile onto whatever branch happens to be checked out.
- **Verify the actual current branch** with `git branch` — do NOT trust the
  session-start gitStatus snapshot; it goes stale (I twice parroted
  `codex/compare-figures` while actually on `bump-readme-pointers`).
- Land via the established flow: feature branch → `gh pr create` → `gh pr merge
  --squash` to main (the `guard-main-branch.sh` hook blocks a direct
  `git push origin main`). Then bring local main current.
- Scope commits: stage only the work's own files; leave unrelated working-tree state
  (submodule-pointer churn, transient `logs/`, `.agent_tmp/`) out.
- Commit/PR when the work is a coherent landable unit — don't wait to be chased.

Relates to [[work-autonomously-escalate-rarely]] and
[[faithfulness-critics-want-to-find-issues]] (the same proxy-drift failure shape).
