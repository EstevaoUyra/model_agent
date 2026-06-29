# S4 — Branch cut from the wrong base swallows parallel work onto main

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · process/delivery (delivery discipline on a shared working tree) |
> | Behavior | branches/commits on a shared checkout without verifying the base, so a merge carries unrelated parallel work to main |
> | Symptom | a squash-merge brings in commits the change never intended (an unmerged feature branch, or another agent's parallel work) |
> | Agent role | orchestrator |
> | Trigger | shared working copy whose HEAD moves under the agent; `git checkout -b` assuming you're on main |
> | Cause (evidence) | wrong base branch + no pre-merge diff check — *intervention-tracked (the fix is "cut from origin/main + diff-verify")* |
> | Detector | human (caught around/after merge; required reverts) |
> | Lever(s) | doc/human-rule (AGENTS.md Git discipline) + practice (worktree off origin/main, scoped staging, diff-verify) |
> | Flags | ⟳ recurred · ✗ a fix-branch itself caused a bad merge |
> | Status | solved (after two burns) |

## The behaviour

The working copy is **shared** — the human lead and other agents commit in parallel — so the main
checkout's HEAD moves under whoever is working. The recurring failure is treating that shared
checkout as if it were a private one: running `git checkout -b` (or branching off whatever is
currently checked out) **without verifying the base**, then opening a PR whose squash carries
commits the change never intended onto `main`.

Two distinct burns (this is why the thread is flagged ⟳✗, not one-shot):
- **(a) PR #47 → revert #48.** A submodule-pointer-bump branch was cut off an **unmerged feature
  branch** (`feat/deparallelize`), so its squash carried a not-yet-validated de-parallelization of
  `full-pass.js` onto main *before* the A/B validation had run. Backed out by **PR #48**
  (`9bf119c`, "Revert premature de-parallelization on main").
- **(b) PR #57 → revert #59.** A docs PR was branched via `git checkout -b` on the assumption HEAD
  was on main, but HEAD had moved to the human's parallel `experiment/dig-cost-levers-v2` work — so
  the docs PR **swallowed ~5 of their commits onto main**. Backed out by **PR #59** (`6bac9e5`,
  "Revert inadvertently-merged digitization-cost experiment from main").

The two cases share a cause (wrong base on a shared tree) but differ in flavour: (a) is the *fix
branch itself* being unsafe (cut off an unmerged branch); (b) is *stale assumption about current
branch*. Both pass a clean local diff because the unwanted commits are already "in" the base.

## Why it happened (graded)

- **Intervention-tracked / structural (strong):** the cause is "wrong base branch on a shared,
  moving HEAD, with no pre-merge verification," and the durable fix is exactly that — work in a
  **worktree cut from `origin/main`**, stage by explicit path, and **verify
  `git diff --stat origin/main...HEAD` is exactly your change before push OR merge**. The fix maps
  one-to-one onto the cause, which is strong evidence for it.
- **Same proxy-drift shape as the leniency bug (agent-stated/inferred):** the distilled note frames
  the lapse as optimizing the visible task (make the edits) while letting an unwatched default (the
  checked-out branch) ride, because no gate forced the choice. Plausible, not isolated-tested.
- **No mentalism:** the agent didn't "intend" to swallow commits; it acted on an assumed base. As
  in S3, it's *acting on ambient git state* rather than a verified one.

## How it responded to intervention (held only after the second burn)

- **First burn (PR #47/#48):** corrected the incident (revert, keep the pointer bumps, hold the
  de-parallelization on its own branch until A/B validation) — but did **not** institutionalize a
  rule, so it did not prevent the second burn. (The cost/parallelism side of #47/#48 is its own
  thread, **T1**.)
- **Second burn (PR #57/#59):** triggered the durable lever — **AGENTS.md "Git discipline
  (non-negotiable)"** (PR #58, `346ded1`): worktree off `origin/main`, scoped staging
  (`git add <file>`, never `-A`), pre-merge diff-verify. This is the lever that addresses the root
  shared-tree problem rather than the incident. Later reconciled with the `guard-main-branch` hook
  docs (PR #70, `d9f2601`), and the hook itself blocks a direct `git push origin main`.

So the intervention **failed once (incident-local fix didn't transfer), then held** once it became a
structural rule + practice. A complementary standing expectation — *land work on main promptly via
branch→PR→squash; never accumulate work on an inherited/stale branch* — is the same dial pointed the
other way (don't let an inherited branch ride at all).

## Confidence & threats-to-validity

**High on the two incidents and the fix; low on rate.** Threats:
- **Detector is human** — both burns were caught by the lead and required reverts; the map sees the
  caught cases. A swallow that was never noticed wouldn't be here (the `U#` blind spot).
- **n = 2 incidents** — enough to show recurrence and a failed first fix, not a rate.
  `[to-verify-on-deeper-dig]`: count merges whose `origin/main...HEAD` diff exceeded the intended
  file set, before vs after PR #58.
- **No corpus quotes** — this is a git-history behaviour (commit/merge topology), not workflow
  narration; verified by the two `Revert …` commits (`9bf119c`, `6bac9e5`) and the AGENTS.md rule
  PR, not by quotes. Per the brief, no corpus quotes manufactured.
- **Bundled with T1:** PR #47/#48 changed *both* the merge base AND a cost optimization — S4 is the
  git-discipline facet, T1 the unvalidated-optimization facet; they are not independent incidents.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-13 | **Burn 1:** #47 cut off an unmerged feature branch → de-parallelization merged to main; reverted | PR #48 (`9bf119c`) |
| 2026-06-14 | **Burn 2:** #57 `checkout -b` on moved HEAD → swallowed ~5 parallel commits; reverted | PR #59 (`6bac9e5`) |
| 2026-06-14 | **Durable fix:** AGENTS.md Git discipline (worktree off origin/main, scoped staging, diff-verify) | PR #58 (`346ded1`) |
| 2026-06-15+ | guard-main-branch hook docs reconciled | PR #70 (`d9f2601`) |

## Links
- `connects-to T1` — PR #47/#48 is the same incident from the cost/optimization angle (T1) and the
  git-discipline angle (S4); the INDEX edge `T1 → S4` ("durable fix = git discipline") is this.
- `connects-to S3` — sibling git-discipline-on-a-shared-tree failure (wrong *repo* there, wrong
  *base branch* here); both fixed by making the target explicit, not inherited.
- `connects-to S1` — "ship it now on whatever branch is checked out" is adjacent to the
  do-it-myself reflex: an unwatched default riding because no gate forced the choice.

## Deeper-dig hook
`git log --merges` around 2026-06-13/14 and inspect the squash parents of #47 and #57; diff
AGENTS.md at PR #58 for the exact Git-discipline clause; confirm `guard-main-branch` hook still
blocks direct pushes to main. Git-grounded; not in the narration corpus.

## Status
**Solved — but only after the first (incident-local) fix failed to transfer.** Held once the rule
became structural (worktree off origin/main + diff-verify) plus the guard hook. `Refs:` memory
`branch-bumps-from-origin-main`, `keep-main-current-branch-promptly`; PRs #47/#48, #57/#59, #58,
#70; AGENTS.md "Git discipline."

## Evidence layer
**Git/memory-grounded — no corpus quotes.** Primary evidence: the two revert commits `9bf119c`
(#48) and `6bac9e5` (#59), the AGENTS.md Git-discipline PR `346ded1` (#58), and the two distilled
memories. No `S4.quotes.jsonl`: the behaviour is commit/merge topology, not verbalized workflow
narration, so per the brief no corpus quotes were manufactured.
