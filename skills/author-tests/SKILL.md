# Skill: Author Tests (from audits)

## Purpose

Turn a faithfulness auditor's findings into **deterministic tests**, so the paper-blind
implementer can **iterate locally** (`edit → pytest → repeat`) and close the divergence
*without a VLM in the loop at every step* — the VLM re-audit then runs only once the local
suite is green. You are the bridge that carries the paper's values (which the auditor read)
into Phase B's paper-blind world, as machine-checkable assertions.

You write **tests only**, in `article_aware/extracted_data/` (the contract). You do **not**
touch `implementation/src/`, and you do **not** re-judge the model — you encode the auditor's
findings faithfully.

## The two kinds of test — and why the split is the whole point

Each finding from [`audit-faithfulness`](../audit-faithfulness/SKILL.md) carries a **tag**.
**Respect it** — it decides whether the implementer is *allowed* to drive the test green:

- **`*_BUG` (CONTRACT-BUG / CODE-BUG) → a MUST-PASS test.** The model *should* reproduce
  this; encode the **expected value + tolerance from the finding** as a deterministic
  assertion on the implementation's measurement record. The implementer drives it green by
  implementing the correct mechanism. This is a legitimate, paper-grounded target.

- **`GENUINE-DIVERGENCE` / `SUSPECTED-PAPER-ISSUE` → an INTENDED-FAILURE tripwire.** A
  faithful mechanism still misses this (a magnitude the cited parameters don't produce, or a
  paper contradiction). Encode it **red** (`pytest.mark.xfail`/soft tier), documenting the
  gap and the *expected* paper value, so it **flips green only if the model genuinely
  improves** — a progress signal, never a fit target.

> **The cardinal error: do not make a genuine divergence a MUST-PASS test.** That hands the
> implementer a target it can only hit by tuning a parameter to fit the figure — re-creating
> the exact laundering (`SQ-004`, the wrong Fig-4C sign) the pipeline exists to prevent. If
> the auditor tagged it `GENUINE`/`PAPER-ISSUE`, it is a tripwire, full stop.

## How to write each test

- **Evaluate on the implementation's measurement record**, with the expected value/threshold
  **digitized from the paper / read by the auditor** (the finding gives it) — never on the
  same record the model draws from (that would be a self-consistency tautology, not a
  fidelity check).
- **Verify the target before you encode it.** The expected value must trace to the finding's
  evidence (a paper quote, the digitized reference). If the finding's number looks off,
  **flag it back** — do not encode a wrong target the implementer would then chase.
- Give each test a stable claim id and a one-line docstring tying it to the finding; tier it
  (`qualitative`/`hard`/`soft`) per the finding's confidence, following
  [`extract-figure`](../extract-figure/SKILL.md)/WORKFLOW §3b conventions.
- A must-pass test must be satisfiable by the **correct mechanism alone** — if the only way
  to pass it is to tune, it is mis-classified; make it a tripwire and say so.
- **When the paper's figure axis is a meaningful or fit-to-data scale (e.g. a d′ fit to
  behavior), assert ABSOLUTE magnitude (value within tolerance), not only shape/correlation —
  a 4× scalar must FAIL.** Shape-invariant tests (correlation, dip-location, peak-position)
  let a curve that is the right shape but 4× too high pass. denison2021 Fig 5 had shape-corr
  0.97 yet sat 4× too high; its scale-invariant shape tests all passed and the magnitude was
  waved off until an adversarial audit caught it. Add an absolute-magnitude assertion
  alongside any shape test on a data/fit-scaled axis.

## Commit when done

**Commit the new/updated tests** on the working branch with a message naming the findings
they encode and which are must-pass vs tripwire. The process-auditor reads it against the
diff, so the message must match what you actually wrote.

## What this skill is NOT

Not the auditor (you don't find divergences — you encode the ones found). Not the
implementer (you never touch `implementation/src/`, and you never write a test you then make
pass). Not a re-judgement — if you disagree with a finding's value, you flag it, you don't
silently re-tag it.
