# M4 — "The spin": re-auditing an unchanged build after a no-op fix, forever

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · process/delivery (orchestration loop logic) |
> | Behavior | a remediation loop re-runs its judge over a build that no fix actually changed, looping without progress (a no-op fix → re-audit → same finding → no-op fix …) |
> | Symptom | RH2009 first `from="fix"` run: the contract was already correct, so `paperFix` was a no-op, and the loop re-audited an un-fixed build forever |
> | Agent role | workflow / orchestrator (the `full-pass.js` loop, not an agent's judgment) |
> | Trigger | a contract-first guard fires `paperFix → continue` on *any* figure-auditor `CONTRACT_BUG` tag, including when the contract is already correct |
> | Cause (evidence) | the loop lacked an arbiter to decide whether a flagged divergence was a *contract* issue or a *code* issue — *intervention-tracked* (commit `2b88d08` adds the arbiter) |
> | Detector | human (observed on the first `from="fix"` RH2009 run) |
> | Lever(s) | structural/logic (make `audit-spec` the arbiter of "is there an open spec question?") + entry-point fix (`from="fix"` starts at implementation) |
> | Status | solved |

## The behaviour

A remediation loop is supposed to converge: audit finds a problem → a fix changes the build → the
re-audit clears it. M4 is the degenerate case where the "fix" step changes **nothing** and the loop
keeps re-judging the same unchanged artifact — work without progress (call it *the spin*).

It surfaced on the first `from="fix"` run of reynolds_heeger_2009 and had two coupled causes, both
in the orchestration logic rather than in any agent's reasoning:

1. **Wrong entry point.** `from="fix"` round 1 ran author-tests derived from the *stale* faithfulness
   audit instead of implementing the freshly corrected contract — so the real fix was never applied.
2. **The spin proper.** A contract-first guard did `paperFix → continue` on *any* figure-auditor
   `CONTRACT_BUG` tag. When the contract was **already correct**, `paperFix` was a no-op, and the
   loop re-audited the un-fixed build again, indefinitely. From the fix commit:

   > "the contract-first guard did paperFix->continue on any figure-auditor CONTRACT_BUG tag; when
   > the contract was already correct, paperFix was a no-op and the loop re-audited an un-fixed build
   > forever (the spin)." — `2b88d08`

The loop had no way to tell "the contract is wrong (fix it)" from "the contract is right; the
divergence is a *code* issue (go implement)," so it kept choosing the no-op branch.

## Why it happened (graded)

- **Missing arbiter on the open-question decision** — *intervention-tracked (strong).* The fix is to
  install `audit-spec` as the arbiter: `DIVERGENT → still an open spec question (continue/block)`;
  `FAITHFUL → no open spec question, the divergence is a CODE issue → fall through and implement.`
  That the remedy is exactly "add the missing branch decision" is the standard intervention-tracked
  signature: the loop spun because nothing adjudicated which branch was real.

The shape worth naming: **a remediation loop without a progress check (did the build actually
change? is the flagged issue the kind this branch can fix?) will re-run its judge over an unchanged
artifact.** It is the process-level analogue of self-certification (E5) and of "a required step
silently mis-runs" (D3) — the loop *believes* it is making progress because it keeps invoking a fix
step, but the fix is empty.

## How it responded to intervention

- **structural/logic (held):** `audit-spec` became the arbiter of whether an open spec question
  exists, breaking the unconditional `paperFix → continue`. A divergence on a *correct* contract now
  falls through to implementation instead of re-auditing forever.
- **entry-point fix (held):** `from="fix"` round 1 now implements the *current* contract (deleting
  unsanctioned knobs), tests come from the contract, and round 2 audits — so a fix run actually
  applies the fix before it judges it.

Status: solved (both branches landed together in `2b88d08`).

## Confidence & threats to validity

High that the spin occurred and was fixed — a named commit describes the exact loop bug and the exact
logic change. Caveats:

- **Single observed instance** (the first `from="fix"` RH2009 run). It is `happened ≥ once`; whether
  other models' fix-runs spun before this landed is `[to-verify-on-deeper-dig]`.
- **Detector is human**, on a run that happened to be watched — consistent with the catalog's
  selection bias. A non-terminating loop *should* be cheap to detect mechanically (a max-rounds /
  no-change guard), and the absence of one is why it could spin in the first place.
- **No clean post-fix proof of non-recurrence** from this slice; the durable claim is "the branch
  decision that caused the spin was removed," not "no loop ever spins again."

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-04 10:52 | First `from="fix"` RH2009 run spins: no-op `paperFix` → re-audit unchanged build forever; fixed by making `audit-spec` the arbiter + `from="fix"` starts at implementation | `2b88d08` |
| 2026-06-04 | Rationale recorded | `proposals/sq-blocking-gate-and-paper-fix-2026-06-04.md` |

## Links

- `connects-to E5` (self-certification) — both are "the process reports progress that did not
  happen"; M4 is the loop-logic form (re-judging an unchanged build), E5 is the agent form (green
  tests ⇒ "done").
- `connects-to D3` (required step silently stops / no coverage gate) — same family: a step runs but
  does nothing useful, and nothing asserts real progress was made.

## Deeper-dig hook

If the spinning RH2009 `from="fix"` run is in the corpus, the signature is repeated
`audit-faithfulness`/figure-auditor invocations on the same `reynolds_heeger_2009` build with no
intervening implement diff. Slice: `grep -rl "paperFix\|CONTRACT_BUG\|from=\"fix\"" evidence/corpus-snapshot/` filtered to RH2009 around 2026-06-04; absence here means it predates/sits outside the snapshot.

## Status

solved · Domain Process-maintenance.

---

## Evidence layer (for verification, not reading)

- **Grounding:** git + proposal, **no quote ledger** — the spin is a property of the `full-pass.js`
  loop logic, not of any agent's narration, so there is nothing in the workflow-agent corpus to
  quote. The behaviour is fully described by the fix commit and its proposal.
- **Refs:** commit `2b88d08` (`.claude/workflows/full-pass.js`) ·
  `proposals/sq-blocking-gate-and-paper-fix-2026-06-04.md` · sibling entries E5, D3.
