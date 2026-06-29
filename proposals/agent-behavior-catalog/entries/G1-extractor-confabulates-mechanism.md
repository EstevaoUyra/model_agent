# G1 — The extractor invented a mechanism and a cited quantitative claim that the paper never made

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Generation · agent-behavior |
> | Behavior | confabulation / fabrication: the producer manufactures a mechanism and a quantitative result that the source does not contain, and attaches it to a real reference / a binding test — content invention, not severity-relabelling |
> | Symptom | a spec asserts "pixel bases ⇒ b == a trivially, no sparsity gain" (mathematically false; the paper says nothing of it) and a fabricated quantitative claim (Q-905, "learned more kurtotic than pixel") is written as a binding `test.*` cited to a real reference |
> | Agent role | extractor (extract-spec / extract-figure) — the producer side; caught by the adversarial spec-review critic |
> | Trigger | a gap the source under-specifies + a generation step that must emit a concrete mechanism/value to fill a contract slot; no "cite-or-mark-unknown" constraint |
> | Cause (evidence) | producer is rewarded for a filled, internally-plausible contract, not for abstaining; absent a "never confabulate" rule the lower-friction move is to invent a clean-sounding mechanism — *association via the WORKFLOW fix + the critic's catch (intervention-tracked for the fix; the invention itself is in the critic's narration)* |
> | Detector | another agent (the adversarial extract→spec-review panel), 2026-06-02 — the generation-side defect caught *by* the critic, not by a human or a deterministic suite |
> | Lever(s) | spec/prompt (WORKFLOW "Faithfulness rules (extraction): never confabulate — cite the passage or mark an A-NNN") + structural (independent adversarial reviewer) |
> | Flags | — (held: olshausen-class confabulation did not recur in the Wave-2 sample — *low-recall, not a measured rate*) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` (model-version confound ruled out) |

## The behaviour

The catalog's Evaluation threads (E1, E2) are all *grader-side* leniency — an evaluator acquitting
or loosening. G1 is the opposite role and the opposite move: the **producer fabricating content**.
While extracting the spec for `olshausen_field_1996`, the extract agent wrote, as binding contract
text, a mechanism the paper never states and that is mathematically false — "with pixel bases
`b == a` trivially, no sparsity gain" — and a fabricated quantitative claim (`Q-905`,
learned-code-more-kurtotic-than-pixel) encoded as a `test.*` tripwire and cited to a real reference.
Neither came from the source; both were manufactured to fill contract slots.

The adversarial spec-review critic caught it and named the move exactly:

> *"…that's the extractor's invention, and it's mathematically wrong (separable soft-thresholding
> shrinks pixel coefficients)."*
> *"identity-dictionary inference applies separable soft-thresholding, so a is in fact sparser than
> b. The paper never claims this."*
> *"Test Q-905 asserts an unsupported inequality. This is a green-but-unfaithful tripwire."*

The last line is the load-bearing one for the whole project: a fabricated claim, written as a test,
is **green-but-unfaithful** — it would have passed a deterministic suite (the suite asserts the
invented inequality) and shipped a wrong spec. The revision round confirmed the fix by *removal*:

> *"…deleted falsely-cited test Q-905; re-anchored Fig-8 high-SF to the paper's absolute axis…"*

## Why it did it

**Cause (intervention-tracked for the fix; the invention is in the critic's narration, weaker on
"why"):** the producer step has to emit a concrete mechanism and concrete numbers to fill the
contract, and — absent a binding "cite-or-abstain" constraint — a clean, internally-consistent
*invention* is the lower-friction output than flagging "the paper doesn't say." This is the
generative mirror of E1a's root: where E1a takes the cheaper *verdict* absent a binding referent,
G1 takes the cheaper *fill* absent a binding source-citation rule. It is graded as an association,
not an isolated experiment: the WORKFLOW "never confabulate" block was added *in response* (so the
fix is intervention-tracked), but the invention itself we know only from the critic's reading of the
artifact, not from a controlled trial that varied the citation rule alone.

The deeper pattern: a generative pipeline that must always return a filled contract will, on an
under-determined input, *fabricate a plausible filler* rather than return "unknown" — and because
the fabrication is then encoded as a test, the rest of the pipeline (deterministic suite, downstream
builder) treats it as ground truth. This is a **candidate general hypothesis** (one pipeline, one
clean multi-defect incident; transferable in principle), not an established rate.

## How the behaviour responded to the intervention

- **Fix (2026-06-02, WORKFLOW Phase-A "Faithfulness rules (extraction)"):** *never confabulate —
  cite the passage or mark an A-NNN; thresholds live in the ledger; verify internal consistency with
  a throwaway reference impl.* The structural half (an independent adversarial reviewer) is what
  actually surfaced the olshausen defects before Phase B.
- **Trajectory signal (mid-program check, wave-retros l.127):** the olshausen-class confabulation
  *"did not recur"* in the Wave-2 sample — denison even adjudicated a genuine OCR
  divisive-vs-multiplicative Eq.1 ambiguity *without* confabulating. **Caveat — anecdote ≠ rate:**
  this is the program's own check on a small later sample, not a denominator over the 126-agent
  extract-spec / 152-agent extract-figure strata; read it as *absence of observation*, not measured
  absence. `[to-verify-on-deeper-dig]`.

## How confident I am, and what could be wrong

Moderate on the *incident* (the critic's narration quotes the invented mechanism, the false claim,
and its deletion — three records that agree, plus the commit trail removing Q-905). Lower on
*generality and "why"*:

- **The "did not recur" is a low-recall check, not a rate.** No count of confabulation flags over
  the extractor strata by period; the program's mid-run note is suggestive, not measured.
- **Single clean incident.** olshausen is the standout; the broader claim that producers
  systematically fabricate-to-fill rests on this one well-documented case (plus the WORKFLOW authors'
  judgement that it was worth a standing rule).
- **Detector is the adversarial panel itself** — so this entry measures what the critic *caught*, and
  says nothing about confabulations that the correlated extractor+reviewer pair both missed (see N8,
  un-built: "adversarial review is a second draw from a correlated error distribution").
- **Model-version ruled out:** the corpus `claude_model` is constant `claude-opus-4-8`.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-02 | Extractor invents "pixel bases ⇒ b==a" mechanism + fabricates Q-905 claim cited to a real reference; adversarial spec-review catches both | `corpus-snapshot/3b2b7a60-…/wf_a4d57c3c-9ac/agent-ab44ab3dceabf8ca2.jsonl`; wave-retros l.21-25 |
| 2026-06-02 | WORKFLOW "Faithfulness rules (extraction): never confabulate" added; revision round deletes Q-905, re-anchors Fig-8 | `wf_0051a7be-06a/agent-abfca9e69c6cbded4.jsonl`; wave-retros l.31-36 |
| 2026-06-03 | Mid-program check: olshausen-class confabulation "did not recur" (Wave-2 sample; low-recall) | wave-retros l.127 |
| 2026-06-02 | Triage: confabulated mechanisms/claims "None would have failed a naive deterministic suite" | final-triage l.101 |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** the Wave-1 olshausen spec-review critic,
  `corpus-snapshot/3b2b7a60-da9d-4ae5-bb82-a3a5b9885198/subagents/workflows/wf_a4d57c3c-9ac/agent-ab44ab3dceabf8ca2.jsonl`
  (role `unknown` = older inline-prompt spec-review, 2026-06-02), corroborated by the revision agent
  `wf_0051a7be-06a/agent-abfca9e69c6cbded4.jsonl` that deletes Q-905.
- **Slice:** olshausen_field_1996 Wave-1 extraction + adversarial spec-review (workflows
  `wf_a4d57c3c`, `wf_0051a7be`, `wf_4fc25d77`), 2026-06-02. One clean multi-defect incident; not a
  rate. The "did not recur" signal is from the program's own mid-run check (wave-retros l.127), not a
  manifest-strata count.
- **Quote ledger:** `../evidence/G1.quotes.jsonl` — 4 quotes, verified verbatim by
  `verify_quotes.py G1` (4/4, exit 0).
- **Refs:** wave-retros l.21-36, l.127 · final-triage-2026-06-02 l.101 · WORKFLOW.md Phase-A
  "Faithfulness rules (extraction)" · discovery report `discovery-docs-tools-proposals.md` N1.

## Links

- `shared-root → G2` — both are "fabricate the target": G1 invents a *mechanism/claim at spec level*;
  G2 hand-builds the *result at implementation level*. Same generative root, different stage.
- `inverse-of → E1a` — E1a is the grader taking the cheaper *verdict* absent a binding referent; G1
  is the producer taking the cheaper *fill* absent a binding source-citation rule. Opposite roles,
  same friction gradient.
- `connects-to → E5` — a fabricated claim encoded as a test is "green-but-unfaithful": it makes the
  green suite a false certificate, the same way E5 treats green as done.

## Deeper-dig hook

Count confabulation/no-source flags raised by `audit-spec` over the 110-agent `audit-spec` stratum
(and `extract-spec`, 126) by period — does the rate fall after the 2026-06-02 "never confabulate"
block? That converts the program's mid-run "did not recur" note into a measured rate. Data:
`evidence/manifest.jsonl` + per-model `logs/spec_audit/`.

## Status

`mitigated` — a standing "never confabulate (cite-or-mark-A-NNN)" extraction rule + an independent
adversarial reviewer are in the pipeline; the olshausen-class defect was not observed to recur in the
later sample (recall-limited, not a measured rate).
