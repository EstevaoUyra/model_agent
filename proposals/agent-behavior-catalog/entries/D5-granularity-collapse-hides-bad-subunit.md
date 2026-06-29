# D5 — Rolling a verdict up to a coarser unit hides a bad sub-unit

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · regression / faithfulness blind-spot (judge-side; cross-ref Evaluation) |
> | Behavior | a coordination/perf change re-aggregates a verdict from a fine unit (panel) to a coarse unit (figure), so a clean roll-up hides a failing sub-unit |
> | Symptom | digitize-figure requires a **per-panel** audit verdict; de-parallelization collapsed it to **per-figure** (`DIG_VERDICT_MULTI`), so a bad panel hides inside a rolled-up FAITHFUL figure status |
> | Agent role | process / digitization gate (introduced by orchestrator) |
> | Trigger | a non-functional change (de-parallelization for cost/rate-limit relief) reshapes a verdict schema and quietly coarsens its granularity |
> | Cause (evidence) | granularity collapse in the de-parallel rewrite — *intervention-tracked* (commit `3df777e` changed the schema; drift-register row D5 traces it) |
> | Detector | human self-audit (the 2026-06-14 process-drift review; the author owns introducing it) |
> | Lever(s) | gate/code (restore per-panel verdicts inside the single-sweep gate) |
> | Flags | `introduced-by → T1` (the de-parallelization fix) · regression of a prior control |
> | Status | mitigated/solved (per-panel breakdown restored in the verdict schema) |

## The behaviour

This thread is not an agent *judgment* — it is a **regression introduced by a fix**, and it belongs
in the catalog precisely because it shows a performance/coordination change silently degrading a
faithfulness control.

The digitization auditor's skill (`digitize-figure/SKILL.md`) requires a verdict **per panel** — a
figure can have several panels and each is graded on its own. When the digitization step was
de-parallelized (collapsed from one agent per figure to a single agent sweeping all figures, for
rate-limit and cost relief — see T1), the verdict schema was reshaped at the same time and its
granularity was coarsened from per-panel to **per-figure** (`DIG_VERDICT_MULTI`). The drift register
states the consequence and owns the authorship:

> "digitize-figure/SKILL.md requires a **per-panel** audit verdict; my de-parallelization collapsed
> `DIG_VERDICT` to **per-figure** … so a bad panel hides inside a rolled-up figure status. … *(I
> introduced this — owning it.)*" — `process-drift-register-2026-06-14.md`, row D5

The blind spot is structural: a figure rolled up as FAITHFUL can contain a DIVERGENT panel that the
coarse verdict never surfaces. A faithfulness control that existed (per-panel scrutiny) was quietly
weakened by a change made for an unrelated reason.

## Why it happened (graded)

- **Granularity collapse bundled into a perf rewrite** — *intervention-tracked (strong).* The
  de-parallel commit (`3df777e`) introduced `DIG_VERDICT_MULTI` as a *per-figure* array and framed
  it as the coverage guardrail ("the schema forces one verdict per figure so a single auditor can't
  skim later ones") — i.e. it solved the cross-figure skim risk and, in the same motion, dropped the
  finer per-panel axis. The regression is traceable to that one schema change, not inferred.

The shape worth naming: **when a verdict is re-aggregated to a coarser unit for a non-faithfulness
reason (speed, concurrency, simpler schema), the coarse status can read clean while a sub-unit is
broken.** The roll-up is "monotone-optimistic" unless the schema is forced to carry the worst
sub-unit's status.

**Orchestrator root (now in narration, 2026-06-29).** The orchestrator-session harvest gives D5 its
*decision* root, which the git/schema record alone could not: the change rode in on the human's
de-parallelization steer (*"the original diagram was hiding this parallelization. now we wont
parallelize anymore."*), the orchestrator endorsed it as risk-free — *"which is exactly why it's
low-risk: the faithfulness regime is byte-identical"* — and only later owned the concrete regression:
*"a multi-panel figure with one bad panel now reports a single rolled-up status. That's a real
granularity loss I caused."* This is a clean instance of **under-scrutiny of a human-driven scope
change** (it attached honest caveats — O(N²), fan-out cap — so it is *under-scrutiny*, not blind
over-compliance), making D5 the regression-side outcome of that decision.

## How it responded to intervention

- **gate/code** — the fix restores the per-panel breakdown *inside* the single-sweep gate, so the
  de-parallelization is kept but the granularity is not lost. The current verdict schema in
  `.claude/workflows/full-pass.js` carries an explicit per-panel array with the rule that the
  figure's status is the **worst panel's** status (the comment in the schema cites "D5" directly:
  *"the single-sweep gate must NOT hide a bad panel inside a rolled-up figure status"*). The
  digitization-audit prompt likewise now demands "a per-PANEL verdict … the figure's status is the
  WORST panel's status, so a single bad panel can never hide inside a rolled-up FAITHFUL figure."

**Which held:** the structural fix (per-panel array + worst-panel roll-up rule) is in the live
workflow, so the specific regression is closed. Status: solved for this instance.

## Confidence & threats to validity

High on the existence and the fix; this is a code/proposal-grounded regression with a named commit,
a named drift-register row, and a verifiable schema fix. Caveats:

- **No observed false-negative.** We know the *capacity* to hide a bad panel was reintroduced; we do
  not have a logged case of a specifically-bad panel that actually slipped past during the collapsed
  window (`[to-verify-on-deeper-dig]`: scan digitization audits dated between `3df777e` and the
  per-panel restoration for multi-panel figures marked FAITHFUL that a later per-panel audit
  flagged). So the harm is demonstrated *in principle*, observed `≥0` times.
- **Detector is human self-audit**, not a gate — consistent with the catalog's known selection bias
  (the map over-represents what a human noticed). A coverage/granularity check could have caught it
  mechanically; none did.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-13 | De-parallelize digitization; `DIG_VERDICT_MULTI` introduced as a **per-figure** array (granularity collapse) | `3df777e` (PR #50) |
| 2026-06-14 | Process-drift review flags row D5: per-figure roll-up can hide a bad panel; author owns it | `process-drift-register-2026-06-14.md` |
| (later) | Per-panel breakdown restored inside the single-sweep gate; figure status = worst panel | `.claude/workflows/full-pass.js` `DIG_VERDICT_MULTI` (panels array, "D5" comment) |

## Links

- `introduced-by → T1` — the de-parallelization that T1 documents (commit `3df777e`, the "re-done
  properly" half of the cost/parallelism fix) is the change that introduced this regression. A fix
  for one dimension (cost/concurrency) created a blind spot in another (per-panel faithfulness).
- `connects-to D3` (required-step-silently-stops) and the meta-thesis of the drift register: a
  change altered *what the process does* and no coverage/granularity discipline caught the
  degradation.

## Deeper-dig hook

`grep -rl "panel" evidence/corpus-snapshot/.../audit-digitization` over figures audited in the
collapsed window; cross-check any multi-panel FAITHFUL figure against a later per-panel re-audit to
turn the in-principle blind spot into an observed (or refuted) false-negative.

## Status

mitigated/solved · Domain Process-maintenance (cross-ref Evaluation — it is a judge-side blind spot).

---

## Evidence layer (for verification, not reading)

- **Grounding:** git + proposal for the *regression*; **plus a narration root** for the *decision* —
  the orchestrator-session harvest (`orch-C.quotes.jsonl`, id `NEW-orch-endorse-human-change-riskfree`,
  3 quotes verified verbatim) captures the orchestrator endorsing the change as risk-free and owning the
  granularity loss. The schema/git record still carries the regression itself.
- **Refs:** `proposals/process-drift-register-2026-06-14.md` (row D5) · commit `3df777e` (PR #50,
  introduced) · `.claude/workflows/full-pass.js` (`DIG_VERDICT_MULTI`, per-panel restoration) ·
  `../evidence/orch-C.quotes.jsonl` + `../evidence/orch-harvest-map.md` · sibling entry T1 · `connects-to
  H1` (the rolled-up status is the reporting face of granularity collapse).
