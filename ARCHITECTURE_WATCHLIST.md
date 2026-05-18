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

### carrasco2021 — returned 2026-05-18 (extension of R&H; 5-variant config)

**Flagship validation.** Figure 7 green (det 7/7 + VLM pass), Supp Fig 4
green-structural (no paper image exists), 31/31 tests. **The modification
smoke test held cleanly for the hardest case**: all 5 ModulationStage
variants run via one `modulation.variant` calibration-string change with
zero edits to protocols/measurements/views/SDT. ARCHITECTURE §1
"variants as config, not code" + §5(4) are strongly validated.

**Resolves the held §1 amendment (3 runs, convergent).** hermann and
carrasco both depend on R&H but had opposite outcomes:
- hermann reused R&H's *calibrated 1D CRF protocol* → severe leak (22
  unauditable carried knobs + regime-conditional in stage code).
- carrasco reused R&H's *clean forward primitives* (E, K, divisive norm,
  attention Gaussian) and built its own protocol/readout → clean reuse,
  zero `rh_model` edits, only a θ-grid convention adaptation handled as an
  assumption; 10 audited:false, all its own frozen-fit stubs (not leak).
- cagly (standalone) confirms the sprawl without a dependency is the
  model's own (no published numbers), a different cause.

Conclusion: the problem is **reuse-surface granularity**, not dependency
per se. *Depend on primitive stages (fine); a calibrated protocol is not a
reuse surface (it drags its calibration across the boundary).* This is now
**acted on in ARCHITECTURE.md §1** (no longer held — the hermann/carrasco
contrast is the convergent evidence the discipline required).

**Framework bug found + fixed (organizer domain):** `test_table._sort_key`
crashed on mixed int/str figure markers (`(0,int)` vs `(0,str)`
incomparable). Never hit before — rh_model used all-int markers. Fixed
with a uniformly-typed key + regression test (23/23). Carrasco worked
around it in-model without framework edits and flagged it — correct
behavior.

**Process risk (record, propose a guard):** the carrasco agent
accidentally ran `git add -A`/`--amend` against the **parent** repo;
it self-reverted and parent integrity is verified intact, but a nested
agent reaching the parent repo is a real hazard. Briefs say "commit inside
THIS repo" but that was insufficient. → Proposal: agent briefs must
explicitly forbid `git add -A` and any parent-repo git op, and/or a
guard (pre-commit refusing commits whose cwd-repo != the model repo).
Logged for the process-improvements discussion, not built now.

### reynolds_heeger_2009 arch-migration — returned 2026-05-18

**The §1 reuse-surface fix is validated end-to-end (headline).** The
formalized `rh_model.crf_protocol.run_crf(stimulus_size,
attention_field_size, gamma, regime, contrasts)` exposes only scientific
params + a regime *name*; a signature-introspection test asserts no
`suppressive_*`/`baseline_*`/`sigma` leaks into the public surface. It is
**byte-identical (max abs diff 0.0, both regimes)** to hermann2010's
current hand-rolled calibrated CRF. So hermann can depend on it carrying
**zero** of its ~10 carried R&H knobs and **zero** regime-conditional —
the §1 amendment is proven in practice, not just argued.

**Behavior preservation airtight (how a migration of a green model should
go):** 64/64 identical pass set; all 10 protocol outputs byte-identical
(hash); all 7 figures **pixel-identical** to pre-migration `5d3e751`
(decoded-array diff 0) → VLM unchanged by construction; modification smoke
test passes; dependents unaffected (carrasco 31/31, hermann 14/14); +17
new ARCHITECTURE-shape tests green. Stage decomposition met **no**
resistance (R&H is feedforward, kernels already pure) — the abstraction is
a *natural* fit here, no `boundary: imposed` needed.

**New convergent contract gap — FIXED (2nd instance of the §3 root
cause).** §1 filed the stage manifest in `article_aware/spec/
model_spec.yaml`, but `article_aware/` is Phase-A-protected and the stage
decomposition is a Phase-B concern; the migration was structurally forced
to put the manifest implementation-side. Same root cause as the §3
calibration defect (a Phase-B-owned artifact filed under Phase-A
protection). Fixed in ARCHITECTURE.md §1 + layout: paper-derived
*pipeline/dataflow* stays Phase-A spec; the *stage manifest* is
Phase-B-owned, `implementation/src/<pkg>/stages/manifest.yaml`. The agent
independently arrived at this resolution — strong signal it is correct.

**Ledger:** paper-derived 51 entries / 0 unaudited; implementation-side
34 / 33 unaudited. Contained, not erased (consistent with hermann/cagly).

## Falsification triggers (escalate to a redesign pass, don't patch around)

- The modification smoke test cannot be met for either model without
  editing unrelated code → the stage decomposition is the wrong unit.
- Calibration `audited:false` count is not materially lower than the
  ad-hoc R&H baseline → the ledger is theatre, not containment.
- Agents spend more effort serving the scaffold than reproducing the model
  → the contract is too heavy; thin it.
