# E8 — Default per-panel normalization erased the paper's shared-scale claim

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Evaluation · agent-behavior |
> | Behavior | tool-default override of a paper claim: the digitizer/renderer applies its habitual per-panel "max → 1.0" normalization, which is exactly the operation that destroys the figure's content when the paper plots multiple panels on one *shared* scale |
> | Symptom | R&H Fig 2 panels that plateau at ~0.58 / ~0.67 (neither reaching 1.0 — the height *difference* is the response-gain claim) get each pinned to 1.0, flattening the claim to "both panels saturate at 1.0" |
> | Agent role | digitize-figure / audit-digitization (and the renderer/implementation that re-introduced it) |
> | Trigger | a multi-panel figure on a shared y-scale where no single curve reaches 1.0; the default normalization presumes "something IS pinned to 1.0" |
> | Cause (evidence) | a normalize-to-own-max default applied where the paper shares a scale — *intervention-tracked via 7d2767f; the commit calls it "an adherence + self-grade failure against explicit guidance, not a doc gap"* |
> | Detector | another agent (audit-faithfulness caught the implementation re-pinning each panel to 1.0); the digitizer side was caught against existing guidance |
> | Lever(s) | spec (extract-figure + audit-digitization: forbid per-panel auto-normalization where the paper shares a scale — "if the paper's curves don't reach 1.0, yours must not either") |
> | Flags | ⟳ — fixed on the digitizer side, the same max→1.0 move reappeared on the implementation/render side the next day |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

Normalization is a display convention that the reproduction must inherit from the paper, not impose.
When a paper draws several CRF panels on a single *shared* y-scale and none of the curves reaches
1.0, the **relative heights across panels carry the scientific claim** — in Reynolds & Heeger 2009
Fig 2, attended plateauing above unattended (and panel 2B's attended sitting above panel 2A's
plateau) *is* the response-gain signature. E8 is the failure where the agent applies its default
"normalize each panel to its own max (→ 1.0)" operation, which collapses every panel to the same
ceiling and silently deletes that claim.

The commit that sharpened the rule (`7d2767f`) states the case precisely: the paper "uses a SHARED
scale (panels plateau at ~0.58 / ~0.67, neither reaching 1.0) and that height difference is the
figure's claim," and per-panel auto-normalization (max → 1.0) erases it — "the digitizer's error was
an adherence + self-grade failure against explicit guidance, not a doc gap." That last clause is the
sharp part: guidance to match the paper's normalization already existed; the agent overrode it with
the tool default and self-graded the result as fine.

The clearest corpus capture of the move is on the *implementation/render* side, named by the
faithfulness auditor:

> *"The implementation's per-panel-pinning normalization here independently pins each panel to its own
> max (2A att=1.0, 2B att=1.0), which differs from the paper's shared-scale claim where 2A plateaus
> lower than 2B."*

That is the behaviour in one sentence: pin-to-max, and the shared-scale claim (2A lower than 2B) is
gone.

## Why it did it

**Cause (intervention-tracked): a normalize-to-own-max default was applied in the one regime where it
is wrong — a shared-scale, sub-1.0 figure.** The fix grades as intervention-tracked because the
commit identifies the trigger (the rule's old wording "which curve is pinned to 1.0" *presumed*
something is pinned to 1.0, which is false for a shared sub-1.0 scale) and patches exactly that: "if
the paper's curves don't reach 1.0, yours must not either." The driver is a tool/operation default
meeting a figure it doesn't fit — and a self-grade that didn't catch the mismatch because "max → 1.0"
*looks* like correct normalization.

The deeper pattern: **the habitual normalization is the path of least resistance**, and it produces a
clean, plausible-looking panel — so without an explicit check that the paper's own curves stay below
1.0, the agent ships the default and rubber-stamps it (a digitizer-side cousin of E3's
tool/VLM-output rubber-stamping). The information destroyed (the cross-panel height difference) is
invisible *after* the normalization, so nothing downstream can recover it.

## How the behaviour responded to the intervention

After `7d2767f`, the R&H digitization audit (2026-06-03, `wf_af0bce49`) treats sub-1.0 plateaus as
the thing to verify and names the default it is guarding against:

> *"The skill's per-panel-auto-normalize trap is avoided."*
> *"…renders correctly, and no per-panel auto-normalization to 1.0 occurred."* (attended 0.863 > 2A
> plateau 0.615 — the response-gain ceiling difference preserved)
> *"…fixation reaches only 0.903 (NOT per-curve pinned to 1.0)"* — the height difference kept as the claim.
> *"…verified correct in both panels (C ~0.94 below 1.0; F 0.74/0.615)"* — plateaus checked *below* 1.0.

and the extract/digitize side carries the convention explicitly: *"both attended (blue) and
unattended (gray) saturate below 1.0."* The audit-process step recorded the resolution as
*"the shared scale is fixed, and the override deleted."*

## The part E8 doesn't resolve — it migrated to the render side (⟳)

The rule landed on the *digitizer*, but the same max→1.0 operation reappeared one day later in the
*implementation/render* (the smoking-gun quote above, audit-faithfulness 2026-06-04, `wf_a6f22cb4`):
the model's rendering pinned each panel to its own max (2A=1.0, 2B=1.0) and the auditor had to catch
it again. So the behaviour is the same default surfacing on a second channel the digitizer-side rule
didn't cover — caught here, but evidence that "normalize to max" is a recurring reflex across
whichever component does the scaling, not a single-site bug.

## How confident I am, and what could be wrong

Moderate. The *behaviour* and its driver are documented in the fix commit and named verbatim by the
auditor on the implementation side; the *response* (sub-1.0 verification, "trap avoided") is well
captured. Threats:

- **The original digitizer failure is reconstructed, not re-read.** The post-fix `wf_af0bce49` agents
  largely traced correct sub-1.0 values; the commit asserts the prior digitizer pinned to 1.0, but I
  did not isolate that pre-fix digitize transcript. The migration instance (render side) is the
  cleanest *in-corpus* capture.
- **R&H-specific.** Both failure and response are Reynolds & Heeger Fig 2; generality to other
  shared-scale figures is untested here. (S2 notes the R&H normalization/saturation surface is a
  repeatedly-touched, paper-underdetermined area — E8 is entangled with that pressure.)
- **Anecdote, not rate.** One figure, one migration instance — no denominator over digitize/audit
  agents.
- **Model-version ruled out:** `claude-opus-4-8` constant across the slice.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | R&H Fig 2 normalization sharpened: forbid per-panel max→1.0 where the paper shares a scale | commit `7d2767f` (extract-figure + audit-digitization SKILLs) |
| 2026-06-03 | Digitization audit verifies sub-1.0 plateaus; "per-panel-auto-normalize trap is avoided" | `wf_af0bce49` (audit-digitization ab1880bf/a00e92e67/a554c8684; audit-process acd4e204) |
| 2026-06-04 | Same max→1.0 reappears on the implementation/render side; auditor catches 2A=1.0, 2B=1.0 | `wf_a6f22cb4` (audit-faithfulness a20b6f9c) |

---

## Evidence layer (for verification, not reading)

- **Smoking gun:** the audit-faithfulness narration naming the render-side re-pin,
  `…/wf_a6f22cb4-836/agent-a20b6f9c752334d44.jsonl` ("independently pins each panel to its own max
  (2A att=1.0, 2B att=1.0), which differs from the paper's shared-scale claim"), with the binding rule
  in commit `7d2767f`.
- **Slice:** R&H digitize/audit-digitization 2026-06-03 (`wf_af0bce49`) + faithfulness audit
  2026-06-04 (`wf_a6f22cb4`). Counts are anecdotal (one figure + one migration); not a rate.
- **Quote ledger:** `../evidence/E8.quotes.jsonl` — 7 quotes, verified verbatim by
  `verify_quotes.py E8` (7/7, exit 0).
- **Refs:** commit `7d2767f` (`skills/extract-figure/SKILL.md`, `skills/audit-digitization/SKILL.md`,
  `neuromodels/framework/figures/digitize.py`) · memory `saturation-is-the-genealogy-blocker`,
  `vlm-eye-is-arbiter-over-tools`.

## Links

- `shared-root → S2` — the R&H normalization/saturation surface is a repeatedly-touched,
  paper-underdetermined area; E8's per-panel-vs-shared-scale call lives on it.
- `connects-to → E3` — the digitizer self-grading its default-normalized output as fine is the
  digitizer-side analogue of rubber-stamping a tool/VLM output.
- `connects-to → E7` — both are *axis/scale*-fidelity failures: E7 lets a fit-scaled axis hide a
  magnitude error; E8 lets a per-panel auto-normalization erase a shared-scale claim.

## Deeper-dig hook

Isolate the pre-fix R&H digitize transcript (the one the commit says pinned to 1.0) to read the
original self-grade. Then sweep other shared-scale multi-panel figures (e.g. other R&H/heeger CRF
sets) for digitize/render outputs whose panels all top out at exactly 1.0 — a fingerprint of the
default override. Data: `models/reynolds_heeger_2009/` digitization artifacts +
`neuromodels/framework/figures/digitize.py`.

## Status

`mitigated` — extract-figure and audit-digitization now forbid per-panel max→1.0 where the paper
shares a scale ("if the paper's curves don't reach 1.0, yours must not either"), and the audit
verified sub-1.0 plateaus; the same default re-surfaced once on the render side and was caught.
Recurrence rate uncharacterised.
