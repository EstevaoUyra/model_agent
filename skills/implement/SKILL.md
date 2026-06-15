# Skill: Implement

## Purpose

**Phase B — build the model.** Turn the `article_aware/` contract into a working
implementation, iterating **locally against the tests** until they pass. You are the
*builder*; you are **paper-blind** by construction, and a separate
[`audit-faithfulness`](../audit-faithfulness/SKILL.md) critic — never you — certifies the
result. Your job is a faithful, readable implementation of the **mechanism the contract
specifies**, and an honest report of what the tests say.

## The wall — you never read `paper/`

The whole approach collapses if the builder peeks at the paper. Build from `article_aware/`
**only**: the spec, the pseudocode, the calibration ledger, the digitized references, and
the tests. If something you need is not in the contract, it is an **underspecification** —
log a spec question (`logs/spec_questions.md`), do not go read the paper and do not invent.
This is what keeps the reproduction honest: the faithfulness reasoning was done by the
paper-aware roles; you implement the mechanism and report what emerges.

## What you build (and what you must not touch)

**Build it yourself, from scratch.** Implement every stage from *this* contract — do
**not** import or copy another model's implementation during the build, even for a stage
the spec marks as shared/lineage. An independent build is what makes the reproduction a
real test of the paper; a reused forward model just *assumes* the other paper equals this
one (and inherits its bugs). Cross-model reuse is a **separate, later, audited** step
(WORKFLOW §4d → the `audit-reuse` skill), done only after this model is faithful on its
own — never part of getting it working. If the spec points at an ancestor's stage, still
build your own and flag the intended reuse as a spec question for the later reuse pass.

- `implementation/src/<pkg>/` — the model (`model.py`), `protocols.py`, `measurements.py`.
  Structure it as a readable stage pipeline; a scientist should read a stage and see the
  science (Pillar 2). Each protocol → measurement → a **record** the view plots.
- **Every function carries a `Citation:` or `Assumption:` docstring** resolving to a ledger
  entry. No exceptions — it is checked.
- **Do NOT touch `article_aware/`** (the contract — spec, tests, pseudocode, the view). The
  **view is Phase-A-owned**: you produce the measurement *record*; the view renders it. If
  the figure looks wrong because of axes/scale/normalization, that is a **contract** matter
  (a finding for Phase A), not something you fix in the view.
- **Render every in-scope figure to a COMMITTED `figures_reproduced/figure_<N>.png`** — this is the
  README's "implementation" view and the coverage gate's render artifact (`tools/check_figure_coverage.py`).
  `implementation/figure_outputs/` is **gitignored scratch**; a render left only there (or committed under
  `figure_outputs/`) is invisible to the README and fails the gate. Promote each fresh render to
  `figures_reproduced/figure_<N>.png` and commit it. One figure → one canonical file.

## Iterate locally — the inner loop (no VLM)

You are expected to **churn**, not stop at the first attempt:

> edit → `pytest` (the deterministic + three-tier + audit-derived tests) → read failures →
> edit → … until the **must-pass** tests are green, or you are genuinely stuck.

The must-pass tests encode the paper's values (a separate test-author wrote them from the
audits); driving them green *is* the work, and you do it without a VLM in the loop. Run the
suite yourself; do not declare done on one attempt.

## The guard — implement the mechanism, never fit the figure

This is the line that separates a faithful build from a laundered one:

- Drive the **MUST-PASS** tests green **by implementing the spec'd mechanism** — the correct
  equation, the correct parameter from the ledger, the correct condition mapping.
- **Leave the intended-failure tripwires RED.** They mark genuine divergences (a faithful
  mechanism that still misses the figure's magnitude). Making one green by tuning is
  **overfitting the reproduction** — the exact failure (`SQ-004`, the wrong Fig-4C sign) this
  whole pipeline exists to prevent.
- **Never tune an `audited:false` knob to make a curve bend the way you want.** If a must-pass
  test resists the correct mechanism, that is a **spec question or a real finding**, not a
  hack — log it and stop; do not force green.

## When you are stuck

Honor the iteration cap. A must-pass test you cannot satisfy with the cited mechanism is
**escalated** (a `spec_questions.md` entry; deferred to a later pass), never forced. A
`STUCK` outcome is a legitimate, honest result — it routes to the human/organizer, who may
find the *contract* is wrong (the auditor's `CONTRACT-BUG`), not your code.

## Commit when done

When your iteration settles — must-pass tests green, or a `STUCK` escalation logged —
**commit your changes** on the working branch with a message stating *what you built/changed*
and *the resulting test state*. The process-auditor reads that message against your diff, so
the stated reason must match what the diff actually did.

## What this skill is NOT

You never write `APPROVED`, never mark a figure faithful, never edit a test to make it pass,
never read the paper. You build the mechanism and report the test state; the separate
faithfulness + process auditors judge it.
