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

**The reproduced corpus is indexed in [PAPERS.md](PAPERS.md)** — every paper in
`models/`, grouped by cluster, with citation, DOI, and recorded status. The
genealogy/rationale lives in
[proposals/corpus-expansion-2026-06-02.md](proposals/corpus-expansion-2026-06-02.md).

## Identify your phase first

Your invocation context tells you which phase you're in. Read the
matching section of [WORKFLOW.md](WORKFLOW.md) before doing anything.

- **Phase 0 (source acquisition):** runs *before* Phase A. Gather all upstream
  sources — published materials (main, Online Methods, Supplementary) into
  `paper/`, original author code into `paper/code/` — and write `paper/SOURCES.md`
  accounting for every artifact (obtained / exists-but-not-obtained /
  confirmed-absent). Follow `skills/acquire-sources/SKILL.md`.
- **Phase A (article extraction):** you have access to a paper and need
  to produce the `article_aware/` artifacts. Read WORKFLOW.md §2 (Phase A) + §3
  (how tests are generated — the figure checklist is authored *from the paper image*).
  You may read `paper/code/` (a spec source); a value you take from it gets a
  `CODE-NNN` entry in `article_aware/spec/code_refs.yaml`, tagged `source: CODE-NNN`.
- **Phase B (model implementation):** you have access to
  `article_aware/` but **NOT** to `paper/`. Read WORKFLOW.md §4 (Phase B) + §5
  (calibration).
- **Adversarial judge:** you receive only `rubric` / `context` /
  `under_review`. Don't ask for or look at anything outside that.

If you're unsure which phase you're in, ask the user. Don't guess.

## Critical DO NOTs

- **NEVER read `paper/` if you're in Phase B.** The whole approach
  collapses if the implementation agent peeks at the paper. This includes
  **`paper/code/`** (the original authors' code) — seeing it makes the
  reproduction a translation, not an independent one. If something
  isn't in `article_aware/`, it's an underspecification — escalate via
  `logs/spec_questions.md`, don't go read the paper.
- **NEVER write to `article_aware/` from Phase B.** Those artifacts are
  the contract; only Phase A modifies them. If the spec is wrong, log a
  spec question; don't silently fix the spec.
- **NEVER skip the citation/assumption docstring.** Every function in
  `implementation/src/` needs `Citation:` or `Assumption:` (or both) in
  its docstring — or `Code:` `CODE-NNN` for a value taken from `paper/code/`. A
  **presence+resolution** check exists
  (`neuromodels/framework/static_checks/check_citations.py`, run manually —
  `python -m neuromodels.framework.static_checks.check_citations`; no CI is
  wired): it asserts every `C-NNN`/`A-NNN`/`CODE-NNN` tag *resolves* to its
  ledger (`citations.yaml` / `assumptions.yaml` / `code_refs.yaml`),
  **not** that the tag is on the right function or that the cited passage
  supports the behavior. That *quality* check is a periodic human audit
  (STATUS.md, WORKFLOW.md §4 and §6). A fourth class, `Lineage:` `LINEAGE-NNN`
  (`lineage_refs.yaml`), tags a value **inherited from another paper in the
  genealogy**; its ledger entry names the ancestor `model:` and a `ref:` into
  that model's spec, and the check verifies the ancestor + ref resolve so the
  link is traceable. `neuromodels provenance --model-dir models/<m>` buckets
  calibrated values by source, surfaces the **code-alone** set (specified by the
  authors' code, absent from the paper), and **traces lineage values through to
  the ancestor's ultimate ground**.
- **NEVER turn a sanity check into an assertion.** The moment you write
  `assert`, it's a test. Move it to `tests/`.
- **NEVER burn iterations past the cap.** The stuck-detector isn't built;
  honor the documented iteration cap. In the autonomous program a STUCK
  model is **deferred to a later wave** (program plan §6), never pushed on
  indefinitely, and never a reason to halt the program.

## Quick reference: where things go

| What you want to do                            | Where to write                          |
|------------------------------------------------|-----------------------------------------|
| Acquired paper materials / SI / Online Methods | `paper/` (Phase-0; Phase-B forbidden)   |
| Acquired original author code                  | `paper/code/` — **gitignored** (Phase-A source; Phase-B forbidden) |
| Source provenance manifest (versioned)         | `paper/SOURCES.md`                      |
| Code-sourced value provenance                  | `article_aware/spec/code_refs.yaml` (`CODE-NNN`) |
| Value inherited from a genealogy ancestor       | `article_aware/spec/lineage_refs.yaml` (`LINEAGE-NNN`) |
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

- **Every agent commits its own output when done** — its changes, or (for a
  report-only role) its report — on the working branch, with a message that
  matches the diff. The process-auditor reads commit messages against diffs, so
  each pass leaves an atomic, honestly-described trail. Commit only inside the
  model repo, never the parent.
- Phase A: after spec+pseudocode complete, after data+figures complete,
  after `APPROVED` is written.
- Phase B: there is no runner — you make milestone commits when a component
  or a figure protocol's tests all pass (on the model's feature branch;
  commit only inside the model repo, never the parent).

For full commit cadence and escalation flows, see
[WORKFLOW.md](WORKFLOW.md).
