# ARCHITECTURE — what we are deliberately watching

The scaffold in ARCHITECTURE.md is a **working hypothesis**, committed now
so the two reproduction agents (hermann2010, cagly2012) exercise it. This
file is the organizer's notes-to-self: what is tentative, what would
falsify it, and the concrete signals to collect from the agent runs before
we solidify anything. Update it as evidence arrives; it is the input to the
next design pass.

## Tentative — do not solidify yet

1. **"Named pipeline stages" as the modularity unit.** Endorsed by the
   literature (LEMS/SciUnit/PyNN) *for the forward path*, but both first
   papers have an **outer fit/compare loop and model variants** that are
   not a forward stage. Watch whether agents can express "the science is
   in the comparison layer" without contorting the pipeline.
2. **Pure-by-default stages.** R&H is feedforward; rate/dynamical models
   are not. The integrator-as-stage rule is untested here. Watch the first
   stateful stage.
3. **measurement record as a single typed schema.** Watch whether one
   schema per figure is natural or whether agents fight it for
   multi-panel / heterogeneous figures.
4. **calibration.yaml namespacing.** Watch whether `<stage>.<param>` is the
   right key granularity or whether per-protocol overrides force a second
   axis (the R&H per-protocol `suppressive_*` mess suggests it might).
5. **Modification smoke test (Acceptance §4).** Unproven that a trivial
   config swap is achievable without unrelated edits. This is the single
   most important thing to verify — it *is* the project thesis.

## Signals to collect from each agent run

For hermann2010 and cagly2012, the organizer records, in
`models/<m>/logs/figure_diagnoses/` and the run README:

- **Where the agent fought the scaffold.** Every time it wanted to put a
  numeric literal in stage code, recompute in the view, or edit two layers
  for one logical change → a contract smell. Count and characterize them.
- **Stage-boundary churn.** How often the agent re-drew stage boundaries
  mid-run. High churn = wrong unit or premature contract.
- **Calibration sprawl.** Count `audited:false` ledger entries at "done".
  Compare to R&H's 4 SQs. Did the ledger contain it or just relocate it?
- **VLM-vs-deterministic disagreements.** Did the measurement-record-as-
  source-of-truth actually prevent test/figure disagreement (the Figure-1
  class)? Any residual disagreement is a scaffold failure, not an agent
  failure.
- **Loop behaviour.** Iterations to convergence; did the (manual) cap
  trigger; did auto-inner-loop + milestone-gates feel right or did the
  agent need gating mid-loop.
- **Modification smoke test outcome.** Did it pass cleanly, pass with
  unrelated edits (partial failure), or prove impossible (thesis at risk)?

## Paper-specific notes for briefing the agents

- **hermann2010 is NOT a new model** — it tests Reynolds & Heeger 2009
  (already reproduced). Its forward path *is* the R&H model. The genuinely
  new parts: a stimulus-encoder variant (flankers/sizes), a CRF→d′
  decision/linking stage, and an outer NLLS+bootstrap fit + nested-model
  comparison. **This is the flagship modifiability test**: ideally
  hermann2010 *reuses R&H stages* rather than re-deriving them — see the
  open decision in the handoff. Scope: deterministic forward + d′ linking;
  fitted params (d′max, c50, n) and bootstrap CIs **frozen/supplied**, not
  reproduced.
- **cagly2012** — MGSM model; offline GEM training is **stubbed as a frozen
  artifact** (user decision). Reproduce the inference path
  (encoding→normalization→estimate→mixture→readout). Watch the
  tightly-coupled λ/posterior stages (4–6) — a likely stage-boundary
  stress point — and the stimulus-dependent (data-dependent) topology,
  which breaks "static pipeline."

## Run findings (live — append per agent return)

### hermann2010 — returned 2026-05-18 (extension of R&H)

**Scaffold validated:** named stages held; the thin-adapter dependency on
`rh_model` held without fighting the contract; one-schema-per-figure was
natural; the view was never tempted to recompute. **Crucially, zero
deterministic/VLM disagreement** — the measurement-record-as-single-truth
design structurally prevented the Figure-1 class. Both figures green
(det 5/5, 6/6; VLM pass). **Modification smoke test passed cleanly**
(`flankers_present`/`regime` config swaps reconfigure one stage, zero
unrelated edits). Converged in 1 iteration/figure (caveat: extension of an
already-correct model — not a hard loop test; cagly2012 is the real one).

**Confirmed watchlist item 4 — the convergent friction predicted:** a
depended-on model that is **not formalized into calibrated stage entry
points** forces the dependent to (a) carry the dependency's
un-re-derivable 1D-discretization calibration as `audited:false` magic
numbers (22 entries, all unaudited), and (b) put a *regime-conditional in
its own stage code* that reaches into an R&H-internal detail
(`suppressive_spatial_sigma_scale` 0.55 vs 1.0) invisible at the dependent
layer. The ledger **contained** the sprawl (reviewable, one namespaced
place) but **did not eliminate** it — relocated cross-dependency debt.
hermann logged SQ-002 and flagged rather than refactoring R&H (correct).

**Candidate scaffold amendment (HELD pending convergent evidence):** add to
ARCHITECTURE.md §1 that *a depended-on model MUST expose calibrated stage
entry points*; a dependent reaching into raw internals + carrying
un-auditable calibration is a dependency-boundary failure, not the
dependent's debt. **Do not amend yet** — wait for carrasco2021 (also
R&H-dependent: independent confirmation?) and cagly2012 (standalone:
R&H-specific or general?). Solidifying now would violate this file's own
discipline.

Also surfaced: SQ-003 — "response gain" is ambiguous as absolute gap vs
multiplicative ratio; the measurement layer forced the choice into the open
(ratio = paper-correct) instead of burying it. This is the measurement
contract working as intended.

### cagly2012 — returned 2026-05-18 (standalone, from-scratch MGSM — hard loop)

**Scaffold held under real difficulty.** 8-stage pipeline; Figures 6 & 8
green (det 4/4 + VLM pass); the 7 failing tests are ONE root cause
(SQ-004) and were left **visible, not gamed**. Modification smoke test
passed cleanly (full→diagonal = one calibration key, zero unrelated
edits) — thesis holds for a from-scratch model. SQ-004 validated the
**stub→real-fit artifact-contract** design: a future real-GEM stage
honoring the same artifact lifts the block with zero inference edits; the
v1 scope limitation is explicit and contained, working as intended.

**Convergent scaffold defect (now 2 independent runs) — ACTED ON:** the
calibration ledger conflated two things with different owners/lifecycles.
- hermann SQ-002: depended-on model's implementation-side calibration has
  no home → carried as unauditable magic numbers.
- cagly SQ-003: `calibration.yaml` is in Phase-A-protected
  `article_aware/`, but stub/implementation-side calibration is written by
  Phase B → a logical self-contradiction in the scaffold.
Root: paper-derived params (Phase A, protected) and implementation-side
calibration (Phase B, writable; the SQ-001/002/004 class) are different
artifacts. **Fixed in ARCHITECTURE.md §3** (split by Phase ownership) — a
proven-by-construction contradiction, not a judgment call needing more
evidence.

**Recorded as known limitations (held, not restructured — workarounds
held):**
- SQ-001: for math with shared terms (Eqs 4/5/6/10/11 share λ), the stage
  boundary is an **imposed modifiability choice, not a natural
  decomposition**. The scaffold still helped (forced duplication out) but
  the boundary "feels arbitrary." Documented in ARCHITECTURE.md §1.
- SQ-002: the static `consumes/produces` pipeline survives data-dependent
  topology **only because the MGSM mixture is finite/enumerable**; a
  combinatorial pool would break it. Documented as a boundary condition.

## Falsification triggers (escalate to a redesign pass, don't patch around)

- The modification smoke test cannot be met for either model without
  editing unrelated code → the stage decomposition is the wrong unit.
- Calibration `audited:false` count is not materially lower than the
  ad-hoc R&H baseline → the ledger is theatre, not containment.
- Agents spend more effort serving the scaffold than reproducing the model
  → the contract is too heavy; thin it.
