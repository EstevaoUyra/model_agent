# T4 — Transient API throttling → a null verdict → the gate crashes or risks a false-green

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Tool/env · environment/substrate (with a gate-robustness behaviour attached) |
> | Behavior | a gate consumes a judging agent's verdict without guarding the case where the agent returned nothing, so a substrate failure (throttling) becomes either a crash or a silent pass |
> | Symptom | many concurrent passes trip server-side rate-limiting → a schema agent returns `null`; the digitization gate threw on `verdict.status` and crashed the run (Flash-Hogan, Sutton); a null faithfulness audit risked a **false-green** |
> | Agent role | process / gate (`full-pass.js`); substrate = the API rate limiter |
> | Trigger | high concurrency (many full-passes at once) trips throttling; a downstream gate reads a field off a `null` verdict |
> | Cause (evidence) | unguarded null verdict from a throttled agent — *intervention-tracked* (commit `16e5b39` null-guards the two gates) |
> | Detector | human (observed run crashes on Flash-Hogan / Sutton; later the audit-spec crash on vicente) |
> | Lever(s) | gate/code (synthesize BLOCKED on null; `filter(Boolean)`; honest `blockedExit`; resume-from-cache) |
> | Flags | dual failure mode — crash (loud) **and** false-green (silent, the dangerous one) |
> | Status | solved |

## The behaviour

The substrate condition itself is blameless: running many passes concurrently trips server-side
rate-limiting ("not your usage limit"), and a schema/judging agent returns `null` instead of a
verdict. That is an environment fact, not an agent mistake. What makes this a *behaviour* worth
cataloguing is how the gate **consumed** that null — it had two distinct failure modes, and they
differ sharply in danger:

1. **Crash (loud, safe-ish).** The digitization gate read `verdict.status` off the `null` and threw,
   taking the whole run down. From the fix commit: *"The digitization gate then threw on
   verdict.status and the whole run crashed (Flash-Hogan, Sutton)."* A crash is bad but
   self-announcing — no wrong figure ships.

2. **False-green risk (silent, dangerous).** A `null` **faithfulness** audit, if treated as "no
   findings," would let a build exit green without ever having been judged — the same class of error
   as passing a wrong figure, but caused by the audit *not running* rather than mis-judging. This is
   the failure that matters: *absence of a verdict read as a passing verdict.*

So one substrate hiccup could either crash the run or, worse, quietly certify an unaudited build.

## Why it happened (graded)

- **Unguarded null at the gate boundary** — *intervention-tracked (strong).* The fix is precisely to
  insert the missing guards: a `null` dig-audit verdict → synthesize a `BLOCKED` verdict (flag the
  figure, never crash), with `figResults` `filter(Boolean)`'d before use; a `null` faithfulness audit
  → an honest `blockedExit` (never false-green a dry round), and resume retries the failed agents
  from cache. The remedy being "treat a missing verdict as a block, not a pass/throw" is the
  intervention-tracked signature: the gate failed because it assumed the verdict always exists.

The shape worth naming: **at a gate, the safe default for a missing/aborted judgement is to BLOCK,
not to pass and not to throw.** A substrate failure (throttle, quota, agent death) must degrade to a
clean, resumable block — never to a silent green. This is the "fail-closed" discipline for an LLM
gate whose judge can vanish.

## How it responded to intervention

- **gate/code (held):** `16e5b39` (#41) null-guarded both gates — synthesize `BLOCKED` on a null
  digitization verdict, honest `blockedExit` on a null faithfulness verdict, `filter(Boolean)` the
  results, and resume-from-cache the failed agents.
- **extended (held):** the same fail-closed discipline was later applied to the `audit-spec` gate so
  a transient agent death (session quota) blocks cleanly and resumably instead of crashing the run —
  the crash seen on the 2026-06-26 vicente run — landed with the #68 process-artifacts versioning.

Status: solved (both the original two gates and the audit-spec gate now fail closed and resume).

## Confidence & threats to validity

High on the mechanism and fix — two named commits describe the exact null-handling change. Caveats:

- **The dangerous mode (false-green) is described as a *risk*, not a logged miss.** The commit says a
  null faithfulness audit "risked" false-green; the *crashes* (Flash-Hogan, Sutton, vicente) are the
  observed events. So the false-green is "the gate *would have* passed an unaudited build" — design
  reasoning, not an observed shipped-wrong-figure (`[to-verify-on-deeper-dig]`: any pre-fix run that
  exited green with a null/absent faithfulness verdict).
- **Substrate-coupled, so partly setup-specific** — the trigger (concurrency-induced throttling) is a
  property of running many passes at once on a shared rate limit; the *behaviour* (gate fails open on
  a missing verdict) generalizes to any LLM-judge gate.
- **Detector is human**, on crashing runs — the loud mode is what got noticed; the silent mode was
  caught by reasoning about the same null, which is the right call but underlines that nothing
  mechanically tested the false-green path.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-12 | Concurrency trips throttling → null schema verdict; digitization gate crashes (Flash-Hogan, Sutton); null faithfulness audit risks false-green. Null-guard both gates + resume-from-cache | `16e5b39` (#41) |
| 2026-06-26 | Same class crashes the `audit-spec` gate on vicente (session quota); null-guard it cleanly + resumably | `f540ab9` (#68) |

## Links

- `connects-to T2` (render sandbox lacks matplotlib) — both are `environment/substrate` conditions
  that surfaced as build/run failures; T4 additionally carries a gate-robustness behaviour (fail
  open vs fail closed).
- `connects-to E1 / E5` on the *false-green* half — "a build exits green without a real verdict" is
  the same end-state as evaluator leniency (E1) and self-certification (E5), reached here by the
  judge *not running* rather than mis-judging.

## Deeper-dig hook

`grep -rl "not your usage limit\|rate-limit\|null verdict\|blockedExit" evidence/corpus-snapshot/` to
find throttled agents in the narration; cross-check any run that exited green in a window with a
known null/aborted faithfulness agent to test whether the false-green was ever realized (vs only
risked).

## Status

solved · Domain Tool/env (substrate trigger + gate-robustness behaviour).

---

## Evidence layer (for verification, not reading)

- **Grounding:** git, **no quote ledger** — the failure lives in gate code (`full-pass.js`) reacting
  to a substrate condition, not in workflow-agent narration; the throttled agents return `null`
  (i.e. *no* narration to quote). Fully described by the two fix commits.
- **Refs:** commit `16e5b39` (#41, null-safe digitization + faithfulness gates) · commit `f540ab9`
  (#68, null-guard the audit-spec gate) · sibling entries T2, E1, E5.
