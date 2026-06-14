# Process drift register — the machinery outran its description (2026-06-14)

## The finding, in one sentence

`.claude/workflows/full-pass.js` — the de-facto process that built the last ~15 models —
has **drifted ahead of every description doc**. VISION.md, WORKFLOW.md, and STATUS.md all
describe a process the workflow no longer executes, and **STATUS.md — whose one job is to
be "canonical on reality" (STATUS.md:5) — still names a VLM loop (`compare-figure-packet
→ VLM subagents → persist verdict`, STATUS.md:82–84) that `full-pass.js` never invokes.**

Per the VISION's own cardinal rule — *"we write the vision down precisely so that it stops
masquerading as machinery that exists — the failure mode STATUS.md was created to correct"*
(VISION.md:13–15) — this is exactly that failure mode, recurring **on the doc stack built
to prevent it.**

## Why this is a Pillar-4 event, not a cleanup chore

Pillar 4: *the process is product only to the extent trials have validated it; documentation
that runs ahead of evidence is the failure mode* (VISION.md:82–94). `full-pass.js` was
iterated hard recently (consolidation, de-parallelization, cost-wiring) and each change
quietly altered *what the process does* without reconciling *what the process says it does*.
The reproductions kept exiting `faithful`/`partial`, so the drift stayed invisible until a
single figure-render note exposed it. **This register is the Pillar-4 yield** — "what the
guardrail didn't catch" — and the honest reading is that the guardrail couldn't catch it,
because of the keystone gap below.

## The keystone: there is no coverage gate

Every gate in `full-pass.js` judges the **content of artifacts that happen to exist** (or an
auditor re-renders its own transient copy and judges that). **Nothing asserts that the
required steps ran and committed their outputs.** The process auditor is paper-blind and
artifact-blind by design and "reads absence as innocence." That is *why* the machinery could
silently stop producing the original crop, the committed render, the visual checklist, and the
VLM verdict, and still exit clean. **The single highest-leverage fix is a coverage gate** that
blocks a clean exit unless every required artifact/step for the target figures provably exists.
It serves Pillar 1 (faithfulness you cannot verify ran is, operationally, unfaithfulness —
VISION.md:150–153) and Pillar 4 (it makes future drift self-revealing instead of silent).

## A correction to an earlier alarm

I first flagged "the VLM `compare_figures` step never runs" as a critical silent-pass. That was
miscalibrated. The 2026-06-02 post-mortem **deliberately retired** the lenient VLM-checklist
quorum (the thing that passed 49% wrong figures) in favour of the paper-aware
`audit-faithfulness` auditor — which the VISION explicitly endorses over an isolated checklist
(*"the faithfulness auditor must be allowed and required to research the paper, the original
code, and the lineage"*, VISION.md:186–193). `audit-faithfulness` **is** wired and **is** the
headline-status source, and comparing the render against the **digitized reference** (already
paper-grounded by the separate digitization audit) is the *better* design, not a gap. So the
VLM divergence is **doc-is-stale, change the doc** — not a missing control. Figures are
verified; the docs just describe the wrong instrument.

---

## The drift register

Each row is adjudicated by **which pillar is at stake** and the VISION's ordering (Faithful >
Understandable > Modifiable > Process). "Change code" = reality is a regression against the
pillar. "Change doc" = reality is the better design and the description must catch up.

### P0 — Pillar 1 (faithfulness; non-negotiable)

| # | Doc says / reality does | Verdict (VISION) | Action |
|---|---|---|---|
| **D1** | WORKFLOW.md:420 makes a FAITHFUL digitization a hard precondition; `full-pass.js:381` says `digBlocked … does not gate the gate` — a DIVERGENT ruler still yields `faithful`. | Grading the model against an *unverified* reference is the "believable but divergent" trap — *worse than worthless* (VISION.md:32–33). The ruler must be trusted before it grades. | **Change code:** a non-FAITHFUL digitization caps the exit at `partial`; never `faithful` while the reference is unverified. |
| **D2** | WORKFLOW.md:435 "any open finding → partial, never reproduced"; `full-pass.js:453,488` keep `overall:'faithful'` while GENUINE_DIVERGENCE flags and BLOCKED figures sit open. | A model labelled `faithful` with an open divergence is the exact *believable* falsehood Pillar 1 forbids. | **Change code:** any open GENUINE_DIVERGENCE or BLOCKED figure ⇒ headline cannot be `faithful`. |
| **D3** | WORKFLOW.md:431 + the post-mortem give the Process Auditor teeth ("drifting holds the model at partial"); `full-pass.js:446,488` capture `proc` but `exit.overall` ignores it — purely decorative. | The Process Auditor is the VISION's "role distinct from the adversarial judge" (VISION.md:186–193). A guardrail whose verdict changes nothing does not guard. | **Change code:** a `drifting`/`toward_green` verdict caps the exit at `partial`. |

### P0 / keystone — Pillar 4

| # | Gap | Verdict | Action |
|---|---|---|---|
| **D0** | No gate asserts that required steps ran / artifacts exist; absence reads as innocence. | The structural enabler of every other row. Pillars 1 + 4. | **Change code:** a coverage gate — clean exit requires, per target figure, the committed three views + a fresh faithfulness verdict; missing ⇒ BLOCK, not a footnote. |

### P1 — Pillar 1 + the binding bottleneck (faithfulness the human can trust *cheaply*)

| # | Doc says / reality does | Verdict | Action |
|---|---|---|---|
| **D4** | WORKFLOW.md §8 + STATUS.md:60–76 treat the README's three views (paper · digitized · implemented) as central; `full-pass.js` commits **neither** the original paper crop (`article_aware/figures/figure_N.png`) **nor** a committed implemented render — it renders to gitignored `figure_outputs/`. The README literally cannot show two of three columns. | The side-by-side three views are *the* cheap-trust artifact — the binding bottleneck is the human's time to validate faithfulness (VISION.md:148–153). Serves Pillars 1 + 2. | **Change code:** crop + commit the original; promote the render to a committed location; the coverage gate (D0) enforces all three. |
| **D5** | digitize-figure/SKILL.md requires a **per-panel** audit verdict; my de-parallelization collapsed `DIG_VERDICT` to **per-figure** (`full-pass.js` `DIG_VERDICT_MULTI`), so a bad panel hides inside a rolled-up figure status. | A hidden bad panel is a faithfulness blind spot. *(I introduced this — owning it.)* | **Change code:** restore per-panel verdicts inside the single-sweep gate. |

### P2 — Pillar 3 (modifiable) + the VLM doc correction

| # | Doc says / reality does | Verdict | Action |
|---|---|---|---|
| **D6** | WORKFLOW.md:425–430 lists a **modification smoke test** (edit a real calibration entry → regenerate → collect) as a `reproduced` acceptance condition; `full-pass.js` never runs or collects it. This is the *operational definition* of Pillar 3 acceptance (VISION.md:78–80). | Pillar 3 is real but **third** — faithfulness wins. The check is the only thing that verifies the modifiability pillar, but it doesn't outrank P0/P1. | **Change code (build minimal), P2;** and until built, **change doc:** WORKFLOW.md must stop asserting a clean exit guarantees it (STATUS discipline). |
| **D7** | WORKFLOW.md + STATUS.md:82–84 describe the `compare-figure-packet` VLM loop as the figure-faithfulness instrument; reality uses paper-aware `audit-faithfulness` (compare-to-digitized). | Reality is VISION-endorsed and better (see correction above). The dead `compare_figures` tooling stays as an *optional* supplement. | **Change doc:** WORKFLOW.md + STATUS.md describe `audit-faithfulness` as the instrument; demote `compare_figures` to optional. Resolves the izhikevich "couldn't run" note (it was reaching for a retired step). |

### P3 — doc honesty & hygiene (Pillar 4)

| # | Drift | Action |
|---|---|---|
| **D8** | STATUS.md's "real loop" (82–84) is the old VLM loop, not the `full-pass.js` loop. | **Change doc:** rewrite STATUS.md's loop to describe `full-pass.js` as it actually runs. |
| **D9** | Vocabulary: WORKFLOW says `reproduced`; the workflow emits `faithful\|partial\|blocked`. `ILLUSTRATIVE`/`SUSPECTED-PAPER-ISSUE` statuses are named but unemittable by the verdict schema; `APPROVED` file vs the structured verdict actually used. | **Change doc:** reconcile vocabulary to what the workflow emits; drop or implement the phantom statuses. |
| **D10** | `run-tests` is invoked as the stale-artifact sweep — a procedure its own SKILL.md never documents (it lives in update-state §3b). The agent reads one skill, gets a different job. | **Change doc/code:** document the sweep where it is invoked, or point the sweep at the skill that owns it. |
| **D11** | The Reproduction-cost README section I wired into the `update-state` invocation isn't in update-state/SKILL.md. *(I introduced this.)* | **Change doc:** add it to the skill. |
| **D12** | WORKFLOW.md:100 + the enforcement proposal want **≥2** independent spec reviewers; `full-pass.js:387` uses one `audit-spec` agent (author≠auditor *is* honored). | **Change doc (keep N=1) — judgment call.** Pillar 4 says validate by trials, not by piling on reviewers; the author≠auditor separation is the real control. Revisit only if trials show a single adversarial auditor misses contract faults. |

---

## The meta-recommendation

The deepest fix is not any single row — it is that **the process changed and no discipline
caught that the description had gone stale.** Two structural commitments, both Pillar 4:

1. **Build the coverage gate (D0).** It is the one mechanism that makes "the machinery
   silently stopped doing a step" impossible — the precondition for trusting any `faithful`
   exit, and for trusting the docs.
2. **Bind doc-reconciliation to workflow change.** When `full-pass.js` changes *what it does*,
   STATUS.md is updated in the same change. The aspiration: STATUS.md (or a generated section
   of it) becomes **checkable against the workflow** — the skills it invokes, the artifacts it
   commits — so a drift between machinery and its canonical-reality doc becomes a failing check,
   not a six-week-old surprise. That is Pillar 4 turning this incident into process.

## Sequenced plan

1. **P0:** coverage gate (D0) + the three faithfulness teeth (D1 digitization-gating, D2
   open-finding⇒not-faithful, D3 process-auditor teeth). These restore the post-mortem's intent
   and are pure Pillar-1 debt.
2. **P1:** the committed three-view artifacts (D4) + per-panel digitization (D5) — cheap human
   trust + the blind-spot I introduced.
3. **P2:** minimal modification smoke test (D6); rewrite the figure-faithfulness docs to
   `audit-faithfulness` (D7).
4. **P3:** the doc-honesty sweep (D8–D12) — STATUS.md loop, vocabulary, attributions — ideally
   landed *with* the coverage gate so reality and description re-converge in one motion.

## What this episode validates

Pillar 4's thesis, exactly: *each reproduction is an experiment on the process; what the agent
lacked, where it silently diverged, which guardrail caught it — that is the real yield.* The
guardrail did **not** catch this; the yield is knowing precisely why (no coverage gate, absence
read as innocence) and that the fix is structural. The models themselves are sound — the
deterministic test layer is rigorous and `audit-faithfulness` does verify figures — but the
**process-as-product was running on documentation that had quietly stopped being true.**
