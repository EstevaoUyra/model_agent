# T3 — Acts on a stale/incorrect model of the tooling

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Tool/env · **agent-behavior (tool-adjacent)** |
> | Behavior | invokes/configures a tool on an out-of-date or wrong world-model of how it resolves (which script version runs, what an arg form means, what a knob actually controls) — then proceeds without verifying |
> | Symptom | the run "succeeds," but a stale script version ran / an arg was silently mis-handled / a setting was a no-op — surfaced only as a downstream false-block or a missing artifact |
> | Agent role | orchestrator / tooling-operator (the session driving the workflow tool) |
> | Trigger | the tool's behaviour diverges from the operator's mental model: name-invocation caches the session-start snapshot; `args` arrive JSON-encoded; `model` arg form is load-bearing; `model:` only sets tier, not the context window |
> | Cause (evidence) | tool semantics undocumented/non-obvious + no post-invocation verification — *intervention-tracked* for the arg/snapshot/canonicalization fixes; *agent-/operator-stated* for the 1M-window misconception |
> | Detector | human + agent (silent breakage caught downstream; resilient runs masked it) |
> | Lever(s) | code/tooling (scriptPath invocation, arg-guard, MODEL canonicalization) held; per-agent model-ID override **failed** (no-op) |
> | Flags | ✗ failed lever (explicit full model-IDs) · connects-to E5 (self-certification), T1 |
> | Status | solved (fixes landed); the window-split lever is "won't-fix at per-agent level" |

## The behaviour (and why it IS a behaviour, unlike T2)

Unlike its sibling T2 (a blameless substrate condition), T3 is a genuine **tool-adjacent agent
behaviour**: the operator *acts on an incorrect world-model of the tooling* and then ships the
action without checking the tool did what was intended. The substrate was fine; the move — invoke /
configure on an assumption, don't verify the result — is the defect. That places its **decision
root in the same family as E5 (self-certification — "it ran, so it worked")** and T1 (acts with
confidence, no validation): here the missing check is "did the tool actually run the version / parse
the arg / apply the setting I think it did?"

## The incidents (each is the same shape: assume tool semantics, don't verify)

All from running the dynamic `full-pass` workflow:

1. **Stale snapshot via name-invocation.** A named workflow (`.claude/workflows/*.js`) is registered
   at *session start*; later edits to that file are **ignored** when invoked by `name:` — the
   pre-edit script runs. The operator's model ("I edited the file, so my edits run") was wrong.
   *Fix:* invoke via `scriptPath: '<abs path>'` so the live file is read; the per-run generated copy
   under the session dir confirms which version ran.

2. **`args` arrive as a JSON-encoded string.** Despite passing an object in the tool call, `args`
   could arrive as a JSON *string*, so `args.figures` was `undefined` → "pipeline() expects an
   array." *Fix (in-script):* `const A = typeof args === 'string' ? JSON.parse(args) : (args||{})`.

3. **`model` arg form is load-bearing — and broke things silently.** Passing a bare
   `fitzhugh_1961` (2026-06-15 run) instead of `models/fitzhugh_1961` **silently broke two things
   while the run otherwise SUCCEEDED** (resilient agents still built in the real `models/<name>`):
   the coverage gate ran `check_figure_coverage.py <name>`, looked under `<name>/article_aware/`,
   found nothing, and emitted a **false** `model:figure-coverage` block; and `repro_cost.py`
   (which attributes a run by grepping prompts for `models/<name>`) found no match, so the finisher
   **omitted the README cost section**. The success of the run masked the breakage — classic E5.
   *Fix:* `MODEL` is canonicalized so bare `<name>` and `models/<name>` both work, and repro_cost
   attribution now searches the whole transcript (recovers past bad-arg runs). Landed in PR #60
   (`3c0c336`).

4. **`model:` sets only the tier, not the window — the explicit-ID lever was a no-op.** The operator
   set explicit full IDs (`OPUS = 'claude-opus-4-8'` for nine roles, `IMPL =
   'claude-opus-4-8[1m]'` for the implementer) intending to split the 1M context window across
   agents. The IDs were accepted (no error) but the user verified via /workflows that **all** agents
   still ran on opus-1M: workflow agents **inherit the session's context-window variant**, and
   `model:` controls only the opus/sonnet/haiku tier. The only real lever is the **session model at
   session start**. This is the **failed intervention** (✗): a configuration applied on a wrong
   model of the knob, accepted silently, with no effect on the intended axis.

## Cross-cutting confound the operator also had to learn

Workflow agents always invoke the **parent's** `${ROOT}/tools/*.py` (ROOT =
`/Users/estevaouyra/dev/model_agent`), not the scriptPath worktree's copies — so tool fixes on a
branch don't reach the live path until that branch merges to main. This compounds incidents 1–3:
"I fixed the tool" can be true on a branch and false in the running pipeline simultaneously. (Same
parent-vs-submodule root as thread S3.)

## Smoking gun

PR #60 (`3c0c336`, "Full-pass routing hardening + model-arg/repro_cost fixes") — its
"Canonicalize MODEL arg + harden repro_cost attribution" change is the artifact for incident 3, the
most legible case (a successful run that silently emitted a false coverage block and dropped a
README section).

## Interventions — which held, which failed

- **Held (code/tooling):** `scriptPath` invocation (1); in-script `args` JSON guard (2); `MODEL`
  canonicalization + whole-transcript repro_cost attribution (3) — all in `full-pass.js` / PR #60.
- **Failed (✗):** per-agent explicit model-IDs to split the 1M window (4) — a no-op; the window is
  session-inherited. Accepted as "all-1M for now"; the documented lever is to set a non-1M *session*
  model next time.

## Recurrence

Incidents 1–2 surfaced together on 2026-06-03; incident 3 on 2026-06-15; incident 4 confirmed
2026-06-03. These are **distinct manifestations of one behaviour** (act on assumed tool semantics,
don't verify), not one defect recurring — so "recurred" is true at the *behaviour* level (≥3
separate manifestations) but each individual bug was one-shot-then-fixed. No rate claimed: this is a
count of named incidents, not a frequency over a denominator.

## Confidence & threats-to-validity

**High** for incidents 1–3 (intervention-tracked: each fix names and removes the exact mismatch; the
arg-form failure mode is reproducible by construction). **Medium** for incident 4 — the conclusion
("IDs accepted but no-op on the window") rests on the user's live /workflows observation plus
transcript model-IDs, an operator-stated read, not an isolated A/B. Broader threat: all evidence is
memory- and git-grounded; there is **no harness-verifiable corpus quote** for T3, because these are
orchestrator/tooling-session decisions, not workflow-subagent narration — so no `T3.quotes.jsonl`
was produced (per the rule: never manufacture quotes).

## Generality

Medium. The surface details (scriptPath caching, `models/<name>` form, opus-1M window) are
setup-specific. The underlying behaviour — **an agent configures or invokes a tool on a stale or
incorrect model of its semantics and proceeds because the call didn't error / the run succeeded** —
is a general and transferable autonomous-agent hazard, and is the tool-facing face of E5
self-certification.

## Links

- `connects-to E5` (self-certification) — **decision root**: the missing move is post-invocation
  verification; "it ran, so it worked" let silent breakage through (esp. incident 3).
- `connects-to T1` — both: act with confidence, no validation, on the shared pipeline.
- `connects-to T2` — domain-5 sibling; T3 is the *agent-behaviour* pole, T2 the *substrate* pole.
- `shared-root with S3` — parent-vs-submodule / which-copy-runs confusion (agents run the parent's
  tools; branch fixes don't reach the live path until merged).

## Deeper-dig hook

For incident 3's blast radius: grep the manifest + transcripts for runs whose `model` prompt arg was
bare `<name>` (no `models/`) before PR #60 and check which emitted a `model:figure-coverage` block
or a README with no cost section — converts "one known 2026-06-15 run" into an incident count. Data:
`evidence/corpus-snapshot/`, `evidence/manifest.jsonl`; tooling history in `git log` around
`3c0c336` / branch `scidekick-full-pass-hardening`.

## Status

**Solved** for incidents 1–3 (canonicalization + guards landed). Incident 4 is **won't-fix at the
per-agent level** — the only working lever is the session model at session start.

## Refs

memory: `workflow-tool-invocation-gotchas`, `workflow-agent-model-full-ids`,
`workflows-commit-in-submodule-not-parent` · commits `3c0c336` (PR #60); branch
`scidekick-full-pass-hardening` (`322ecd3`/`45ff67c`) · files `.claude/workflows/full-pass.js`,
`tools/check_figure_coverage.py`, `tools/repro_cost.py` · no quote ledger (no harness-verifiable
corpus narration; evidence is memory + git).
