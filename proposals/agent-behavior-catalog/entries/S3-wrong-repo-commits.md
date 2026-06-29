# S3 — Workflow agents commit in the wrong repository

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · process/delivery (with an agent-behavior root: acting on an implicit cwd) |
> | Behavior | writes/commits outputs to the parent repo instead of the model submodule it is working on |
> | Symptom | per-model artifacts (digitization audits) + a finalize step land in `model_agent/`, not `models/<m>/` |
> | Agent role | workflow agents (figure-audit lane) + the finalize step |
> | Trigger | agent runs with cwd = parent root, but the skill uses *model-relative* paths and says "commit your output" |
> | Cause (evidence) | path/cwd mismatch: relative skill paths resolve against the parent unless the agent is pinned to the model — *intervention-tracked (the fix is exactly "pin cwd")* |
> | Detector | human (noticed mis-placed commits, 2026-06-04) |
> | Lever(s) | structural (`SK()` pins cwd) + gate-ish (`.gitignore` blocks stray writes) + doc (AGENTS.md rule) — held |
> | Flags | ⟳ ("got this wrong twice") |
> | Status | solved (PR #28) |

## The behaviour

A reproduction run operates on exactly one model = one submodule (`models/<m>/`). The rule
(AGENTS.md) is: every workflow agent reads, writes, and **commits inside that submodule, never in
the parent `model_agent` repo**. The recurring failure was the opposite: agents committed their
outputs into the parent.

The mechanism is mundane and structural, which is why it's worth cataloguing rather than blaming an
agent's "judgment": workflow agents are launched with **cwd = the parent root**, but the skills they
run use **model-relative paths** (`logs/`, `article_aware/`, `implementation/`, `figure_outputs/`)
and instruct "commit your output." An agent that doesn't first `cd` into the model therefore
resolves those relative paths against `model_agent/` and commits there. Two concrete escapes:
- the figure-audit lane dumped **every digitization report** into
  `model_agent/logs/digitization_audit/` instead of the submodule;
- a finalize step **bumped the parent submodule pointer and opened `model_agent` PRs** — i.e.
  committed on the parent, exactly forbidden.

The distilled note records this happened **twice** before the fix landed ("I got this wrong twice,
2026-06-04") — so it's a recurrence within the same day, not a one-shot.

## Why it happened (graded)

- **Intervention-tracked / structural (strong):** the cause is a path-resolution mismatch (implicit
  cwd ≠ the model the agent is supposed to act on), and the fix targets exactly that — `full-pass.js`
  `SK()` now **pins every skill-based agent to its model repo** (cd in; all paths relative to it;
  commit inside, never the parent). That the targeted structural fix resolves it is strong evidence
  the cause is structural, not an agent reasoning error.
- **No mentalism:** the agent didn't "decide" to pollute the parent; it executed "commit your
  output" against whatever cwd it inherited. The behaviour is *acting on an implicit/ambient
  state* — the coordination-domain cousin of T3 (acting on a stale tool-model).

## How it responded to intervention (the fix held)

Three layered levers, landed together in PR #28 (`78b5795`, merge `34da1f5`) plus the finalize
change (`c2acb0d`):
- **Structural (the load-bearing one):** `SK()` pins each agent to its model submodule.
- **Finalize re-homed:** the finalize step lands results in the **model's own repo** — a PR onto the
  *submodule's* main (`gh pr create` + `gh pr merge` in the submodule) — and never touches
  `model_agent`. Parent submodule-pointer bumps are a separate, deliberate step, not part of a run.
- **Defense-in-depth (gate-ish):** the parent `.gitignore` ignores per-model artifact paths
  (`logs/{digitization_audit,faithfulness_audit,figure_comparisons,spec_audit}`, `test_runs.jsonl`)
  so a stray write *can't* pollute the parent even if an agent slips; corpus-level
  `logs/process_audit/` stays tracked. Nine already-misplaced audits were removed in the same PR.

This is a **solved** thread: a structural cause met a structural fix plus a backstop. The remaining
"how to apply" nuance (which the distilled note preserves) is that the submodule's *own* main was
going stale on feature branches — model results must land on the submodule's main, while
process/skill/workflow-definition changes are genuine parent artifacts and go on `model_agent` via
PR. That distinction (results→submodule, process→parent) is the durable rule.

## Confidence & threats-to-validity

**High on the mechanism and the fix; low on rate.** Threats:
- **Detector is human** — noticed via misplaced commits, so we see the incidents the lead caught.
- **"Twice" is a counted-low anecdote** (the distilled note), not a corpus rate of wrong-repo
  commits. `[to-verify-on-deeper-dig]`: count parent vs submodule commit targets across full-pass
  runs before/after `78b5795`.
- **No corpus quotes** — the behaviour is a commit *target* (a git side-effect), not something the
  workflow narration verbalizes cleanly; verified instead by the git history of the fix and the
  removed misplaced files in PR #28.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-04 | Finalize lands results in the model's OWN repo (submodule), not parent | `c2acb0d` (PR #27) |
| 2026-06-04 | Root-cause fix: agents pinned to submodule via `SK()`; `.gitignore` backstop; 9 misplaced audits removed | `78b5795` / merge `34da1f5` (PR #28) |

## Links
- `connects-to S4` — both are git-discipline failures on a *shared* working tree (wrong repo here;
  wrong base branch there); both fixed by making the target explicit rather than inherited.
- `connects-to T3` — same root shape as "acts on a stale tool-model": executing against ambient
  state (inherited cwd) instead of the intended target.

## Deeper-dig hook
`git log` in `model_agent` for per-model artifact paths committed to the *parent* before `78b5795`
(they were removed in that commit — see its `--stat`); and diff `full-pass.js` around `SK()` to
confirm the cwd-pin is still present. Behaviour is git-grounded, not in the narration corpus.

## Status
**Solved (PR #28).** Structural pin + finalize re-home + `.gitignore` backstop; held since.
`Refs:` memory `workflows-commit-in-submodule-not-parent`; PR #28 (`78b5795`), PR #27 (`c2acb0d`);
AGENTS.md "commit only inside the model repo, never the parent."

## Evidence layer
**Git/memory-grounded, now plus orchestrator-session narration.** Primary evidence: PR #28 commit
`78b5795` (the `SK()` pin, the `.gitignore` additions, and the deletion of 9 mis-placed per-model audits
visible in its `--stat`), plus the distilled memory. The orch harvest (2026-06-29) adds the **founding
orchestrator-level instance** verbatim: the orchestrator *designed* finalize to commit on the parent
(*"I designed finalize to commit on the parent, which violated the existing [rule]"*, *"by bumping the
parent + opening model_agent PRs"*) and the human caught it (*"the workflows should be commiting in their
own submodule, not on model_agent"*) — "you caught it twice." A live agent parent-write was also surfaced
rather than folded in (*"That violates 'agents commit only in their submodule, never the parent.'"*) and a
pre-#5 *"accidental parent write self-reverted with no contamination."* Quotes id `S3` across
`../evidence/orch-B.quotes.jsonl` + `orch-C.quotes.jsonl` (6 quotes), verified verbatim; see
`../evidence/orch-harvest-map.md`.
