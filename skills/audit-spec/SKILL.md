# Skill: Audit Spec (Phase-A / contract auditor)

## Purpose

Independently audit the article-aware **contract** — `model_spec.yaml`,
`calibration.yaml`, `assumptions.yaml`, `citations.yaml`, `code_refs.yaml`,
`lineage_refs.yaml`, and the `pseudocode/` protocols — against the paper and the
acquired ground truth (`paper/`, `paper/code/`, SI). It catches **contract bugs**
— a wrong equation, a wrong pooling geometry, an untraceable or contradicted
value, a model-level fault mis-scoped as figure-level — **before they propagate
into figures**, where they get papered over with per-panel knobs.

This is the safeguard that was missing: today only rendered *figures* are
independently audited, so a wrong spec (e.g. a suppressive-pooling geometry that
doesn't match EQ-6) survives until it shows up as a figure symptom and gets
mis-fixed. `audit-spec` audits the contract itself.

**Two call sites, one skill:**
1. **Phase-A gate** — after `extract-spec`, before implementation.
2. **paper-fix verify** — after the paper-fix route corrects a spec from ground
   truth, this independently verifies the correction (builder ≠ auditor).

The auditor is **adversarial**: incentivized to FIND divergences, never to pass.
Read the actual sources, never a builder's summary. Never audit a contract you
authored.

## Inputs

- `article_aware/spec/*` and `article_aware/pseudocode/*` (the contract).
- `paper/` including `paper/code/` and SI — the auditor MAY read all of it (it is
  **not** a Phase-B implementer; the phase wall does not apply to an auditor).
- For the paper-fix-verify call: the diff under review and the SQ it claims to
  resolve.

## What to check

1. **Equation / mechanism fidelity.** Each `EQ-NNN` in `model_spec.yaml` matches
   the paper's equations and — where acquired — the code. *Open the cited source
   and compare operator-for-operator.* (This is the check that would have caught
   the A-006 wrong suppressive geometry.)
2. **Provenance integrity.** Every calibrated value's `source:` tag must (a)
   resolve — run `python -m neuromodels.framework.static_checks.check_citations
   <model>` — and (b) be *correct*: open the cited `C-NNN` passage / `CODE-NNN`
   file:line / `LINEAGE-NNN` ancestor entry and confirm it actually supports the
   value. A tag that resolves but doesn't support the value is a finding.
3. **Code-alone honesty.** Values tagged code-alone (`CODE-NNN`, no `C-NNN`) must
   be surfaced as *paper-insufficient*, not laundered as paper-resolved. Where a
   code value **contradicts** the paper (e.g. `IthetaWidth=360°` vs a Table-1
   `180°`), the tension must be stated explicitly. Run `neuromodels provenance`
   and sanity-check the code-alone set.
4. **No figure-fitting in the contract.** A model-level quantity must be ONE
   value, not a per-panel knob. A per-figure parameter that substitutes for a
   model mechanism (the `suppressive_drive_gain` antipattern) is a finding.
5. **`audited:false` residue.** List every load-bearing `audited:false` value —
   each is an open contract question (a latent SQ) and must block per the SQ gate.
6. **SQ dispositions.** An SQ marked `RESOLVED` must be genuinely resolved by
   paper/code/lineage with `human_resolution` set — not "RESOLVED" while
   `human_resolution: <pending>`.
7. **Scope correctness.** Is each fault scoped right — model vs figure? A
   model-level fault (shared forward model / core equation / `model.*`
   calibration) patched per-figure is itself a finding.

## Output

A structured verdict — `FAITHFUL` | `DIVERGENT` | `BLOCKED` — with findings
(each: what, where `file:line`, severity, and the fix or the SQ it should raise).
**Report-only**: write to `logs/spec_audit/<stamp>.md` and commit on the working
branch. Do **not** edit the contract — findings route to Phase A / the paper-fix
resolver, never fixed by the auditor.

## Rules

- Adversarial; default to finding issues (see the separate-builder-from-critic
  convention). A clean pass must be *earned* by reading the sources.
- Independent: never audit a spec you wrote.
- You MAY read `paper/` and `paper/code/`. A Phase-B implementer may not — you are
  not one.
