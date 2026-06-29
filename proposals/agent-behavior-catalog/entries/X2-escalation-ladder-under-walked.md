# X2 — The escalation ladder gets skipped: self-resolvable items default to "human"

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Escalation · agent-behavior |
> | Behavior | premature escalation: routing an item to a human without first walking the resolution ladder (paper → code → corpus → references) |
> | Symptom | 58% of human-routed items (75 / 130, 38 models) were orchestrator-resolvable; soft "human" tags proliferate without a recorded resolution attempt |
> | Agent role | orchestrator / resolver (+ the spec/process auditors that surface the residue) |
> | Trigger | an open issue is not trivially auto-closeable, and there is no controlled vocabulary or forced rung-walk distinguishing "needs a human" from "I didn't try" |
> | Cause (evidence) | vocabulary collapse (many soft strings → "a person must do it") + no forcing ladder — *survey-tracked + intervention-tracked* |
> | Detector | cold cross-corpus survey (38 models) + peer agent (spec-audit catching settled items left `open_for_human`) |
> | Lever(s) | prompt/spec (R1–R6 ladder + typed H-reasons) + doc (controlled `resolution_attempt` / `human_reason` fields) |
> | Flags | ↔ inverse-of X1 (same dial) |
> | Status | mitigated (ladder specified) · `claude_model` constant `claude-opus-4-8` (confound ruled out) |

## The behaviour

X2 is the **systemic / rate** reading of the escalation dial: across the corpus, agents stopped short
of resolving issues they had the materials to resolve, and tagged them for a human instead. Where X1
is a handful of vivid incidents, X2 is the population fact behind them.

A cross-corpus survey on 2026-06-29 classified every open item in every model's `issues.yaml`,
`assumptions.yaml`, and `spec_questions.yaml` into "orchestrator-resolvable (A)" vs "genuinely-human (B)"
(`proposals/process-faithfulness-gaps-2026-06-29.md`, Finding 2):

- **130 human-routed items total; 75 (58%) were class A** — the paper, the released code, the corpus, or
  one citation hop resolved them without any person.
- Over-routing clustered on five recurring kinds: (1) authors' released code already answers it (denison
  entirely; bogacz SQ-003); (2) the paper's own *figure* beats its rough *prose* (ratcliff "4:1" vs the
  fitted ~11:1 panel; pestilli caption vs its own legend); (3) pure bookkeeping (stale doc lines,
  duplicate IDs, ledger flips — heeger, lee, vicente); (4) ratify/re-run-a-stale-audit (rozell, cagly,
  bienenstock); (5) standard citation-grounded conventions (ratcliff s=0.1 scale-invariance).

The narration shows the micro-mechanism. In boynton, the spec-auditor found an item parked for a human
whose disposition text *already answered itself*:

> *"…the resolution text already settles it as optional"* — boynton spec-audit (Q-010, left `open_for_human`)

And the corrective, when applied, looks like an agent refusing the default — choosing to walk the ladder
rather than punt:

> *"…pushing toward applying a paper-grounded fix rather than punting to [\"human DECISION\"]"* — bienenstock process-audit
> *"Do NOT call a code-settled question human"* — audit-spec skill rule (in-prompt, applied)

## Why it did it

**1. Vocabulary collapse — no controlled term for "not auto-closeable" (survey-tracked).** Items carried
`owner: human`, `human_resolution: pending`, `open_for_human`, "must be ratified by a faithfulness
auditor with the paper" — all different strings, all collapsing into "a person must do it." Only 2 of
130 items used an explicit `owner: human`; the rest were soft, ambiguous prose. With no vocabulary
separating "I tried the paper/code/corpus and they fail" from "I didn't try," the cheap default is to
mark it human-needed. This is the strongest-evidence cause: it is a counted property of the artifacts.

**2. No forcing rung-walk (intervention-tracked, by the shape of the fix).** Before the R1–R6 ladder,
nothing *required* an agent to record which resolution rung it had attempted. The fix is precisely a
forcing function — walk R1 (released author code) → R2 (paper text/figure, *figure beats prose*) → R3
(citation-grounded convention) → R4 (mechanical) → R5 (corpus papers) → R6 (one-hop references), record
the rung that resolved it, and reach HUMAN only with a typed reason (H1 irreducible / H2 cross-model
shared convention / H3 genuine underdetermination / H4 scope-or-values call). That the cure is "make the
attempt mandatory and named" is the evidence the disease was "the attempt was optional and unnamed."

The deeper pattern (shared with X1): **escalation to a human is the lowest-friction terminal state** —
it is never *wrong* to ask a person — so absent a discipline that prices the un-walked rungs, agents
drift to it.

## How the behaviour responded to intervention

- **PR #14 (2026-06-03, prompt) — partial.** The audit skills already carried the "last resort"
  escalation rule and the cap-artifact warning, and auditors *did* use it to catch settled-but-parked
  items (the boynton Q-010 and bienenstock φ catches above). But the rule lived only on the **auditing**
  side; the **upstream** issue/README authoring kept generating soft human tags, so the population-level
  over-routing persisted to the 06-29 survey.
- **R1–R6 ladder (2026-06-29, prompt/spec + doc) — specified, not yet measured.** The fix adds the
  forced rung-walk, the typed H-reasons, and two controlled fields (`resolution_attempt`, `human_reason`)
  replacing the soft prose, plus a guardrail set (asymmetric authority; human items deferred not
  pre-resolved). Status is **mitigated/specified**: the 58% was measured *before* the ladder; the
  post-ladder rate is `[to-verify-on-deeper-dig]`.

## The X1 ↔ X2 relationship — one dial, two readings (first-class finding)

X1 and X2 describe the **same directional failure — over-routing to a human** — and the catalog pairs
them as "inverse / same dial" for two reasons:

- **Same dial, different zoom.** Escalation propensity is one control variable. X2 is it set too high
  read as a **rate** (58% across 38 models, with a measured vocabulary-collapse mechanism); X1 is the
  same setting read as **incidents** (specific findings routed to a human, plus the auditor penalising a
  rung-1 self-resolution). They are split into two threads, per the catalog's keying rule, because their
  **causes differ**: X1's incidents are driven by a *sticky human-routing label* and a "*closing a
  human-tagged item = drift*" heuristic; X2's rate is driven by *vocabulary collapse + no forcing
  rung-walk*. Same symptom direction, different mechanism → two threads.
- **The genuine inverse is the fix's risk.** Turning the dial down — the very R1–R6 ladder that fixes X2
  — over-applied yields **under-routing**: resolving unilaterally what truly needs a human. The ladder
  encodes its own brakes against this overshoot: **H2** (cross-model shared conventions — divisive-norm
  saturation, φ-boundedness — must *not* be resolved unilaterally; see S2) and **asymmetric authority**
  (R1 code resolves what the paper is *silent* on but may *never* override what the paper's figure/text
  positively shows — the forbidden ADJ-001 move where a numpy port refuted a printed panel). So "harden
  over-routing" and "guard against under-routing" are the two stops on one dial — which is exactly why
  the index calls X1↔X2 an inverse pair rather than two unrelated behaviours.

## How confident I am, and what could be wrong

The **58% rate is strong** — it is a deliberate full classification of all 130 human-routed items across
38 models, not a keyword sample. The narration excerpts are illustrative of the mechanism, not the
source of the rate. Threats:

- **Classifier is a single judgment pass.** "Class A vs class B" was decided by the surveying agent/lead;
  a second independent classification could move the boundary (some H4 scope-calls are genuinely
  contestable). The denominator (130) is solid; the 58% split has reviewer-dependence
  `[to-verify-on-deeper-dig: blind re-classify a sample]`.
- **Pre/post not yet measured.** The ladder was specified after the survey; "mitigated" reflects the
  specified fix, not a re-measured rate. No claim that over-routing *fell*.
- **X1 vs X2 boundary.** The same incidents (boynton, bienenstock) appear in both threads; the split is
  on cause, not on disjoint evidence. Read the 58% as X2's; read the drift-flag and sticky-label as X1's.
- **Single survey window / one corpus**; `claude_model` constant (`claude-opus-4-8`) so a model-version
  change is ruled out.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | Audit skill: paper→lineage→human "last resort" rule (auditing side only) | PR #14 (`b7d6fff`) |
| 2026-06-15 | Concrete micro-instances: boynton Q-010 settled-but-`open_for_human`; bienenstock φ "DECISION (human)" | session `a651000f` |
| 2026-06-29 | Cross-corpus survey: 75/130 (58%) human-routed items were orchestrator-resolvable | `proposals/process-faithfulness-gaps-2026-06-29.md` (Finding 2) |
| 2026-06-29 | Fix specified: R1–R6 ladder + typed H-reasons + `resolution_attempt`/`human_reason` fields | same proposal; memory `resolution-authority-ladder` |

---

## Evidence layer (for verification, not reading)

- **Primary rate source (documentary):** `proposals/process-faithfulness-gaps-2026-06-29.md`, Finding 2 —
  full classification of 130 human-routed items across 38 models, 75 class A (58%). Distilled in memory
  `resolution-authority-ladder` (R1–R6, typed H1–H4, the 58% figure, the five over-routing clusters).
- **Narration corpus (mechanism, not rate):** session `a651000f-a156-41c6-b8cc-3db390b5524f` —
  boynton spec-audit (`wf_5abd222b-313/agent-ad7696f85a677b32c`, the Q-010 settled-but-parked instance),
  bienenstock spec-audit (`wf_b4c958b9-2de/agent-a0c55f5cd85c1d7f1`, the in-prompt rule) and
  bienenstock process-audit (`…/agent-a74375a95a6cec53d`, "punting to human DECISION" framed as the
  thing the corrective refuses). Read narrowly (grep-then-excerpt).
- **Smoking gun:** the 58% classification (75/130) — a counted, not anecdotal, over-routing rate.
- **Quote ledger:** `../evidence/X2.quotes.jsonl` — 3 quotes, all verified verbatim by
  `verify_quotes.py X2` (3/3, exit 0).
- **Confidence & threats:** rate strong (full classification); split is single-pass; pre/post unmeasured;
  shares incidents with X1 (split on cause). See "How confident I am" above.
- **Refs:** memory `resolution-authority-ladder`, `paper-resolvable-findings-arent-human-routed`,
  `saturation-is-the-genealogy-blocker` · proposal `process-faithfulness-gaps-2026-06-29` (Findings 1–3) ·
  PR #14.

## Links

- `inverse-of` **X1** — same escalation dial; X2 = rate view, X1 = incident view (different causes).
- `connects-to` **S2** (one shared decision resolved N×) — the under-routing failure the ladder's H2
  guardrail protects against; the dial's opposite stop.
- `connects-to` **E2 / E5** — "lowest-friction terminal state" pattern (grade-own-homework / self-certify
  / defer-to-human are all the cheap exit).
- `shared-root` with X1 and the resolution-authority ladder (`process-faithfulness-gaps-2026-06-29`).

## Deeper-dig hook

(1) Blind re-classify a random sample of the 130 items to put an error bar on the 58%. (2) After the
R1–R6 ladder lands in the authoring (not just auditing) phase, recount human-routed-but-class-A items to
measure whether the rate falls — the pre/post the survey could not do. Data lives in each model's
`issues.yaml` / `assumptions.yaml` / `spec_questions.yaml`; the survey method is in
`process-faithfulness-gaps-2026-06-29.md`.

## Status

`mitigated` — the 58% over-routing rate was measured and the R1–R6 ladder + controlled vocabulary
specified to fix it; the post-ladder rate is unmeasured and the inverse under-routing hazard (S2/H2)
stays open.
