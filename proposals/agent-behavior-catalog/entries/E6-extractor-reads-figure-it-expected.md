# E6 — The extractor read the figure it expected, not the one in front of it

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior |
> | Behavior | theory-driven perception / confirmation bias: the curve's shape is inferred from the model's equation (a formula that peaks at c=0 ⇒ "interior-peak hump") instead of being read off the plotted pixels, so a monotonic curve is reported as an inverted-U |
> | Symptom | all three independent extract-figure agents described the Panel-A modulation curve as an inverted-U peaked at intermediate contrast when, within the plotted x-range, it is monotonically decreasing |
> | Agent role | extract-figure (Phase-A figure describer) |
> | Trigger | a curve whose generating formula has an interior extremum, but whose plotted x-axis starts at a nonzero contrast so only one flank is visible; "contrast gain ⇒ interior peak / response gain ⇒ monotone" is a strong learned mechanism prior |
> | Cause (evidence) | shape inferred from the model equation rather than the leftmost visible data point — *intervention-tracked via the fix commit + agent-stated in the post-fix narration* |
> | Detector | human (cross-agent agreement was the tell: 3/3 made the same error) → skill rule c112359 |
> | Lever(s) | prompt/spec (extract-figure rule: "do not infer curve shape from model equations; look at the leftmost visible point and observe direction") |
> | Flags | ⟳ — the interior-peak-vs-monotone disagreement persists across independent post-fix agents (residual, [to-verify]) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` (model-version confound ruled out) |

## The behaviour

The `extract-figure` agent's job is the first, load-bearing read of a paper figure: describe what is
actually plotted so everything downstream (digitize, implement, audit) inherits a faithful target.
E6 is the failure where that read is contaminated by what the agent *knows the model should do*. A
contrast-modulation curve whose generating formula peaks at zero contrast can, when the plotted
x-axis starts at a nonzero contrast, appear **monotonically decreasing across the entire visible
range** — only the right-hand flank of the theoretical peak is in frame. Three independent extract
agents, reasoning from the equation rather than the pixels, all reported it as an inverted-U with an
interior maximum at intermediate contrast.

The original incident is recorded in the fix itself (commit `c112359`, "do not infer curve shape
from model equations"): *"all 3 independent agents described the Panel A modulation curve as
inverted-U peaked at intermediate contrast when it is monotonically decreasing within the plotted
range."* That 3-of-3 agreement is the diagnostic signature — this is not a random slip but a *shared
prior* pulling every agent the same wrong way. The prior is specific and legible: in this corner of
the literature, **contrast gain shows up as an interior-peak difference curve and response gain as a
monotone-rising one**, so an agent that has decided which mechanism is in play can "see" the matching
shape.

## Why it did it

**Cause (intervention-tracked + agent-stated): the shape was deduced from the mechanism, not
measured from the leftmost visible point.** The fix commit names exactly this — "A curve whose
formula peaks at c=0 may appear monotonically decreasing throughout the plotted range if the x-axis
starts at a nonzero contrast. Look at the leftmost visible point and observe direction — do not
assume an interior peak." The graded evidence is the intervention: the rule was added precisely
because all three agents made the equation-driven error, and the post-fix narration (below) shows
agents now performing the leftmost-point check the rule prescribes. It remains an *association*, not
an isolated experiment: the original three transcripts predate the durable corpus snapshot (the fix
is dated 2026-05-11; the snapshot begins 2026-06-02), so the smoking gun for the *failure* lives in
the commit message, and the corpus carries the *response*.

The deeper pattern: for a describer with a strong generative model of the system, **the expected
shape is the lower-friction read** than a pixel-by-pixel trace. The agent has a reason for the curve
to look a certain way, and absent a hard rule forcing it to the visible data, it supplies the
theory-consistent description. This is the extractor-side analogue of E1b (a perceptual gap) but with
a different driver: E1b is the eye missing a *local* defect in a curve it traced; E6 is the eye
*overwriting* the global shape with a prediction.

## How the behaviour responded to the intervention

In the post-fix corpus (six pestilli_ling_carrasco_2009 extract agents, 2026-06-06), agents now
reason explicitly about the contrast-gain-vs-response-gain distinction and, crucially, **negate the
equation-default reading against the pixels**:

> *"…difference rises monotonically with contrast, highest at high contrast"* — and, on the same
> curve, the explicit denial of the inverted-U default: the difference *"monotonically increases with
> contrast, largest at the highest contrast."*
> *"neither is a mid-contrast hump (a mid-contrast hump would indicate contrast gain, not response
> gain)"* — the agent now states the mechanism⇄shape mapping *as a thing to check*, not assume.

This is the rule landing: the agent verbalizes the very check the fix installed (which way does the
curve actually go, vs which way the mechanism would predict).

## The part E6 doesn't resolve — a residual disagreement (⟳)

The intervention did not make the read deterministic. On the same paper, independent post-fix agents
still split on whether a difference curve is an interior-peak hump (contrast gain) or a monotone rise
(response gain):

> *"It is a unimodal hump with a strict INTERIOR maximum at intermediate contrast"* … *"The (c) hump
> must have an interior peak, not a monotone curve."* — agent a3739b26
> *"Row 1 = single interior HUMP peaked at intermediate contrast"* — agent a4ee50
> vs *"difference rises monotonically with contrast … (NOT a mid-contrast hump)"* — agent abc5ef4b

These agents were each assigned different figures/panels of the same multi-panel paper, so this is
**not** a clean A/B contradiction on one identical curve — the pestilli figures genuinely contain
both shapes across panels, and adjudicating who is right needs the figure in hand. But the residual
is real and worth flagging: the *same* model-driven shape category (interior-peak vs monotone) is
still the axis along which independent extractors diverge, which is exactly the dimension the original
failure ran on. Whether any of the post-fix interior-peak reads is itself an equation-inferred error
is a `[to-verify-on-deeper-dig]` (overlay each agent's claim on its assigned panel).

## How confident I am, and what could be wrong

Moderate. The *failure* is documented in the fix commit (3/3 agents) but its transcripts are
pre-snapshot, so I cannot re-read them — the corpus gives the post-fix behaviour, not the original
error. The *response* is well-grounded (verbatim negations of the inverted-U default). Threats:

- **The original three transcripts are not in the corpus** — the 3/3 rate is the commit author's
  count, not one I re-verified against logs (it predates the snapshot).
- **Different panels, not one curve** — the residual disagreement is across agents working different
  figures; it is suggestive of a persisting model-driven read, not proof of a repeated error.
- **One paper** — both the failure and the response are pestilli/carrasco contrast-modulation
  figures; generality to other figure types is untested here.
- **Model-version ruled out:** all post-fix extract agents ran `claude-opus-4-8` (manifest constant).

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-05-11 | 3/3 extract agents call a monotone modulation curve an inverted-U; skill rule added | commit `c112359` (extract-figure SKILL: "do not infer curve shape from model equations") |
| 2026-06-06 | Post-fix extract agents verbalize the leftmost-point check; explicitly negate the inverted-U default | `wf_19edde3c` (6 pestilli extract-figure agents) |
| 2026-06-06 | Residual: independent agents still split interior-peak vs monotone across panels | same workflow (a3739b26 / a4ee50 vs abc5ef4b) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun (the failure):** commit `c112359` message — "all 3 independent agents described the
  Panel A modulation curve as inverted-U peaked at intermediate contrast when it is monotonically
  decreasing within the plotted range." (Transcripts predate the corpus snapshot.)
- **Corpus slice (the response + residual):** 6 `extract-figure` agents on
  pestilli_ling_carrasco_2009 in `wf_19edde3c-0d3` (2026-06-06), under
  `e8552c97-.../subagents/workflows/`. Counts are descriptive (one workflow); not a rate.
- **Quote ledger:** `../evidence/E6.quotes.jsonl` — 7 quotes, verified verbatim by
  `verify_quotes.py E6` (7/7, exit 0).
- **Refs:** commit `c112359` (`skills/extract-figure/SKILL.md`).

## Links

- `connects-to → E1b` — both are figure-perception gaps; E1b is the auditor's eye missing a *local*
  defect in a curve it traced, E6 is the extractor's eye *overwriting* the *global* shape with the
  model's prediction (theory-driven vs detail-blind).
- `connects-to → E7` — both are extraction-fidelity failures where a downstream "shape" judgement
  rides on an under-checked read (E7 = right shape, wrong scale; E6 = wrong shape).

## Deeper-dig hook

Recover the three pre-snapshot extract transcripts (if archived) to read the original equation-driven
rationale directly. Then overlay each post-fix interior-peak claim (a3739b26, a4ee50) on its assigned
pestilli panel to test whether the residual disagreement is a persisting equation-inferred error or a
genuine multi-panel difference. Data: `models/pestilli_ling_carrasco_2009/` figure artifacts.

## Status

`mitigated` — the extract-figure skill now forces a leftmost-visible-point direction check and
agents verbalize it; a residual model-driven interior-peak-vs-monotone disagreement persists across
panels (uncharacterised).
