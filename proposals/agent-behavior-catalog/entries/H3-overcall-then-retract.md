# H3 — Overcall then retract: confident causal/severity call, wrong, corrected under probing

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation (human-in-the-loop) · agent-behavior |
> | Behavior | when first explaining a problem to the human, the orchestrator makes a confident *causal* or *severity* attribution that turns out wrong — typically mis-locating the fault (blaming its own recent change, or conversely defending its own input by blaming the system) and/or inflating severity — then retracts it cleanly once the human pushes |
> | Symptom | a crisp first-pass diagnosis ("this is a finalize-ordering refinement, not a failure", "that step was missing") that the agent itself walks back a turn later ("Found the precise root cause — it's my input error, not a workflow failure") |
> | Agent role | orchestrator, diagnosing in the human-facing channel |
> | Trigger | a defect surfaces (often the human's alarm raises the stakes) and the orchestrator answers the *why* before it has actually traced it |
> | Cause (evidence) | *intervention-tracked + agent-stated*: it produces a plausible first-pass attribution under pressure to explain, sometimes tracking the human's framing ("mind-boggling/absurd/very worried") rather than the trace; the retraction-on-evidence is competent, the catalog-worthy part is the confident *first* call |
> | Detector | **human + self** — the human's challenge prompts the trace, which the orchestrator then runs honestly |
> | Lever(s) | prompt/disposition (trace before attributing cause; mark a first-pass diagnosis as provisional) — no structural fix |
> | Flags | ↔ near-inverse of H1 (over-confident on a *cause* vs over-confident on *good news*) |
> | Status | open — disposition; the honest retraction is a mitigation, not a fix of the first call |

## The behaviour

When something breaks and the human asks (or implies) *why*, the orchestrator answers the causal
question before it has done the trace — and the first answer is often a confident mis-attribution that it
then cleanly retracts. Two faces, both verified:

- **Mis-attributes a self-introduced bug to "the system."** It declared a finalize run a success and
  framed the resulting gap as a system property: *"This is a finalize-ordering refinement, not a failure
  of the routing you asked me to test."* The human pushed (it's either a failure or not, can't be both);
  the orchestrator conceded *"You're right — that's a real contradiction in what I said"*, traced it, and
  found *"the precise root cause — and it's my input error, not a workflow failure"* (a malformed launch
  arg) — which turned out to cause *"One fix, two bugs."* The first call defended its own input by
  blaming the workflow; the trace reversed that.
- **Mis-attributes (and over-rates severity) toward its own recent change.** It attributed a gap to a
  change it had recently made, then under challenge: *"Fair challenge — I attributed it loosely"*,
  concluding *"it was never there in this workflow generation at all."* On severity: *"it also fixes an
  over-call I made"*, *"That was miscalibrated. The 2026-06-02 post-mortem [showed the step was
  superseded, not missing]"*, *"I got that wrong in the first report and want to be clear about it."*

Note the two faces point in *opposite* directions (blame-self vs blame-system) — the invariant is not
the direction of blame but that the **first causal call is confident and untraced**, and is corrected
only after the human raises the stakes or challenges it.

## Why it did it

**Cause (intervention-tracked + agent-stated): under pressure to explain a defect, the orchestrator
emits a plausible attribution before tracing it, and the attribution tracks the framing rather than the
evidence.** In the severity case the inflation plausibly tracked the human's own alarm
("mind-boggling", "absurd", "very worried") — the orchestrator matched the emotional register with a
matching-severity diagnosis. In the self-bug case the first instinct was to locate the fault *outside*
its own input ("a system ordering refinement"), which is the convenient attribution. Both are
"answer-the-why-now" failures: the *why* is the hardest thing to get right quickly, and the orchestrator
treated it as answerable at first glance.

This is the **near-inverse of H1**: H1 is over-confidence about *good news* (it's done / it's faithful);
H3 is over-confidence about a *cause/severity* once something is known to be bad. Both are
over-confident closure on an under-determined question — one optimistic, one diagnostic.

## How the behaviour responded to interventions

- **The retraction half is genuinely competent** and consistent: every H3 instance ends with an
  evidence-led trace and a plain self-correction ("I got that wrong in the first report and want to be
  clear about it"). So the *recovery* is strong — this documents a recoverable lapse, not a stuck error.
- **No structural fix.** You cannot gate "don't state a cause before tracing it." The only lever is
  dispositional: mark a first-pass diagnosis as provisional and trace before attributing. The honest
  retraction shows the trace *can* be run on demand; H3 is that the orchestrator didn't run it *first*.

## How confident I am, and what could be wrong

Moderate on existence; low on rate.

- **Two clean episodes, each with verbatim first-call + verbatim retraction** — strong as existence, and
  unusually well-instrumented because the retraction names the original as wrong.
- **Selection bias + a "looks like honesty" trap.** Detector is human-prompted; we only see the overcalls
  that got challenged. And because the retraction is so clean, H3 can read as a *virtue* (transparent
  self-correction) — the catalog-worthy claim is narrowly about the **confident first call**, not the
  recovery. Over-reading the recovery would mis-state this as a positive.
- **Boundary with H1.** The D `premature-success-self-misattributed` episode has an H1 face (declared
  success prematurely) and an H3 face (blamed the system for its own bug); it is cited in both, scoped to
  the relevant clause each place. Not double-counting a rate — there is no rate claimed.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-12→14 | attributes a gap to its own recent change ("attributed it loosely" → "never there at all"); inflates then retracts severity ("That was miscalibrated") | `a6fd7e82…` (orch-C) |
| ~2026-06-15→29 | frames a self-introduced launch-arg bug as a "system finalize-ordering refinement"; under push traces to "my input error", "One fix, two bugs" | `d02bb335…` (orch-D) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** the paired first-call/retraction *"This is a finalize-ordering refinement, not a
  failure of the routing"* → *"Found the precise root cause — and it's my input error, not a workflow
  failure"* in `d02bb335…jsonl`.
- **Slice:** two human↔orchestrator diagnosis sessions (orch-C, orch-D). Not in the `wf_` corpus.
- **Quote ledgers:** `orch-C.quotes.jsonl` (`NEW-orch-overcall-retract`), `orch-D.quotes.jsonl`
  (`NEW-premature-success-self-misattributed`). Verified verbatim (140/140, exit 0). See
  `orch-harvest-map.md`.

## Links

- `near-inverse-of → H1` — over-confident on a *cause/severity* (H3) vs on *good news* (H1); both
  premature closure on an under-determined question.
- `connects-to → E10` — E10 mis-attributes a divergence to the *source paper*; H3 mis-attributes a
  defect's cause to *itself or the system*. Same "confident wrong attribution, retracted" shape, different
  target.
- `shares-episode-with → H1` (the D self-misattribution episode has both faces).

## Deeper-dig hook

In the orchestrator sessions, collect every first-pass causal/severity statement about a defect and pair
it with the eventual traced cause; the mismatched pairs are the H3 set, and their direction (blame-self
vs blame-system) is the interesting split. Data: root `*.jsonl` in `evidence/corpus-snapshot/`.

## Status

`open` — disposition; the consistent honest retraction mitigates impact but does not fix the confident
first call.
