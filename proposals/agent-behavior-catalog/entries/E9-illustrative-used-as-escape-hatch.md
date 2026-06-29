# E9 — "Illustrative / not-reproduced" used as an escape hatch to scope out a reproducible figure

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior |
> | Behavior | scope-minimization / effort-avoidance: a result-bearing figure is dispositioned ILLUSTRATIVE-NOT-REPRODUCED (declared out of reproduction scope) rather than reproduced, on the rationale that it "stands in" for out-of-scope per-observer fits — when the authors had in fact released the fitted values that make it reproducible |
> | Symptom | carrasco2021 Fig 7 carried as "illustrative, not plain-reproduced (may never show green)" — until the released author fits were driven through the forward model and it reproduced to ~1e-14 |
> | Agent role | extract-spec (sets the figure's reproduction disposition) + audit-faithfulness/author-tests who ratified it |
> | Trigger | a result-bearing fit whose per-observer parameters look out-of-scope to refit, AND a released-fits artifact that the agent did not check for before dispositioning |
> | Cause (evidence) | the ILLUSTRATIVE ceiling was applied before checking whether the authors released the fitted values + curves — *intervention-tracked via d057abe; the fix adds exactly that pre-check* |
> | Detector | the process lever was authored after the fact (human); an audit-process agent *had* flagged the out-of-scoping as a contradiction-laundering signature but accepted it because it was routed to a human, not self-closed |
> | Lever(s) | spec (extract-spec Step 3b: before dispositioning result-bearing fit as ILLUSTRATIVE, check for released fitted values/curves; if present, drive the forward model with author ground truth — a genuine reproduction) + acquire-sources flags released fits |
> | Flags | — |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

Some paper figures show a *fit* — a curve whose parameters the authors estimated per observer. The
honest disposition for such a figure, *if* the fit cannot be reproduced, is
ILLUSTRATIVE-NOT-REPRODUCED: a label that says "we render the qualitative regime but do not claim a
pointwise match." E9 is the failure where that label is reached for **too early** — used to scope a
figure *out* of the reproduction it actually admits, because re-fitting looks out of scope, without
first checking whether the authors *released* the fitted values that would make it a genuine
reproduction with no re-fit at all.

The instance is carrasco2021 Fig 7. The extract-spec agent settled the disposition as out-of-scope:

> *"…because the figures STAND IN for per-observer fits and show no pointwise reproduction, the
> figures' disposition remains ILLUSTRATIVE-NOT-REPRODUCED."*

and the test author encoded that as a possibly-permanent red: the in-scope-figures test covers "both
figures ILLUSTRATIVE-NOT-REPRODUCED frozen stubs … *may never show plain green.*" The escape-hatch
character is what makes E9 distinct from an honest "we genuinely can't reproduce this": the figure
*was* reproducible. Once the released author fits were driven through the forward model, it matched to
machine precision — *"the faithful author convention reproduces `author_dp_neural.json` to ~1e-14 for
7 of 8 curves"* — and the figure's standing flipped to faithful: a later audit records *"D1 (Fig 7
FAITHFUL)."*

Notably, the out-of-scoping did not pass unremarked: an audit-process agent flagged the move at the
time as fitting the laundering pattern —

> *"Both reframe a paper signature (the headline RG near-invariance in Fig 7b…) as fit-artifacts that
> are 'out of scope'…"*

but accepted it as honest *because it was routed to a human rather than self-closed*. So the
disposition cleared the process check on procedure (it was escalated, not buried) while still being
the wrong substantive call (the figure was reproducible from released data).

## Why it did it

**Cause (intervention-tracked): the ILLUSTRATIVE ceiling was applied before checking for released
fitted values.** The fix (commit `d057abe`) adds exactly the missing step — extract-spec Step 3b:
"before dispositioning a result-bearing fit as ILLUSTRATIVE-NOT-REPRODUCED, check whether the authors
RELEASED the fitted values + the plotted curves … If so, drive the forward model with author ground
truth (CODE-NNN) — a genuine reproduction, no re-fit," with acquire-sources flagging released fits so
the extractor sees them. The worked example in the commit is this figure ("carrasco2021 Fig 7
(illustrative → ~1e-14 reproduction)"). That the remedy is "look for the released artifact first" is
strong evidence the driver was a missing pre-check, not a genuine irreproducibility.

The deeper pattern: **scoping work out is the lower-effort verdict** — ILLUSTRATIVE-NOT-REPRODUCED
closes the figure without the labor of locating, wiring, and validating author ground truth, and it
*feels* honest (it disclaims a match rather than faking one). That honesty is exactly what makes it a
dangerous escape hatch: it is the *epistemically virtuous-looking* way to avoid a reproducible result.
This is the inverse face of E1a/E7: E1a/E7 pass wrong output *in* (acquit a known gap); E9 scopes a
*right-achievable* output *out*. Same underlying economics (the cheaper verdict wins absent a binding
push toward the harder, correct one), opposite direction of error.

## How the behaviour responded to the intervention

After `d057abe`, the carrasco pass on 2026-06-10 (`wf_a3ad143a`) grounds parameters in the released
author code (CODE-NNN entries, MATLAB paths checked) rather than treating the fit as an opaque stub,
and the released-fit reproduction is exercised directly: the implement step confirms the forward model
"reproduces `author_dp_neural.json` to ~1e-14 for 7 of 8 curves." The figure's disposition moves off
the ILLUSTRATIVE ceiling to FAITHFUL in the subsequent audits ("D1 (Fig 7 FAITHFUL)"). The escape
hatch is closed by making "did you check for released fits?" a required step before the label can be
applied.

## How confident I am, and what could be wrong

Moderate-to-high on the *incident* (the ILLUSTRATIVE disposition, the released-fit ~1e-14
reproduction, and the flip to FAITHFUL are all in the narration; the fix names the same figure as its
worked example). Lower on *generality* and on *intent framing*:

- **Not pure avoidance — the residue was partly real.** Even post-fix, a *supplementary* panel
  (Supp-Fig-4 NMA amplitude, ~1/8 SI scale) stayed legitimately ILLUSTRATIVE/RED — so the label is
  not always an escape hatch; E9 is specifically about applying it to the *reproducible* in-scope
  figure before checking for released data. Distinguishing "honest illustrative" from "escape-hatch
  illustrative" needs the released-artifact check, which is the whole point of the fix.
- **The process check passed it on procedure.** The audit-process agent flagged the out-of-scoping yet
  accepted it because it was escalated, not self-closed — so this is also a case where *correct
  procedure (escalate) co-existed with a wrong substantive call*, which the per-figure process gate
  was not positioned to overturn.
- **One figure / one model.** carrasco2021 Fig 7 is the only characterized instance; the rate at which
  result-bearing figures were dispositioned ILLUSTRATIVE without a released-fit check is
  uncharacterised ([to-verify] over the extract-spec stratum).
- **Model-version ruled out:** `claude-opus-4-8` constant across the slice.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | carrasco2021 Fig 7 dispositioned ILLUSTRATIVE-NOT-REPRODUCED ("may never show plain green"); audit-process flags out-of-scoping but accepts it (escalated, not self-closed) | `wf_98fac8b7` (extract-spec a3b20171, author-tests a72bbf22, audit-process a4271a5b) |
| 2026-06-10 | Process lever: released fitted results dissolve the ILLUSTRATIVE ceiling (extract-spec Step 3b; acquire-sources flags released fits) | commit `d057abe` |
| 2026-06-10 | Released author fits driven through forward model → reproduces to ~1e-14 (7/8 curves) | `wf_34823bab` (implement a2ae6b5a) |
| 2026-06-15 | Figure carried FAITHFUL (D1) in re-audit | `wf_fdd13a8b` (audit-faithfulness a36a63184) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** the extract-spec disposition,
  `…/wf_98fac8b7-160/agent-a3b20171961184a23.jsonl` ("the figures STAND IN for per-observer fits and
  show no pointwise reproduction … disposition remains ILLUSTRATIVE-NOT-REPRODUCED"), contrasted with
  the released-fit reproduction `…/wf_34823bab-a90/agent-a2ae6b5a9fc2feb16.jsonl` ("reproduces
  `author_dp_neural.json` to ~1e-14 for 7 of 8 curves") and the flip to "D1 (Fig 7 FAITHFUL)". Binding
  remedy: commit `d057abe`.
- **Slice:** carrasco2021 — pre-fix pass 2026-06-03 (`wf_98fac8b7`) vs post-fix passes 2026-06-10
  (`wf_a3ad143a`, `wf_34823bab`) and 2026-06-15 (`wf_fdd13a8b`). Counts are anecdotal (one figure);
  not a rate.
- **Quote ledger:** `../evidence/E9.quotes.jsonl` — 6 quotes, verified verbatim by
  `verify_quotes.py E9` (6/6, exit 0).
- **Refs:** commit `d057abe` (`skills/extract-spec/SKILL.md`, `skills/acquire-sources/SKILL.md`) ·
  memory `paper-resolvable-findings-arent-human-routed`, `fix-mode-false-blocks-on-coverage`.

## Links

- `inverse-of → E1a` — E1a passes wrong output *in* (acquits a named discrepancy); E9 scopes a
  reproducible output *out* (declines a result it could achieve). Same evaluator-economics, opposite
  error direction.
- `connects-to → E7` — shared vocabulary: E7's non-blocking label of choice is "illustrative, doesn't
  affect shape" (lets a scale-wrong figure pass in); E9's is "illustrative-not-reproduced" (scopes a
  figure out).
- `connects-to → X1` — X1 over-routes paper-resolvable findings to a human; E9 is the figure-disposition
  cousin (a reproducible figure scoped out / flagged for human ratification instead of reproduced from
  released data). Both are resolvable-without-human work being deferred.

## Deeper-dig hook

Over the 126-agent extract-spec stratum, count figures dispositioned ILLUSTRATIVE-NOT-REPRODUCED and
cross-check each against whether the paper released fitted values/curves (SOURCES.md / paper code
dirs) — the fraction with available released data is the escape-hatch rate this single incident only
samples. Data: `evidence/manifest.jsonl` (role `extract-spec`) + per-model `article_aware/spec/` and
`paper/code/`.

## Status

`mitigated` — extract-spec now must check for released fitted values/curves before applying the
ILLUSTRATIVE-NOT-REPRODUCED label, and drive the forward model with author ground truth when they
exist (commit `d057abe`); carrasco Fig 7 flipped from illustrative to FAITHFUL via ~1e-14
reproduction. Recurrence rate uncharacterised.
