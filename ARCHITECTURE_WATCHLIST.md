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

## Falsification triggers (escalate to a redesign pass, don't patch around)

- The modification smoke test cannot be met for either model without
  editing unrelated code → the stage decomposition is the wrong unit.
- Calibration `audited:false` count is not materially lower than the
  ad-hoc R&H baseline → the ledger is theatre, not containment.
- Agents spend more effort serving the scaffold than reproducing the model
  → the contract is too heavy; thin it.
