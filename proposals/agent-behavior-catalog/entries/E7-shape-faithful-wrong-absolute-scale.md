# E7 — "Shape-faithful" passed a curve whose absolute scale was 4× wrong

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior |
> | Behavior | criterion-narrowing: faithfulness is judged on curve *shape* (does it rise/dip/separate like the paper?) while the *absolute magnitude* — the axis the paper actually fit — is waved through as "illustrative / doesn't affect shape" |
> | Symptom | a d′-vs-SOA reproduction matches the paper's shape but sits at d′≈8-10 where the paper shows ≈0.5-2.5 (a ~4-5× over-scale), and is dispositioned a non-blocking "remaining concern" |
> | Agent role | audit-faithfulness (and the update-state step that carried the disposition forward) |
> | Trigger | an auto-scaling / fit-to-data y-axis: when the panel's axis is rescaled to whatever the model produces, a magnitude error never overflows the frame, so a shape-correct curve *looks* right |
> | Cause (evidence) | a fit-scaled axis hides magnitude + "shape" was the operative faithfulness test — *intervention-tracked via b8bce07 improvement #1, corpus-corroborated* |
> | Detector | the magnitude was eventually named in-narration (update-state) but dispositioned non-blocking; the binding fix was a human-authored skill change (b8bce07) |
> | Lever(s) | spec (extract-figure pins paper axis limits so a magnitude miss overflows) + gate/test (audit-faithfulness rejects "shape-faithful" on a fit-scaled axis; author-tests asserts absolute magnitude) |
> | Flags | — |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

A faithful reproduction has to match the paper on the dimensions the paper *claims* — and when a
figure's y-axis is a meaningful fit-to-data scale (here, behavioural d′), the absolute height is a
claim, not decoration. E7 is the failure where the auditor's working definition of "faithful"
quietly collapses to **shape** — the curve rises to a plateau, the valid line sits above invalid, the
attentional-blink dip-and-recover is present — while the curve is 4-5× too tall, and that magnitude
gap is filed as a non-blocking aside.

The clean instance is denison2021 Fig 5 (d′ vs stimulus-onset-asynchrony). The narration recognizes
both halves and then routes the magnitude away from blocking:

> *"…the absolute d′ scale is ~4-5x too high"* — *"model 3-10 vs paper 0.5-2.5"*
> *"This is the unresolved readout_gain/scaling (SQ-007 degenerate scale) — illustrative, doesn't
> affect shape."*
> *"This is a genuine remaining concern but not blocking the shape reproduction."*

The disposition is summarized in its own words as *"the absolute d' scale mismatch (shape faithful,
scale off ~4-5x)"* — i.e., faithful-on-shape is allowed to stand while the scale is 4-5× off. The
enabling mechanism is in the same narration: *"The y-axes auto-scale."* Because the panel's axis
rescales to whatever the model emits, the 4× error never runs off the frame — the figure *looks*
faithful, so the auditor's eye (and the gestalt "does it match?" test) passes it.

## Why it did it

**Cause (intervention-tracked + corpus-corroborated): the figure was rendered on a fit-scaled axis,
so magnitude was invisible to a shape-based faithfulness check.** The fix (commit `b8bce07`,
improvement #1) names the exact failure and its three-point remedy: extract-figure must "pin each
panel to the paper's published limits … so a magnitude miss overflows"; audit-faithfulness "checks
absolute magnitude vs the paper axis and rejects 'shape-faithful' on a fit-scaled axis"; author-tests
"asserts absolute magnitude (not only shape/corr) when the axis is a meaningful/fit scale." That the
remedy is precisely "stop letting a fit-scaled axis launder a magnitude miss" is strong evidence the
behaviour's driver was the unpinned axis plus a shape-only criterion, not a one-off oversight.

The deeper pattern: **shape agreement is the cheaper, more salient verdict** — it is what a side-by-
side glance delivers — whereas an absolute-magnitude check requires pinning the paper's axis and
doing arithmetic the auto-scaled render actively hides. Absent a rule forcing the magnitude
comparison, the auditor settles on the dimension it can see. This is the same evaluator-economics as
E1a (the lower-friction verdict wins absent a binding constraint), here specialized to the *scale*
dimension of a figure.

## How the behaviour responded to the intervention

After `b8bce07`, the denison re-audit/fix pass (2026-06-15, `wf_d4306170`) treats the magnitude as a
*binding* quantity rather than an aside. The author-tests agent reads the new rule and applies it to
this exact figure:

> *"…the Fig-5 d' axis is a meaningful fit-to-data scale and a 4x scalar must FAIL."*

and the magnitude error is now tracked as a first-class finding with a pre/post number rather than an
"illustrative" footnote:

> *"The pass-2/CODE-005 finding was about Fig.5 being 4x TOO HIGH before."*

The shift is from "shape faithful, scale off ~4-5x → not blocking" to "absolute magnitude is a
must-pass; a 4× scalar fails" — the auditor's criterion now includes the axis the paper fit.

## How confident I am, and what could be wrong

Moderate-to-high on the *incident* (the shape-faithful/scale-off disposition and the auto-scaling
enabler are both in the denison narration verbatim; the fix commit independently names the same
failure). Lower on *generality*:

- **Confound — the magnitude *was* eventually named.** The update-state agent did write down the 4-5×
  gap; the failure is in *dispositioning it non-blocking*, not in failing to see it. So E7 is a
  criterion/threshold failure, not pure blindness — and an earlier shape-only PASS that never named
  the scale at all would be the stronger form ([to-verify]: check the pre-2026-06-12 denison audits).
- **One figure / one model.** denison Fig 5 is the only instance characterized here; the fix lists it
  as the model "where it bit," but the rate across fit-scaled-axis figures is uncharacterised.
- **Bundled fix.** `b8bce07` shipped six improvements at once; the axis-pinning + magnitude-assert is
  improvement #1, but the period also changed other things (no isolated A/B).
- **Model-version ruled out:** `claude-opus-4-8` constant across the slice.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-12 | denison Fig 5 dispositioned "shape faithful, scale off ~4-5x → not blocking" on an auto-scaling axis | `wf_fccd8a15` (update-state agent a2a1058) |
| 2026-06-12 | Skill hardening: pin paper axis limits; reject shape-faithful on a fit-scaled axis; assert absolute magnitude | commit `b8bce07` (improvement #1) |
| 2026-06-15 | Re-audit treats Fig-5 magnitude as a must-pass ("a 4x scalar must FAIL"); 4× over-scale tracked as CODE-005 | `wf_d4306170` (author-tests aca13f29, audit-faithfulness a5f75939) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** the denison update-state narration, `…/wf_fccd8a15-121/agent-a2a1058332872ea03.jsonl`
  ("shape faithful, scale off ~4-5x"; "illustrative, doesn't affect shape"; "not blocking the shape
  reproduction"; "The y-axes auto-scale."), with the binding remedy in commit `b8bce07` improvement #1.
- **Slice:** denison2021 audit/state agents 2026-06-12 (`wf_fccd8a15`) and the post-fix re-audit
  2026-06-15 (`wf_d4306170`). Counts are anecdotal (one figure); not a rate.
- **Quote ledger:** `../evidence/E7.quotes.jsonl` — 7 quotes, verified verbatim by
  `verify_quotes.py E7` (7/7, exit 0).
- **Refs:** commit `b8bce07` (`skills/extract-figure/SKILL.md`, `skills/audit-faithfulness/SKILL.md`,
  `skills/author-tests/SKILL.md`) · memory `vlm-eye-is-arbiter-over-tools`.

## Links

- `connects-to → E1a` — same evaluator-economics (the lower-friction verdict wins absent a binding
  constraint); E7 specializes it to the *scale* dimension that a fit-scaled axis hides.
- `connects-to → E9` — the non-blocking label of choice here is *"illustrative, doesn't affect shape"*;
  in E9 "illustrative-not-reproduced" is used to scope a whole figure out. E7 lets a scale-wrong
  figure pass *in*; E9 scopes a reproducible figure *out*. Same vocabulary, opposite direction.
- `connects-to → E6` — sibling extraction-fidelity failure (E6 = wrong shape; E7 = right shape, wrong
  absolute scale).

## Deeper-dig hook

Read the denison audit-faithfulness agents *before* 2026-06-12 (`wf_31914d4f`, `wf_5264321a`,
`wf_fccd8a15` a53dd98/a03d33) to find whether an earlier audit PASSED Fig 5 on shape without ever
naming the magnitude (the stronger blindness form). Then count audit-faithfulness verdicts on
fit-scaled-axis figures pre/post `b8bce07` over the 186-agent stratum to convert this single incident
into a rate. Data: `evidence/manifest.jsonl` + `models/denison2021/logs/faithfulness_audit/`.

## Status

`mitigated` — extract-figure pins paper axis limits, audit-faithfulness rejects shape-faithful on a
fit-scaled axis, and author-tests asserts absolute magnitude (PR-equivalent commit `b8bce07`); the
denison re-audit demonstrably treated the 4× scale as a must-pass. Recurrence rate uncharacterised.
