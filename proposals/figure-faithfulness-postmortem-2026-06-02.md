# Post-mortem: why the verification gate passed unfaithful figures

*2026-06-02. Trigger: the user, inspecting boynton_2009, found that Figures 2/7/8
"have very clear problems" despite a green verdict. A corpus-wide Opus-vision
audit (paper-image vs reproduced, 77 in-scope figures across 23 models) then found
**49% major-or-wrong** (16 faithful / 23 minor / 33 major / 5 wrong) — and the only
two all-green models are the two with no paper image to check against. This is a
pillar-1 (faithfulness) failure, so the first task is to understand the **process**
failure (pillar 4), not to patch figures.*

## One sentence

We operationalized "faithful to the paper" as "conforms to a paper-blind
qualitative checklist," and the checklists — by design — excused the exact
quantitative and layout dimensions where the reproductions diverge (tuning width,
baseline, normalization convention, panel count); the VLM, though it had the paper
image open, was instructed to defer to those checklists. So **honest
implementations and an honest gate produced confidently-green figures that don't
look like the paper.**

## The evidence (primary artifacts, not inference)

**The gate's decision rule, identical across every wave** (wave1/2/3 +
final-batch Phase-B workflow scripts). Each of 3 independent VLM voters was told:

> open the GENERATED png and the PAPER figure, read `<figure>_visual_checklist.md`,
> evaluate every BINDING item (**honor non-binding/UNSURE — judge
> gestalt/shape/structure/relationships, not styling or absolute magnitudes the
> checklist excludes**). **PASS only if all binding items hold and the gestalt
> matches the paper.**

So the rule was `PASS ⟺ (all binding checklist items hold) ∧ (gestalt matches)`.
Both conjuncts are weak, and the voter was explicitly forbidden from failing on
"absolute magnitudes" or anything the checklist marked non-binding.

**The checklist excused the discriminating dimensions.** `boynton_2009`
`figure_7_visual_checklist.md`, verbatim, under "NOT binding (do not check / do not
fail on these)":

> ABSOLUTE response heights, **exact tuning width**, and the flank suppression
> magnitude (Gmin). … only the peak-raise + central-enhancement shape is binding.

Those excused items *are* the audit's findings: the reproduced curve is ~2× too
broad (excused: "exact tuning width"), sits on no baseline (excused: "absolute
response heights"), and inverts the normalization (excused: under "absolute
heights"; and the checklist never says *which* curve is pinned to 1.0). The
reproduction **passed its checklist honestly** — the checklist was the lenient
part.

**The checklist pre-blessed the spurious panel.** `figure_2_visual_checklist.md`
has a section literally titled "The difference curve (if plotted)". Every boynton
figure carries an "attended − neutral" difference panel the paper does not have —
because the Phase-A checklist invited it.

**Normalization convention was never specified.** The checklists say
"Y = normalized response" but never which curve = 1.0. Phase B chose neutral = 1.0;
attended overshoots past 1.0. The paper pins the *attended* peak to 1.0. The same
inversion recurs across all of pestilli, heeger 5, and doostani — a corpus-wide
convention gap with a single Phase-A origin.

## The causal chain (five links)

1. **Paper-blindness pushed the faithfulness criterion into a paper-blind proxy.**
   Phase B cannot see the paper, so "is this faithful?" had to be encoded as
   something checkable without it → a binary, qualitative checklist ("higher peak
   at 0°", "bell-shaped", "enhancement centered"). A paper-blind proxy
   *structurally cannot* encode "matches the paper's width / baseline /
   normalization."

2. **Checklists were authored for necessity + buildability, and excused the
   discriminating dimensions.** They were tuned so a paper-blind agent *could build
   to them* and a faithful figure *would* pass — but never validated for
   **sufficiency** (passing ⇒ looks like the paper). Width, baseline, absolute
   level, panel layout were marked non-binding precisely because they're hard to
   pin paper-blind.

3. **The VLM was leashed to the checklist, not to the paper.** It had the paper
   open, but the prompt made the checklist the standard and the paper merely
   context — and told it to honor the checklist's exclusions and judge "gestalt."
   Gestalt + excused magnitudes = a wrong-width, no-baseline, inverted-normalization
   bell curve passes.

4. **All three green lights read the same ruler.** Deterministic tests assert on
   the measurement record, which encodes the *same* qualitative claims as the
   checklist; the VLM checks the same checklist; the implementer self-checks against
   it too. Three independent-looking checks all descend from one lossy Phase-A
   encoding, so they agree with each other and with the build — and none of them
   measures distance to the paper figure.

5. **The verdict was asymmetrically tuned to avoid false-fails, which guarantees
   false-passes.** WORKFLOW.md: "*Stale figures cause false-needs-work, never
   false-green*"; "do not fail on a non-binding magnitude"; "partial is fine, never
   block"; "DEFER any figure that resists." The autonomous program's prime directive
   was *don't halt* — and a gate optimized to not-halt is a gate that passes.
   Throughput beat faithfulness, the one pillar meant to win every conflict.

## The single missing step

**Nothing in the pipeline ever compared the rendered figure to the paper image and
failed on divergence with authority over the checklist.** Phase A defines a proxy;
no step validated the proxy for sufficiency. The corpus audit run on 2026-06-02 is
exactly that missing step — it should be institutionalized, not run once.

## Provenance — how the anti-pattern crept in (nobody decided it)

The leniency was never a considered policy. It accreted from local fixes to the
*opposite* failure (false-rejects), with a cost-model imported from the wrong
domain. Two traceable sources:

1. **The WORKFLOW.md "never false-green" line** entered in one commit, `617bdaa`
   (2026-06-02): *"bell GREEN (figure_4 noise was a stale PNG…); strengthen
   stale-figure guideline."* A stale on-disk PNG made the VLM correctly reject a
   render whose underlying model was fine — a false-**reject**. The lesson written
   was "re-render first; stale = false-needs-work, never false-green." Narrowly true
   for staleness (an out-of-date render lags an improving model), it hardened into a
   general reassurance that false-greens don't happen.

2. **`skills/extract-figure/SKILL.md` line 136**: *"Prefer comparative claims over
   absolute ones where possible ('right stripe brighter than left' is more robust
   than 'right stripe has value 0.8')."* This is the origin of "exact tuning width —
   NOT binding." A normal testing instinct (comparative claims don't flake on
   scale/style) — but "robust to quantitative divergence" *is* the leniency, baked
   into the spec layer.

**The single conceptual error:** an inverted error-cost model. A CI test suite
rightly engineers against false-**fails** (flaky tests erode trust). A *faithfulness*
gate has the opposite asymmetry — a false-**green** ships an unfaithful model under a
"faithful" banner (pillar-1 violation); a false-red costs one re-check. Every retro
optimized against false-reds by CI reflex.

**Why it stayed invisible:** (a) "checklist == faithfulness" made every
"don't over-fail" instruction locally self-consistent with a false premise; (b)
during the autonomous run nobody compared to the paper — removing the human from the
verdict removed the only instrument not calibrated to the lenient proxy, so the
organizer optimized the visible signals (throughput, stuck-ness) while the real one
drifted. The fix must be a standing, paper-binding faithfulness instrument the
program cannot optimize away.

## Process implications (for the redesign pass — pillar 4)

1. **Invert the standard.** The paper image is the standard; the checklist is an
   aid. The faithfulness gate fails a figure that doesn't look like the paper
   *regardless of the checklist*. (Today: checklist binds, paper informs. Flip it.)

2. **Bind the dimensions the checklists excused** — they move from "NOT binding" to
   binding, checked against the paper image: normalization convention (which curve =
   1.0), tuning width / bandwidth, baseline / floor, panel count & layout (no panels
   the paper lacks; no missing model panels), axis range / scale / sign convention.
   *Note the user's scope ruling (2026-06-02): figures are MODEL-PANELS-ONLY — the
   absence of the paper's empirical data points / error bars is in-scope and NOT a
   failure. The binding additions are about matching the model curves and layout,
   not re-creating data overlays.*

3. **Specify normalization in Phase A, one convention corpus-wide.** "Attended (or
   the model's reference condition) peak normalized to 1.0" must be stated in the
   spec/checklist, identically everywhere.

4. **Flip the verdict's error bias.** In a *faithfulness* library a false-pass is
   far costlier than a false-fail. The non-halt policy belongs to the **program**
   (move on to the next model; defer the hard one) — never to the **verdict** (don't
   call it green when it isn't). Let the audit fail figures and route them to a
   fix/defer queue with an honest status.

5. **Validate the proxy for sufficiency.** For each checklist, Phase A confirms that
   a deliberately-wrong figure (wrong width, inverted normalization, extra panel)
   *fails* it — not just that the right one passes. A checklist that a known-bad
   figure passes is too loose by construction.

## What this is NOT

Not a model-correctness story for most figures. The majority of "major" verdicts
are presentation/convention (normalization, spurious panels, axes, width/baseline
in the *view*), fixable without touching the science. A smaller set are genuine
model/measurement bugs (hara_gardner 8, zhu_rozell 8/2/3/7, lee_maunsell 2,
carandini 11, pestilli 2, doostani's data≈model perfect-fit artifact). The fix
plan separates the two; this document is only about *why the gate didn't catch
either*.
