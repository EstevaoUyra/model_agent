---
name: branch-bumps-from-origin-main
description: "Git discipline — work in a worktree off origin/main, stage by path, diff-verify before merge (documented in AGENTS.md)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a6fd7e82-9088-4e49-8e88-9c0c3e990d90
---

**The working copy is SHARED** (the human + other agents work in parallel), so the main checkout's
HEAD moves under you. Never `git checkout`/`git checkout -b` in the shared copy for your own change.
This is now a **non-negotiable rule documented in AGENTS.md → "Git discipline"**:

1. **Use a dedicated worktree per change, cut from `origin/main`:**
   `git fetch -q origin && git worktree add ../ma-wt-<name> -b <name> origin/main` → edit/commit/push/PR
   from inside it → `git worktree remove ../ma-wt-<name>`. Agents stop fighting over HEAD/index.
2. **Stage by explicit path** (`git add <file>`), never `-A`/`-a`.
3. **Before push OR merge, verify `git diff --stat origin/main...HEAD` is EXACTLY your change.** A file
   you didn't intend = wrong base; stop, don't merge.

**Why:** twice burned. (a) PR #47 cut a pointer-bump branch off an unmerged feature branch → merged
the gated de-parallelization to main (revert #48). (b) PR #57: I ran `git checkout -b` assuming I was
on main, but HEAD had moved to the human's parallel `experiment/dig-cost-levers-v2` work → a docs PR
swallowed 5 of their commits onto main. The diff-verify in step 3 catches both before merge.
Related: [[keep-main-current-branch-promptly]].
