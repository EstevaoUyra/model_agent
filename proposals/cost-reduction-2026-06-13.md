# Cost reduction — making the reproduction process cheaper (2026-06-13)

Pillar-4 process knowledge (see [VISION.md](../VISION.md)). Authored from a ~20-pass
batch on 2026-06-12/13 (`flash_hogan_1985`, `sutton_1988`, `zhang_1996`,
`roxin_ledberg_2008`, `bienenstock_cooper_munro_1982`, `pfister_gerstner_2006`, plus
their cleanup rounds). This is the *why and what*; it is **input to canon, not canon**.

This doc focuses on the **two highest-ROI, lowest-risk token cuts** — a **scoped
re-audit** and a **read-optimized paper/contract digest** — plus the process-quality
improvements that also save tokens. Three further levers (model tiering, killing the
round-recursion, per-model budget caps) are larger and/or riskier and are tracked
separately (§5).

---

## 1. What the batch actually cost (evidence)

- One full-pass costs **~1.3–3.3M subagent tokens, 14–44 agents, 1–5.8 hours**.
- **Rounds, not passes, are the multiplier.** `pfister_gerstner_2006` took **6 passes**
  (extract → fix → build → fix → build+descope → fix) ≈ **8M+ tokens for one model**;
  `roxin_ledberg_2008` took 4; `bienenstock_cooper_munro_1982` 2 (one 3.8 h).
- **Every agent ran Opus** — including digitization, README rewrites, test-authoring,
  process-audit (roles that don't need frontier reasoning).
- **Re-audits re-do everything.** Roxin's last `from='fix'` spent **5.8 hours
  re-auditing all three figures — including the already-faithful Fig 1 — to fix one
  figure's calibration.** This is the single clearest unit of waste in the batch.

The throughline: most tokens are spent **reloading context and re-verifying things that
did not change**, not on the reasoning that earns the cost (the implement step and the
adversarial faithfulness audit).

---

## 2. Proposal 1 — scope the re-audit to what changed

**Problem.** The verify loop's faithfulness audit re-renders and re-audits **every
figure on every round**, regardless of what changed. A one-figure calibration fix
triggers a full re-render + re-derivation of all figures (Roxin: 3 figures, one already
faithful, 5.8 h, for a Fig-4 retag).

**Change.** Make the re-audit incremental, driven by the *scope* the audit already
tags (`scope: model | figure`):

- Track what changed since the last green/locked audit — from the resolver's declared
  target and/or `git diff` of `article_aware/` + `implementation/`.
- **Figure-scope change** (one figure's protocol / view / per-figure calibration) →
  re-render and adversarially re-audit **only that figure**, and run the full
  **deterministic test suite** (already exists, cheap) as a regression gate on the rest.
- **Faithful + locked figures** → a cheap **render-hash / test-diff check** ("did its
  output change?"), not a fresh VLM + adversarial re-derivation. A figure is *locked*
  once it has passed an independent audit and nothing in its dependency set changed.
- **Model-scope change** (forward model, a shared mechanism, or a calibration value
  consumed by multiple figures) → **invalidate everything; full re-audit.** This is the
  load-bearing guard (see §6).

**Expected saving.** Fix rounds dominated this batch; scoping a typical fix round from
"re-audit N figures" to "re-audit 1 figure + a cheap regression hash" is roughly a
**3–5× cut per fix round**, with **no loss of rigor** — the figure that changed still
gets the full adversarial treatment; the others get a deterministic regression check
that is strictly cheaper, not weaker.

**Where it plugs in.** `full-pass.js` verify loop: the `audit-faithfulness` call
currently audits the whole model; give it the changed-figure set + a lock list, and
gate the per-figure adversarial re-render on membership. The `scope=model` findings
already exist to drive the invalidation.

---

## 3. Proposal 2 — cache a read-optimized paper/contract digest

**Problem.** Each pass spawns 14–44 agents, and most of the **builder-side** roles
(implement, test-author, README/state, stale-sweep) re-read the **full paper PDF +
`extracted_text.md` + all `article_aware/spec/*.yaml`** from scratch. The paper is
ingested ~10× per pass. That re-ingestion is pure duplicated cost.

**Change.** Phase A emits a compact, read-optimized **`paper_digest.md`** (a few KB vs
the multi-page PDF + sprawling YAML): the equations *with their numeric constants*, the
parameter tables, a one-paragraph-per-figure target summary (axes, what each panel
plots, the digitized minima/landmarks), and the binding citations. Phase A already
*extracts* all of this into the contract; the digest is a **read-optimized view** of it,
authored once.

- **Builder-side agents read the digest** + only the specific files they must edit —
  not the full PDF every time.
- **Crucial nuance — the digest is NOT the auditor's ground truth.** The whole point of
  the adversarial **faithfulness/spec auditor** is to check against the *real* paper; it
  must keep reading `paper/` directly (otherwise the digest becomes a single point of
  laundering — a wrong digest would silently pass). So the saving is on the *many cheap
  builder roles*, not on the (few, deliberately expensive) auditor roles. That is still
  most of the agent-count.

**Expected saving.** Cuts the per-agent ingestion tax across the ~10–30 builder-side
agents per model-lifetime; compounds with the round count. Smaller per-unit than
Proposal 1 but broad and zero-risk on the builder side.

---

## 4. Process improvements (quality — and they also save tokens)

- **The auto-implement is unreliable at "add a new figure" and "rewrite calibration."**
  In this batch I had to hand-spawn **directed resolver agents three times** — Pfister
  Figs 2/6 (declare protocols), Pfister descope, Roxin Fig 4 calibration — each then
  needing a `from='fix'` to verify: **double the work** every time. Fix: either harden
  the `implement` skill to add-figure / rewrite-calibration reliably, **or** give
  `from='fix'` an explicit "apply this audit-specified code fix" path so an
  audit-with-a-precise-fix is applied in-run instead of via a resolver + re-run. This is
  both a quality win (fewer organizer interventions) and a cost win (kills the two-step).

- **Keep these — the cost is in redundancy, not rigor.** The expensive parts that
  *earn* their cost and must not be cut: the **adversarial builder ≠ auditor**
  separation (it caught Zhang's gamed tripwire, the √λ defect, the sign-wrong pair
  model), **honest blocking** (no force-green), **resume-from-cache**, and **directed
  resolvers for precise fixes**. Cut redundancy and recursion, not the adversarial
  verification.

---

## 5. Deferred / separately tracked (larger or riskier)

- **Model tiering** — Opus only for the implementer + the adversarial faithfulness/spec
  audit; route digitization, README/state, test-authoring, process-audit, stale-sweep
  to a cheaper tier (Haiku/Sonnet). Plausibly 30–50% off. Deferred only because it needs
  per-role quality validation, not because it's hard.
- **Kill the round-recursion** (the §"#3" analysis): exhaustive first-audit + batched
  resolution; early paper-underdetermination triage; keep the `MAX_PAPERFIX` safety but
  resume in-run instead of restarting. **Riskiest** — it touches the verify-loop control
  flow that catches leniency-drift, so it needs its own validated change.
- **Per-model token budget cap** — block with findings-so-far at a ceiling (e.g. ~2M
  tokens) rather than recursing; bounds the long tail.

---

## 6. Risks & falsification

- **Scoped re-audit must never let a model-scope change skip the global check.** The
  failure mode: a change mislabeled `figure`-scope that actually perturbs a shared
  mechanism → other figures silently drift unaudited. Mitigations: (a) default to
  *model-scope = full re-audit* whenever the change touches `model.*`, a shared
  calibration key, or a stage used by >1 figure; (b) the deterministic full-suite
  regression gate runs **every** round regardless of scope, so a cross-figure
  regression still trips a test even if the adversarial re-render was skipped.
  **Falsifier:** if a scoped round ever ships a figure that a full re-audit would have
  caught, the scoping is too aggressive — revert to full re-audit for that change class.
- **The digest must never become the auditor's source of truth.** Falsifier: if a
  faithfulness verdict can be produced without any agent reading `paper/`, the digest
  has leaked into the audit path — re-isolate it to builder roles.
- Both proposals are **null-safe to disable**: if scoping or the digest misbehaves, fall
  back to "re-audit everything / read the full sources" with no correctness change, only
  cost.

---

## Status

**Proposed, not built.** Recommended order: Proposal 1 (biggest single win, contained
to the verify loop) → Proposal 4 process-improvement (implement reliability, removes the
resolver two-step) → Proposal 2 (digest). Validate each on one model against a
full-re-audit baseline before rollout. Related: WORKFLOW.md §6 (the faithfulness regime
the scoping must not weaken); the companion operational lesson from this batch was the
≤3–4 concurrent-pass limit (6 triggered a server-side rate-limit cascade).
