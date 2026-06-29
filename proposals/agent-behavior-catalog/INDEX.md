# Agent Behavior Catalog — index, schema & mining protocol

**Purpose.** A comprehensive, citable record of the agent *behaviors and biases* that
surfaced in this project, and how they responded to interventions. This project is a
~2-month, multi-agent, self-evaluating pipeline (agents reproduce neuroscience figures and
other agents audit them), so its logs are a natural record of how agents decide, interact,
and change under fixes.

> ## ⚠️ Two stages — do not confuse them
>
> **Stage 1 (this catalog) — the research map.** Comprehensive, honest, navigable. Its job is
> to record *what we observed* and *where to dig deeper*, with reliable entry-points (verified
> quotes, source paths, PR/hash). **Comprehensiveness is the GOAL here.** Breadth, even of
> "boring" infra threads, is a feature: it's a map, not a thesis.
>
> **Stage 2 (a later, separate paper) — the argument.** We will *select and sharpen a subset*
> of this map into ONE claim for a possible submission (e.g. **Workshop on Agent Behavior,
> WAB @ COLM 2026**). Cutting, collapsing, novelty-positioning, paper-candidate ranking, and
> "is this too internal?" are **Stage-2 decisions made later** — parked in
> `paper-framing-leads.md`. They are NOT reasons to narrow the catalog now.
>
> **Implication for critique:** judge this catalog on whether it's a *good, trustworthy,
> comprehensive map that sets us up to choose a framing later* — NOT as a finished paper.

This file is the apex: the schema, the domains/facets, the coverage statement, the mining
protocol, and a one-line index of every thread. Full entries live in `entries/<id>.md`.
Deterministic spine + evidence in `evidence/`. Mirrors the `MEMORY.md` index pattern.

---

## The unit: a longitudinal thread, keyed on (behavior, cause)

The unit is not one incident but the *life history* of a behavior under intervention:

> first appearance → intervention attempt → did it hold? → recurrence / **migration** /
> regression → next attempt → … → current status

**Keying rule (this is what the catalog exists to make explicit):**
- **Split** when the *mechanism/cause* differs even if the *symptom* is identical
  (E1 split into E1a leniency vs E1b perceptual blind spot — same "wrong figure passes,"
  different cause).
- **Merge** when the cause is shared even if the surface differs.

A bias that survives targeted fixes, or migrates to a new channel after a fix, is stronger
evidence than a clean one-shot — failed/partial interventions are the most informative.

---

## Entry schema (`entries/<id>.md`)

The schema is the **superset the best entry needed**: E1's most valuable content (cause,
confidence, migration) had no field in the first draft and had to go off-template — those are
now first-class fields. Every thread answers these; mark unknowns `[to-verify-on-deeper-dig]`.

**Identity & framing**
- `ID + short name` — behavior-phrased canonical name; symptom as subtitle.
- `Behavior` (behavioral-science terms, NOT project jargon) · `Symptom` (the observable).
- `Kind` — `agent-behavior | process/delivery | environment/substrate` (a tag, see Domains).

**Mechanism (the "why" — graded by evidence)**
- `Trigger / precondition` — the conditions under which it fires.
- `Cause / mechanism` — hypothesized, each tagged:
  `{intervention-tracked (strong) | agent-stated/possibly-post-hoc (weak) | inferred}`.
  *(No mentalism: write "the narration stated X," not "the agent believed X.")*

**Context**
- `Agent role(s)` — builder / critic / faithfulness-auditor / digitizer / extractor /
  orchestrator / README-gen / router … (a facet — see below).
- `Detector` — who/what caught it: `human post-mortem | another agent | test/gate |
  blind re-audit | cold log-mining`. *(This operationalizes the catalog's selection bias —
  if every Detector is "human," the map measures human attention, not agent behavior.)*

**Intervention & trajectory**
- `Timeline` — dated rows (appearance → intervention → outcome → recurrence/migration), each
  with its ref (PR#/hash, proposal, log path).
- `Intervention lever(s)` — typed: `prompt/spec | gate/test | structural/role | doc |
  human-rule` — and **which held**.
- `Recurred?` / `Failed-or-reverted intervention?` / `Migrated-to?` (sibling thread ID).

**Evidence & honesty**
- `Smoking gun` — single most legible artifact, exact path/hash.
- `Evidence layer` — corpus slice, n / denominator, **verified-verbatim count** (`X of N`),
  source paths (in `evidence/`). Anecdote ≠ rate: any frequency/disappearance claim needs a
  denominator or a `[to-verify]`.
- `Confidence & threats-to-validity` — **required** (confounds in plain language).
- `Scope/generality` — descriptive only: setup-specificity vs bias-generality (NOT a
  paper-relevance score — that's Stage 2).

**Links & next steps**
- `Links` — typed edges to other threads: `migrated-to | inverse-of | shared-root | connects-to`.
- `Deeper-dig hook` — the exact next query + where the data lives.
- `Status` — `open | mitigated | solved` · `Refs`.

---

## Domains (a facet, not a folder)

Threads carry a **domain tag**; they are NOT filed in domain folders (a thread can touch
several). Note the two organizing axes below are different — domains 1–2 classify the agent's
*decision move*; 3–5 classify the *system locus*. Neutral names (no "pathology/failure"
valence — valence is per-thread).

1. **Evaluation** — judging own/others' output: leniency, self-preference, sycophancy,
   tool/VLM rubber-stamping, gestalt blind spots, self-certification.
2. **Escalation** — when to defer/route: over-deference to humans, premature/late escalation,
   authority-ladder violations.
3. **Coordination** — multi-agent/structure: role creep, wrong-repo commits, parallel work
   swallowed, **one shared decision resolved N× independently** *(sole home — was double-filed
   under Escalation; cross-ref only)*.
4. **Process-maintenance** — over time: process outran its spec, no coverage gate, silent
   drift, docs masquerading as machinery.
5. **Tool / environment** — substrate that shaped behavior. **Split into:**
   - *substrate conditions* (the agent did nothing wrong — e.g. sandbox lacks a library) →
     marked `Kind: environment/substrate`, an appendix, not an agent behavior.
   - *tool-adjacent agent behaviors* (ships an unvalidated change; acts on a stale tool-model)
     → real behaviors, cross-reffed to their decision-domain home.

   *(Renamed from "Tool-trust" to avoid colliding with the Evaluation behavior "tool rubber-
   stamping," which lives in domain 1 as E3.)*
6. **Generation / fabrication** *(added 2026-06-29)* — the producer side: the agent **makes
   something up** rather than mis-judging something real. Confabulating a mechanism, fabricating
   a quantitative claim with a real-looking citation (G1), building the result then self-verifying
   the construction ("we drew the answer", G2). Domains 1–2 are *grader-side* (judging output);
   domain 6 is *generation-side* (producing false output) — a whole family the memory-seeded Pass 1
   missed because memory skews to audit/orchestration lessons. Surfaced by the skill-history +
   `issues.yaml` sweeps.

---

## Coverage & blind spots (what this map cannot see)

The catalog is built from biases **we noticed and fixed** — a detection/survivorship bias.
These classes are excluded *by construction*; listed here as named, mostly-empty categories so
holes read as holes. Reserved ID-space: **`P#`** positive/competent baselines, **`U#`**
suspected-but-uncaught (hypothesis, no artifact).

- **Positive / competent behaviors** (`P#`) — every thread is a pathology, so the map has **no
  denominator**: the rate of leniency needs the population of *correct* verdicts, which isn't
  cataloged. The "after" of each fix is the only positive signal. *(Seed P-threads: auditor
  true-positive catches; correct rung-1 self-resolution; faithful-first-try builds.)*
- **Never-caught failures** (`U#`) — figures that passed and are *still* wrong because nothing
  re-checked them. The map cannot see its own false-negative rate. **Now bounded, not just named:**
  thread **U1** ran the injected-fault probe — a silently-skipped *enumerated* artifact is caught by
  the coverage gate (deterministic, no human); the open residue is wrong-but-present content, a
  figure dropped from the target list, and non-enumerated steps. A *measured* floor, not a shrug.
- **Under-instrumented roles** — the corpus is auditor-heavy (see matrix). Builder/digitizer/
  describer/orchestrator biases are under-sampled, not absent.
- **Diffuse / statistical tendencies** — the `Smoking gun` requirement favors discrete
  incidents over gradual drifts (slow overconfidence, verbosity creep) that have no single
  artifact.
- **Emergent multi-agent dynamics** — *partially filled (2026-06-29)*: **C6** (a span-crossing
  decision owned by no one), **C7** (correlated reviewers — "adversarial" review as a second draw
  from the same error distribution) now cover the independence/ownership failures. Still open: a
  builder↔critic settling into a mutually-agreeable wrong equilibrium, anchoring cascades down the
  agent tree (Method B — interaction-graph — is the instrument, not yet run).
- **Human-in-the-loop behaviors** — the corrective half of most threads is the human lead's
  judgment; agent over-compliance with *wrong* human steering is barely covered (X1 adjacent).

### Instrumentation matrix (mining depth by role; from `evidence/manifest.jsonl`, 2026-06-29)

| Role | agents | narration tok | date span |
|------|-------:|--------------:|-----------|
| unknown (older inline-prompt) | 493 | 712,536 | 06-02→06-28 |
| audit-faithfulness | 186 | 695,903 | 06-03→06-28 |
| digitize-figure | 168 | 1,205,644 | 06-03→06-27 |
| audit-digitization | 166 | 603,742 | 06-03→06-27 |
| extract-figure | 152 | 294,297 | 06-03→06-27 |
| implement (builder) | 144 | 523,185 | 06-02→06-28 |
| author-tests | 131 | 360,519 | 06-03→06-28 |
| extract-spec | 126 | 422,414 | 06-02→06-26 |
| audit-process | 121 | 244,516 | 06-03→06-28 |
| audit-tests | 115 | 298,488 | 06-04→06-28 |
| audit-spec | 110 | 359,364 | 06-04→06-27 |
| update-state | 71 | 130,916 | 06-03→06-28 |
| run-tests | 51 | 112,096 | 06-02→06-28 |
| acquire-sources | 28 | 36,649 | 06-04→06-26 |
| **total** | **2062** | **6,000,269** | |

`unknown` (24%) is a recall hole for any role-keyed slice — treat as a sampled stratum, not
absence. `claude_model` is constant `claude-opus-4-8` across the corpus (model-version
confound ruled out).

---

## Mining protocol

Three passes; deterministic code filters before any LLM reads (6M tok → thread-sized bundles).

**Pass 1 — top-down** (memory `*.md`; `proposals/*.md`; `git log` reverts + repeated-subsystem
clusters; `presentation-storyboard.md`). Fast, ~mechanical; seeds the index.

**Pass 2 — bottom-up artifacts** (`logs/process_audit/*`, `logs/test_runs.jsonl`, `.agent_tmp/`,
per-model committed logs).

**Pass 3 — the narration corpus (PRIMARY EVIDENCE).** Source: the workflow subagents in
`evidence/corpus-snapshot/*/subagents/workflows/wf_*/agent-*.jsonl` (durable snapshot; spine =
`evidence/manifest.jsonl`, rebuilt by `evidence/build_manifest.py`). It is *verbalized
narration* — behavioral proxy, NOT CoT, NOT internal state.
- **Method A — intervention pre/post:** slice a role's narration before/after each dated fix;
  characterize the rationale change in the agents' words. **For counts, slice by manifest
  strata (role×period), not keywords** — keyword filters destroy recall and manufacture
  "didn't recur." E1 is the proof-of-concept (#5→#56→#73).
- **Method B — interaction-graph:** trace a verdict across the agent tree (multi-agent dynamics).
- **Method C — bottom-up discovery:** sampled sweep for un-distilled behaviors (low recall by
  design; the only escape from the selection bias above + the `U#` calibration probe).

**Fan-out hardening (prerequisites — build before scaling):**
- A committed `SUBAGENT-BRIEF.md` handed verbatim to every agent (schema + guardrails + output
  contract) — one brief = the defense against rubric drift.
- Output contract: every quote returned as `(source_path, exact_verbatim_substring)`.
- A mechanical grep harness verifies every pair against `evidence/corpus-snapshot/` — converts
  "orchestrator re-reads 17 bundles" into one script run, so verification actually happens
  rather than being rubber-stamped.

---

## Thread index

Flags: ⟳ recurred after a fix · ✗ failed/reverted fix · ⇄ migrated · ↔ inverse/paired thread.
*(Paper-candidate ★ ranking moved to `paper-framing-leads.md` — Stage 2.)*
Domains: E=Evaluation · X=Escalation · C=Coordination · M=Process-maintenance · T=Tool/env · **G=Generation**.

**Build status (2026-06-29):** **38 threads across 37 entry files**, built in three sweeps — Pass-1
(memory-seeded), then the *intervention-surface* sweeps (workflow + skill + drift-register + AGENTS/
WORKFLOW/tools histories + 39 `issues.yaml`) that the "is it complete?" check demanded. Quote
evidence: **85/85 promoted quotes verified verbatim** against `corpus-snapshot/` (`verify_quotes.py`,
exit 0) across 18 ledgers; threads without a ledger are git/proposal/`issues.yaml`-grounded (the
behaviour isn't in the workflow-agent narration — see each entry's Evidence layer). Completeness is
*bounded*: Tier-1 intervention surfaces swept; **U1** puts a measured floor on the never-caught class;
remaining open work = a Method-C raw-narration sample + `P#` positive baselines.

#### Evaluation (E)
| ID | Thread | Role | Flags | Status | Entry · refs (denominator) |
|----|--------|------|-------|--------|----------|
| [E1a](entries/E1-faithfulness-audit-blindspot.md) | Evaluator leniency — acquits a discrepancy it named | auditor | ⇄→E1b | mitigated | ledger ✓; PR #5,#56 (≈13 models relabel-to-illustrative) |
| [E1b](entries/E1-faithfulness-audit-blindspot.md) | Perceptual blind spot — local curve defect passes | auditor | ⟳ | mitigated | ledger ✓; PR #73 |
| [E2](entries/E2-leniency-drift-grading-own-homework.md) | Leniency drift / grades own homework | builder+audit-process | — | mitigated | ledger ✓(5); *facet: tautological test authoring (#294261d)* |
| [E3](entries/E3-tool-vlm-rubber-stamp.md) | Rubber-stamps its own tool/VLM output (false GREEN) | digitizer/auditor | ↔E12 | mitigated | ledger ✓(2) |
| [E4](entries/E4-sycophancy-flattery.md) | Sycophancy / flattery | orchestrator (chat) | — | mitigated | ledger ✓(2); thin — chat not corpus |
| [E5](entries/E5-self-certification-green-tests.md) | Self-certification (green ⇒ "done") | builder/organizer | ⟳ ↔D3,M6 | recurring | ledger ✓(3); *facet: unknown reported as green (#94511bc)* (≈16 models) |
| [E6](entries/E6-extractor-reads-figure-it-expected.md) | Reads the figure it *expected*, not the one there | extract-figure | ⟳ | mitigated | ledger ✓(7); PR c112359 |
| [E7](entries/E7-shape-faithful-wrong-absolute-scale.md) | Shape-faithful but wrong absolute scale | audit-faithfulness | — | mitigated | ledger ✓(7); denison 4× |
| [E8](entries/E8-per-panel-normalization-overrides-shared-scale.md) | Default normalization overrides paper's shared scale | digitizer/builder | ⟳ | mitigated | ledger ✓(7); R&H Fig2 |
| [E9](entries/E9-illustrative-used-as-escape-hatch.md) | "Illustrative" escape hatch to dodge a reproducible result | extract-spec | — | mitigated | ledger ✓(6); carrasco F7 |
| [E10](entries/E10-false-paper-issue-attribution.md) | False paper-issue attribution (blame source, retracted) | builder/auditor | ⟳ | mitigated | issues.yaml; hara,bienenstock,rao |
| [E11](entries/E11-binding-magnitude-hidden-in-test-code.md) | Binding magnitude hidden in test code, escapes ledger | extract/author-tests | ⟳ | mitigated | wave-retros; (2/6 at extraction) |
| [E12](entries/E12-judges-stale-artifact-false-needs-work.md) | Judges a stale artifact → false NEEDS-WORK | auditor | ↔E3 | mitigated | ledger ✓(3); spratling,bell (inverse of E3) |

#### Generation (G) — *new domain: the producer makes something up*
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [G1](entries/G1-extractor-confabulates-mechanism.md) | Confabulates a mechanism / fabricates a cited claim | extract-spec/figure | — | mitigated | ledger ✓(4); olshausen Q-905 (caught by critic) |
| [G2](entries/G2-result-bearing-stub-we-drew-the-answer.md) | Result-bearing stub / "we drew the answer" | implement | ⟳ | mitigated | faithfulness-enforcement B1; +absent-source sub-case |

#### Escalation (X)
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [X1](entries/X1-over-routing-to-human.md) | Over-routing to human for paper-resolvable findings | spec/process-auditor | ⟳ ↔X2 | mitigated | ledger ✓(6) (≈18 models human-routing) |
| [X2](entries/X2-escalation-ladder-under-walked.md) | Escalation-ladder under-walked (58% self-resolvable) | orchestrator/resolver | ↔X1 | mitigated | ledger ✓(3) |
| [X3](entries/X3-misroutes-model-fault-as-code-tunes-per-figure-knob.md) | Misroutes model-fault as code → tunes per-figure knob | implement/audit-spec | — | mitigated | ledger ✓(4); RH gain 4→12→16 |

#### Coordination (C)
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [S1](entries/S1-organizer-over-reach.md) | Organizer over-reach / do-it-myself reflex | orchestrator | ⟳ | recurring | git/memory |
| [S2](entries/S2-shared-decision-resolved-n-times.md) | One shared decision resolved N× (everyone owns it) | orchestrator+auditors | ⟳ ↔C6 | open | ledger ✓(4); saturation |
| [S3](entries/S3-wrong-repo-commits.md) | Commits in wrong repo (parent vs submodule) | workflow/finalize | ⟳ | solved | git; PR #28 *(+read-side phantom-blocker facet)* |
| [S4](entries/S4-parallel-work-swallowed-onto-main.md) | Parallel work swallowed onto main | orchestrator | ⟳✗ | solved | git; PR #47/#48,#58 |
| [C5](entries/C5-default-reuse-inherits-ancestor-bug.md) | Default cross-model reuse inherits ancestor's bug | implement | — | mitigated | ledger ✓(4); hermann←R&H (root of S2) |
| [C6](entries/C6-no-owner-of-integrative-question.md) | Integrative question owned by *no one* | (cross-figure) | ↔S2 | mitigated | faithfulness-enforcement E3 (inverse of S2) |
| [C7](entries/C7-correlated-reviewers.md) | Correlated reviewers — review = 2nd draw from same errors | extractor+reviewer | — | mitigated | faithfulness-enforcement E2 |

#### Process-maintenance (M)
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [D1](entries/D1-process-outran-docs.md) | Process outran its docs | orchestrator/docs | ⟳ | mitigated | drift register (≥6 instances D7–D12) |
| [D2](entries/D2-generated-output-drift.md) | Generated-output drift (README re-fixed) | README-gen/finalize | ⟳ | mitigated | PR #61–#65,#70,#72 (≈7 models) |
| [D3](entries/D3-required-step-silently-stops.md) | Required step silently stops (no coverage gate) | process/gate | ↔E5 | mitigated | PR #56,#66 *(+D6: Pillar-3 check never runs)* |
| [D5](entries/D5-granularity-collapse-hides-bad-subunit.md) | Granularity-collapse — rolled-up status hides bad sub-unit | (digitization gate) | introduced-by→T1 | solved | drift register D5 |
| [M4](entries/M4-no-op-fix-spin.md) | "The spin" — re-tries a no-op fix forever | orchestrator | — | solved | #2b88d08 (needs an arbiter) |
| [M5](entries/M5-capture-without-resolution.md) | Capture-without-resolution — filed finding stays inert | (process) | →D3 | open | sq-blocking (≠D3: actuation not detection) |
| [M6](entries/M6-non-termination-effort-exhaustion.md) | Non-termination — never declares "stuck" | (fix loop) | ↔E5 | mitigated | final-triage (4.4h; needs a stopwatch) |

#### Tool / environment (T)
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [T1](entries/T1-cost-fix-reverted.md) | Ships unvalidated optimization to main (reverted ×2) | orchestrator | ✗⟳ →E5,S4 | solved | PR #45→#48→#50→#59→#60 |
| [T2](entries/T2-render-sandbox-lacks-matplotlib.md) | Render sandbox lacks matplotlib | builder/render | ⟳ | solved | *(Kind: substrate)* |
| [T3](entries/T3-acts-on-stale-tool-model.md) | Acts on stale tool-model | orchestrator/tooling | ✗ | solved | git/memory |
| [T4](entries/T4-throttle-null-verdict-gate.md) | Throttling → null verdict → crash / false-green risk | process/gate | — | solved | PR #41,#68 |
| [T5](entries/T5-law-of-the-instrument-wrong-tool.md) | Law of the instrument — runs the wrong tool it has | digitizer | — | solved | ledger ✓(3); tracer on a dictionary |

#### Coverage instruments
| ID | Thread | Role | Flags | Status | Entry · refs |
|----|--------|------|-------|--------|----------|
| [U1](entries/U1-silently-skipped-step-probe.md) | Never-caught floor — injected-fault probe | (measurement) | measures→D3 | open (bounded) | probe `evidence/u1_coverage_probe.sh` |

### Migration & link edges (the catalog's core signal — structural, not prose-only)
- `E1a ⇄ E1b` — fix bound the referent (ended leniency); wrong-figure-passes **migrated** to a perceptual blind spot.
- `E3 ↔ E12` — **inverse**: E3 rubber-stamps → false GREEN; E12 distrusts a correct model → false RED. Same eye, opposite sign.
- `X1 ↔ X2` — **inverse**: hardening over-routing risks under-routing. Same escalation dial.
- `S2 ↔ C6` — **inverse**: a shared decision owned by *everyone* (S2, resolved N×) vs by *no one* (C6, resolved 0×).
- `E5 ↔ M6` — **inverse**: terminates too early (E5) vs never terminates (M6). `E5 ↔ D3` — self-certification at agent vs process scale.
- `C5 → S2` (**generative root**: default reuse inherits the bug S2 then re-resolves) · `D5 introduced-by T1` (de-parallelization regression) · `T1 → E5,S4`.
- `G1 ⋈ G2` (fabricate-the-target: invent a mechanism vs build the result) · `T5 ⋈ X3` (law-of-the-instrument: nearest *tool* vs nearest *knob*).
- `M4` needs an arbiter · `M5` needs a consumer · `M6` needs a stopwatch (three distinct non-progress modes).

*Pass-1 + the intervention-surface sweeps are fully built. Remaining: a Method-C raw-narration
sample (Tier 2) and `P#` positive baselines append below this line when run.*
