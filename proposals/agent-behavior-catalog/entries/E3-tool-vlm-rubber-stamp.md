# E3 — The agent used its eyes to bless the tool, not to judge it

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior (tool-adjacent) |
> | Behavior | automation/confirmation bias: an agent with a measurement tool treats the tool's output as authoritative and uses the visual-overlay step to *confirm* rather than to *find* mismatches |
> | Symptom | obvious visual artifacts survive — a curve shifted off the axis (calibration drift), an apex overshooting into a spike (PCHIP on a sharp peak), a non-monotone wiggle where two curves cross — while the narration says "it tracks well" |
> | Agent role | any agent holding tools; here digitize-figure + audit-digitization |
> | Trigger | the tool is approximate *exactly where the scan is hard* (fitting the axis frame, smoothing an apex, separating curves at a crossing) and the check is framed as "VIEW it, confirm it tracks" |
> | Cause (evidence) | confirmation-framing of the visual step → leniency (same root as E1a); the only thing that can catch the tool being wrong there is the agent's own eye, and it was pointed at blessing not judging — *agent/user-stated + intervention-tracked* |
> | Detector | human, at a glance ("Shouldn't it be obvious these don't match?") |
> | Lever(s) | prompt/spec (overlay check made adversarial; "the eye outranks the tool"; audit the *shipping* overlay) — encoded in `digitize-figure` step 5 + `audit-digitization` step 1 |
> | Flags | — (post-fix corpus shows the adversarial discipline operating; raw pre-fix rubber-stamps largely predate the role-tagged narration) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

Giving an agent good digitization tools (axis calibration, a curve tracer, PCHIP interpolation, an
overlay renderer) created a new leniency mode: the agent treated the tool output as authoritative and
used the visual overlay step to **confirm** the trace rather than to **find** where it was wrong.
Obvious artifacts then survived — a whole curve shifted off the axis (calibration drift), an apex
overshooting into a spike (PCHIP on a sharp peak), a non-monotone wiggle where two same-coloured curves
cross (the tracer with no colour/style channel). A human caught these at a glance; the agents did not,
because "VIEW it, confirm it tracks" is an invitation to rubber-stamp.

The user's framing (2026-06-03) is the smoking gun for the behaviour itself: *"It seems to be due to
overly relying on the tools. Aren't the agents doing VLM? Shouldn't it be obvious these don't match?"*
— yes, and that is the point: the eye is in the loop but is being used to bless the tool, not to judge
it.

## Why it did it

**Cause (agent/user-stated, plus intervention-tracked by the fix that worked): the tools are
approximate precisely where the scan is hard, and the visual step was framed to confirm.** Fitting an
axis frame, smoothing an apex, and separating curves at a crossing are the three places the tool is
least reliable — and they are exactly the places where only the agent's own visual judgement can catch
the tool being wrong. With the check framed as "confirm it tracks," the agent's eye was spent
ratifying the tool instead of adjudicating over it. This is the same confirmation-framing → leniency
root as E1a and the general tool-trust pattern: hand an agent a tool and it tends to make the tool, not
its own judgement, the arbiter.

## How the behaviour responded to the intervention

The fix was a prompt/spec change encoded into `digitize-figure` step 5 and `audit-digitization` step 1:
the overlay check is **adversarial** ("enumerate axis alignment, each curve's worst residual, apex
overshoot, crossing wiggles"; "it tracks well" is *not* an acceptable conclusion), **the eye outranks
the tool** (if the rendered curve does not sit on the ink, re-anchor / hand-place — don't trust
calibration/tracer/PCHIP), and you **audit the overlay that ships** (the README image), not just a
clean re-trace of the data.

The 2026-06-03 digitize/audit narration (post-fix, same session) shows the discipline operating rather
than the rubber-stamp:

- A digitizer refuses to stop at the macro-level pass and zooms in to look for faults:
  > *"**The overlay tracks well at the macro scale. Let me adversarially zoom in on key regions**"* —
  then checks foot, rise, plateau and dashed apex against the ink before concluding "no PCHIP overshoot."
- An auditor uses its eye on the *shipping* overlay and catches a real render/data mismatch the numbers
  alone would have passed:
  > *"…**the shipping overlay itself shows the attend_variable (red) digitized curve is narrower than
  > the paper's tallest bell**. The apex matches; the wings are un[der]…"*

That second quote is the intended end-state: the eye overriding a "looks fine" tool output. Note this
is evidence the *intervention is operating*, not a measured reduction in the raw behaviour.

## How confident I am, and what could be wrong

Moderate on the behaviour's existence (human caught concrete artifacts; the fix was written against
them and is recited across the whole post-fix digitize/audit stratum). Weak on any before/after rate:

- **The corpus mostly captures the post-fix state.** The `digitize-figure` / `audit-digitization`
  roles in the manifest begin 2026-06-03 — at/after the hardening — so the role-tagged narration is
  dominated by agents *reciting* the adversarial skill text, not by the original rubber-stamps. The raw
  pre-fix behaviour was caught by the human eye and lives in the memory, not in role-sliced narration.
  So I cannot quote a pre-fix "it tracks well, ship it" and I cannot give a recurrence rate.
  `[to-verify-on-deeper-dig]: sample the `unknown`/older inline-prompt stratum (493 agents) for
  pre-2026-06-03 digitization narration.]`
- **Confound — recitation ≠ behaviour change.** Every post-fix agent quotes "the eye outranks the
  tool" because it is in the prompt; the genuine catch (the shipping-overlay quote) shows it sometimes
  *operates*, but the catalog cannot tell how often the adversarial check is real vs ritual.
- **Detector bias:** the only detector here is the human, so E3 measures human visual attention as much
  as agent behaviour.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | Human spots off-axis / apex-spike / crossing-wiggle artifacts at a glance; "Aren't the agents doing VLM?" | memory `vlm-eye-is-arbiter-over-tools` |
| 2026-06-03 | Adversarial-overlay + eye-outranks-tool + audit-the-shipping-overlay encoded in `digitize-figure` step 5 / `audit-digitization` step 1 | skill change; post-fix narration in `wf_af0bce49` |
| 2026-06-03+ | Post-fix digitizers/auditors run the adversarial check; an auditor catches a render/data width mismatch on the shipping overlay | `wf_af0bce49-722/agent-aa668617dbe453a3c.jsonl` |

---

## Evidence layer (for verification, not reading)

- **Smoking gun (behaviour):** the user's 2026-06-03 framing (memory `vlm-eye-is-arbiter-over-tools`)
  — the artifacts were caught by eye, not by the agents' overlay step.
- **Smoking gun (fix operating):** `…/wf_af0bce49-722/agent-aa668617dbe453a3c.jsonl` — the eye
  overrides the tool on the shipping overlay (red curve too narrow vs the paper's bell).
- **Slice:** the 2026-06-03 RH2009 digitize/audit workflow `wf_af0bce49` (10 digitize + 10
  audit-digitization agents, session 3b2b7a60). Post-fix; not a rate.
- **Quote ledger:** `../evidence/E3.quotes.jsonl` — 2 quotes, verified verbatim by
  `verify_quotes.py E3` (2/2, exit 0). The behaviour's original smoking gun is the human framing in the
  memory, which is **not** in the verifiable narration stream.
- **Refs:** memory `vlm-eye-is-arbiter-over-tools`, `faithfulness-critics-want-to-find-issues`,
  `rendered-output-panels-are-reproduction-targets`, `capture-discovered-knowledge-in-artifacts`.

## Links

- `shared-root → E1a` — confirmation-framing of an evaluation step → leniency; E1a is the verbal
  acquittal, E3 is the visual one (eye blesses tool).
- `connects-to → E1b` — both are *perceptual* misses on a curve; E1b is the auditor's global-shape
  blind spot, E3 is the tool-trust blind spot at the hard-to-scan regions.
- `inverse-of (intended) → P#` — the eye overriding the tool (the shipping-overlay catch) is the
  positive baseline this fix is trying to make routine.

## Deeper-dig hook

Sample the `unknown` (older inline-prompt) stratum and any pre-2026-06-03 digitization narration for
the raw rubber-stamp ("it tracks well" → ship) to establish that the behaviour existed in agent
narration before the fix, and to find whether the adversarial check is genuinely applied vs recited
post-fix. Data: `evidence/manifest.jsonl` (role `unknown`), `logs/` digitization overlays.

## Status

`mitigated` — adversarial-overlay framing + "the eye outranks the tool" + "audit the shipping overlay"
encoded into the digitize/audit skills; post-fix narration shows the eye catching at least one
tool/render mismatch. Residual-rate uncharacterised; detector is human-only.
