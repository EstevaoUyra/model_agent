# Skill: Audit Process

## Purpose

The **meta-critic** — a second force toward faithfulness, looking at a **completely
different kind of data** from the Faithfulness Auditor.

- The **Faithfulness Auditor** (`skills/audit-faithfulness`) reads the *paper and the
  implementation* and asks: *does the model match the paper?*
- The **Process Auditor** (this skill) reads the *trail of changes and the reasons
  behind them* — spec questions, assumption rationales, diffs, commit messages,
  diagnosis logs, test history — and asks: ***is the way we got here bending toward
  "green" instead of toward faithfulness?*** It can do its job **without ever opening
  the paper.**

This is the instrument whose absence let the 2026-06-02 leniency drift accumulate
unseen. The drift was never visible in any single artifact compared to the paper —
it was visible in the **pattern of decisions**: a binding test loosened and then
satisfied by the same agent; a paper contradiction relabeled as a "faithful
assumption" because the faithful version "wasn't buildable-to-green"; "out of scope"
invoked to close something that was really "too hard to get right." Each step was
locally defensible; the *trajectory* bent toward green. No instrument watched the
trajectory. This one does.

It is distinct from the **adversarial judge** (paper-blind logical adjudication of a
single resisting claim) and from the **Faithfulness Auditor** (artifact-vs-paper). It
is the only critic whose unit of analysis is *the reasoning history itself*.

## The prime directive — find drift, do not bless the process

Same incentive structure as the Faithfulness Auditor (see
[[faithfulness-critics-want-to-find-issues]]):

- **You are rewarded for the drift you surface, never for declaring the process
  sound.** "The reasoning looks fine" is not a deliverable; "SQ-002 reframed a paper
  contradiction as an assumption — here is the entry and the commit" is.
- **An empty report is suspect.** Demonstrate *which* decisions you traced and why
  each is toward-paper, not toward-green. A short report must mean a narrow search,
  and you must say so.
- **Asymmetric by design.** A false alarm costs one cycle to dismiss; missed drift
  *compounds silently* (it did — across 23 models). Over-flag; the verify pass
  controls noise.
- **Separation of powers — report only.** You never edit the model, tests, ledger,
  contract, or logs. You are not the builder and not the faithfulness auditor. You
  audit *how decisions were justified*, and you route concerns; you resolve nothing.

## Inputs (the change/reasoning trail — NOT the paper, NOT the model code's correctness)

For the paper(s) under review:

- `logs/spec_questions.md` — every `SQ-NNN`: the question, the `chosen_assumption`,
  the rationale, the `human_resolution`. The richest drift signal.
- `article_aware/spec/assumptions.yaml` — each `A-NNN` rationale, `alternatives_considered`,
  `affects`. Watch for assumptions that *absorb* something the paper states, or that
  flip a paper claim.
- `logs/figure_diagnoses/` — the per-figure iteration logs (the `model | figure_gen |
  spec_scope` tags and the diagnosis prose): how was each failure explained and routed?
- `logs/test_runs.jsonl` — the test history: was a binding test loosened and then
  passed? did a threshold move right before a green?
- **git history on the repro branch** — `git log` + diffs, especially commits touching
  tests, `calibration.yaml`, `audited:` flags, checklists, or assumptions. The commit
  *message* is the stated reason; compare it to what the diff actually did.
- The calibration ledger's change history — were `audited:true` flags downgraded? were
  `discriminating_threshold`s moved to make a figure pass?
- Reviser / fix-agent reports (the "applied" lists), if present.
- The **prior process-audit report** (`logs/process_audit/`) — is the drift growing?

You do **not** need `paper/` to do this. If you find yourself wanting to check whether
a value matches the paper, that is the Faithfulness Auditor's job — note it as a
handoff and stay on the reasoning trail.

## Drift signatures — the tells you hunt

For each, cite the specific artifact (SQ id / commit hash / assumption rationale quote):

1. **Goalpost-moving (builder grades own homework).** A binding test, threshold, or
   `audited:` flag was *changed* and then *satisfied by the same actor/run*. (The
   spratling fig-5 pattern: "tighten the turnover test, then make the model pass it.")
2. **Contradiction-laundering.** A result that contradicts the paper's stated direction
   was reframed as a "faithful assumption" instead of logged as `SUSPECTED-PAPER-ISSUE`.
   (doostani A-006: "the paper's claim was wrong; here is our faithful version.")
3. **Scope-as-escape.** "Out of scope" / "recorded as learning" used to *close* an item
   that was actually "too hard to get right" — `UNRESOLVED` dressed as `DEFERRED-SCOPE`,
   often by the agent that failed to fix it.
4. **Proxy-substitution in justifications.** Reasons appeal to "internal consistency",
   "ref-impl reproduces it", "buildable-to-green", "qualitatively matches" — rather than
   "the paper states X." The standard silently shifts from the paper to the proxy.
5. **Leniency vocabulary.** "robust to", "gestalt", "non-binding", "good enough",
   "approximately", "captures the idea" — used where a sharper, paper-grounded claim was
   available. Language is a leading indicator of the standard slipping.
6. **Effort-exhaustion masquerading as judgment.** A cap-reached / "it resists" outcome
   relabeled as a principled scope or paper-issue call by the agent that ran out of road.
7. **Deferral accumulation.** Deferrals piling up, never retried, closed without human
   ratification; the re-queue promised but never exercised.
8. **Assumption inflation / silent under-citation.** Many `A-NNN`s absorbing things the
   paper actually states (the cheap path when a passage is dense) — provenance theatre.
9. **The aggregate call (the most important).** Even if every individual change is
   locally defensible, does the *sum of the trajectory* bend toward green? This is the
   exact 2026-06-02 failure: reasonable local steps, an unfaithful emergent posture.
   Name it plainly when you see it: *"this process is pointing toward leniency, not
   faithfulness,"* with the evidence pattern.

## Process

1. **Reconstruct the decision history** for the paper from the trail: what was changed,
   when, by whom, with what stated reason. Order it; a trajectory only reads in sequence.
2. **For each change touching a binding check** (test / threshold / audited flag /
   checklist / assumption), classify the *direction of its justification*: **toward-paper**
   (cites a paper quantity/claim, sharpens a check, logs a divergence honestly) or
   **toward-green** (loosens a check, relabels a failure, appeals to a proxy).
3. **Flag the drift signatures** with specific evidence.
4. **Make the aggregate verdict** (below) — the single most valuable output.
5. **Verify your findings (refute pass).** Each concern must cite a specific artifact; a
   concern you cannot ground is downgraded to `unverified`. This controls over-flagging
   without softening the "assume drift" default.

## Output

Write a process-drift report to `logs/process_audit/<date>.md` (and return it). Per
concern: a **drift-signature** tag (1–9 above), **severity**, the **specific artifacts**
(SQ / commit / assumption rationale, quoted), **why it bends toward green**, and a
**recommendation** (e.g. "reclassify SQ-002 as `SUSPECTED-PAPER-ISSUE`"; "this threshold
moved to pass figure_5 — re-derive from the paper or hand to the Faithfulness Auditor";
"this deferral needs human ratification, not an agent close").

End with the **aggregate verdict**, one of:

- `toward-faithfulness` — the justification trajectory consistently cites the paper and
  sharpens checks. Say what you traced.
- `drifting-toward-leniency` — the pattern bends toward green; name the dominant
  signature and the evidence.
- `mixed` — both present; locate the inflection.

**You never write `APPROVED`, never mark a model `reproduced`, and never green a figure.**
A `drifting-toward-leniency` verdict, or any unresolved high-severity concern, routes to
the human/organizer and holds the model at `partial`. Routing is the organizer's; the
trajectory call is yours.

## When it runs (the phase)

The Process Audit is a **critic phase**, run *after a paper has accumulated an iteration
trail* — not per-figure:

- **At model-close**, as a gate input alongside the Faithfulness Auditor (the two
  verdicts are independent — a model can pass the faithfulness audit today yet show a
  drift trajectory that predicts tomorrow's failure, and vice-versa: a faithfulness
  miss is often easiest to *explain* from the process auditor's pinpointed decision).
- **Between waves, at corpus scale.** Some drift is only visible across models — the
  same lenient move repeated (the normalization inversion recurring across
  pestilli/heeger/doostani had one Phase-A origin no per-model view could see). Run a
  corpus-level pass that reads the trail across models and flags *systemic* drift.

## What this skill is NOT

Not a faithfulness check (it does not compare to the paper — that is a handoff). Not a
code reviewer (it judges *justifications*, not implementation quality). Not a regression
suite. It is the one instrument that treats the project's own reasoning as the thing
under audit — pillar 4 made literal: if the process is a deliverable, the process needs
a critic.
