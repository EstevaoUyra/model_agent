# Cost reduction — making the reproduction process cheaper (2026-06-13)

Pillar-4 process knowledge (see [VISION.md](../VISION.md)). Authored from a ~20-pass
batch on 2026-06-12/13 (`flash_hogan_1985`, `sutton_1988`, `zhang_1996`,
`roxin_ledberg_2008`, `bienenstock_cooper_munro_1982`, `pfister_gerstner_2006`, plus
their cleanup rounds). This is the *why and what*; it is **input to canon, not canon**.

Three primary levers, in priority order — **(1) de-parallelize the per-figure fan-out
within a model**, **(2) scope the re-audit to the diff**, **(3) a read-optimized
paper/contract digest** — plus one process-quality fix and a couple of supporting token
levers. **The faithfulness regime is preserved by all of them**: every role, the phase
order, and the adversarial separation (digitizer ≠ auditor, builder ≠ auditor) are
unchanged.

---

## 1. What the batch actually cost (evidence)

- One full-pass costs **~1.3–3.3M subagent tokens, 14–44 agents, 1–5.8 hours**.
- **Rounds, not passes, are the multiplier.** `pfister_gerstner_2006` took **6 passes**
  ≈ **8M+ tokens for one model**; `roxin_ledberg_2008` took 4; `bienenstock_cooper_munro_1982`
  2 (one 3.8 h).
- **The 14–44 agent count is mostly per-figure fan-out.** Each per-figure stage
  (describe → digitize → audit) runs one agent *copy per figure* (`pipeline(FIGURES, …)`
  / `parallel(…)`). N figures = N copies of each role. That fan-out is the source of both
  the agent count (→ the rate-limit cascade at 6 concurrent passes) and most of the
  duplicated context-reads.
- **Every agent ran Opus** — including roles that don't need frontier reasoning.
- **Re-audits re-do everything.** Roxin's last `from='fix'` spent **5.8 hours
  re-auditing all three figures — including the already-faithful Fig 1 — to fix one
  figure's calibration.** The single clearest unit of waste in the batch.

Throughline: most tokens go to **spinning up redundant agents, reloading context, and
re-verifying things that did not change** — not the reasoning that earns the cost (the
implement step and the adversarial faithfulness audit).

---

## 2. Lever 1 — de-parallelize the per-figure fan-out (single sweep per role)

**This is an execution-topology change only. The workflow diagram, the roles, the phase
order, and the adversarial separation are all unchanged.** The diagram always drew *one
box per role* — it was hiding that each box fans out to one copy per figure. Collapse
that fan-out: **each role becomes a single agent that sweeps all figures sequentially.**
The digitization gate goes from `pipeline(FIGURES, digitize-agent, audit-agent)` (2N
agents) to **one digitize agent over all figures → one audit agent over all figures** (2
agents), in the same order. Same for the describe-figure stage and any other per-figure
fan-out. Digitizer ≠ auditor still holds — only the **count per role** drops from N to 1.

Three wins, two of them bigger than the token math:

- **Concurrency ↓ → cures the throttle.** The rate-limit cascade this batch (6 passes ×
  ~14 agents → server-side throttling that crashed five runs) came from the fan-out.
  One-per-role drops the per-pass agent count enough that the throttling largely goes
  away. Automatic, no tuning.
- **Recursion ↓ → the big one.** The most expensive pattern was *layered discovery* —
  Roxin's Fig-3 fix revealed Fig-4 had the **identical** defect, costing a whole extra
  round. That happens *because per-figure auditors are siloed*: no single one sees the
  shared defect. **One auditor over all figures catches "these N figures share a defect"
  in one pass**, attacking the #1 cost multiplier (rounds), not just per-agent overhead.
- **Per-agent fixed overhead ↓.** Two agents' worth of system-prompt + skill-load
  instead of 2N.

**Token nuance (honest).** De-parallelization does not *by itself* collapse the
shared-context reload — the API is stateless, so the single agent re-sends its growing
transcript each turn. The clean token win comes from **intra-agent prompt caching**,
which is trivial here because it is *one conversation*: the paper/contract prefix
auto-caches across the agent's turns at ~0.1× input cost (the 5-min cache TTL easily
covers a single sweep). That is *easier* than caching across parallel per-figure agents,
which needs an engineered shared prefix. So Lever 1 and intra-agent caching compose
naturally — with caching on, the sequential sweep reads the paper once, not N times.

**Guardrail — preserve coverage.** A single auditor over all figures **must emit a
structured per-figure verdict** (one explicit FAITHFUL/DIVERGENT per figure), so "audit
all at once" cannot silently degrade into "skim figures 4–6." This keeps the
leniency-drift the regime guards against (the Zhang goalpost-move) from sneaking in
through diluted attention.

**Risk — high-figure-count models.** For 3–4 figures this is pure upside. For 10–14
(R&H, Heeger), one agent holding all figures grows an O(N²) transcript and dilutes
attention on the later figures (quality + possible context-limit). Mitigation: **cap the
sweep** — one agent per ~4–5 figures rather than strictly 1 — and/or lean on intra-agent
caching to keep the growing prefix cheap. The cap is a tuning knob, not an architecture
change; the topology (one-box-per-role, same order, same separation) is identical either
way.

**Where it plugs in.** `full-pass.js`: replace the `pipeline(FIGURES, extract-figure, …)`
digitization gate and any `parallel(figures.map(...))` with a single agent per role given
the **full figure list**. The `phase()` / role structure is untouched.

---

## 3. Lever 2 — scope the re-audit to the diff

**Problem.** The verify loop's faithfulness audit re-renders and re-audits **every figure
on every round**, regardless of what changed. A one-figure calibration fix triggers a
full re-render + re-derivation of all figures (Roxin: 3 figures, one already faithful,
5.8 h, for a Fig-4 retag).

**Change.** Make the re-audit incremental, driven by the *scope* the audit already tags
(`scope: model | figure`):

- Track what changed since the last green/locked audit — the resolver's declared target
  and/or `git diff` of `article_aware/` + `implementation/`.
- **Figure-scope change** (one figure's protocol / view / per-figure calibration) →
  re-render and adversarially re-audit **only that figure**, and run the full
  **deterministic test suite** (already exists, cheap) as a regression gate on the rest.
- **Faithful + locked figures** → a cheap **render-hash / test-diff check** ("did its
  output change?"), not a fresh VLM + adversarial re-derivation. A figure *locks* once it
  has passed an independent audit and nothing in its dependency set changed.
- **Model-scope change** (forward model, a shared mechanism, a calibration value consumed
  by >1 figure) → **invalidate everything; full re-audit.** The load-bearing guard (§7).

This is the "focus on the diff" half of the plan — the natural partner to Lever 1: with a
single sweep per role *and* diff-scoping, a fix round becomes **one auditor re-auditing
only the changed figure(s)**.

**Expected saving.** Fix rounds dominated this batch; scoping a typical fix round from
"re-audit N figures" to "re-audit 1 figure + a cheap regression hash" is roughly a
**3–5× cut per fix round**, with **no loss of rigor** — the changed figure still gets the
full adversarial treatment; the rest get a deterministic regression check that is
strictly cheaper, not weaker.

---

## 4. Lever 3 — read-optimized paper/contract digest

**Problem.** The builder-side roles (implement, test-author, README/state, stale-sweep)
re-read the **full paper PDF + `extracted_text.md` + all `article_aware/spec/*.yaml`**
from scratch. That re-ingestion is pure duplicated cost.

**Change.** Phase A emits a compact, read-optimized **`paper_digest.md`** (a few KB vs
the multi-page PDF + sprawling YAML): equations *with their numeric constants*, the
parameter tables, a one-paragraph-per-figure target summary (axes, what each panel plots,
the digitized minima/landmarks), and the binding citations. Phase A already *extracts*
all of this into the contract; the digest is a **read-optimized view** of it, authored
once.

- **Builder-side agents read the digest** + only the specific files they must edit.
- **Crucial nuance — the digest is NOT the auditor's ground truth.** The adversarial
  faithfulness/spec auditor must keep reading `paper/` directly — otherwise the digest
  becomes a single point of laundering (a wrong digest would silently pass). So the saving
  is on the cheap builder roles, not the (few, deliberately expensive) auditor roles.

**Expected saving.** Cuts the per-agent ingestion tax; compounds with the round count.
Smaller per-unit than Levers 1–2 but broad and zero-risk on the builder side. (Note: once
Lever 1 collapses the per-role fan-out, the digest's value concentrates in the few
remaining builder agents, and **intra-agent caching** subsumes part of it — keep it as
the cross-agent complement.)

---

## 5. Process improvement (quality — and it also saves tokens)

- **The auto-implement is unreliable at "add a new figure" and "rewrite calibration."**
  This batch I hand-spawned **directed resolver agents three times** (Pfister Figs 2/6,
  Pfister descope, Roxin Fig 4 calibration), each then needing a `from='fix'` to verify:
  **double the work** every time. Fix: harden the `implement` skill for those operations,
  **or** give `from='fix'` an explicit "apply this audit-specified code fix" path so a
  precise audit fix is applied in-run instead of via a resolver + re-run. Both a quality
  win (fewer organizer interventions) and a cost win (kills the two-step).

- **Keep these — the cost is redundancy, not rigor.** The parts that *earn* their cost
  and must not be cut: the **adversarial builder ≠ auditor** separation (caught Zhang's
  gamed tripwire, the √λ defect, the sign-wrong pair model), **honest blocking** (no
  force-green), **resume-from-cache**, and **directed resolvers for precise fixes**.

---

## 6. Supporting & deferred levers

- **Intra-agent / within-pass prompt caching** — the token backstop for Lever 1
  (paper/contract prefix cached across the single sweep's turns at ~0.1×; cache **read
  ≈ 0.1×**, **write = 1.25×** at 5-min TTL / **2×** at 1-h; strict prefix match, so keep
  the stable context first and the per-figure work after the `cache_control` breakpoint).
- **Model tiering** — Opus for the implementer + the adversarial audits; route the
  now-single digitize/describe/state/stale-sweep agents to a cheaper tier (Haiku/Sonnet).
  Plausibly 30–50% off; needs per-role quality validation.
- **Batches API at 50%** — once the per-figure fan-out is gone there is little *within*-pass
  to batch, so this becomes a **cross-model** lever: run independent models' non-latency-
  sensitive agents as a batch at half price.
- **Kill the round-recursion** further — exhaustive first-audit + batched resolution; early
  paper-underdetermination triage; keep the `MAX_PAPERFIX` safety but resume in-run rather
  than restart. **Riskiest** (touches the leniency-drift control flow). Note Lever 1
  already partially does this (one auditor sees all figures at once).
- **Per-model token budget cap** — block with findings-so-far at a ceiling (~2M tokens)
  rather than recursing; bounds the long tail.

---

## 7. Risks & falsification

- **De-parallelization must not silently drop per-figure coverage.** Falsifier: if the
  single auditor's output lacks an explicit per-figure verdict, or a figure that a
  fanned-out per-figure auditor would have flagged ships unflagged, the sweep is skimming
  — enforce the structured per-figure verdict (and, on high-figure models, the fan-out cap).
- **Scoped re-audit must never let a model-scope change skip the global check.** Mitigations:
  (a) default to *model-scope = full re-audit* whenever the change touches `model.*`, a
  shared calibration key, or a stage used by >1 figure; (b) the deterministic full-suite
  regression gate runs **every** round regardless of scope. Falsifier: if a scoped round
  ever ships a figure a full re-audit would have caught, the scoping is too aggressive.
- **The digest must never become the auditor's source of truth.** Falsifier: if a
  faithfulness verdict can be produced without any agent reading `paper/`, the digest has
  leaked into the audit path.
- **All three are null-safe to disable** — revert to the fan-out / full re-audit / full
  sources with no correctness change, only cost.

---

## Status

**Proposed, not built.** Recommended order: **Lever 1** (de-parallelize — biggest
structural win, cuts concurrency *and* recursion, and it's a topology change that leaves
the regime byte-identical) → **Lever 2** (diff-scoped re-audit) → the **process-improvement**
(implement reliability) → **Lever 3** (digest), with intra-agent caching as the token
backstop. Validate each on one model — a **small** model first, then a **high-figure**
model for Lever 1 (where the fan-out cap is tested) — against a full-fan-out / full-re-audit
baseline. Related: WORKFLOW.md §6 (the faithfulness regime none of this may weaken); the
companion operational lesson was the ≤3–4 concurrent-pass limit (6 triggered the rate-limit
cascade) — which Lever 1 also relieves from the inside.
