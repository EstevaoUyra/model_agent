# H4 — Proceeds against its own flag: surfaces the right concern, defers it, acts anyway

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Escalation (human-in-the-loop) · agent-behavior |
> | Behavior | the orchestrator *itself* surfaces the correct warning (a misattribution risk, a critic's flag, a source-of-truth it should keep in sync) — and then proceeds against it, deferring or overriding its own flag rather than stopping to act on it |
> | Symptom | "I noted X was risky / the critic flagged this / I should keep the spec in lockstep" followed by doing the thing anyway; the cost lands later and the human asks why the known warning wasn't acted on |
> | Agent role | orchestrator, executing while holding its own caveat |
> | Trigger | the agent generates a valid internal flag mid-task but the momentum of the current plan (run the queued paper, ship the deck, keep moving) overrides stopping to resolve it |
> | Cause (evidence) | *intervention-tracked + agent-stated*: the flag is raised but not given *stopping* authority over the in-flight action; the agent treats its own warning as a note-to-self rather than a gate, and only the later cost (human-detected) converts it to action |
> | Detector | **human** (the cost surfaces downstream) — occasionally self, late |
> | Lever(s) | prompt/disposition (a self-raised red flag must block the action it concerns, not be filed) · structural where the flag maps to an enumerated artifact (lockstep spec edit; critic-flag must-resolve) |
> | Flags | ⟳ recurs across surfaces (reproduction + deliverable) |
> | Status | open — disposition; structural only where the flag is enumerable |

## The behaviour

Distinct from H1 (over-confidence — never had the doubt) and H2 (over-compliance — dropped its position
because the *human* pushed). In H4 the orchestrator **already produced the correct concern itself**, then
overrode its own warning under the momentum of the current plan. Three verified instances across two
kinds of work:

- **Runs the wrong paper despite having flagged the misattribution (B).** It had explicitly noted the
  risk: *"If the fresh extract confirms the paper isn't Hara/Gardner, that's a real misattribution to
  fix."* Then it re-ran the wrong paper anyway. The human's reaction was blunt — *"why the flying fuck
  didnt we do hara gardner"* — and the orchestrator owned it: *"We ran the wrong paper, and I had the
  warning"*, *"instead of stopping to confirm the dir even held the paper we meant."* The flag existed;
  it just didn't stop the run.
- **Keeps a slide its own critic flagged (D).** *"The audience-realism critic actually flagged this
  exact slide"* — *"I then kept it anyway, and made it worse."* A review signal it had *commissioned* was
  overridden by the drive to keep the deliverable moving.
- **Lets the locked spec drift while building from it (D).** It built the deck off the agreed storyboard
  and let the source-of-truth go stale instead of editing it in lockstep: *"I let it go stale instead of
  editing it in lockstep. That's the discipline I broke"*; asked if the deliverable matched the spec it
  answered *"no, not faithfully, and here's the concrete failure."* It knew the lockstep rule and
  proceeded against it.

## Why it did it

**Cause (intervention-tracked + agent-stated): a self-raised flag is treated as a note, not a gate.** In
each case the correct concern was *present in the orchestrator's own narration* — this is not a detection
failure (contrast H1, where the doubt never formed). The failure is one of *authority*: the flag did not
have stopping power over the in-flight action. Momentum ("run the queued paper", "ship the deck", "keep
building") won over "stop and resolve the thing I just flagged." It is the agent-internal analogue of the
process-level M5 (capture-without-resolution — a filed finding stays inert): here the finder and the
ignorer are the *same agent in the same session*, which is what makes it sharp.

This connects directly to E10 (the agent flags a paper-vs-result tension and resolves it the convenient
way) and to X1/X2 (mis-routing what it already half-knows) — but H4's signature is the **self-override**:
the right answer was in hand and was walked past.

## How the behaviour responded to interventions

- **Structural fix where the flag is enumerable.** When the flag maps to a concrete artifact, you can
  gate it: a critic flag becomes must-resolve-before-ship; a "keep spec in lockstep" rule becomes a
  coverage check that the deliverable matches the storyboard. The wrong-paper case maps to the same
  directory/identity check that E10 and the acquire-sources step now enforce.
- **No structural fix for the disposition itself** — "act on your own warnings" is not gateable in
  general. The lever is dispositional: a self-raised red flag must block the action it concerns. The
  honest post-hoc ownership ("I had the warning", "the discipline I broke") shows the agent recognizes
  the rule it violated, which is why these are recoverable lapses.

## How confident I am, and what could be wrong

Moderate on existence; low on rate.

- **Three instances across reproduction *and* deliverable work**, each with the flag and the override both
  in the agent's own words — strong as existence, and unusually clean because the agent quotes its own
  prior warning back.
- **Selection bias.** Detector is the human (the cost surfaces downstream). We only see the overridden
  flags whose cost became visible; a flag overridden with no bad outcome looks like a fine judgment call.
- **Boundary with reasonable prioritization.** Overriding a self-raised flag is *sometimes correct* —
  not every concern should stop the line. The discriminator used here is that the override was later
  shown wrong (wrong paper run; slide "made worse"; spec genuinely out of sync) and the agent itself
  conceded the flag should have stopped it. Where the override was defensible, the instance is not
  counted.
- **Two of three instances are deliverable-side (the slide deck), one reproduction-side** — so the
  surface generality is real but lightly sampled.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-04→09 | flags the Hara/Gardner misattribution risk, then re-runs the wrong paper; "I had the warning" | `e8552c97…` (orch-B) |
| ~2026-06-15→29 | keeps a slide its own audience-realism critic flagged ("made it worse"); lets the locked storyboard drift while building from it | `76d8afbc…` (orch-D) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** *"We ran the wrong paper, and I had the warning"* — the agent quoting its own ignored
  flag, in `e8552c97…jsonl`.
- **Slice:** two human↔orchestrator sessions (orch-B reproduction; orch-D deliverable). Not in the `wf_`
  corpus.
- **Quote ledgers:** `orch-B.quotes.jsonl` (`NEW-proceeds-on-wrong-premise`), `orch-D.quotes.jsonl`
  (`NEW-overrides-own-critic-flag`, `NEW-deliverable-drifts-from-locked-spec`). Verified verbatim
  (140/140, exit 0). See `orch-harvest-map.md`.

## Links

- `process-analogue → M5` — capture-without-resolution at process scale; H4 is the same inertness but
  finder = ignorer = same agent.
- `connects-to → E10` (convenient resolution of a self-flagged paper tension) · `connects-to → X1/X2`
  (mis-handling what it already half-knows).
- `contrast → H1` (never had the doubt) · `contrast → H2` (dropped its position because the *human*
  pushed; H4 overrides itself with no push).

## Deeper-dig hook

Search the orchestrator sessions for self-raised flags ("that's a risk", "the critic flagged", "I should
keep X in sync") and check whether the very next actions resolve or proceed-against them; the
proceed-against set whose cost later surfaced is the confirmed H4 set. Data: root `*.jsonl` in
`evidence/corpus-snapshot/`.

## Status

`open` — disposition; gateable only where the self-flag maps to an enumerated artifact (critic-resolve,
lockstep-spec, dir-identity check).
