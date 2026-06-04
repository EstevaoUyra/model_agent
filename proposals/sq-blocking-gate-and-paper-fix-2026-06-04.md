# Proposal: SQ as a blocking fault + the paper-fix route + a Phase-A auditor

**Date:** 2026-06-04 · **Status:** PROPOSED · **Origin:** the RH2009 suppression
post-mortem — a contract bug that was *captured honestly five times* (SQ-001 →
SQ-005) but *never resolved*, because the process has capture machinery and no
resolution machinery.

## The failure this fixes
The suppressive-drive geometry was wrong (a 1D normalization measure; S came out
far too small → CRFs wouldn't saturate). It was flagged on day one (SQ-001,
2026-04-28) and parked behind a never-built "pending human review" gate. The
implementation kept **looping** around it, tuning a per-figure
`suppressive_drive_gain` (4 → 12 → 16) to force the curves over — a *model-level*
fault patched *per-figure*. Green figures + green tests made it look done until
it finally hit STUCK at SQ-005. Two structural holes:
1. **An SQ doesn't block anything** — it's a passive note the loop tunes around.
2. **The contract is never independently audited** — only rendered figures are,
   so the wrong geometry survived in the spec until it surfaced as a figure
   symptom (and got mis-fixed).

## The change

### 1. SQ becomes a blocking circuit-breaker — and the audit auto-fires it
The implement phase's exit condition stops being "tests green" and becomes:

> **tests green AND no open in-scope SQ AND no load-bearing `audited:false` value
> AND no `CONTRACT_BUG`/`PAPER_ISSUE` audit finding.**

You cannot loop the implementation to a "faithful" state while the contract is
faulted. (The `audited:false` clause catches the silent-knob dodge: an unaudited
load-bearing value a figure depends on *is* an unresolved contract question, even
if no SQ was filed.)

**The audit is a first-class SQ source, and a new SQ auto-fires paper-fix.** SQs
are raised both by the implementer *and* by the audit (figure faithfulness +
`audit-spec`). After **every** implement+audit cycle, route by finding tag —
automatically, with no manual decision and no implementer patch in between:
- **`CONTRACT_BUG` / `PAPER_ISSUE` / any newly-filed SQ** → the *spec* is wrong →
  **auto-trigger the paper-fix route.**
- **`CODE_BUG`** → the *implementation* is wrong → back to the implement loop.

**Priority — contract first, never implement with an open SQ (point 3).** Within a
cycle, a spec fault is resolved (paper-fix) and re-audited *before* any
implementation runs. The loop only builds a `CODE_BUG` once the contract is clean.
You can never reach the implement step while an SQ is open.

This is the edge RH2009 got wrong: audit-r0 found "CRFs don't saturate" — a
`CONTRACT_BUG` (wrong geometry) — but it was handed to the implementer, who
treated it as code-level and tuned a gain. Under this rule that finding auto-fires
paper-fix and never reaches the gain knob.

### 2. Blocking scope: model-fault → all figures; figure-fault → one figure
Read scope from the SQ's `spec_ref`:
- **model-level** (shared forward model, a core `EQ-NNN`, `model.*` calibration —
  e.g. `pipeline.compute_suppressive_drive`) → **block every figure**. This makes
  the per-figure-knob hack *impossible*: a model-level fault can only be cleared
  by fixing the model, not by tuning figure-local parameters.
- **figure-level** (a per-figure protocol / override — e.g.
  `figure_7.visual_checklist`) → block that figure only; others proceed.

### 3. The paper-fix subroutine (triggered by a blocking SQ)
A terminating, ground-truth-first resolution route — **≤ `MAX_PAPERFIX` (2)
iterations**:
1. **Use already-acquired ground truth.** Phase 0 ran `acquire-sources` once;
   read `paper/code/` + `SOURCES.md`. **Do not re-acquire** (re-fetch only an item
   in the SOURCES.md *"exists-but-not-obtained"* gap list).
2. **Independent resolver corrects the spec via a RESOLUTION LADDER — human last
   (point 1):**
   (1) this paper's code/supplement → `CODE-NNN`;
   (2) **related genealogy papers via lineage → `LINEAGE-NNN`** (a `PAPER_ISSUE`
   is usually resolvable from a related paper, so it goes through the ladder, not
   straight to a human);
   (3) a **human decision — last resort only.**
   A `CONTRACT_BUG` unresolved by (1)/(2) → open SQ, BLOCKED. A `PAPER_ISSUE`
   unresolved by (1)/(2) → **dispositioned as a documented paper defect** (flagged
   + human decision-request with owner+expiry) — a FAITHFUL state, not a block.
3. **`audit-spec` verifies the correction** — builder ≠ resolver ≠ auditor.
4. **Return to implement** against the corrected contract.

**Hard exit (point 2).** If the Phase-A audit — the original gate *or* a paper-fix
`audit-spec` — does not pass within `MAX_PAPERFIX`, **the whole workflow exits
BLOCKED.** We never implement or render against a contract that could not be made
faithful; the run records the blocked state and stops.

### 4. A Phase-A auditor: the `audit-spec` skill (new)
The missing safeguard. `skills/audit-spec/SKILL.md` independently audits the
**contract** (equations, provenance tags, code-alone honesty, no figure-fitting,
`audited:false` residue, SQ dispositions, scope) against the paper + ground truth.
**One skill, two call sites:** a **Phase-A gate** after `extract-spec`, and the
**verify step** of the paper-fix route. Adversarial; report-only; never audits a
spec it authored.

### 5. Finalize on every exit — README-as-entrypoint + commit + PR (no exception)
Whatever the exit (normal, blocked-at-gate, blocked-at-paper-fix, or an unexpected
throw), the run ends in a single idempotent `finalize()` invoked from a
`try/finally` wrapper, so it cannot be skipped:
- **README always reflects state** — the per-figure reproduction views (paper ·
  digitized · implemented) + the changelog — *regardless of exit type*.
- **When the exit needs a human** (a paper-fix/audit block, or flagged
  dispositions), the README opens with a clearly-marked **"👉 DECISION NEEDED"**
  section: what is blocked/flagged, *why* (which audit / paper-fix), the open
  findings, and exactly where to look (`logs/spec_audit/`,
  `logs/faithfulness_audit/`, the SQ). The README is the human's entrypoint.
- **Everything is committed, pushed, and PR'd — without exception.** The model
  repo's remaining work is committed (and pushed if it has a remote); the parent
  repo bumps that submodule pointer, commits, pushes, and opens/updates a PR whose
  body is the entrypoint summary. The PR is the durable human entrypoint.

> Note: this makes **every** full-pass run push and open/update a PR — an
> outward-facing side effect by design.

## Control flow (fresh `from="extract"` pass)
```
Phase 0  acquire-sources (once per paper)
Phase A  extract-spec → audit-spec (gate)              ← NEW; a finding here → paper-fix
         digitization gate (figures)
Implement → audit (figures + audit-spec)               ← the audit is an SQ source
   exit ONLY if: green AND no open in-scope SQ AND no load-bearing audited:false
                 AND no CONTRACT_BUG/PAPER_ISSUE finding
   else, every cycle — CONTRACT FIRST (never implement with an open SQ):
     CONTRACT_BUG / PAPER_ISSUE / new SQ → paper-fix ladder → re-audit (do NOT implement yet)
     CODE_BUG (only once contract is clean) → implement
   paper-fix ladder (≤MAX_PAPERFIX):  scope = model? block ALL figures : block that figure
        1. paper code/supplement     → CODE-NNN
        2. related genealogy papers  → LINEAGE-NNN   (human = last resort)
        3. audit-spec verifies       ← same Phase-A auditor → return to implement
   audit-spec NOT faithful within MAX_PAPERFIX (gate OR paper-fix) → WHOLE WORKFLOW EXITS, BLOCKED
Verify   figure faithfulness audit
Report   finalize() — runs on EVERY exit (normal · blocked · thrown), via try/finally:
           (1) update-state README = current figure-reproduction state + changelog,
               + a "👉 DECISION NEEDED" entrypoint on top when the exit needs a human;
           (2) commit ALL remaining work + push + open/update PR (PR body = the entrypoint).
           WITHOUT EXCEPTION.
```

## What it would have prevented
SQ-001 (model-level) would have **blocked every CRF figure** the day it was
raised. No per-figure gain could clear it. The paper-fix route would have pulled
the authors' code (as it just did for SQ-005), corrected the suppressive geometry,
`audit-spec` would have verified it, and implementation would have resumed against
a correct contract — in April, not after a six-week gain-knob spiral.

## Guards
- **builder ≠ resolver ≠ auditor** throughout (the heeger-drift lesson).
- **Perverse-incentive guard.** Blocking-on-SQ could tempt hiding a divergence.
  Countered by (a) the independent figure + spec audits treating an *unregistered*
  divergence as a violation, and (b) the `audited:false` exit clause catching the
  silent knob. Filing the SQ must stay the lower-friction path.

## Build status
- **Exists:** `acquire-sources` (Phase 0), the `CODE-`/`LINEAGE-` provenance
  ledgers + `check_citations` + `neuromodels provenance`.
- **New here:** `skills/audit-spec/SKILL.md` (drafted); the SQ-blocking exit
  condition + model/figure scope + the paper-fix subroutine, to be wired into
  `.claude/workflows/full-pass.js`.
