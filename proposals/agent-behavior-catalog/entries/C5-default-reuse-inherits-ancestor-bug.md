# C5 — A model built by default-reuse inherits its ancestor's bug

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · agent-behavior (builder / cross-model) |
> | Behavior | builds a new model by reusing an ancestor's stage by default, importing the ancestor's *implementation* (and its unverified defects) instead of re-deriving from this paper |
> | Symptom | hermann2010 consumes reynolds_heeger_2009's calibration "reuse surface" and inherits R&H's stale, non-saturating `suppressive_drive_gain` — the same divisive-normalization saturation defect, now a hermann bug |
> | Agent role | implement (builder) |
> | Trigger | a faithful-*looking* ancestor exists in the genealogy and the default architecture imports its stage rather than building independently |
> | Cause (evidence) | default reuse of a frozen, *itself-unverified* ancestor stage — *narration-shown* (the stale gain propagates) + *intervention-tracked* (eb83a14 codifies build-from-scratch-by-default) |
> | Detector | another agent (per-model audit flagged the inherited saturation divergence) + human (recognized it as a default-reuse process gap → eb83a14) |
> | Lever(s) | doc/spec (WORKFLOW §4d: from-scratch by default) + structural/role (new `audit-reuse` auditor) |
> | Flags | generative-root → S2 · shares the R&H saturation surface with S2/E2 |
> | Status | mitigated (rule + auditor codified; the later audited-reuse pass is not yet observed running) |

## The behaviour

hermann2010 reuses an upstream model, reynolds_heeger_2009 (R&H), for the divisive-normalization
machinery the two papers share. The reuse was the **default** architecture: hermann calls R&H's
`crf_protocol.run_crf` and reads R&H's calibration namespace directly, holding none of those knobs
itself. The builder narration states this plainly:

> *"The F1/Q-104 finding's root cause was the stale R&H `regime.contrast_gain.*` reuse surface that
> hermann consumes via `rh_model.crf_protocol.run_crf`."*

The problem: the ancestor it inherited from was **not itself faithful** on the reused stage. R&H's
`regime.response_gain.suppressive_drive_gain` was frozen at a pre-faithfulness value, and that stale
value flowed straight into hermann's curves, so hermann reproduced R&H's saturation defect rather
than this paper's behaviour:

> *"But `regime.response_gain.suppressive_drive_gain` is still at the stale value `4.0`. This is
> exactly what the three failing NF1 tests demand — re-slaving it to a corrected saturation gain."*

How far off the inherited value was is itself the evidence that the defect was inherited, not local:

> *"the response-gain `suppressive_drive_gain` must be raised to **~150** — about 37x the original
> Fig-2B-family value (4)"*

So a "new" model's faithfulness was hostage to an upstream model's *implementation* — exactly the
hazard of reusing an ancestor's code instead of re-deriving the mechanism from the paper.

## Why it did it (graded)

- **Default reuse of an unverified ancestor stage** — *intervention-tracked (strong).* The fix
  commit (eb83a14) names the cause directly: hermann "reused R&H 2009 by default and inherited its
  broken suppression-saturation." The remedy it codifies — from-scratch by default, reuse only as a
  later *audited* step — is the inverse of the observed move, which is the standard intervention-
  tracked evidence pattern.
- **The inheritance mechanism is shown, not just asserted** — *narration-shown.* The builder's own
  words trace the stale ancestor value propagating into hermann's failing tests (quotes above). The
  saturation mechanism is recognised as shared with the ancestor: *"It's the same saturation
  mechanism the paper requires (`R&H raised figure_2B 4→6 for exactly this reason`)."*

The deeper shape: **reuse is the low-friction default** — importing a working-looking ancestor stage
is cheaper than re-deriving it — but it silently transfers the ancestor's *unverified* state. When
the ancestor is mid-reproduction (R&H was itself STUCK), default reuse imports a bug.

## Relation to S2 (this is the generative root S2 sits on)

C5 and S2 are the same R&H saturation surface seen from two angles, and the catalog keeps them split
on cause:

- **C5 (here) — inheriting a broken *implementation* via default reuse.** One builder pulls the
  ancestor's stage and gets its defect for free.
- **S2 — the shared *decision* resolved N× independently.** The *paper-underdetermined* saturation
  choice surfaces across RH2009 / heeger / hermann and each loop re-litigates it locally.

C5 is the generative root: it is *because* models reuse the R&H stage that one underdetermined
saturation decision propagates across the genealogy and becomes S2's "resolved N times." Link:
`generative-root → S2`.

## How it responded to intervention

One lever, codified the same day the build exposed it (2026-06-04):

- **doc/spec** — WORKFLOW.md §4d (new): the default is an independent from-scratch implementation;
  cross-model reuse is a deliberate *later* step, allowed only after this model is faithful on its
  own **and** a reuse audit confirms the ancestor's implementation matches *this* paper. §4a
  tightened to point there; `skills/implement/SKILL.md` told to build it itself and flag any
  intended reuse as a spec question.
- **structural/role** — a new `audit-reuse` auditor that independently verifies a candidate reuse
  matches this paper's equations/parameters/behaviour before adoption (verdict
  `REUSE-OK | REUSE-MISMATCH | PARTIAL`, recorded as `LINEAGE-NNN`), explicitly a post-faithful step
  outside the per-model full-pass graph.

**Which held: unverifiable here.** The rule and auditor exist in the repo, but this catalog has no
observation of a later audited-reuse pass actually running the `audit-reuse` skill, so "did the fix
hold" is `[to-verify-on-deeper-dig]` — status is *mitigated by design*, not *validated by trial*.

## Confidence & threats to validity

Moderate-high on the mechanism, lower on generality.

- **Single genealogy.** All the evidence is the R&H attention-normalization family; "default reuse
  inherits the ancestor's bug" is observed once (hermann ⟵ R&H), so it is `happened ≥ once`, not a
  rate.
- **The ancestor was concurrently broken (confound).** R&H was itself STUCK mid-full-pass when
  hermann reused it; some of the inheritance is "reused a model that wasn't done yet," which is a
  *sharper* version of the hazard but means the clean "reused a finished-but-subtly-wrong ancestor"
  case is not isolated here.
- **"By default" is partly intervention-stated.** The narration shows hermann *consuming* the reuse
  surface and carrying "zero R&H discretization knobs by design"; that the reuse was the
  un-deliberated default (vs a chosen design) is the commit's framing, consistent with but not
  independently proven by the narration.
- `claude_model` constant `claude-opus-4-8` across all 30 hermann2010 agents — model-version
  confound ruled out.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-04 (early) | hermann2010 build consumes R&H's `regime.*` reuse surface; inherits the stale `suppressive_drive_gain` → saturation divergence surfaces in NF1 tests | corpus `wf_7f2034c2` (hermann2010 implement agents) |
| 2026-06-04 13:39 | Codify build-from-scratch-by-default + `audit-reuse` auditor + WORKFLOW §4d | `eb83a14` |

## Links

- `generative-root → S2` (shared-decision-resolved-N-times) — C5 is *why* the R&H saturation surface
  is shared across the genealogy; S2 is the symptom of re-resolving it per model.
- `connects-to E2` (leniency-drift / grading-own-homework on the heeger saturation knob) and the
  memory thread `saturation-is-the-genealogy-blocker` — same reuse surface.

## Deeper-dig hook

Search the corpus for any agent that ran `audit-reuse` / emitted a `LINEAGE-NNN` verdict (none found
in this slice) to test whether the codified later-audited-reuse step ever executed — that is the
only way to upgrade Status from *mitigated by design* to *validated*. Slice: `grep -rl "LINEAGE-\|REUSE-OK\|REUSE-MISMATCH" evidence/corpus-snapshot/`.

## Status

mitigated (codified; not trial-validated) · Domain Coordination.

---

## Evidence layer (for verification, not reading)

- **Source corpus:** hermann2010 build, workflow `wf_7f2034c2` (30 agents, all `claude-opus-4-8`).
  Quotes drawn from three `implement` agents: `agent-a7b84004b08d576b5`, `agent-afb61726f7b7da76e`,
  `agent-a991fdfe6014249d5`.
- **Quote ledger:** `../evidence/C5.quotes.jsonl` — 4 promoted quotes, verify with
  `python3 ../evidence/verify_quotes.py C5` (must exit 0).
- **Refs:** commit `eb83a14` (WORKFLOW §4d, `skills/audit-reuse/SKILL.md`, `skills/implement/SKILL.md`)
  · memory `saturation-is-the-genealogy-blocker` · sibling entry S2.
