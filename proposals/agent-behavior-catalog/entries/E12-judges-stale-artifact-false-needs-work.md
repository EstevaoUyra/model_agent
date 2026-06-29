# E12 — The evaluator scored an out-of-date picture and flagged an already-correct model

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior (tool-adjacent) |
> | Behavior | an evaluator judges a *stale artifact* (a committed render that no longer reflects the committed model) and issues a NEEDS-WORK verdict against a model that is already correct |
> | Symptom | a figure flagged "wrong / not faithful" when the model code, freshly run, produces the right figure — the shipped PNG simply predates the last fix; in the worst case it burns a whole fix cycle on a model that needed no change |
> | Agent role | faithfulness/VLM evaluator; figure resolver; audit-digitization |
> | Trigger | the evaluator reads a *committed view* (PNG/overlay in `figures_reproduced/` or the README) instead of regenerating it from the committed model immediately before judging; the model advanced but the artifact was never re-rendered |
> | Cause (evidence) | view ≠ source: the scored artifact is not derived from the thing under test → *intervention-tracked* (the fix is "regenerate deterministically before reading") |
> | Detector | human post-mortem (organizer; wave-1 retro across spratling/bell); also caught in-corpus by a resolver agent that re-rendered and found the model correct |
> | Lever(s) | gate/structural ("the measurement record / a fresh deterministic re-render is the source of truth — never judge a possibly-stale render") |
> | Flags | ⟳ recurred (spratling fig5, then bell fig4) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

An evaluator's job is to compare the *reproduced figure* to the paper. But the figure it
actually looked at was sometimes a **committed PNG that no longer matched the committed model** —
the implementer fixed the model, but the picture in `figures_reproduced/` (or the README) was
never regenerated. Scoring that stale picture, the evaluator declared the figure wrong and sent
the model back for "more work" — even though the model, run fresh, already produced the correct
figure. In the worst documented case a stale PNG **"wasted a whole bell-fig4 fix cycle (the model
was already correct)."**

This is a verdict error with a definite *sign*: the stale render is an older, worse state of the
work, so judging it can only push toward **false NEEDS-WORK**, never toward a false pass. That
asymmetry is the load-bearing fact of this thread (see "Why it only goes one way").

## Why it did it

**Cause (intervention-tracked): the evaluator judged a *view* that was not derived from the
*source* under test.** The pipeline commits rendered artifacts (a human entry-point PNG, overlays)
alongside the model code. When a fix lands but the "regenerate before reading" step is skipped, the
artifact and the model diverge. An evaluator that reads the artifact at face value is no longer
testing the model — it is testing a snapshot of a past model. The fix that worked treats this
structurally: re-render every figure deterministically from the committed model *immediately
before* reading it, and treat the measurement record (not any committed picture or any builder's
claim that "the PNG is current") as the source of truth.

The in-corpus smoking gun is a resolver agent on the RH2009 model doing exactly the right thing and
thereby exposing the trap: it found the shipped figure was an old-axis plateau while the corrected
model produces a full sigmoid, and stated the artifacts **"were never regenerated after the fix":**

> *"The stale shipped figure_2.png (old axis) only shows the upper plateau region."*
> *"…the committed/shipped artifacts are STALE … they were never regenerated after the fix."*

An audit-digitization agent shows the defensive discipline operating — it refuses to trust the
committed overlay and re-renders first:

> *"re-rendered the overlay myself (matched the committed one, not stale)"*

That last quote is the intended end-state: confirm the artifact is current *before* spending a
verdict on it.

## Why it only goes one way (the asymmetry — and why E12 is a calibration anchor)

The organizer's final triage states the rule plainly: **"Stale figures cause only
false-needs-work, never false-green."** The reasoning: a stale artifact is a *prior* render of the
work. If that prior state had been acceptable it would already have shipped; once the model is
improved past it, the stale picture shows the older, worse output — so scoring it can only
*under*-credit the model. It cannot manufacture a pass.

This makes E12 the **inverse of E3** (and a near-mirror of E1): where E3 trusts a tool's output and
acquits a wrong figure (false GREEN), E12 distrusts a correct model because it read a non-current
view (false RED). Because the error has a known sign, it doubles as a *calibration anchor* for the
whole evaluation layer: when the deterministic metric is green but the VLM says red, the standing
diagnosis order becomes "re-render and re-check first — it's probably a view problem, not a model
problem," rather than re-opening the model.

## How the behaviour responded to the intervention

- **First seen (spratling fig5):** the impl/fix agents' "regenerate before VLM" step proved
  unreliable; the VLM scored an out-of-date render. Guideline added: the VLM step regenerates every
  figure from the committed model immediately before reading it.
- **Recurred (bell fig4):** the same class returned and cost a full fix cycle on a model that was
  already correct — so the lesson was **strengthened**: don't trust an agent's "I regenerated"
  claim; the verifier/organizer must render deterministically, and a det-green / VLM-red split means
  "re-render and re-check first."
- **Post-fix (RH2009 resolver, in-corpus):** the resolver and audit-digitization agents now
  *check for staleness as a first move* — re-rendering from committed code and comparing — which is
  how the RH2009 stale-figure trap was caught rather than acted on.

Note (anecdote ≠ rate): "recurred" is grounded in two named incidents (spratling fig5, bell fig4)
from the organizer's retro; this is "happened ≥ twice," not a measured frequency. No
denominator over the evaluator population is computed here `[to-verify-on-deeper-dig]`.

## How confident I am, and what could be wrong

Moderate on the behaviour and its sign; weak on rate.

- **The raw false-NEEDS-WORK incidents (spratling, bell) live in the organizer's retro, not in
  role-tagged workflow narration.** What the corpus verifiably contains is the *fix operating*: a
  resolver naming a shipped figure as stale-vs-corrected-model, and an auditor re-rendering before
  judging. So I can quote the mechanism and the defensive discipline, but not a verbatim
  "I score this stale figure as NEEDS-WORK" from the originating evaluator.
- **The asymmetry claim ("only false-needs-work, never false-green") is the organizer's stated
  rule, not an independently measured property.** It is mechanistically plausible (a stale render is
  a strictly older state) but rests on the project's own logic, not a counted population. There is a
  *competing note* elsewhere in the corpus (a skill-doc line read by an agent) that "stale renders
  produced false verdicts in both directions"; that line is documentation the agent read, not a
  counted observation, and it concerns a broader notion of staleness (e.g. stale *tests/baselines*,
  not stale *output renders*). The output-render asymmetry is the one the retros assert.
- **Detector bias:** the original detector is the human organizer, so E12 partly measures human
  attention; the in-corpus catches are post-fix and show recitation-plus-application of the
  re-render discipline.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-02 | VLM scores a STALE render (spratling fig5); model actually produced the turnover → guideline: regenerate from committed model before reading | `wave-retros.md` l.96-100 |
| 2026-06-02 | Asymmetry recorded: stale figures cause only false-needs-work, never false-green | `final-triage-2026-06-02.md` l.108-110 |
| 2026-06-02 | Recurred (bell fig4): a stale PNG wasted a whole fix cycle on an already-correct model → lesson strengthened (deterministic re-render, don't trust agent's claim) | `wave-retros.md` l.150-156; commits 617bdaa, fb14bc3 |
| 2026-06-04+ | Post-fix: RH2009 resolver finds shipped figures stale vs corrected model; auditor re-renders before judging | `e8552c97…/wf_246026d2-440`, `…/wf_1dbdd4b1-ef4` |

---

## Evidence layer (for verification, not reading)

- **Smoking gun (behaviour + asymmetry):** organizer retro — `wave-retros.md` l.96-100 / l.150-156
  ("a stale PNG wasted a whole bell-fig4 fix cycle (the model was already correct)") and
  `final-triage-2026-06-02.md` l.108-110 ("Stale figures cause only false-needs-work, never
  false-green"). These are proposal-grounded; the originating evaluator verdict is **not** in the
  role-tagged narration stream.
- **Smoking gun (fix operating, in-corpus):** RH2009 resolver
  `e8552c97…/wf_246026d2-440/agent-ada4fd3bce40fd99d.jsonl` (shipped figure stale vs corrected
  model, "never regenerated after the fix") and audit-digitization
  `e8552c97…/wf_1dbdd4b1-ef4/agent-a43922d74e8dda8e1.jsonl` (re-rendered before trusting).
- **Quote ledger:** `../evidence/E12.quotes.jsonl` — 3 quotes, verify with
  `python3 ../evidence/verify_quotes.py E12` (exit 0). The originating false-NEEDS-WORK incidents
  (spratling/bell) are proposal/retro-grounded only — stated here per the catalog's honesty rule.
- **Refs:** proposals `wave-retros.md`, `final-triage-2026-06-02.md`; commits 617bdaa, fb14bc3.

## Links

- `inverse-of → E3` — **the central edge.** E3 uses the eye to *bless* a tool's output and acquits
  a wrong figure (false GREEN); E12 *distrusts* a correct model because it scored a non-current view
  (false RED). Same evaluation step, opposite sign of error.
- `connects-to → E1` — E1 is the other "wrong verdict" thread; E1a/E1b are false-pass (too lenient),
  E12 is false-fail (spuriously strict). Together they bracket the calibration of the verdict.
- `connects-to → T3` — T3 acts on a stale *tool-model* (a tooling snapshot / bad model-arg); E12
  scores a stale *output artifact*. Both are "the thing I'm acting on is out of date," different
  objects.

## Deeper-dig hook

Slice the `audit-faithfulness` + resolver narration for the RH2009/spratling/bell models and count
NEEDS-WORK verdicts that were later reversed by a re-render (false-RED rate), vs verdicts that held.
That would convert the asymmetry from a stated rule into a measured one. Data:
`evidence/manifest.jsonl` (roles `audit-faithfulness`, `update-state`), per-model figure-resolution
logs; grep `stale`, `regenerate`, `re-render` in text/thinking blocks only (file-reads of the
skill doc dominate a naive grep).

## Status

`mitigated` — deterministic "regenerate from the committed model before reading" + "measurement
record is the source of truth" encoded as the standing diagnosis order; post-fix agents check for
staleness as a first move. Residual false-RED rate uncharacterised; original detector is human.
