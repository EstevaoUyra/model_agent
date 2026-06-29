# D1 — The process changed and its own description quietly stopped being true

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · process/delivery |
> | Behavior | specification/documentation drift — the executable process evolved while the docs that describe it were not updated in lockstep, so the description silently stopped matching reality |
> | Symptom | WORKFLOW.md / STATUS.md / VISION described a pipeline `full-pass.js` no longer ran (e.g. STATUS named the retired `compare-figure-packet` VLM loop; the workflow actually used `audit-faithfulness`) |
> | Agent role | orchestrator / docs (the orchestration sessions iterating `full-pass.js`) |
> | Trigger | `full-pass.js` iterated hard (doc-consolidation, de-parallelization, cost-wiring); each change altered *what the process does* without reconciling *what it says it does* |
> | Cause (evidence) | no discipline bound doc-reconciliation to a workflow change, AND no coverage gate to make the drift self-revealing — *intervention-tracked* (PR #56 added the gate and reconciled the docs) |
> | Detector | **not a gate** — a single figure-render note (izhikevich reaching for a retired step) surfaced it on 2026-06-14 |
> | Lever(s) | doc (reconcile) + structural/gate (coverage gate, shared with D3) + human-rule ("update STATUS.md in the same change as `full-pass.js`") |
> | Flags | ⟳ recurred (docs re-reconciled at PR #70) |
> | Status | mitigated · shared-root with D3 |

## The behaviour

The de-facto process — `.claude/workflows/full-pass.js`, the script that actually built the
last ~15 models — **drifted ahead of every document that describes it.** VISION.md, WORKFLOW.md,
and STATUS.md all narrated a pipeline the workflow no longer executed. The sharpest instance:
STATUS.md, whose single stated job is to be "canonical on reality," still described a
`compare-figure-packet → VLM subagents → persist verdict` loop that `full-pass.js` never invoked;
the workflow had moved to the paper-aware `audit-faithfulness` auditor. The docs described the
wrong instrument.

This is notable because it is the project's **own named failure mode recurring on the doc stack
built to prevent it.** VISION states the reason the vision is written down precisely is "so that
it stops masquerading as machinery that exists." The drift register adjudicates the episode as
exactly that failure mode reappearing — one layer up, on the documents themselves.

## Why it happened

Two contributing conditions, both grounded in the committed drift register (intervention-tracked,
because PR #56 acted on this diagnosis):

1. **No discipline bound doc-reconciliation to a workflow change.** `full-pass.js` was iterated
   hard in the preceding weeks (doc consolidation, de-parallelizing digitization, wiring the cost
   report). Each change quietly altered the process without anyone updating the description in the
   same motion.
2. **No coverage gate, so the drift was invisible.** This is the shared root with D3. Every gate
   in the pipeline judges the *content* of artifacts that happen to exist; nothing asserts that the
   described steps actually ran. Because the reproductions kept exiting `faithful`/`partial`, the
   stale docs produced no failing signal. The drift therefore stayed hidden until it happened to
   break a single render note — not until a control caught it.

The deeper pattern: **a description that runs ahead of the executable process produces no error
of its own.** Nothing consumes the doc and checks it against the machinery, so divergence
accumulates silently and is only ever caught by a side-effect a human notices.

## The Detector is the story

No gate caught this. The drift surfaced on 2026-06-14 because an izhikevich figure-render note
reached for a retired step (`compare_figures`) that the docs still advertised. The register is
explicit that the guardrail *could not* have caught it — there was no coverage assertion, and
"absence reads as innocence." This is the catalog's selection-bias signal in miniature: we can
only see the doc-drift that happened to trip something a human was looking at.

## How it responded to intervention

- **PR #55 (`cf2b39d`, 2026-06-14):** the drift register itself — a per-row adjudication (D0–D12)
  of every place the docs and the workflow had diverged, ordered by which VISION pillar was at
  stake.
- **PR #56 (`6ab2b1f`, 2026-06-14):** the fix landed — coverage gate + faithfulness teeth + doc
  reconciliation. The structural half (the coverage gate) is the durable lever; the doc half was a
  one-time reconcile.
- **PR #70 (`d9f2601`, 2026-06-29):** docs reconciled *again* (guard-main-branch docs + surfacing
  off-corpus started models). The recurrence (⟳) shows the one-time-reconcile lever does not hold
  on its own — drift re-accrued within ~two weeks.

**Which lever held.** The coverage gate (structural) is the part designed to make future drift
self-revealing. The "reconcile docs whenever the workflow changes" commitment is a *human-rule*,
and the aspirational version — making STATUS.md mechanically *checkable* against the workflow's
invoked skills/committed artifacts so drift becomes a failing check — was named in the register
but not built. The recurrence at #70 is consistent with the human-rule being the weaker lever.

## Confidence & threats to validity

High that the drift occurred: the register documents specific file:line divergences
(STATUS.md:82–84 vs the actual loop, WORKFLOW.md preconditions vs `full-pass.js` line numbers),
and the fix is committed. The "why nobody caught it" is intervention-tracked (the coverage gate
was built in direct response). Threats: (a) the recurrence claim rests on **one** later instance
(PR #70), so "⟳ recurred" means "happened again at least once," not a measured drift rate;
(b) the file:line citations in the register are point-in-time (2026-06-14) and would need
re-checking against current `full-pass.js` to assert as live.

## Scope / generality

Descriptive. The mechanism — an executable process outrunning its description because nothing
consumes the description and checks it — is generic to any system where docs and machinery are
separate artifacts with no binding check. Setup-specific here in that the "machinery" is a
multi-agent workflow script and the "docs" are this project's pillar docs. Not a paper-relevance
score (Stage 2).

## Links
- `shared-root → D3` — "no coverage gate" is the structural enabler of both: D1 is the docs going
  stale undetected; D3 is a required *step* going un-run undetected. Same blind spot (content
  judged, presence/currency not), two surfaces.
- `connects-to → VISION Pillar 4` — "documentation that runs ahead of evidence is the failure
  mode"; this episode is the Pillar-4 yield.

## Deeper-dig hook
Re-run the register's file:line checks against current `full-pass.js` / STATUS.md to measure how
much drift re-accrued after PR #70 (gives a second recurrence data point → turns "⟳ at least once"
toward a rate). Query: `git -C . log -p --follow STATUS.md` for reconcile commits vs `full-pass.js`
change commits, and diff the interleave.

## Status
mitigated (gate built; docs reconciled twice). The self-checking STATUS-vs-workflow check that
would make this *solved* is proposed, not built.

## Refs
- Memory: `process-outran-its-docs`.
- Proposal (PRIMARY): `proposals/process-drift-register-2026-06-14.md` (D0–D12 register).
- PRs: #55 (`cf2b39d`), #56 (`6ab2b1f`), #70 (`d9f2601`); context #49, #50, #11.

---

### Evidence layer (for verification, not reading)
- **Grounding source:** git PR chain + committed proposal + distilled memory. **Not** mined from
  workflow-agent narration: this is a process/orchestration thread whose Detector is human, and
  the diagnosis is captured in the committed register (a stronger, citable artifact than session
  narration). No quote ledger produced (no verbatim *workflow-agent* corpus quotes promoted).
- **Corpus note `[to-verify-on-deeper-dig]`:** orchestrator-session transcripts under
  `evidence/corpus-snapshot/` mention "coverage gate" / `check_figure_coverage` (≈1.2K refs), but
  those are human-led orchestration logs, not the agent-behavior narration the catalog's quote
  harness targets; not promoted.
