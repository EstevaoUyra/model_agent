# M6 — Non-termination: a fix loop runs indefinitely without ever recognizing "stuck"

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance / Tool · process/delivery (loop budget / termination) |
> | Behavior | a remediation loop keeps iterating on a hard problem and **never declares STUCK** — it burns effort indefinitely instead of recognizing non-convergence and deferring; "effort-exhaustion masquerading as judgment" |
> | Symptom | a fix loop "hung silently" — one ran **4.4 hours** before a human killed it; there was no `stuck-detector` to call it |
> | Agent role | fix agent (builder-side remediation) inside the workflow loop |
> | Trigger | a fix that does not converge within reasonable effort, combined with no hard cap / time budget / stuck-detector and no defer-fallback — the loop has no terminal "I cannot make this green" state |
> | Cause (evidence) | missing termination control (no budget, no stuck-detector) — *intervention-tracked* (the remedy is "all fix agents are now hard-capped with a defer-fallback") |
> | Detector | **human** (a person watched the run and killed it at 4.4 h) — the absence of an automatic detector *is* the finding |
> | Lever(s) | structural — hard-cap every fix agent (max effort/time) + a defer-fallback so exhausting the cap yields DEFER, not an indefinite hang |
> | Flags | `inverse-of E5` · `connects-to E2` · `connects-to M4` · ⟳ (the unbuilt stuck-detector recurs across AGENTS.md history) |
> | Status | mitigated (hard cap + defer-fallback landed; a real stuck-*detector* still noted as unbuilt) |

## The behaviour

A remediation loop should have two terminal states: *converged* (the fix worked) and *stuck* (this
cannot be made green within reasonable effort — defer and escalate). M6 is when the second state is
missing: the loop keeps trying, makes (or attempts) changes, re-audits, tries again, and **never
crosses a threshold that says "stop, I'm stuck."** With no budget and no stuck-detector, the natural
behaviour is to burn iterations indefinitely. The legible instance is a fix loop that ran for hours
unnoticed:

> "**Long fix loops can hang silently** (one ran 4.4 h before I killed it); all fix agents are now
> hard-capped with a defer-fallback." — final-triage process-learnings

The faithfulness-enforcement audit names the *judgment* face of the same thing — a Process-Auditor
drift signature it hunts for:

> "effort-exhaustion-masquerading-as-judgment" — faithfulness-enforcement (drift signatures)

i.e. continued effort gets read as (or reported as) deliberation, when it is really just the absence
of a termination criterion. The recurring backdrop is that the **stuck-detector was a documented-but-
unbuilt control** for much of the project's history (the AGENTS.md note that the stuck-detector isn't
built), which is exactly why a loop could hang with nothing to call it.

## Why M6 is the **inverse** of E5 (and not the same as M4)

- **vs. E5 (self-certification — "green tests ⇒ done").** E5 is *premature termination*: the loop
  declares **done too early**, inferring success from a passing self-check. M6 is the **opposite
  pole**: the loop **never declares stuck** and so does not terminate at all. Same missing thing — a
  *correct* terminal-state criterion — failing in opposite directions: E5 stops when it shouldn't; M6
  doesn't stop when it should. That is why they are linked `inverse-of` on one dial (the
  done/stuck decision), not merged.
- **vs. M4 (the no-op spin — re-auditing an unchanged build forever).** M4 and M6 both fail to
  terminate, but the *mechanism differs.* M4 is a **loop-logic bug**: a guard chose a *no-op* branch
  (`paperFix` on an already-correct contract), so the loop re-judged an **unchanged** artifact —
  fixed by adding the missing branch *arbiter* (`2b88d08`). M6 is **effort-exhaustion**: the fix
  agent is doing *real* (changing) work but never recognizes non-convergence — fixed by a *budget*
  (hard cap) + defer-fallback. M4 = spinning on nothing and needs an arbiter; M6 = grinding on
  something and needs a stopwatch. They are siblings under "non-termination," distinct in cause and
  cure, so kept as separate threads.

## How it responded to intervention

The lever is **structural — a termination budget**: every fix agent is hard-capped (a max effort/time
bound), and exhausting the cap routes to a **defer-fallback** — so hitting the limit produces a clean
DEFER/escalation instead of an indefinite hang. This converts "burn hours silently" into "spend a
bounded budget, then defer," which is the correct terminal behaviour the loop lacked. M6 is filed
**mitigated** rather than solved: the cap+fallback addresses the *symptom* (unbounded runtime), but
that is a blunt timeout, not a true *stuck-detector* that recognizes non-convergence early on signal
(repeated identical failures, no error reduction). The AGENTS.md history's recurring "stuck-detector
isn't built" note is the open remainder — a budget bounds the damage; it does not *diagnose* stuck.

## Confidence & threats to validity

Moderate. The 4.4-hour hang is a concrete, dated, human-killed instance, and the remedy (hard cap +
defer-fallback) is explicitly recorded. Threats:

- **Anecdote ≠ rate.** "One ran 4.4 h" is a single observed hang; it does not establish how often fix
  loops failed to terminate, nor the distribution of fix-loop runtimes. No denominator (fix runs with
  vs. without a hang) is available in this slice.
- **Detector is human, and that *is* the point.** The hang was caught only because a person was
  watching and killed it — there was no automatic detector (the stuck-detector was unbuilt). The
  catalog's selection bias in literal form: an *un*watched hang of this kind is invisible (it would
  sit in the `U#` never-caught class until someone noticed the wall-clock or cost).
- **Cap ≠ detector.** "Mitigated" is about bounding runtime; the stronger claim — the loop *recognizes*
  stuck and defers on signal rather than on a timeout — is not established and the unbuilt-detector
  note suggests it remained open.
- **Effort-exhaustion-as-judgment is partly inferential.** That continued effort was *reported as*
  deliberation is named by the audit as a drift signature to hunt, i.e. a hypothesis about how the
  behaviour masks itself, not a per-incident measured fact.

## Scope / generality

Descriptive, and general: any agentic remediation/optimisation loop without an explicit budget and a
non-convergence (stuck) criterion can run indefinitely; "add a hard cap + defer-fallback" is the
generic blunt fix and "build a stuck-detector that recognizes non-convergence" is the generic better
one. Setup-specific in the fix-agent/full-pass loop and the 4.4-hour instance.

## Links
- `inverse-of E5` — **same terminal-state dial, opposite failure.** E5 declares done too early; M6
  never declares stuck. Hardening one risks the other (a too-eager stuck-detector under-tries; a
  too-lax one hangs).
- `connects-to E2` — effort-exhaustion is one of the named drift signatures the Process Auditor hunts
  (alongside goalpost-moving / scope-as-escape); M6 is the runtime face of that signature.
- `connects-to M4` — sibling under "non-termination," distinct cause/cure: M4 = no-op spin (needs an
  arbiter); M6 = effort-exhaustion (needs a budget).
- `connects-to D3` — both are "nothing watches for a bad terminal condition": D3 = no gate asserts a
  step ran; M6 = no detector asserts a loop is stuck. (D3 covers absence of a step; M6 absence of a
  stop.)

## Deeper-dig hook
(1) Turn the anecdote into a rate: pull fix-loop wall-clock / iteration counts (cost or transcript
timestamps under `evidence/corpus-snapshot/` + `logs/`) and look for the tail of long-running fix
agents before vs. after the hard cap landed — denominator = fix runs. (2) Test whether a *stuck*
signal (repeated identical audit findings with no diff between rounds) precedes the cap firing — that
would specify a real stuck-detector beyond the timeout. Data: `final-triage-2026-06-02` (l.111-112),
`faithfulness-enforcement-2026-06-02` (drift signatures), AGENTS.md history (stuck-detector notes),
`tools/repro_cost.py` transcripts.

## Status
**mitigated** — fix agents are hard-capped with a defer-fallback (bounds the hang); a true
non-convergence stuck-*detector* remains noted as unbuilt, so the diagnosis-not-just-timeout side is
open.

## Refs
- Proposal (PRIMARY): `proposals/final-triage-2026-06-02.md` (l.111-112, the 4.4 h hang + hard-cap +
  defer-fallback).
- Proposal: `proposals/faithfulness-enforcement-2026-06-02.md` (l.176, "effort-exhaustion-
  masquerading-as-judgment" among the Process-Auditor drift signatures).
- Context: AGENTS.md history (recurring "stuck-detector isn't built" note).
- Siblings: **E5** (self-certification, the inverse pole), **M4** (no-op spin), **E2** (drift
  signatures).

---

### Evidence layer (for verification, not reading)
- **Grounding:** committed human-authored post-mortems (the dated 4.4 h hang + the named drift
  signature) + AGENTS.md history. **No quote ledger produced** — the Detector is a human watching the
  wall-clock (there was no automatic stuck-detector to narrate), and the diagnosis lives verbatim in
  the proposals (stronger, citable) rather than in workflow-agent narration. Per the brief,
  proposal-grounded → no ledger expected.
- **`[to-verify-on-deeper-dig]`:** long-running fix-agent transcripts may exist under
  `evidence/corpus-snapshot/`, but a hung loop's own narration would not contain a "stuck" admission
  (that is precisely what was missing); the runtime signal lives in timestamps/cost logs, not
  agent-behavior narration. Not promoted.
