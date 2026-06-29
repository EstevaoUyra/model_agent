# C7 — Correlated reviewers: "adversarial" review is a second draw from the same error distribution

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination / Evaluation · agent-behavior (multi-agent independence failure) |
> | Behavior | two agents meant to cross-check (extractor + reviewer) **share their misreadings**, so the "adversarial" review is a *correlated second draw* from the same error distribution, not an independent ground-truth check; in the degenerate case the review panel is N=1 and self-certifies |
> | Symptom | extractor + reviewer reading the same dense passage make the same error; the spec-review "panel" is one agent that writes its own APPROVED verdict; shared mis-transcriptions of core equations slipped (CHM Eq.5/7; hara_gardner Eq.1/6/7) |
> | Agent role | extract-spec / audit-spec (the extractor–reviewer pair); spec-review gate |
> | Trigger | the second reviewer reads the *same source passage* with the *same priors/tooling* as the first, with no independent anchor (author code, related paper, a different modality); "adversarial framing" is applied without engineered independence |
> | Cause (evidence) | independence failure between two agents drawing from a correlated error distribution — *agent-stated/structural* (the proposal names it; it is partly a structural property of the setup, not only a per-incident act) |
> | Detector | **human post-mortem** (faithfulness-enforcement cluster E; final-triage shared-misreading catches) |
> | Lever(s) | structural — give the second look a *different* anchor: the standing Faithfulness Auditor holds the paper AND the implementation AND, where they exist, author code + lineage papers; a verify-the-finding refute pass |
> | Flags | independence-failure multi-agent dynamic (WAB-relevant); borders a structural property (correlation) — flagged in threats-to-validity |
> | Status | mitigated |

## The behaviour

The pipeline's load-bearing faithfulness mechanism is a two-agent structure: an **extractor** reads
the paper and writes the spec/claims, and a **reviewer** adversarially checks that extraction. The
intended safety comes from *independence* — two looks are better than one only if the second look can
fail where the first succeeded and vice versa. C7 is when that independence does not hold: the
reviewer reads the *same dense passage* with the *same priors and tooling* as the extractor, so the
two error distributions are **correlated**. The second draw mostly repeats the first's mistakes; the
"adversarial" label adds confidence without adding an independent measurement.

> "**E2. The judge never ran; reviewers are correlated.** Extractor + reviewer reading the same dense
> passage share misreadings; 'adversarial' framing adds a second draw from a correlated error
> distribution, not ground truth." — faithfulness-enforcement, cluster E

The degenerate extreme is N=1 — the review *is* the extractor, certifying itself:

> "**E1. Spec-review 'panel' is N=1, self-writes APPROVED.** One agent judges and creates the gate
> file from its own verdict; it approved the loose spratling shape proxy and boynton's wrong Fig.8
> value." — faithfulness-enforcement, cluster E

The consequence shows up as *shared* mis-transcriptions of the very equations both agents read — the
errors that a correlated pair is least able to catch because both inherited them from the same dense
passage:

> "mis-transcribed core equations (carandini-heeger-movshon Eq.5/7, hara_gardner Eq.1/6/7)" —
> final-triage (the catches the two-agent structure *did* make once the second look had an anchor)

So C7 is double-edged in the record: it names *why* the pair can fail (correlation), and the
final-triage list shows the pair *working* once a genuinely independent anchor was present — which is
the intervention story below.

## Why C7 is distinct from E1 (single-agent leniency) and from S2

- **vs. E1 (Evaluator leniency — acquits a discrepancy it named).** E1 is a *single-agent* property:
  one auditor sees a divergence and lets it pass (a calibration/leniency failure inside one head). C7
  is a *between-agent* property: each agent might be individually fine, but the *pair* provides no
  independent information because their errors are correlated. You cannot fix C7 by making each agent
  stricter — two strict-but-correlated reviewers still share the same blind spot. The fix is
  *independence* (a different anchor), not *severity*. (The N=1 self-APPROVE case is where C7
  collapses *into* an E1-like single-agent act — noted as the degenerate extreme, not the general
  thread.)
- **vs. S2 (one decision resolved N×).** S2 is redundant *resolution* of one decision across models;
  C7 is redundant *error* between two reviewers of one artifact. S2's redundancy is in the decision
  graph; C7's is in the error distribution.

## How it responded to intervention

The lever is **structural — engineer the independence the pair lacked.** The standing Faithfulness
Auditor (the post-mortem's Part-2 remedy) holds not just the paper but the *implementation* and,
where they exist, the *author's own code* and *lineage (parent/descendant) papers* — anchors the
original extractor↔reviewer pair never had. A second look anchored to author code is no longer a
re-draw from the same passage; it can fail where a paper-only read succeeds. Findings additionally
pass a **verify-the-finding (refute) pass** to control over-flagging while keeping the inverted
error-bias. The final-triage equation catches (CHM, hara_gardner) are the evidence this de-correlated
second look pays off once it exists. C7 is filed **mitigated**: the correlation is named and a
de-correlating anchor is the documented fix, but "reviewers are now independent" is a structural claim
about the *design*, not a measured drop in shared-error rate.

## Confidence & threats to validity

Moderate. The behaviour is named explicitly in a human post-mortem and is consistent with the
shared-equation slips in final-triage. Threats:

- **Borders a structural property, not a per-incident behaviour.** "Correlated error distribution" is
  a property of how the two agents are wired (same source, same priors), not a discrete act with a
  single artifact — so it sits at the edge of the catalog's `Smoking gun` convention. The N=1 self-
  APPROVE and the shared equation slips are the closest discrete proxies; the correlation itself is
  inferred from those plus the design.
- **Anecdote ≠ rate.** Two named shared mis-transcriptions show correlated error happened; they do
  not quantify *how correlated* the pair is, nor the fraction of misreadings both agents shared vs.
  one caught. Measuring correlation needs a denominator (paired extractor/reviewer verdicts on the
  same passages), which this slice does not have.
- **Detector is human.** By construction: if the two agents are correlated, *neither* reports the
  shared error, so only an out-of-band reader (the human audit, or a later differently-anchored
  auditor) surfaces it. Selection-bias signal again.
- **Outcome is a design claim.** "Mitigated" rests on the anchored Faithfulness Auditor being the
  documented de-correlator; an actual reduction in shared-error rate is unmeasured.

## Scope / generality

Descriptive, and unusually general: any "have a second reviewer check it" safeguard inherits C7 if the
second reviewer shares the first's inputs, priors, or tooling — correlated reviewers give the
*appearance* of independent verification while providing a correlated re-draw. The lesson (engineer an
*independent anchor*, do not just add a second pass) is generic to LLM-judge / self-critique / panel
designs. Setup-specific in the extractor↔reviewer pair and the equation-transcription instances.

## Adjacent facet — eval-design validity leak (different mechanism, same family)

The orchestrator-session harvest surfaced a *second* way the check stops being a check, by a different
mechanism than correlation: the orchestrator set up a blind quality test **with the answers visible**,
and the human stopped it — *"that's a real validity hole, and you're right to stop it"* (`orch-D`,
`5fff61cd…`). C7 is reviewers that aren't *independent*; this is an evaluation whose *blinding is broken*
(the construct leaks the answer). Filed here as the nearest home because both are "the safeguard provides
the appearance of measurement without the substance," but the mechanism is answer-leakage, not reviewer
correlation. Single instance, human-caught, not built out as its own thread.

## Links
- `connects-to E1` — E1 is the single-agent leniency C7 must be distinguished from; the N=1 self-
  APPROVE case is where C7 degenerates into an E1-shaped self-certification.
- `connects-to C6` — sibling multi-agent coordination failure from the same audit cluster: C6 = no
  reviewer scoped to the whole (no integrative look); C7 = two reviewers that look but not
  independently (no *independent* look).
- `connects-to E3` — both are "a second check that isn't really a check": E3 = the eye rubber-stamps
  the tool's output; C7 = the reviewer rubber-stamps a correlated re-read.

## Deeper-dig hook
(1) The real measurement: pull paired extract-spec / audit-spec verdicts on the *same* passages
(slice `evidence/corpus-snapshot/` by the extract→audit pair per model) and count shared vs. caught
errors — denominator = reviewed passages — to turn "correlated" from a named property into a rate.
(2) Test the de-correlation claim: compare shared-error rate before vs. after the anchored
Faithfulness Auditor existed. Data: `faithfulness-enforcement-2026-06-02` (cluster E; Part-2 §1),
`final-triage-2026-06-02` (the equation catches), per-model extract-spec/audit-spec transcripts.

## Status
**mitigated** — correlation between extractor and reviewer is named; the documented de-correlator (an
independently-anchored Faithfulness Auditor + refute pass) exists; an actual drop in shared-error rate
is unmeasured.

## Refs
- Proposal (PRIMARY): `proposals/faithfulness-enforcement-2026-06-02.md` (cluster E1/E2; Part-2 §1 the
  Faithfulness Auditor holding paper + impl + author code + lineage; the refute pass).
- Proposal: `proposals/final-triage-2026-06-02.md` (l.101-103, the two-agent structure's equation
  catches; CHM Eq.5/7, hara_gardner Eq.1/6/7).
- Cousins: **C6** (no integrative owner), **E1** (single-agent leniency), **E3** (tool rubber-stamp).

---

### Evidence layer (for verification, not reading)
- **Grounding:** the committed faithfulness-enforcement post-mortem (cluster E) + the final-triage
  process-learnings. **No quote ledger produced** — by construction a correlated pair does not report
  its own shared error, so the Detector is a human/out-of-band reader, and the diagnosis lives
  verbatim in the proposals (stronger, citable). Per the brief, proposal-grounded → no ledger
  expected.
- **Honesty note (per brief):** C7 borders a *structural property* (reviewer correlation) rather than
  a single discrete behaviour; recorded in threats-to-validity. The discrete proxies are the N=1 self-
  APPROVE and the shared equation mis-transcriptions; the correlation itself is inferred from those +
  the design.
- **Adjacent-facet quote:** the eval-design validity leak is in `../evidence/orch-D.quotes.jsonl`
  (`NEW-eval-validity-leak-human-caught`, verified verbatim). See `../evidence/orch-harvest-map.md`.
