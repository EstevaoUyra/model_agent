# proposals/ — the process-knowledge home (Pillar 4)

[VISION.md](../VISION.md) Pillar 4: *the method for extending the library is
itself a deliverable, co-equal with the models.* This directory is where that
deliverable accumulates — the **validated lessons, the open improvements, and
the decision surface** distilled from running real agents against real papers.

It is **not canon.** Canon is the living set ([VISION](../VISION.md) ·
[STATUS](../STATUS.md) · [ARCHITECTURE](../ARCHITECTURE.md) ·
[DESIGN](../DESIGN.md)). These documents are the *input* to changing canon:
observations → proposals → (human decides) → canon edit.

## What's here

| Document | What it is |
|---|---|
| [design-pass-2026-05-18.md](design-pass-2026-05-18.md) | Consolidation of one full empirical cycle (hermann · cagly · carrasco · R&H migration + the `run_crf` refactor). The thesis verdict, the scaffold-change ledger, per-section contract status, and the **v2 decision surface (§8)**. |
| [process-improvements-2026-05-18.md](process-improvements-2026-05-18.md) | Candidate framework/skill changes from the R&H session, each as observation → proposal. Inputs to §6 of the design pass. |
| [corpus-expansion-2026-06-02.md](corpus-expansion-2026-06-02.md) | The plan to grow the library beyond 4 models: taxonomy + phylogeny of mechanistic vision models, the 1-deep + 2-complementary cluster shape (attention-normalization · sparse coding · predictive coding), the literature-grounding process upgrade, and the deferred-ontology seeding notes. |
| [reproduction-program-plan-2026-06-02.md](reproduction-program-plan-2026-06-02.md) | How we drive the ~21–23 corpus models to reproduction via dynamic workflows — mostly autonomously (critique agents substitute for the human gates, one human review at the end), in waves with revisits and a process retro between waves. Folds in the open-branch guardrails (parent-write guard, multi-VLM default, falsification-trigger escalation). **Awaiting "go".** |

## Where the rest of the process knowledge lives

- **Per-model operational briefs** stay *inside each model submodule* (they are
  model-specific): `AGENT_BRIEF.md` (cagly2012, carrasco2021, hermann2010),
  `MIGRATION_BRIEF.md` (reynolds_heeger_2009), `REFACTOR_BRIEF.md`
  (hermann2010). The *generalizable* lesson each trial taught is lifted out —
  into the design pass (§1, §3) and into
  [ARCHITECTURE_WATCHLIST.md](../ARCHITECTURE_WATCHLIST.md) (what would falsify
  the structural bets).
- **The validated method itself** is the [skills/](../skills/) directory +
  [WORKFLOW.md](../WORKFLOW.md). Proposals 2–3 of the design pass are about
  promoting proven patterns (the brief template, the closed loop) into skills.

## The through-line to the current bottleneck

The design pass §7 (open spec questions across all models) and §8.4 (schedule
the calibration audit + cross-model SQ adjudication) are the **same problem**
the VISION names as the binding constraint: *the human's time to validate
faithfulness*. The "where do things stand" review those sections ask for is
exactly what the VISION's next build — a **trust-triage report** with
evidence-grounded confidence and a researching faithfulness-auditor — is meant
to produce. Read those sections as the requirements for that artifact.

When a proposal here is adopted, edit canon and note the decision (the design
pass ledger is the model: defect → evidence → fix → commit → status).
