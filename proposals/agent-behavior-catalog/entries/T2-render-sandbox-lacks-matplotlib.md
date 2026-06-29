# T2 — Render sandbox lacked matplotlib (substrate, not a bias)

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Tool/env · **environment/substrate** |
> | Behavior | not an agent bias — an environmental precondition that shaped agent behaviour |
> | Symptom | figure render + render-dependent tests fail with `ModuleNotFoundError: No module named 'matplotlib'`; figure passes block on stale renders |
> | Agent role | builder / render; audit-digitization (any role that renders or re-renders) |
> | Trigger | agent runs bare `python`/`pytest` → resolves to the system Homebrew interpreter, which lacks matplotlib (it lived only in the project `.venv`, and only as an optional `[sanity]` extra) |
> | Cause (evidence) | interpreter-resolution + dependency-packaging defect — *intervention-tracked* (the fix names and removes exactly this) |
> | Detector | human (caught the repeated render block); agent narration also shows agents self-navigating the substrate |
> | Lever(s) | structural/config (pin agents to `.venv`) + packaging (matplotlib → core dep) — both held |
> | Flags | ⟳ observed twice (R&H; a count of 2, not a rate) |
> | Status | solved (2026-06-10) |

## Why this is in the map but is NOT an agent behaviour

This thread is kept for **comprehensiveness** (Stage-1 is a map), but it is explicitly tagged
`Kind: environment/substrate`: **the agent did nothing wrong.** The figure-rendering step failed
because the interpreter the agents reached for did not have `matplotlib` installed — a property of
the *environment*, not of any judgement, evaluation, or escalation the agent made. It belongs in
domain 5's *substrate-conditions* appendix, the counterpart to the *tool-adjacent agent behaviours*
(e.g. T3). Reading it as a "bias" would be a category error. Its value here is twofold: (1) it is a
clean substrate confound to rule out when interpreting other threads — several render/test failures
in the corpus are this, not an agent defect — and (2) the agents' response to it is mildly
informative (see below).

## Symptom

`full-pass` agents executed `python …` / `pytest` without an absolute interpreter path. On the
machine, bare `python`/`pytest` resolved to the **system Homebrew** interpreter
(`/usr/local/bin`, PEP-668 externally-managed), which had no matplotlib. The complete environment
was the project `.venv` (`/Users/estevaouyra/dev/model_agent/.venv`, py3.10.9), but nothing pointed
agents at it, and matplotlib was packaged only as an optional `[sanity]` extra — so even fresh
installs could come up without it. Result: figure rendering and render-dependent tests
(`test_panel_axes.py`) failed with `ModuleNotFoundError`, and figure passes **blocked on stale
renders**.

## What the agents actually did (the mildly-informative part)

Even before the systematic fix, at least one agent **navigated around the substrate on its own**.
On 2026-06-06 (four days before the fix), an `audit-digitization` agent working on
`pestilli_ling_carrasco_2009` narrated that its expected tooling wasn't present in the running
interpreter and then located and switched to the `.venv`:

> *"The framework module isn't installed. I'll do the overlay/crop work directly with PIL/matplotlib"*

> *"The root `.venv` has matplotlib and the framework. Let me use it."*

So the substrate condition shaped behaviour two ways: it cost some agents a blocked render, and it
prompted others to spend turns discovering the correct interpreter. Neither is a bias; both are
downstream of an environment that didn't guide the interpreter choice. (These two quotes are the
harness-verifiable signal. The raw `No module named 'matplotlib'` string also appears in tool-result
output across ~10 workflow transcripts, but those are tool outputs, not agent narration, so the
quote harness — which reads narration only — cannot certify them; treated as corroborating, not
promoted.)

## Recurrence — a count, not a rate

The render block was observed **twice for reynolds_heeger_2009 (R&H)** per the decision record.
That is a count of 2 incidents on one model, **not** a frequency over a denominator — we did not
enumerate every render across the corpus, so no rate is claimed.
[to-verify-on-deeper-dig: count render-step failures attributable to a non-`.venv` interpreter
across all `digitize`/render agents in the manifest.]

## Smoking gun

Commit `5711a19` ("Fix figure rendering: matplotlib core dep + pin agents to the .venv"), whose own
message states the root cause and notes "R&H hit this twice." Merged via PR #33 (`d6a59b2`).

## Interventions that held

Both landed together (2026-06-10) — a bundled fix, not isolated tests:
- **Packaging:** `pyproject.toml` moved matplotlib from the `[sanity]` extra to **core
  `dependencies`** (rendering is a core deliverable). (seaborn stayed in `[sanity]` — not in the
  render path.)
- **Config/structural:** `.claude/workflows/full-pass.js` defines `PY = ${ROOT}/.venv/bin/python`
  and `SK()` directs every agent to use `PY` for all Python (tests and `-m <pkg>.views` rendering);
  `skills/run-tests/SKILL.md` + `AGENTS.md` updated to use the `.venv` interpreter.
- Verified at fix time: the `.venv` ran the previously-failing panel-axes tests (18 passed).

Diagnostic for any recurrence: if a render/test fails with no-matplotlib again, the interpreter in
use is **not** the `.venv` (someone ran bare `pytest`/`python`).

## Confidence & threats-to-validity

**High** on the mechanism and the fix — the cause is intervention-tracked (the fix removes exactly
the named defect, with a verification at fix time). Threats: the "twice" is a small-n anecdote on a
single model, not a measured rate; and the two verified narration quotes come from **one** agent on
**one** date, so they evidence "the substrate shaped behaviour ≥ once," not its prevalence.

## Generality

Low as an "agent" finding (it's substrate). But the *shape* — "an autonomous agent's default
interpreter/toolchain differs from the one its task needs, with nothing steering the choice" — is a
common, transferable hazard for agent harnesses, and a confound any log-mining of agent "failures"
must subtract out before attributing a defect to the agent.

## Links

- `connects-to T3` — both are domain-5 (Tool/env). T2 is the *substrate-condition* pole (agent
  blameless); T3 is the *tool-adjacent behaviour* pole (agent acts on a wrong model of the tooling).
  Together they are the two halves of domain 5's split.
- `connects-to E1b`/`E3` — the fix's own note reiterates "audit the shipping image after rendering"
  (`vlm-eye-is-arbiter-over-tools`, `rendered-output-panels-are-reproduction-targets`); a render
  that silently didn't run is exactly what those threads warn about consuming as if valid.

## Deeper-dig hook

Slice the manifest for `digitize-figure` + render-touching roles before 2026-06-10 and grep their
tool-result blocks (not narration) for `No module named 'matplotlib'` to convert the "twice" into a
real incident count and a per-model spread. Data: `evidence/corpus-snapshot/`, spine
`evidence/manifest.jsonl`.

## Status

**Solved** (2026-06-10).

## Refs

memory: `workflow-sandbox-lacks-matplotlib` · commits `5711a19`, PR #33 (`d6a59b2`) · files
`pyproject.toml`, `.claude/workflows/full-pass.js`, `skills/run-tests/SKILL.md`, `AGENTS.md` ·
quotes: `evidence/T2.quotes.jsonl` (2/2 verified verbatim, `verify_quotes.py T2`, exit 0).
