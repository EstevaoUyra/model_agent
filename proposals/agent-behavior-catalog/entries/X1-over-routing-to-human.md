# X1 — Findings get routed to a human when the paper already answers them

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Escalation · agent-behavior |
> | Behavior | over-deference: an item the paper's own ground truth resolves (ladder rung 1–2) is tagged "human-only," and a peer's rung-1 self-resolution is then penalised as illegitimate |
> | Symptom | `owner: human` / "DECISION (human, not agent)" / "needs a human ratify-or-route" on figure-resolvable findings; process-auditor flags a paper-grounded closure as **drift** |
> | Agent role | spec-auditor, process-auditor, README-gen (the artifacts they audit) |
> | Trigger | a finding carries a soft human-routing tag; the agent treats the tag as binding regardless of whether the value is on disk in the paper |
> | Cause (evidence) | sticky human-routing label + "closing a human-tagged item = drift" heuristic — *intervention-tracked + agent-stated* |
> | Detector | human post-mortem ("If it was solvable why would it need a human?") + peer agent (rule-8 cap-artifact catch) |
> | Lever(s) | prompt/spec (rule 8: "routed to human is usually a cap artifact", PR #14) + human-rule (rung-1 ratification) |
> | Flags | ⟳ recurred after the prompt fix · ↔ inverse-of X2 (same dial) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` (confound ruled out) |

## The behaviour

The escalation ladder reserves the human as a **last resort**: rung 1 (the paper's own figure/text)
and rung 2 (released author code / lineage) are meant to be resolved *without* a person. X1 is the
failure where an item that rung 1 settles is nonetheless parked for a human — and, in its sharper
form, where an agent that *did* resolve such an item from the paper is treated as having
misbehaved.

Two faces of the same over-deference showed up in one batch (boynton_2009 + bienenstock_cooper_munro,
2026-06-15, session `a651000f`):

1. **Routing a paper-resolvable finding to a human.** boynton's F-2 was a discriminator-threshold
   that sat above the paper's own digitised c=0 gap. The fix lowered it to 0.02, grounded directly in
   the paper's digitised panel; the spec-auditor independently confirmed the grounding:
   > *"The fix is paper-grounded: 0.02 < digitized 0.026 gap"* — boynton spec-audit
   Yet the prior critics had routed that very question to a person:
   > *"F-2 is a contract-vs-figure tension the faithfulness auditor should adjudicate"* — boynton process-audit
   The bienenstock README did the same with the φ-runaway root cause, parking it as
   > *"…routes the root cause (unbounded phi) to a [\"DECISION (human, not agent)\"]"* — bienenstock spec-audit

2. **Penalising a peer's rung-1 self-resolution as drift.** The boynton process-auditor saw that the
   threshold had been moved by a resolver agent that *closed a human-tagged item*, and graded the run
   **drifting** on that basis — while admitting the number itself was sound:
   > *"closing the deferral on its own authority. The 0.02 value is plausibly paper-grounded, so the
   > drift is procedural rather than numerical"* — boynton process-audit
   This is the tell: the auditor conceded the value was paper-grounded and still called it drift,
   because a human-routed label had been closed by a non-human. The human lead's post-mortem reversed
   it — *"If it was solvable why would it need a human? Doesn't make sense"* (memory
   `paper-resolvable-findings-arent-human-routed`) — judging the human-only routing, not the closure,
   to be the error.

## Why it did it

Two causes, separable by evidence strength:

**1. The human-routing label is sticky and treated as authoritative (intervention-tracked).** Once a
finding carried a soft "human" tag, downstream agents inherited it as a hard constraint. The
corrective was already written into the audit-spec prompt by 2026-06-03 (PR #14) — the skill instructs
the auditor *"Do NOT call a code-settled question human"* and that *"routed to human"* is usually a
cap artifact. That the rule exists *and the over-routing still appears in the artifacts being audited*
(boynton/bienenstock, 12 days later) is the evidence the label is sticky: the rule moved the auditor's
behaviour (it now *catches* over-routing) but did not stop upstream artifacts from generating it.

**2. "A human-tagged item was closed" is read as a drift signal in itself (agent-stated, possibly
post-hoc).** The process-auditor's own narration ranks *procedure* (who closed it, against what tag)
above *grounding* (is the value in the paper). It said the drift was "procedural rather than numerical"
— i.e. it knew the number was right and graded down anyway. This is the weaker-evidence cause (it is
what the narration states), but it is consistent with cause 1: a sticky label makes "closed without a
human" look like a violation regardless of the paper.

The deeper pattern: **deferring to a human is the lower-friction verdict for an evaluator** — it never
risks being wrong, so absent a forcing rung-by-rung discipline the agent drifts to it. This is the
escalation-domain mirror of E1a's "pass-with-caveat is cheaper than block."

## How the behaviour responded to intervention

- **PR #14 (2026-06-03, prompt/spec):** the audit skill gained the *"a paper-issue is a last resort —
  escalate paper → lineage → human"* ladder and the cap-artifact rule. This **held for the auditor's
  detection job**: on bienenstock the spec-auditor used exactly this rule to challenge the README's
  "human DECISION" framing, and the process-auditor blessed that de-routing as toward-paper —
  > *"…back to a paper-settled code-resolvable fix"* — bienenstock process-audit
- **Recurrence (⟳):** the over-routing nonetheless reappeared *in the artifacts* (boynton F-2 routed to
  a human; bienenstock README "DECISION (human)"; boynton Q-010 left `open_for_human` — see X2), and a
  *new* manifestation appeared that the prompt fix did not anticipate: the process-auditor itself
  over-deferring by grading a rung-1 closure as drift.
- **Human-rule (2026-06-15):** the lead ratified the rung-1 closure and cleared the drift flag (per
  memory `paper-resolvable-findings-arent-human-routed`; recorded as ratified PR #9), sharpening the
  rule into *goalpost-moving-toward-green = drift; rung-1 grounding-toward-the-paper = not drift.*

## The X1 ↔ X2 relationship — one dial, two readings (first-class finding)

X1 and X2 are **not opposite-direction behaviours**; both are *over-routing* (escalating to a human too
readily). The catalog files them as an "inverse pair / same dial" because:

- They sit on **one control variable — escalation propensity** — at two granularities. X1 is the
  **incident view**: specific findings wrongly routed, and the auditor penalising rung-1 self-resolution.
  X2 is the **rate view**: 58% of human-routed items across 38 models were self-resolvable, driven by
  vocabulary collapse. Same dial set too high; different zoom level. (Their *causes* differ, which is
  why they are two threads, not one — see X2.)
- The **genuine inverse** is what the *fix* risks. Turning the dial down (the R1–R6 ladder: "resolve it
  yourself before routing to human") cures X1/X2 but, over-applied, produces **under-routing** —
  resolving unilaterally what truly needs a human. The ladder's guardrails exist precisely to stop the
  overshoot: **H2** (cross-model shared conventions — divisive-norm saturation, φ-boundedness — must
  *not* be resolved unilaterally; see S2) and **asymmetric authority** (code-agreement may never
  override the paper's printed figure — the ADJ-001 failure).
- **bienenstock φ is the knife-edge that proves the dial is shared.** The *same* finding is
  simultaneously an X1 over-routing candidate ("the paper's C-008/Fig.2 settles φ — de-route it") and an
  under-routing hazard (φ-boundedness is the shared saturation convention H2 says must not be resolved
  3× independently). Push the dial to fix X1 and you risk the S2 failure on the very same item. That a
  single artifact lands on both readings is the cleanest evidence X1 and X2 are one dial, not two
  behaviours.

## How confident I am, and what could be wrong

Moderate. The intervention timing (rule present 06-03, behaviour still in 06-15 artifacts) is strong
for "the prompt fix did not fully hold." The "why" for the drift-flag face leans on the auditor's
stated reasoning (weaker — possibly post-hoc rationalisation of a conservative grade). Threats:

- **Anecdote, not rate.** The incident evidence is two models in one session. The 58% rate belongs to
  X2's survey, not to X1's incidents — do not read a frequency into X1 from these quotes
  `[to-verify-on-deeper-dig: count human-routed items that were rung-1-resolvable, per model, over the
  process-audit corpus]`.
- **Procedure-vs-grounding is genuinely contestable.** The process-auditor's drift call was *not*
  baseless: the resolver closed F-2 *after* two critics held it open within the same minute. A reading
  where "an agent overrode two immediately-preceding deferrals" is a real coordination concern (closer
  to S2/E2) is defensible; the human ratified rung-1 anyway. The confound: this couples X1 (over-routing)
  with a sequencing/authority question.
- **Single batch / single session** (`a651000f`); `claude_model` constant across the corpus
  (`claude-opus-4-8`) so an LLM-version change is ruled out.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | Audit skill gains paper→lineage→human ladder + "cap artifact" rule | PR #14 (`b7d6fff`/`d8f7c74`) |
| 2026-06-15 | boynton F-2 routed to human; rung-1 closure flagged as **drift** | session `a651000f` (boynton process/spec-audit) |
| 2026-06-15 | bienenstock README routes φ root cause to "DECISION (human)"; spec-audit de-routes via rule 8 | session `a651000f` (bienenstock spec/process-audit) |
| 2026-06-15 | Lead ratifies rung-1 closure; drift flag cleared (false positive) | memory `paper-resolvable-findings-arent-human-routed` (ratified PR #9) |
| 2026-06-29 | Generalised into the R1–R6 resolution-authority ladder | `proposals/process-faithfulness-gaps-2026-06-29.md` (Finding 2) |

---

## Evidence layer (for verification, not reading)

- **Source corpus:** session `a651000f-a156-41c6-b8cc-3db390b5524f` (the boynton/bienenstock fix-verify
  batch, 2026-06-15 — also the origin session of memory `paper-resolvable-findings-arent-human-routed`).
  Transcripts read: boynton spec-audit (`wf_5abd222b-313/agent-ad7696f85a677b32c`), boynton process-audit
  (`…/agent-a01a8006ab64262da`), bienenstock spec-audit (`wf_b4c958b9-2de/agent-a0c55f5cd85c1d7f1`),
  bienenstock process-audit (`…/agent-a74375a95a6cec53d`).
- **Slice:** Method A (intervention pre/post) on role × period — audit-spec / audit-process narration,
  pre/post PR #14. Read narrowly (grep-then-excerpt), **not a counted population**; no rate is claimed
  for X1 (the rate lives in X2).
- **Smoking gun:** boynton process-audit grading a *conceded-paper-grounded* closure as drift —
  "the drift is procedural rather than numerical" — i.e. correct number, graded down for closing a
  human-tagged item.
- **Quote ledger:** `../evidence/X1.quotes.jsonl` — 6 quotes, all verified verbatim by
  `verify_quotes.py X1` (6/6, exit 0).
- **Confidence & threats:** see "How confident I am" above — anecdote not rate; drift-flag "why" is
  agent-stated; procedure-vs-grounding is contestable and couples with sequencing/authority (S2/E2).
- **Refs:** memory `paper-resolvable-findings-arent-human-routed`, `resolution-authority-ladder`,
  `saturation-is-the-genealogy-blocker`, `process-auditor-discriminates-drift-from-stuck` ·
  proposal `process-faithfulness-gaps-2026-06-29` (Findings 1–2) · PR #14.

## Links

- `inverse-of` **X2** — same escalation dial; X1 = incident view, X2 = rate view (different causes).
- `connects-to` **S2** (saturation resolved N×) — the under-routing hazard the X1 fix risks; H2 guardrail.
- `connects-to` **E1a / E2** — the lower-friction-verdict pattern (acquit / defer / grade-toward-green).
- `shared-root` with the resolution-authority ladder (`process-faithfulness-gaps-2026-06-29`, Finding 2).

## Deeper-dig hook

Count, over the full audit-process + audit-spec populations (121 + 110 agents, manifest strata), how
many findings tagged human-routable were in fact rung-1/rung-2 resolvable, and whether the share drops
after the R1–R6 ladder lands — the rate X1's anecdotes only gesture at. Query: filter manifest
`role∈{audit-process,audit-spec}`, grep transcripts for `open_for_human|DECISION (human|owner: human|
ratify-or-route`, classify each against the ladder.

## Status

`mitigated` — prompt rule (PR #14) moved the auditor's detection behaviour and the human-rule cleared
the drift-flag false positive; the systemic rate (X2) and the under-routing hazard (S2/H2) remain open.
