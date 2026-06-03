# AGENTS.md — entry point for agent sessions

This file is the thin operational entry point for agents working in this
repo. For full guidance, follow the pointers below.

> **Start with [VISION.md](VISION.md)** for *why this project exists* — the
> four pillars (faithful · understandable · modifiable-by-scientific-judgment ·
> process-as-deliverable), ordered and in tension. Then **read
> [STATUS.md](STATUS.md)** for *what is actually built*: [WORKFLOW.md](WORKFLOW.md)
> (the single consolidated process/structure doc) describes the *target*; parts (the
> framework runner, stuck detector, `logs/*.csv`) are **not built**. The
> citation/assumption
> static check *is* built but presence-only and run manually (no CI). STATUS.md
> is the canonical map of what actually exists and wins on any conflict.

## Identify your phase first

Your invocation context tells you which phase you're in. Read the
matching section of [WORKFLOW.md](WORKFLOW.md) before doing anything.

- **Phase A (article extraction):** you have access to a paper and need
  to produce the `article_aware/` artifacts. Read WORKFLOW.md §2 (Phase A) + §3
  (how tests are generated — the figure checklist is authored *from the paper image*).
- **Phase B (model implementation):** you have access to
  `article_aware/` but **NOT** to `paper/`. Read WORKFLOW.md §4 (Phase B) + §5
  (calibration).
- **Adversarial judge:** you receive only `rubric` / `context` /
  `under_review`. Don't ask for or look at anything outside that.

If you're unsure which phase you're in, ask the user. Don't guess.

## Critical DO NOTs

- **NEVER read `paper/` if you're in Phase B.** The whole approach
  collapses if the implementation agent peeks at the paper. If something
  isn't in `article_aware/`, it's an underspecification — escalate via
  `logs/spec_questions.md`, don't go read the paper.
- **NEVER write to `article_aware/` from Phase B.** Those artifacts are
  the contract; only Phase A modifies them. If the spec is wrong, log a
  spec question; don't silently fix the spec.
- **NEVER skip the citation/assumption docstring.** Every function in
  `implementation/src/` needs `Citation:` or `Assumption:` (or both) in
  its docstring. A **presence+resolution** check exists
  (`neuromodels/framework/static_checks/check_citations.py`, run manually —
  `python -m neuromodels.framework.static_checks.check_citations`; no CI is
  wired): it asserts every `C-NNN`/`A-NNN` tag *resolves* to a ledger entry,
  **not** that the tag is on the right function or that the cited passage
  supports the behavior. That *quality* check is a periodic human audit
  (STATUS.md, WORKFLOW.md §4 and §6).
- **NEVER turn a sanity check into an assertion.** The moment you write
  `assert`, it's a test. Move it to `tests/`.
- **NEVER burn iterations past the cap.** The stuck-detector isn't built;
  honor the documented iteration cap. In the autonomous program a STUCK
  model is **deferred to a later wave** (program plan §6), never pushed on
  indefinitely, and never a reason to halt the program.

## Quick reference: where things go

| What you want to do                            | Where to write                          |
|------------------------------------------------|-----------------------------------------|
| Phase A artifact (spec, pseudocode, etc.)      | `article_aware/`                        |
| Phase B model code                             | `implementation/src/`                   |
| Phase B test                                   | `implementation/tests/`                 |
| Phase B exploration script                     | `implementation/sanity_checks/`         |
| Escalate spec ambiguity (impl agent)           | `logs/spec_questions.md` (append-only)  |
| Record suspected paper error                   | `assumptions.yaml` / `spec_questions.md` |

For the full directory layout and boundary rules, see
[WORKFLOW.md](WORKFLOW.md) §1 (boundaries) and §8 (per-model layout).

## Useful commands

```bash
# Install (editable) with optional sanity-check plotting deps
pip install -e ".[sanity,test]"

# Run all model tests
pytest models/<model>/implementation/tests/

# Run a sanity check
python models/<model>/implementation/sanity_checks/check_<topic>.py
```

## When to commit

- Phase A: after spec+pseudocode complete, after data+figures complete,
  after `APPROVED` is written.
- Phase B: there is no runner — you make milestone commits when a component
  or a figure protocol's tests all pass (on the model's feature branch;
  commit only inside the model repo, never the parent).

For full commit cadence and escalation flows, see
[WORKFLOW.md](WORKFLOW.md).
