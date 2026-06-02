# Reproduction program plan — 2026-06-02

How we drive the ~21–23 corpus models
([corpus-expansion-2026-06-02.md](corpus-expansion-2026-06-02.md)) to
reproduction **progressively, via dynamic workflows, mostly autonomously**,
committing and pushing throughout, and improving the process between waves.
Pillar-4 process-knowledge (see [VISION.md](../VISION.md)); input to canon, not
canon. **Status: awaiting "go" for the pilot. No reproduction work has started.**

## 0. Mandate & the autonomy deviation (stated honestly)

Per explicit user direction (2026-06-02), the human gates that DESIGN §1 and §3
call non-negotiable — **Phase-A `APPROVED` and faithfulness-verdict
adjudication** — are **delegated to the organizer + adversarial critique agents**
for this program. The human is called **once, at the end**, with a consolidated
confidence × impact triage report over the whole corpus.

This trades *faithfulness-certainty for throughput*. The dominant risk is
**green-but-unfaithful** reproductions accumulating with no human to catch them
live (every reproduction benchmark in the literature confirms "it runs ≠ result
matches" is the top failure mode). The managed mitigation is the critique
architecture (§1) + the final review (§9) + the early-escalation exceptions (§6).
This is a deliberate, scoped override of DESIGN §1's "full autonomy is a
non-goal" — recorded as a deviation, not a silent change to canon.

## 1. Autonomous gate substitution — how critique agents replace the human

The earlier-designed faithfulness machinery *is* the substitute:

- **Phase-A gate (was: human approves `article_aware/`)** → an **adversarial
  spec-review panel**: critique agents attack the spec for *completeness* (can a
  paper-blind implementer build it?) and *faithfulness* (does every assumption
  carry literature-grounded evidence — §5 provenance table?). Pass with
  confidence → proceed; any sustained attack → revise. Replaces `APPROVED`.
- **Verdict gate (was: human adjudicates)** → the **leaf rubric**
  (*code-present / executes / result-matches*, kept strictly separate) +
  **multi-subagent VLM** (tiered, §5) + the **adversarial judge** (attacker /
  defender, DESIGN §3) + **perspective-diverse critique** (correctness /
  faithfulness-to-paper / does-it-reproduce). Confidence is **tiered by
  objectivity** (env/runs = high; "matches the figure" = low). Low-confidence
  leaves get extra critique rounds and are **flagged in the final report — never
  silently passed**.
- **The single human call = the consolidated triage report** (§9), sorted
  confidence × impact, so one review session adjudicates the whole corpus.

## 2. The unit — one model's reproduction pipeline

```
setup → Phase A (extract + literature-grounding) → [autonomous spec-review panel]
      → Phase B closed loop (impl→test→figure→multiVLM→diagnose→fix, capped)
      → faithfulness validation (provenance + leaf rubric + judge) → [autonomous verdict]
      → commit+push milestones throughout
```

Built and hardened during **Wave 1** (and refined every iteration after), this
becomes a **reusable workflow script** — i.e. the "framework runner" the docs
describe but STATUS.md says was never built is now *realized as the reproduction
workflow*, reused and improved every wave. That is Pillar 4 paying for itself.

Phase-A and Phase-B run as **separate agents with separate briefs and directory
scope**; Phase-B agents stay paper-blind (brief-enforced, as today).

## 3. The spiral — waves of ~3, improved every iteration, re-run until solid

Each **wave = ~3 models**, run as ~3 workflows with the organizer adjudicating
between them:

1. **W-extract** — parallel fan-out (one agent / paper) → Phase-A artifacts →
   spec-review panel.
2. **W-reproduce** — per-model bounded closed loop, models in parallel
   (pipeline) → status (green / partial / blocked).
3. **W-validate** — parallel fan-out → per-model triage reports.
4. **Improve (organizer)** — consolidate what was learned into concrete edits to
   the **agent guidelines, briefs, skills, and docs** → committed.

**Two principles make a separate one-paper "pilot" unnecessary (user direction,
2026-06-02):**

- **Improve at every iteration, not only between waves.** Course correction is
  continuous: the moment an agent fights the scaffold, a footgun hits, or a
  guideline proves thin, the guidelines/skills/briefs are updated and the fix
  applies immediately downstream. The improvement loop *is* the validation
  mechanism — a one-paper pilot is both too narrow (it won't surface the range of
  problems we will certainly hit) and redundant (the loop already course-
  corrects).
- **Re-iterate the same group more than once if needed.** A wave is *not*
  one-pass. If the retro surfaces fixable issues, re-run the group with the
  improved guidelines until it is solid (or a STUCK / falsification trigger
  fires, §6). **Wave 1 therefore doubles as the machinery shakedown** — expect
  more re-iterations early; that is by design, not failure. **No mid-program
  human checkpoint**; the human is called once, at the end (§9).

Then spawn the next wave, and at planned points **revisit** earlier waves:
re-run the upgraded process and wire up **cross-cluster benchmarks** (extra-
classical RF effects are predicted by all three clusters — the first to wire up)
that only exist once neighbors do. That is the "come back and improve the
originals."

## 4. Sequencing — engines first (the §1 reuse-surface rule), then dependents

Each cluster has a **shared engine**; reproduce it first so dependents reuse
*primitive stages*, never a calibrated protocol (the hermann-vs-carrasco lesson).

| Wave | Models | Why |
|---|---|---|
| **Wave 1** (anchors, breadth-first; doubles as machinery shakedown) | Lee & Maunsell 2009 (C1, cheapest/familiar) · Olshausen–Field 1996/97 (C2 dictionary) · Spratling 2010 DIM (C3 engine) | one anchor per motif → exercises all 3 early, fastest process-gap surfacing; expect more re-iterations here |
| **Wave 2** | Denison 2021 (C1 dynamic) · Rozell LCA (C2 engine) · Rao & Ballard 1999 (C3 anchor) | engines + the dynamic C1 |
| **Wave 3** | Verhoef & Maunsell 2017 (C1, has code) · Zhu & Rozell 2013 (C2, reuses LCA) · Bogacz 2017 (C3 ref solver) | reuse-heavy; **revisit Wave 1** here |
| **Wave 4+** | Ni/Ray 2012 (C1 tuned) · Bell–Sejnowski (C2) · Spratling 2012 (C3) · Hara/Gardner 2016, Pestilli 2009, Boynton 2009, Heeger 1992 / CHM 1997 precursors (C1) … | drain the remaining lineage; periodic revisits |

Order is a hypothesis; the per-iteration improvement may reorder it, and any wave
may re-run more than once. ~7–8 waves total.

## 5. Process guardrails carried from the open-branch learnings

These were notes with a human backstop; **under autonomy they are mandatory.**

- **HARD parent-write guard (the #1 autonomy hazard).** A prior agent
  accidentally `git add -A` / `--amend`-ed the *parent* repo; the brief clause
  alone was insufficient. So: (a) every model repo gets a **pre-commit hook
  refusing any commit whose top-level repo ≠ that model repo**; (b) briefs
  forbid `git add -A` and *any* parent-repo git op; (c) **parent submodule
  pointer-bumps + parent push happen ONLY in the organizer's serial
  between-workflow steps**, never inside a parallel model agent.
- **Multi-subagent VLM as default**, tiered by figure status (1 subagent for
  stable-green; **≥3 + mandatory parent image-read** for changed / contested /
  soft-blocked) — it caught a hallucination and a latent failure single runs
  missed. With no human verdict, this is the primary visual backstop. Persist
  per-subagent splits, not just the adjudicated result.
- **Visual claims are VLM-binding; tighten deterministic proxies.** A
  "saturation" proxy passed at 0.918 while VLM read non-saturating. Any claim
  whose words are visual ("saturates", "looks sigmoidal") → VLM is the binding
  check, deterministic test is a regression tripwire only.
- **Deterministic layout guards for schematic figures** (the Figure-1 class:
  det-perfect, visually broken). Phase A must assert spatial structure (positions
  in the measurement record), not just sampled values.
- **Closed-form before sweep.** Before brute-forcing calibration knobs, write the
  closed form for the recorded quantity and identify which knob can move the
  failing value — avoids the "nothing works, looks stuck" trap.
- **Structured issue categories** (`model | figure_generation | spec_scope`) on
  every verdict, so the autonomous loop routes the next fix correctly.
- **Two-ledger calibration** (ARCHITECTURE §3) + **measurement-record as single
  truth** (§2) + **modification smoke test** (§5(4)) are the validated backbone —
  keep. Surface `audited:false` counts + open SQs in the final report (high count
  is honest, but it is exactly what the human must see).
- **Citation/Assumption presence check.** STATUS.md: the static check was never
  built and "self-discipline carries it." With no human auditor, I add the
  *cheap presence* check (every `src/` function has `Citation:`/`Assumption:`) to
  the loop — presence only, quality deferred.
- **test-log provenance ordering.** Enforce commit-code → re-run tests → VLM →
  commit-state; flag dirty-tree rows so verdicts and test rows never disagree on
  provenance.

## 6. Escalation — when I break silence before the end (the rare exceptions)

Autonomy ≠ never-call. I break the "call only at the end" rule for, and only
for, the **falsification triggers** and genuine blockers:

- **Modification smoke test impossible** for a model without editing unrelated
  code → stage decomposition is the wrong unit → **stop, escalate a redesign
  pass** (do not patch around).
- **Calibration `audited:false` not materially below the ad-hoc baseline**, or
  **agents spending more effort serving the scaffold than reproducing** → the
  contract is theatre/too heavy → escalate.
- **A model that won't reproduce is NOT a stop condition (user direction,
  2026-06-02).** At the iteration cap / repeated-diff signal, log `STUCK`,
  **leave it and move on** — **re-queue it for a later wave**, where more
  neighbors (cross-cluster benchmarks) and the improved process may unblock it.
  **Never halt the program for one or two problem models.** A few models still
  unreproduced at the end is an **acceptable, recorded outcome** — learning, not
  failure.
- A **hard-rule conflict** or something genuinely weird → stop and ask.

Otherwise: run to completion, deliver §9.

## 7. Git/GitHub discipline & observability

- Per model: `gh repo create --private` → scaffold to ARCHITECTURE shape →
  register submodule → **push to its private repo throughout** (Phase-A done,
  each figure green, verdict). Same pattern as cagly/carrasco/hermann.
- Parent: pointer-bump + push at each model milestone, serially, by the
  organizer (never a model agent — §5 guard).
- **`main`-push guardrail → settled mechanism (2026-06-02).** A user-level hook
  refuses any direct `git push origin main` (parent and model repos), directing
  to a feature branch + PR. **Decision:** all reproduction work happens **on a
  feature branch in each model's own repo, pushed throughout**; the model repo's
  `main` is advanced **once, by a squash-merge PR** at the end (before the human
  review), keeping each model's `main` clean of per-attempt noise. The **parent**
  integrates via PR with a **history-preserving merge** (its branch carries
  meaningful framework history that should not be squashed). No
  `ALLOW_MAIN_COMMIT` bypass.
- **Observable without being called:** committed+pushed progress means nothing is
  lost on failure; workflows are resumable; each model's `README.md`
  (update-state) + a **live `PROGRAM_STATUS.md`** + `/workflows` let you peek any
  time. You won't be *called* until the end, but you can always *look*.

## 8. Controls & cost

**No token/cost cap** (user direction 2026-06-02: large budget, run to
completion). The per-model *iteration* cap stays — it guards against burning
effort on a STUCK model (stuck-detector still unbuilt), not against spend. ≤3
models/wave; workflows run in background and resume; I report cost per wave in
the retro for visibility, not as a gate. The wave structure bounds blast radius
and keeps each retro's improvements compounding.

## 9. The end deliverable (the single human call)

1. A **consolidated confidence × impact triage report** over all ~21–23 models:
   per-model verdict, the low-confidence/high-impact leaves flagged for your
   eyes, open SQs and `audited:false` calibration across the corpus, **and an
   explicit list of any models left unreproduced/deferred with what each one
   taught us** (expected, not a blocker).
2. The **process-improvement ledger** (every wave retro consolidated) — what the
   program taught the method.
3. **All repos committed & pushed**; parent pointers current.

One review session adjudicates the corpus. That report *is* the bottleneck-
solving artifact from the original discussion, now produced at corpus scale.

## 10. v2 decisions I'll take autonomously (design-pass §8), flagging the rest

- **Build-or-cut the vaporware:** the *runner* is realized as the reproduction
  workflow (§2); the *stuck-detector* becomes the documented cap + repeated-diff
  check I honor (§6); the *citation/assumption static check* I build as the cheap
  presence check (§5). These were the largest documented-vs-real gaps.
- **Logged for the final review, not blocking:** the named-regime-geometry preset
  refinement (SQ-004), cross-model SQ adjudication, and any contract amendments
  the retros surface.
