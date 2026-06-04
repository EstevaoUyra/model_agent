# Human spec-review packet: divisive-normalization saturation across the attention-normalization genealogy

**Date:** 2026-06-04 · **Owner:** human spec-review / Faithfulness Auditor (NOT a paper-blind builder, NOT the organizer unilaterally) · **Status:** OPEN

Three models in the attention-normalization genealogy block (or drift) on the **same theme** —
divisive-normalization *saturation/width* cannot be reached on the shipped normalization mechanism
without an unaudited choice. Surfaced 2026-06-04 by hardened full-passes on `heeger_1992` and
`hermann2010` run after `reynolds_heeger_2009` blocked. They are **not one knob** — there are two
distinct quantitative decisions below — but they share an owner and a root surface (the R&H
normalization implementation), so they should be decided together, once.

---

## Decision Q1 — Suppression-saturation on the R&H normalization surface (RH2009 + hermann2010)

**Coupling:** `hermann2010` is built **on the R&H reuse surface** (its `calibration.yaml` says so and
routes the fix to "reynolds_heeger_2009 / raise the R&H saturation gain"). So RH2009's blocker
propagates into hermann — one root cause, two models.

**Symptom:** the 1D-discretized R&H divisive normalization cannot reach the paper's CRF plateau.
- RH2009 `SQ-005`: the contract's 2D-plane suppression fix (A-006) makes the suppressive drive S
  *smaller*, not larger (measured 1D S/AE ≈ 0.243 vs genuine-2D ≈ 0.059), so it cannot deliver
  saturation. **STUCK.**
- hermann2010 `NF1`: Fig-1a response-gain CRFs do not saturate; `suppressive_drive_gain` was
  re-slaved 4→16 for Fig-1b convergence (0.954 vs digitized 0.9915, ~4.6% residual the 1D mechanism
  "cannot fully close"). The response-gain twin is **STILL BROKEN**; builder left it RED, escalated,
  no force-green.

**Choose one (applies to the shared surface):**
- **(a) Audited saturation constant** — add a single audited `model.suppression_normalization` κ /
  saturation gain to the R&H spec calibration ledger, evidenced against the paper, shared by both
  models. (Cleanest if a paper-grounded value exists.)
- **(b) Mechanism is wrong** — revise A-006/A-013: the 1D reduction of the 2D suppressive field is
  the defect; specify the genuine-2D pooling. Reclassify the RH2009 MUST-PASS accordingly.
- **(c) Stimulus geometry** — revisit the cited `σ_space=20` / `stimulus_size` that set the
  pooling ratio.

**Do NOT** let the organizer or a builder "just raise the gain" — that is exactly the
goalpost-move the process auditor exists to catch. The digitized references (RH2009 Fig-1b 0.9915,
hermann att_lq 0.017) are the ceiling-of-evidence, not the mechanism's reachable plateau.

---

## Decision Q2 — heeger_1992 operator orientation width Vₑ (already adjudicated; needs sign-off)

**Distinct from Q1** (this is orientation *width*, not the CRF gain), included because it is the same
class: a saturation/width quantity that is paper-underdetermined and was drifted toward green.

**Adjudicated 2026-06-04 by an independent auditor** (report:
`models/heeger_1992/logs/faithfulness_audit/sq005_independent_adjudication_2026-06-04.md`,
commit c871dfd). Verdict: **C — irreducible paper-issue.**

- p.184 literally binds "60 deg" to "each **filter**" (= operator Vₑ → plotted bell 42.4°), but the
  paper's own Fig 5C draws a ~56° bell, which no Gaussian Vₑ=60 can produce. Genuine text-vs-drawing
  contradiction.
- The drawn panels imply **Vₑ ≈ 76–80°** (5C→79.8°, 6B→75.8°). The **shipped `84.853 = 60·√2` is
  faithful to neither horn** — it fits the literal text *number* and over-widens every drawn panel.
- The shipped note ("matches BOTH … no contradiction, just a mis-mapping") is **laundering** and
  should be rejected. The "RESOLVED" reversal was builder-grades-own-homework (process auditor:
  DRIFTING, high severity — the binding operator-width test Q-506 was deleted, 3 tripwires flipped
  to green in the same same-author session).

**Recommended human disposition:** reopen `SQ-005` as flagged SUSPECTED-PAPER-ISSUE (not RESOLVED);
model stays **PARTIAL**; restore the deleted operator-width discriminator; if the drawing-horn is
chosen, set `linear_operator.fwhm_ori_deg = 79.0`, `audited:false`, with a note that **explicitly
states it violates the literal "filter orientation range 60 deg" clause** (not 84.853, which is not
drawing-faithful).

---

## Cross-cutting note (not a decision, a watch-item)
Both `hermann2010` Fig 3 and `carrasco2021` ship **ILLUSTRATIVE-NOT-REPRODUCED** panels that
hand-enter the paper's headline fit values instead of fitting them. The Step-4 constructed-result
check catches these; flag as a genealogy-wide habit to watch, not a per-model bug.

---

## What is NOT yet done (left for human sign-off)
Nothing above has been applied to any model. Branches `full-pass/heeger_1992-20260603` and
`full-pass/hermann2010-20260603` are unmerged; the heeger drift state (84.853 / "RESOLVED") is still
on its branch, with the independent adjudication committed alongside it as the binding record.
