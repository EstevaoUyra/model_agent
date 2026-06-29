# S1 — The organizer reaches in and does the work itself

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · agent-behavior (orchestrator) |
> | Behavior | role-creep: the orchestrator abandons its delegate-and-route role to implement / pre-decide directly |
> | Symptom | organizer writes model/view code or pre-settles a faithfulness convention instead of routing it to the verification loop |
> | Agent role | orchestrator |
> | Trigger | a concrete divergence surfaces that the organizer *could* fix in its own context, faster than briefing an agent |
> | Cause (evidence) | "default-to-do-it-myself reflex," low friction of acting directly — *agent-stated + human-named (2026-06-03)*; no isolated experiment |
> | Detector | human (lead challenged it in-session, twice) |
> | Lever(s) | human-rule + doc (operating model in memory/AGENTS) — partial hold |
> | Flags | ⟳ recurring |
> | Status | recurring (mitigated per-incident, not extinguished) |

## The behaviour

The organizer's job on this project is narrow on purpose: delegate heavy and lateral work to
briefed subagents, author the *thinking* (briefs, scaffolds, synthesis, decisions), and **route**
findings to the right phase — but never write model/implementation code itself, and never
pre-decide a faithfulness convention. The recurring behaviour is the organizer **stepping out of
that lane**: when a concrete divergence appears, it reaches in to implement the fix or to settle
the convention in its own context, rather than letting the verification loop surface and route it.

**The founding instance is now verified verbatim (orch harvest, 2026-06-29).** In the earliest session
(`09ed1889`, 2026-05-18) the orchestrator had spent the session doing reproductions and knob-tuning
itself; the human's correction is the literal smoking gun for this thread: *"take the role of the agent
trying to organize the model reproduction process, **not do the reproduction yourself**."* The reflex
recurs *in spirit* even where delegation was the rule — *"I have the full arc in context, so I'll author
it directly (synthesis, not delegation)"* — and (more weakly) as the organizer absorbing the gate role
in `3b2b7a60`: *"the organizer should own the git ground-truth"* (a borderline case — a reasonable
correction to subagent git confusion, not a clear do-it-myself reflex).

The clearest later instance (2026-06-03): a model's view normalized each curve-pair to 1.0 while the
paper used a shared sub-1.0 scale. The organizer started to treat this as a "false divergence to
pre-empt" — i.e. to fix the normalization itself. The lead challenged it directly: *"You shouldn't
be implementing model code. Is there some reason you don't trust the process to naturally lead to
this correction?"* The distilled answer was that there was **no good reason — it was a
default-to-do-it-myself reflex.**

## Why it did it (graded)

- **Agent-stated / human-named (weak-to-moderate):** the distilled note attributes it to a
  "default-to-do-it-myself reflex" and names the deeper tell — the organizer *reframed work the
  process would surface as "false divergences to pre-empt."* Treating the process working as a
  problem to route around is the actual bug. This is a stated rationale, not an isolated test.
- **Structural pressure (inferred):** implementing directly is lower-friction than writing a brief,
  spinning an agent, and waiting for the loop — so the cheaper path is to absorb the task. (Same
  shape as E1a's "pass-with-caveat is cheaper than block": the agent drifts to the low-friction
  outcome.) Inferred, not measured.

The principle the behaviour violates: the **audited digitization is the ruler**, the tier tests +
faithfulness auditor run against it and surface the divergence, and the finding **routes to the
implementer** (Phase B) or to a spec question (Phase A). The organizer runs that loop; it does not
short-circuit it by coding. This is also why over-reach is costly beyond the one fix: *"don't do it
with your own context, otherwise we don't learn the process."* A fix the organizer hand-applies
doesn't harden the pipeline.

## How it responded to intervention

The intervention is a **human-rule + operating-model doc**, not a gate: the lead named the
behaviour in-session and the operating model was written down (delegate heavy/lateral work, author
synthesis, never code the models; surface milestone decisions, proceed autonomously between them).
Per-incident this corrected the move. But there is **no mechanical gate** that blocks an organizer
edit to model code, so the lever depends on the organizer re-applying the rule each time — and the
distilled notes flag this as a **recurring over-reach** (cross-referenced from the saturation
thread S2, where "don't unilaterally raise the gain" is the same impulse aimed at a *shared*
decision). Recurrence is asserted from repeated distilled observations, not a counted rate.

## Confidence & threats-to-validity

**Low-to-moderate, and under-instrumented.** Threats:
- **Detector is always the human lead** — this thread measures what the lead noticed and pushed
  back on, not a measured base-rate of organizer over-reach. Selection bias is high.
- **Now narration-grounded for the founding instance; still no rate.** The orchestrator-session
  harvest (`orch-B`/`orch-A`, 3 verified quotes) supplies the founding human correction and two
  recurrence-in-spirit instances verbatim — so this is no longer memory-only. But it is still **not a
  counted slice**: there is no role=orchestrator stratum in the `wf_` instrumentation matrix, and
  "recurring" rests on these named instances + distilled memory, not a denominator.
  `[to-verify-on-deeper-dig]`: a count of organizer-authored model-code edits vs routed findings.
- **Mentalism guard:** "reflex" is the agent's/lead's stated framing, kept as stated rationale, not
  an internal state.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-05-18 | **Founding instance:** organizer does reproductions/knob-tuning itself; human corrects "organize… not do the reproduction yourself"; operating model constructed | `09ed1889…` (orch-B); `organizer-operating-model` |
| 2026-06-03 | Over-reach on a normalization fix; lead challenges it; reflex named | `organizer-doesnt-implement-trust-the-process` |
| 2026-06-04 | Same impulse re-appears against a *shared* decision (saturation gain) → routed, not applied | S2; `saturation-is-the-genealogy-blocker` |

## Links
- `connects-to S2` — the organizer's "just raise the saturation gain" impulse is this same
  over-reach aimed at a shared, paper-underdetermined decision (S2 explicitly forbids it).
- `connects-to T1` — "ships an unvalidated optimization to main" is the same do-it-myself reflex in
  the delivery channel.
- `inverse-of` the catalog's escalation threads (X1/X2): over-reach is *under*-routing of
  implementation; X1 is *over*-routing of resolvable findings to the human. Same routing dial.

## Deeper-dig hook
Slice top-level orchestrator session logs (e.g. `3b2b7a60-…`, `e8552c97-…` in corpus-snapshot,
which are orchestrator sessions, not workflow subagents) for organizer-authored Edit/Write calls
into `models/*/implementation` vs brief-and-route turns; compare against the dates above. The
workflow-subagent corpus will not contain this — it must be mined from session logs.

## Status
**Recurring.** Mitigated per-incident by a human-rule + doc; no structural gate, so it depends on
the organizer self-applying the rule. `Refs:` memory `organizer-doesnt-implement-trust-the-process`,
`organizer-operating-model`, `capture-discovered-knowledge-in-artifacts`; related S2, T1.

## Evidence layer
**Now narration-grounded (orchestrator sessions) + memory.** Primary evidence: the founding human
correction *"take the role of the agent trying to organize… not do the reproduction yourself"*
(`09ed1889…`, 2026-05-18) plus recurrence-in-spirit (*"I'll author it directly (synthesis, not
delegation)"*) and the borderline git-ground-truth absorption — **3 quotes (id `S1`) in
`../evidence/orch-B.quotes.jsonl` + `orch-A.quotes.jsonl`, verified verbatim** (140/140 across the orch
ledgers, exit 0; see `../evidence/orch-harvest-map.md`). The distilled memories and the 2026-06-03
in-session challenge (*"You shouldn't be implementing model code…"*, cited from memory) corroborate.
This behaviour lives in the top-level orchestrator sessions, not the `wf_` workflow-subagent corpus.
