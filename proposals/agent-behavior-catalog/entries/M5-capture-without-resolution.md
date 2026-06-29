# M5 — Capture without resolution: a finding is filed honestly, then nothing actions it

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · process/delivery |
> | Behavior | the process has **capture machinery but no resolution machinery**: a divergence is recorded correctly (an SQ, a `notGreen` list, a deferral) and then left inert — it blocks nothing, re-queues nothing, downgrades nothing — and the loop tunes around the parked note |
> | Symptom | the RH2009 suppressive-geometry contract bug was filed five times (SQ-001 → SQ-005) and never resolved; `notGreen` was computed, logged, and returned with no consequence; the promised re-queue of deferrals never ran |
> | Agent role | implementer + auditors + the workflow loop (the parked note is everyone's and no actuator's) |
> | Trigger | a finding sink exists (SQ file / failing-figure list / DEFER) but no rule consumes it — nothing reads the sink and forces a block, a re-queue, or a status downgrade |
> | Cause (evidence) | structural — capture path with no resolution path — *intervention-tracked* (the SQ-blocking proposal makes an SQ a blocking circuit-breaker; the re-queue that "made the no-stop policy benign was never exercised") |
> | Detector | **human post-mortem** (the RH2009 suppression post-mortem; the 2026-06-02 faithfulness enforcement audit). Not a gate — the gates were the inert thing |
> | Lever(s) | proposed structural/logic: SQ becomes a blocking exit condition + auto-fires the paper-fix route (status PROPOSED at time of source) |
> | Flags | ⟳ recurred (five filings of one SQ; `notGreen`/re-queue both inert) · `connects-to D3`, `connects-to E5` |
> | Status | open (fix proposed, not confirmed landed in this slice) |

## The behaviour

The pipeline could *notice* a problem perfectly well and still do nothing about it. The capture side
worked: an implementer or an auditor would file a spec question (SQ), a Phase-B script would compute
the list of failing figures, a hard case would be marked DEFER. What was missing was the **other
half** — a rule that reads those records and *forces a consequence*. A filed SQ did not block the
implement step; a `notGreen` list was logged and discarded; a DEFER was closed as "scope" instead of
being re-queued for payback. So the finding sat in a sink, visible and correct, while the loop kept
iterating *around* it.

The canonical instance is the RH2009 suppressive-drive geometry. It was a model-level contract bug
(a 1D normalization measure, so the suppression term came out too small and the contrast-response
curves would not saturate). It was caught on day one and filed — and then re-filed, again and again,
as the loop tuned a per-figure gain to force the curves over instead of resolving the underlying
contract:

> "a contract bug that was *captured honestly five times* (SQ-001 → SQ-005) but *never resolved*,
> because the process has capture machinery and no resolution machinery." — sq-blocking proposal

The structural reading the proposal gives is the heart of M5:

> "**An SQ doesn't block anything** — it's a passive note the loop tunes around."

The same shape recurs in the faithfulness-enforcement audit, in two other sinks:

> "**C1. `notGreen` is inert.** Every Phase-B script computes the failing-figure list, logs it, and
> returns — no re-queue, no block, no status downgrade. The verdict is decorative."

> "**C5. The promised re-queue never ran; deferrals were closed as 'scope.'** The payback that made
> the no-stop policy benign was never exercised."

Three different sinks (the SQ file, the `notGreen` list, the deferral queue), one mechanism: a record
is created and no machinery is wired to its other end.

## Why M5 is **not** D3 (read this — it's why it's a separate thread)

D3 and M5 are adjacent and easy to conflate; the distinction is the whole reason M5 exists as a key.

- **D3 — a required *step* silently stops, and nothing notices.** The defect is on the **detection**
  side: a step (commit the paper crop, render, write the VLM verdict) quietly stops running, and *no
  gate asserts the step ran* — "absence reads as innocence." The finding never exists because the
  thing that would have produced it didn't happen, unobserved.
- **M5 — a *finding* is produced correctly and then ignored.** The defect is on the **actuation**
  side: the step ran, the divergence was *captured* (filed five times, even), it is fully visible —
  but no rule consumes the record to force a block/re-queue/downgrade. Capture ≠ resolution.

Put plainly: in D3 nothing watched, so nothing was recorded; in M5 something watched, recorded it
loudly and repeatedly, and the recording did nothing. D3's gap is "did the step happen?"; M5's gap is
"does recording the problem *do* anything?" The two share an ancestor — *a check exists but its
consequence doesn't* — but they fail at opposite ends of the pipe, so hardening one leaves the other
open. (After deliberating whether to fold M5 into D3 as a facet: it survives as its own thread. A
coverage gate that asserts every required step ran, D3's fix, would not have actioned RH2009's
SQ-001 — the step that filed the SQ *did* run; what was missing is the resolver that reads the SQ.)

## How it responded to intervention

The proposed lever is **structural/logic**: make an open in-scope SQ a *blocking circuit-breaker* so
the implement phase can no longer exit "faithful" while a contract is faulted, and have a newly-filed
SQ **auto-fire the paper-fix route** — wiring the capture sink to a resolution actuator with no manual
hand-off in between. At the time of the source this was `Status: PROPOSED`; whether it landed and held
is `[to-verify-on-deeper-dig]` (the sibling thread M4 shows the closely-related loop-arbiter change
did land in `2b88d08`, but that fixed the *no-op spin*, not the inert-capture sink as such). So M5 is
filed **open**: the failure is well-evidenced; the cure is documented as a plan, not yet confirmed as
a held intervention in this slice.

## Confidence & threats to validity

Moderate-to-high on the *behaviour*, low on the *outcome*. The behaviour is triple-attested in two
independent human post-mortems (the SQ-001→005 history; the `notGreen`/re-queue findings), and the
"five times" count is an explicit enumeration, not an estimate. Threats:

- **Anecdote ≠ rate.** "Five filings of one SQ" is one model's history; C1/C5 are two named sinks. It
  shows the pattern happened across ≥3 sinks, not a corpus-wide frequency of inert findings.
- **Detector is human, every time.** Both sources are human retrospectives — the catalog's
  selection-bias signal in pure form: the inert-capture behaviour was, by its nature, invisible to
  the gates (the gates *were* the inert things), so only a human reading the trail could surface it.
- **Outcome unverified.** The fix is `PROPOSED`; "open" reflects that this slice does not confirm the
  blocking-SQ rule shipped or that a later SQ was actually actioned by machinery.

## Scope / generality

Descriptive. The mechanism — a system with a place to *record* problems but no rule that *consumes*
those records into a forced consequence — is generic to any pipeline with a backlog/queue/flag store
and an optimisation loop that can route around it. Setup-specific in the particular sinks (SQ files,
`notGreen` lists, DEFER) and in the RH2009 suppressive-geometry instance.

## Links
- `connects-to D3` — **opposite ends of the same pipe.** D3 = a required step silently stops (no gate
  asserts it ran); M5 = the step ran and filed a finding that no machinery actions. Shared ancestor:
  a check without a consequence.
- `connects-to E5` — self-certification ("green tests ⇒ done") is the cognitive cousin: E5 infers
  success from no complaint; M5 is when there *was* a complaint and it still rode along inert.
- `connects-to M4` — M4 is a loop that re-runs a no-op fix forever; M5 is a loop that leaves the
  finding un-fixed and tunes around it. Both are "no real progress, loop continues."
- `shared-root → S2` — S2's RH2009 `SQ-005` is one of the very filings counted here; S2 is *why the
  decision was hard* (shared, paper-underdetermined), M5 is *why filing it changed nothing* (no
  resolution machinery).

## Deeper-dig hook
(1) Confirm whether the blocking-SQ exit condition + auto-paper-fix actually landed in
`.claude/workflows/full-pass.js` after 2026-06-04 and whether a *later* SQ was blocked/resolved by
machinery (not a human) — that would move M5 from open→mitigated. (2) Count, across all models'
`SQ-*`/exit records, how many filed SQs were ever resolved vs. closed-as-scope vs. still open
(denominator = filed SQs) to turn "five times" into a rate. Data: `sq-blocking-gate-and-paper-fix`,
per-model SQ ledgers, `logs/exit.json`, the Phase-B `notGreen` computation in `full-pass.js`.

## Status
**open** — behaviour well-evidenced across three sinks and two post-mortems; the resolution-machinery
fix is `PROPOSED`, not confirmed-landed-and-held in this slice.

## Refs
- Proposal (PRIMARY): `proposals/sq-blocking-gate-and-paper-fix-2026-06-04.md` (l.4-7 capture-vs-
  resolution; l.17-19 "an SQ doesn't block anything").
- Proposal: `proposals/faithfulness-enforcement-2026-06-02.md` (C1 `notGreen` inert; C5 re-queue never
  ran).
- Siblings: **D3** (silent step-stop), **E5** (self-certification), **M4** (no-op spin), **S2**
  (the shared RH2009 saturation decision behind SQ-005).

---

### Evidence layer (for verification, not reading)
- **Grounding:** two committed human-authored post-mortems + the SQ history; **no quote ledger
  produced.** The Detector is by definition a human reading the change/decision trail (the gates were
  the inert artifacts), and the diagnosis lives verbatim in the proposals, which are stronger, citable
  sources than the workflow-agent narration. Per the brief, this thread is proposal-grounded → no
  ledger is expected.
- **`[to-verify-on-deeper-dig]`:** SQ identifiers and `notGreen` appear in orchestrator-session and
  per-model logs under `evidence/corpus-snapshot/`, but those are human-led orchestration/loop logs,
  not the agent-behavior narration the quote harness targets; not promoted.
