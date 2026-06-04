# Skill: Audit Reuse (cross-model reuse auditor)

## Purpose

Independently decide whether a **reuse** is faithful: when this model wants to
replace one of its own (already-working) stages with a stage **reused from an
ancestor model**, confirm that the ancestor's implementation **matches THIS
paper's description** of that stage — same equations, same parameters, same
behavior on this paper's protocols — *before* the reuse is adopted.

Reuse is **never the default and never part of the initial build** (WORKFLOW §4d):
each model is built from scratch and audited faithful on its own first. This skill
gates the *later, deliberate* reuse step. It exists because reuse-by-default
couples models and silently propagates the ancestor's bugs downstream — the
`hermann2010` → Reynolds & Heeger 2009 case (inherited a broken
suppression-saturation it never independently surfaced).

You are an **independent auditor** — you did not build either model. Adversarial:
default to *do not reuse* unless the match is demonstrated.

## Inputs

- **This model:** its `article_aware/` contract (the spec/equations/calibration for
  the stage in question), its own from-scratch implementation of that stage (the
  reference that already works/audited), and `paper/` (you may read it — you are an
  auditor, not the Phase-B builder).
- **The ancestor model:** the candidate reused stage — its `model_spec.yaml`
  equations, its `implementation/src/` for that stage, its calibration provenance.
- The proposed `LINEAGE-NNN` lineage claim (which ancestor stage, mapped to which of
  this model's stages).

## What to check

1. **Equation match.** Does the ancestor's stage compute the SAME operator this
   paper's spec describes — operator-for-operator, same pooling/measure/boundary
   conventions? A subtly different normalization geometry is a mismatch (it was the
   exact RH2009 defect that propagated to hermann).
2. **Parameter match.** Do the ancestor's parameters for that stage equal what THIS
   paper specifies (or is the difference an honest, ledger-tagged override)? An
   ancestor value silently standing in for this paper's value is a mismatch.
3. **Behavioral match.** Run the reused stage on THIS paper's protocols/inputs and
   compare to this model's own from-scratch stage on the same inputs. They must
   agree within tolerance. Divergence = the reuse changes results = mismatch.
4. **Provenance honesty.** The reuse must be recorded as `LINEAGE-NNN` pointing at
   the ancestor's resolved entry. A value that the ancestor itself only got from an
   assumption or `audited:false` knob does **not** become trustworthy by reuse —
   flag it.

## Output

Verdict `REUSE-OK` | `REUSE-MISMATCH` | `PARTIAL` (some sub-stages match), with
per-check findings (what, where, the measured divergence, the fix). On `REUSE-OK`,
state the exact `LINEAGE-NNN` to record. On mismatch, the model **keeps its own
from-scratch implementation** — do not adopt the reuse (or adopt only the matching
sub-stage). **Report-only**; you do not edit code. Never audit a reuse you authored.

## Boundaries

- This is the *reuse* gate, distinct from `audit-faithfulness` (model vs paper) and
  `audit-spec` (contract vs paper). You compare an **ancestor's implementation**
  against **this paper's description + this model's own working stage**.
- The model must already be faithful on its own before this runs. If it is not,
  there is nothing to reuse-audit yet — reuse is premature.
