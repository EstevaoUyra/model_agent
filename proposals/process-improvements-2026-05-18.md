# Process improvements — to discuss

Observations from the Reynolds & Heeger reproduction session on 2026-05-18
(first end-to-end VLM pass + the 2A/3C/4C deterministic fixes). Each item is
framed as **observation → proposal** for later discussion. None of these were
acted on unilaterally; they are candidates for the framework/skills.

---

## 1. Deterministic "saturation" claims are a weak proxy for the visual

**Observation.** Figure 2A's `test_figure_2A_crfs_are_monotonic_and_saturating`
passes at `final_slope/max_slope ≈ 0.918` (threshold `< 0.95`), yet two
independent VLM subagents unanimously report the 2A CRFs still look
non-saturating / non-converging. A curve can satisfy `final < 0.95·max` while
visually still ramping hard.

**Proposal.** Phase A quantitative claims that stand in for a *visual*
property should use a criterion tight enough that passing it implies the
visual reads correctly — e.g. `final_slope < 0.5·max_slope`, or an explicit
"within X% of an asymptote" plateau check, or require the half-saturation
contrast to sit a fixed margin inside the swept range. Alternatively, treat
the VLM as the binding check for any claim whose words are visual
("saturates", "converges", "levels off") and keep the deterministic test only
as a cheap regression tripwire. Worth a Phase-A test-design guideline.

## 2. Make multi-subagent VLM the default for contested figures

**Observation.** 2–3 subagents per figure caught two things a single run
missed: a confident **hallucination** on Figure 1 (one subagent invented
pixel-measured "two distinct bands" that aren't there) and a **latent**
Figure 4E weak-saturation that the prior single-subagent run passed.

**Proposal.** Tier the VLM step in `update-state`: 1 subagent for figures
that are stable and clearly green; **3 subagents + mandatory parent
image-read** for any figure that is (a) a det/VLM disagreement, (b)
provisional/soft-blocked, or (c) broken/changed since last run. The honed
skill already recommends 2–3; make it a rule keyed to figure status rather
than a suggestion, and record the per-subagent split in the verdict file
(currently only the adjudicated result is persisted).

## 3. VLM-only failures need a deterministic layout guard

**Observation.** Figure 1 is deterministically perfect (10/10) but visually
broken: all population fields are compressed at panel center instead of the
left/right hemifields. The deterministic tests sample only the *recorded
neuron's value*, never the *spatial layout*, so a whole class of
figure-correctness bugs is invisible to the suite and only the VLM catches
them.

**Proposal.** For schematic / population-visualization figures, Phase A
should add at least one deterministic test that asserts spatial structure
(e.g. the two stimulus bumps occur at the expected x-positions and are
separated by more than their width). This converts an entire failure class
from "VLM-only, discovered late" to "caught by the cheap suite".

## 4. Calibration-vs-cited-constant policy + structural-analysis-first

**Observation.** SQ-001, SQ-002, SQ-004 are all the same pattern:
implementation-side calibration that deviates from (or supplements) cited
constants, `article_aware/` left unchanged, "provisional green, soft-blocked,
un-audited". Three are now stacked and silently propping up Figures 2/3/4.
Separately: the Figure 4C fix only became obvious after a *closed-form*
analysis (`c* ≈ σ/(gain·k2)`, `k2` set by the C-011 θ-kernel) showed that no
sanctioned knob could move it — the brute-force sweeps alone would have
looked like "nothing works, stuck".

**Proposal.** (a) Add a recurring **calibration audit** checkpoint where a
human signs off (or rejects) the accumulated `chosen_assumption` SQs before
they compound; surface the soft-blocker count in the state report header.
(b) Add explicit guidance (a skill or WORKFLOW note): *before* sweeping
calibration knobs, write down the closed-form for the recorded response and
identify which knob can actually move the failing quantity — this both saves
sweep time and produces the precise evidence a good spec question needs.

## 5. Promote the calibrate→sweep→confirm loop to a first-class sub-process

**Observation.** The loop that fixed 2A/3C/4C worked well and was identical
each time: (1) read the figure's *full* failing+passing predicate set, (2)
write a no-assert sweep over the sanctioned knobs evaluating **all** the
figure's predicates (not just the failing one, to avoid regressions), (3)
pick a value with margin, (4) confirm with the real pytest.

**Proposal.** A `calibrate-figure` skill (sibling to `compare-figure`)
encoding exactly that loop, including the "evaluate all predicates, not just
the red one" guard and the "pick the point with margin, not the boundary"
rule. The three `implementation/sanity_checks/check_fig*` scripts written
this session are concrete templates.

## 6. Tag each VLM issue as model / figure-generation / checklist-scope

**Observation.** Figure 2's "missing inset schematics" is a *figure-generation*
gap; Figure 1's geometry is a *figures.py/protocol layout* issue; Figure 7's
prior failures were *checklist-scope* (SQ-003). These route to completely
different fixes, but the verdict JSON only carries free-text `issues`, so the
"next correction" routing is manual every time.

**Proposal.** Add a structured `category` per issue in the verdict schema
(`model | figure_generation | checklist_scope`) and have `update-state`'s
"next correction" prefer model issues over figure-generation over scope.
`compare-figure/SKILL.md` already names this taxonomy in prose — push it into
the data.

## 7. test_runs.jsonl commit-hash ordering is a footgun

**Observation.** Running pytest before committing tags the log rows with the
*old* commit hash; the correct sequence (commit code → re-run tests → VLM →
commit state) is non-obvious and easy to get wrong, which would make verdicts
and test rows disagree on provenance.

**Proposal.** Either (a) the test-log plugin records the *working-tree dirty*
flag alongside the commit hash, and `verdict_status.py` / `log_freshness.py`
warn when results were logged against a dirty tree; or (b) a small
"refresh-state" macro/skill that enforces the ordering end-to-end so a human
doesn't have to remember it.

---

### Net state at time of writing (context)

Deterministic 64/64. Green (det + fresh VLM pass): Figures 3, 5, 6, 7.
Broken: Figure 1 (VLM-only, layout/geometry), Figure 2 (VLM-only, 2A
non-convergence + missing insets), Figure 4 (4C fixed, 4E weak saturation).
Open soft blockers: SQ-001, SQ-002, SQ-003 (Phase-A checklist trim pending),
SQ-004.
