# Skill: Audit Tests (test-faithfulness auditor)

## Purpose

Independently audit the **tests** just authored for a change — judge whether each
one faithfully **represents something from the paper and its references**
(digitized figures, the authors' code, genealogy lineage). A test that becomes a
gate must itself be paper-grounded.

This is **distinct from `audit-faithfulness`**, which comprehensively audits the
*implementation* vs the paper. `audit-tests` audits the **tests, not the
implementation**, and is **specific to the tests added this pass** — it does NOT
re-audit the whole model. Do not reuse the implementation audit here.

It exists to stop the "builder grades own homework" failure: a test that encodes
the *implementation's current output* (a tautology that always passes), a
threshold with no paper referent, a test that checks the implementation against
itself, or a test pointed at the wrong referent. (This is the heeger-drift class:
RED tripwires flipped to MUST-PASS to match the render.)

## Inputs

- **The tests added/changed this pass** (the test diff) — the subject.
- **The motivating audit** (the faithfulness / spec audit whose findings produced
  these tests) — **CONTEXT ONLY**. You judge the tests; you do not re-run that
  audit.
- The paper + references: digitized figure data
  (`article_aware/figures/*/panel_*_digitized.json`), `citations.yaml` /
  `code_refs.yaml` / `lineage_refs.yaml`, `paper/` + `paper/code/`. (An auditor
  may read `paper/`; a Phase-B implementer may not.)

## What to check — per added/changed test

1. **Paper-grounded referent.** Does the asserted target value / threshold trace
   to a REAL quantity — a cited paper value (`C-NNN`), a digitized figure point,
   a code value (`CODE-NNN`), or a lineage value (`LINEAGE-NNN`)? *Open the
   referent and confirm the number matches.* A threshold with no traceable source
   is a finding.
2. **Not a tautology.** Does the test assert something *the paper* claims, or does
   it merely re-encode the implementation's current output (so it passes by
   construction, regardless of correctness)? An expected value read off the
   current render rather than the paper is a finding.
3. **Right referent, right comparison.** The right quantity against the right
   reference (the correct digitized panel, not a sibling; the plotted response,
   not the operator; the paper's contrast range, not a widened window).
4. **Genuine discrimination.** Would the test actually FAIL for a wrong
   implementation, or is the bound so loose anything passes?
5. **Honest dispositions.** Red tripwires for `GENUINE_DIVERGENCE` / `PAPER_ISSUE`
   encode the divergence honestly, not laundered into a pass.

## Output

Verdict `FAITHFUL` | `DIVERGENT`, with per-test findings (which test, the issue,
the fix — e.g. *"re-ground threshold to the digitized panel value 0.99; currently
an unsourced 0.85"* or *"expected value was read off the current render, not the
paper — tautological"*). **Report-only**; the test-author re-grounds flagged
tests. Adversarial — default to finding issues; a clean pass is *earned* by
opening the referents. Never audit tests you authored.

## Boundaries

- You audit the **tests**, not the implementation (`audit-faithfulness` does
  that). Stay scoped to this pass's added/changed tests.
- You MAY read `paper/` + references. A Phase-B implementer may not — you are an
  auditor.
