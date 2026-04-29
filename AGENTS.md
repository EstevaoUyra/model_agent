# AGENTS.md — entry point for agent sessions

This file is the thin operational entry point for agents working in this
repo. For full guidance, follow the pointers below.

## Identify your phase first

Your invocation context tells you which phase you're in. Read the
matching section of [WORKFLOW.md](WORKFLOW.md) before doing anything.

- **Phase A (article extraction):** you have access to a paper and need
  to produce the `article_aware/` artifacts. Read WORKFLOW.md §"Phase A".
- **Phase B (model implementation):** you have access to
  `article_aware/` but **NOT** to `paper/`. Read WORKFLOW.md §"Phase B".
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
  its docstring. The static check enforces presence.
- **NEVER turn a sanity check into an assertion.** The moment you write
  `assert`, it's a test. Move it to `tests/`.
- **NEVER bypass the STUCK gate.** If `STUCK` exists for a test, stop
  working on that test and surface the situation to the human.

## Quick reference: where things go

| What you want to do                            | Where to write                          |
|------------------------------------------------|-----------------------------------------|
| Phase A artifact (spec, pseudocode, etc.)      | `article_aware/`                        |
| Phase B model code                             | `implementation/src/`                   |
| Phase B test                                   | `implementation/tests/`                 |
| Phase B exploration script                     | `implementation/sanity_checks/`         |
| Escalate spec ambiguity (impl agent)           | `logs/spec_questions.md` (append-only)  |
| Record suspected paper error (human only)      | `logs/paper_issues.md`                  |

For the full directory layout and boundary rules, see
[REPO_STRUCTURE.md](REPO_STRUCTURE.md).

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
- Phase B: framework runner handles attempt commits; you make milestone
  commits when a component or figure protocol's tests all pass.

For full commit cadence and escalation flows, see
[WORKFLOW.md](WORKFLOW.md).
