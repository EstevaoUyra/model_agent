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
  re-checked them. The map cannot see its own false-negative rate. Only the **injected-fault
  calibration probe** (see protocol) can estimate it.
- **Under-instrumented roles** — the corpus is auditor-heavy (see matrix). Builder/digitizer/
  describer/orchestrator biases are under-sampled, not absent.
- **Diffuse / statistical tendencies** — the `Smoking gun` requirement favors discrete
  incidents over gradual drifts (slow overconfidence, verbosity creep) that have no single
  artifact.
- **Emergent multi-agent dynamics** — no domain yet houses builder↔critic settling into a
  mutually-agreeable wrong equilibrium, or anchoring cascades down the agent tree (WAB
  explicitly wants these — Method B is the instrument).
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

Flags: ⟳ recurred after a fix · ✗ failed/reverted fix · ⇄ migrated to another thread.
*(Paper-candidate ★ ranking moved to `paper-framing-leads.md` — Stage 2.)*
Domain: E=Evaluation · X=Escalation · C=Coordination · M=Process-maintenance · T=Tool/env.

**Build status (2026-06-29):** all 17 threads have full entries (`entries/`). Quote evidence:
**40/40 promoted quotes verified verbatim** against `corpus-snapshot/` (`verify_quotes.py`, exit 0)
across 9 ledgers; threads without a ledger are git/proposal/memory-grounded (the behaviour isn't in
the workflow-agent narration — see each entry's Evidence layer). Still TODO: the `P#`/`U#` seeds and
a Method-C un-distilled-discovery sweep (no new threads found yet — these were the Pass-1 known set).

| ID | Thread | Dom | Role | Flags | Status | Entry · key refs |
|----|--------|-----|------|-------|--------|----------|
| [E1a](entries/E1-faithfulness-audit-blindspot.md) | Evaluator leniency — acquits a discrepancy it has named | E | auditor | ⇄→E1b | mitigated | E1 · ledger ✓; PR #5,#56 |
| [E1b](entries/E1-faithfulness-audit-blindspot.md) | Perceptual blind spot — local curve defect passes | E | auditor | ⟳ | mitigated | E1 · ledger ✓; PR #73 |
| [E2](entries/E2-leniency-drift-grading-own-homework.md) | Leniency drift / grading own homework (heeger Vₑ) | E | builder+audit-process | — | mitigated | ledger ✓ (5); `process-auditor-discriminates-drift-from-stuck` |
| [E3](entries/E3-tool-vlm-rubber-stamp.md) | Agent rubber-stamps its own tool/VLM output | E | digitizer/auditor | — | mitigated | ledger ✓ (2); `vlm-eye-is-arbiter-over-tools` |
| [E4](entries/E4-sycophancy-flattery.md) | Sycophancy / flattery in agent output | E | orchestrator (chat) | — | mitigated | ledger ✓ (2); thin — lives in chat, not corpus; `dont-flatter-be-plain` |
| [E5](entries/E5-self-certification-green-tests.md) | Self-certification (green tests ⇒ "done") | E | builder/organizer | ⟳ ↔M(D3) | recurring | ledger ✓ (3); `re-audit-after-every-model-change` |
| [X1](entries/X1-over-routing-to-human.md) | Over-routing to human for paper-resolvable findings | X | spec/process-auditor | ⟳ ↔X2 | mitigated | ledger ✓ (6); `paper-resolvable-findings-arent-human-routed` |
| [X2](entries/X2-escalation-ladder-under-walked.md) | Escalation-ladder under-walked (self-resolvable→human) | X | orchestrator/resolver | ↔X1 | mitigated | ledger ✓ (3); `resolution-authority-ladder` |
| [S1](entries/S1-organizer-over-reach.md) | Organizer over-reach / do-it-myself reflex | C | orchestrator | ⟳ | recurring | git/memory; `organizer-doesnt-implement-trust-the-process` |
| [S2](entries/S2-shared-decision-resolved-n-times.md) | One shared decision resolved N× independently (saturation) | C | orchestrator+auditors | ⟳ | open | ledger ✓ (4); `saturation-is-the-genealogy-blocker` |
| [S3](entries/S3-wrong-repo-commits.md) | Workflow agents commit in wrong repo (parent vs submodule) | C | workflow/finalize | ⟳ | solved | git/memory; PR #28 |
| [S4](entries/S4-parallel-work-swallowed-onto-main.md) | Parallel work swallowed onto main / branch-discipline | C | orchestrator | ⟳✗ | solved | git/memory; PR #47/#48,#58 |
| [D1](entries/D1-process-outran-docs.md) | Process outran its docs (machinery ≠ description) | M | orchestrator/docs | ⟳ | mitigated | git/proposal; PR #55,#56,#70 |
| [D2](entries/D2-generated-output-drift.md) | Generated-output drift (README re-fixed repeatedly) | M | README-gen/finalize | ⟳ | mitigated | git; PR #61–#65,#70,#72 |
| [D3](entries/D3-required-step-silently-stops.md) | Required step silently stops running (no coverage gate) | M | process/gate | ↔E5 | mitigated | proposal/git; PR #56,#66 |
| [T1](entries/T1-cost-fix-reverted.md) | Ships unvalidated optimization to main (reverted ×2) | T | orchestrator | ✗⟳ →E5,S4 | solved | git; PR #45→#48→#50→#59→#60 |
| [T2](entries/T2-render-sandbox-lacks-matplotlib.md) | Render sandbox lacks matplotlib (substrate) | T | builder/render | ⟳ | solved | ledger ✓ (2); `workflow-sandbox-lacks-matplotlib` *(Kind: substrate)* |
| [T3](entries/T3-acts-on-stale-tool-model.md) | Acts on stale tool-model (snapshot / bad model-arg) | T | orchestrator/tooling | ✗ | solved | git/memory; `workflow-tool-invocation-gotchas` |

### Migration & link edges (the catalog's core signal — kept structural, not prose-only)
- `E1a ⇄ E1b` — fix bound the referent (ended leniency); the wrong-figure-passes symptom
  **migrated** to a perceptual blind spot the referent never constrained.
- `X1 ↔ X2` — **inverse**: hardening over-routing risks under-routing. Same dial.
- `E5 ↔ D3` — self-certification is the cognitive root of "a required step silently stops."
- `T1 → E5` (shipping unvalidated = self-certification) · `T1 → S4` (durable fix = git discipline).
- `S2 shared-root` — one R&H saturation decision surfaced across RH2009 / heeger / hermann.

*The Pass-1 known set (above) is fully built. A Method-C un-distilled-discovery sweep + the `P#`
(positive baseline) / `U#` (never-caught) seeds will append below this line when run.*
