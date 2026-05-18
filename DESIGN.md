# Neuromodels — Design rationale

This document captures the **why** behind the system. For *where* things
live, see [REPO_STRUCTURE.md](REPO_STRUCTURE.md). For *how* to use the
workflow end-to-end, see [WORKFLOW.md](WORKFLOW.md).

When implementation choices later look ambiguous, the answer is in
WORKFLOW.md or REPO_STRUCTURE.md. When the *underlying reason* for a
design choice is unclear, the answer is here. When this document is
wrong, update it before writing code.

> **See also:** [STATUS.md](STATUS.md) (what is actually built) and
> [ARCHITECTURE.md](ARCHITECTURE.md) (the contract structure every
> reproduction must produce — the stage pipeline, the
> protocol→measurement→view figure split, calibration-as-data, the closed
> loop, and the verifiable+modifiable acceptance criteria). The end goal
> is not faithful reproduction alone; it is a substrate a scientist can
> verify and modify. ARCHITECTURE.md supersedes the older structural
> assumptions sprinkled through §§2–8 below where they conflict.

---

## 1. Goals and non-goals

### Goals

- Given a published article describing a computational model, produce:
  - A structured specification of the model.
  - A clean Python implementation that passes a generated test suite.
  - A set of reproduced figures that visually correspond to those in
    the paper.
  - A log of every assumption made (where the paper underspecified) and
    every suspected paper issue (where the paper appears wrong or
    ambiguous).
- Surface underspecification as a first-class output, not as silent
  decisions buried in code.
- Provide a library structure such that researchers can extend or
  modify any model without re-reading the entire paper.
- Detect when the agent is stuck and escalate to a human, rather than
  burning iterations.

### Non-goals (v1)

- **Stochastic models / fitting loops.** v1 reproduces the
  **deterministic forward/inference path**. A model whose parameters come
  from a stochastic fit or offline training (GEM/EM, NLLS+bootstrap) is in
  scope **only with the fitting stage stubbed**: the learned parameters
  are supplied as a frozen, persisted artifact (ARCHITECTURE.md §1) and
  the forward path consumes them deterministically. Reproducing the
  fitting/optimization/bootstrap itself is deferred. (Decision 2026-05-18,
  prompted by hermann2010 and cagly2012, both of which wrap the forward
  model in an outer fit/compare loop.)
- **Full autonomy.** A human is in the loop for: approving the
  article-aware artifacts (spec, pseudocode, extracted data, reproduced
  figures), deciding the verdict on adversarial-judge reviews, and
  resolving stuck signals.
- **Multi-paper synthesis.** Each model run targets one paper. If the
  spec needs to be enriched from another paper, that is a human
  decision that produces a new round of extraction.
- **Reproducing real experimental data.** The target is the *paper's
  simulated outputs* (its figures and tables), not the empirical data
  those figures were compared against.

---

## 2. The Phase A / Phase B cleavage

The hard split between Phase A (article-aware) and Phase B (no article
access) is the most important design choice in this system. It forces
the spec to be self-contained: anything the implementation agent cannot
find in the spec is, by definition, an underspecification — and gets
recorded as an `Assumption`. Without this split, the implementation
agent would silently re-derive things from the paper, and the spec
would drift into being a partial summary rather than a complete
contract.

This is enforced by **tooling, not prompt instructions**. Prompts are a
hint; tool config (Claude Code permissions, working directory scope) is
a guarantee. The boundary table in
[REPO_STRUCTURE.md](REPO_STRUCTURE.md#boundaries-enforced-by-tooling-not-just-prompts)
makes it concrete.

The downstream consequence: the spec must be *executable*. That's why
`model_spec.yaml` includes a `pipeline` field listing computation steps
in order — not because it's elegant, but because the implementation
agent cannot reverse-engineer the dataflow from equations and prose
alone without re-reading the paper.

Figure-level tests follow the same rule. Qualitative claims live as
ordinary pytest files in `article_aware/extracted_data/test_<figure>.py`,
with paper-specific claim helpers co-located in that directory. Each
protocol in `model_spec.yaml` declares the exact `expected_outputs` its
runner must return, and the tests exercise those outputs directly in
Python. This keeps the paper-derived contract in `article_aware/`
instead of duplicating it under `implementation/`, while avoiding a
second expression language or eval path.

---

## 3. Adversarial judge protocol

LLM judges are unreliable for evaluating implementations: they tend toward
over-permissive verdicts and miss subtle bugs (sign errors, off-by-one, wrong
normalization). The mitigation is structural — two judges with opposite
roles (attacker, defender), both seeing the same three inputs (`rubric`,
`context`, `under_review`) and neither seeing the other's output. The human
reads both and decides. This isn't majority voting; it's a way to surface
counter-arguments the human might otherwise miss.

**Judges must not see** the paper, run/test IDs, spec refs, review-queue
paths, other tests, the other judge's output, or prior judge runs on the
same test. This isolation prevents pattern-matching to past verdicts.
Operational details (CLI, input file format) are in
[WORKFLOW.md](WORKFLOW.md#adversarial-judge-usage).

**No autonomous judge decisions in v1.** Building an automated path before
calibration data exists would silently inherit judge biases. Tests reduce
to deterministic checks wherever possible — judges are reserved for claims
that genuinely resist coding ("the response profile is sigmoidal-looking"),
not as a default.

---

## 4. Stuck detection — why git diff, not self-report

Self-reported "what I changed" from the agent is unreliable: agents
rationalize, summarize wrong, or omit. The aggregated log uses **git
diff as the load-bearing signal**. The agent's `agent_rationale` is
logged for *human* reading, not as input to the stuck classifier.

### Diff features

Computed from the model repo git diff between the current attempt
commit and the attempt commit recorded on the last failing run of the
same `test_id`:

- `diff_hash` — content hash of the diff.
- `lines_changed` — count.
- `files_touched` — set of file paths.
- `regions_jaccard_prior` — Jaccard similarity of changed line ranges
  against the union of changed line ranges in this debugging session
  for this test.

### Trigger thresholds (initial; expected to iterate)

The detector emits an unblock signal if, for any test in an active
debugging session:

- 2 consecutive identical `diff_hash` values → thrashing, no actual
  change.
- 4 attempts with `regions_jaccard_prior > 0.7` → oscillating in the
  same code regions.
- 6 attempts total → conservative cap regardless of progress shape.

Thresholds will be wrong; tune from real runs. The features are the
contract; the rules are policy.

### Why diff identity is the key feature

The "stuck" failure mode that's hardest to recover from is the agent
making the *same change* repeatedly with no insight. Identity-of-diff
catches this directly. Region overlap (Jaccard) catches the slower
form: nibbling at the same code without expanding the search.
Total-attempt cap is the backstop — even healthy exploration shouldn't
go forever without escalation.

---

## 5. Spec edits invalidate prior passes

If the human edits any file in `article_aware/` after Phase B has
started, every prior test pass was validated against the *old* spec.
The runner records `spec_commit_hash` on every test row; queries that
ask "what is currently passing" filter to rows whose `spec_commit_hash`
matches the current head of `article_aware/`.

In v1 this is an **advisory filter** — the human or agent reads it and
reruns affected tests. Selective dependency-aware invalidation
(re-running only tests that depend on the changed spec components) is
on the deferred list. This is acceptable because spec edits during
Phase B are expected to be rare and the cost of re-running the suite
is low.

---

## 6. Per-model versioning

Each model directory is a nested git repository tracked from the
parent monorepo as a submodule. This gives:

- **Independent history per model** — you can see the full evolution
  of one reproduction without noise from framework changes or other
  models.
- **Co-evolution at the parent level** — the parent monorepo's commits
  bump the submodule pointer when a model milestone happens, so the
  parent's history shows the order things landed across models and
  framework.
- **Replayability** — the framework records both the model commit hash
  and the parent framework commit hash with every test row, so any
  past run can be replayed against the same code state.

The parent monorepo *is* the framework repo throughout v1. Lifting the
framework into a package-only repo is a deferred refactor; doing it
prematurely creates split-history headaches before we know which
boundary actually wants to be permanent.

---

## 7. Why sanity checks live alongside tests

Sanity checks survive where ad-hoc debugging scripts get thrown away. The
rationale (binary tests don't show *shape*; dual text+PNG output serves
agents and humans differently; shared helpers enforce cross-model style)
and the operational rules live in
[`skills/write-sanity-check/SKILL.md`](skills/write-sanity-check/SKILL.md).

The line between sanity check and test (no `assert` in a sanity check) is
load-bearing — keeping the two surfaces separate prevents them from
collapsing into each other.

---

## 8. Citation/Assumption docstring rule

Every function in `implementation/src/` carries either `Citation:`
(into the paper, via the `C-NNN` IDs in `citations.yaml`) or
`Assumption:` (into `assumptions.yaml` via `A-NNN` IDs), or both. A
static check enforces *presence*. The full rule and examples are in
[WORKFLOW.md](WORKFLOW.md#step-4--implement-the-model-bottom-up).

What this rule does *not* do: verify *quality*. The cited paragraph
might not actually support the function's behavior. The discipline is
the lightest mechanism that surfaces underspecification at the level
where it matters (per-function), and forces the agent to consciously
distinguish "the paper says this" from "I assumed this." Periodic
human audit is required for quality; automated quality auditing is on
the deferred list.

---

## 9. Deferred decisions

These are explicitly punted to keep v1 scoped. Each appears here so we
do not re-litigate them when they come up; the answer is "deferred,
see DESIGN.md §9".

- **Spec schema specifics.** Pydantic models for `model_spec.yaml`
  pinned against the first real article (Reynolds & Heeger 2009).
  Future models may surface fields we don't yet have.
- **Stochastic models.** Distributional comparison (KS test, percentile
  bounds over N runs), seed management, and noise-aware tolerances.
  Will add when the deterministic path is solid.
- **Citation/Assumption quality audit.** Static check verifies presence
  only. Sampling-based audit of whether cited passages actually support
  function behavior is for a later round.
- **Cache invalidation on spec change.** v1 is advisory: filter by
  `spec_commit_hash`. Selective dependency-aware invalidation is later.
- **Autonomous judge decisions.** No automated path treats judge
  output as a decision in v1. Calibration data needs to exist first.
- **Tolerance defaults.** Initial values will iterate from real runs.
  No principled derivation in v1.
- **Stuck-detector thresholds.** Initial values in §4 will iterate
  from real runs.
- **Multi-paper synthesis.** Out of scope. Enriching a spec from
  another paper is a human action that produces a new round of
  extraction.
- **UI for human review.** Human review uses files in `review_queue/`;
  no web UI is planned for v1.
- **Framework repository split.** The parent monorepo remains the
  framework repo throughout v1. Lifting the framework into a
  package-only repo is a future refactor.
