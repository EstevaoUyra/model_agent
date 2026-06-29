# T1 — Cost/parallelism fix reverted, then re-done

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Tool/env · process/delivery |
> | Behavior | ships an unvalidated optimization to shared main, then must revert |
> | Agent role | orchestrator |
> | Trigger | a plausible-looking process change, confidence without validation |
> | Cause (evidence) | no A/B-before-adopt + weak mainline discipline — *inferred* |
> | Detector | human (caught on/after merge) |
> | Lever(s) | human-rule (git discipline, AGENTS.md) + process (A/B-before-adopt) |
> | Flags | ✗ reverted ×2 · → connects-to E5 (self-certification), S4 (git discipline) |
> | Status | solved |

## Behavior / bias
Not an agent *judgment* bias — a **process-change failure mode**: an optimization is landed on
`main` before it is validated, then has to be reverted. Cataloged because it is a clean,
unambiguous example of a *fix that did not hold* (the dimension explicitly requested), and
because the second cycle shows the lesson did not transfer the first time.

## Symptom
`main` carries an unvalidated / inadvertently-merged change; a subsequent commit backs it out.

## Timeline
| Date | Event | Ref |
|------|-------|-----|
| 2026-06-13 | Cost proposal: de-parallelization as lever #1 | PR #45 (`1d1fc33`); `cost-reduction-2026-06-13.md` |
| 2026-06-13 | **Revert 1:** premature de-parallelization backed out of main | PR #48 (`9bf119c`) |
| 2026-06-13 | Re-done properly + A/B validated (flash_hogan −77% cost) | PR #50/#51 (`3df777e`/`5935d58`), #52 (`8d9df39`) |
| 2026-06-14 | **Revert 2:** inadvertently-merged digitization-cost experiment removed | PR #59 (`6bac9e5`) |
| 2026-06-14 | Re-done experiment-free | PR #60 (`3c0c336`) |

## Recurrence / failed intervention
**Two distinct revert cycles within ~24h.** The first revert (premature merge) did not prevent
the second (a different unvalidated change reaching main), indicating the corrective lesson was
incident-local, not yet institutionalized. The durable fix landed separately as **git discipline**
(worktree off origin/main, scoped staging, diff-verify) — see thread **S4**.

## Smoking gun
Two `Revert …` commits on main within a day: `9bf119c`, `6bac9e5`.

## Interventions that held
- A/B validation *before* adopting a process change (`digitization-cost-levers-ab`).
- Git-discipline rule in AGENTS.md (PR #58, `346ded1`) — addresses the root delivery failure.

## Generality
**Low–medium.** Specific to a human/agent committing to a shared mainline, but the underlying
shape — "agent ships an unvalidated optimization, confident it helps" — recurs in autonomous
agents and connects to E5 (self-certification).

## Refs
memory: `digitization-cost-levers-ab`, `branch-bumps-from-origin-main` · proposals:
`cost-reduction-2026-06-13`, `cost-baseline-2026-06-13` · PRs #45, #48, #50, #51, #52, #58, #59, #60
