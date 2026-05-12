# Skill: Run Tests

## Purpose

Run figure-level and internal tests during Phase B iteration, capturing each
invocation in `logs/test_runs.jsonl` for later reflection by the
`update-state` skill.

---

## Where tests live

- **`article_aware/extracted_data/test_figure_*.py`** — paper-derived claim
  tests, one file per figure or per panel (e.g., `test_figure_3C.py`,
  `test_figure_3F.py`). Each test calls a `run_<protocol>()` function and
  asserts against named outputs. **Source of truth for paper claims; do not
  duplicate these under `implementation/tests/`.**

- **`implementation/tests/`** — hand-written tests for building blocks that
  have no direct paper-claim analog (kernel normalization, helper behavior).

---

## Always `cd` into the model directory first

The neuromodels test-log plugin writes to `<rootdir>/logs/test_runs.jsonl`,
where rootdir is set by pytest's nearest `pytest.ini`. Each model has its own
`pytest.ini` that scopes rootdir to the model directory. **If you run pytest
from the parent (`pytest models/<name>/...`), rootdir walks up to the
framework's `pytest.ini` and the log lands at the framework level instead of
per-model.**

Every command below assumes you've `cd`'d into `models/<model_name>/`.

---

## Command cookbook

### Run all tests for one figure (all panels)

```bash
pytest article_aware/extracted_data/test_figure_<N>*.py
```

Filename glob is the figure filter. Examples:
- `test_figure_1*.py` → just `test_figure_1.py`
- `test_figure_2*.py` → both `test_figure_2A.py` and `test_figure_2B.py`
- `test_figure_3*.py` → both `test_figure_3C.py` and `test_figure_3F.py`

Pytest's `-m` flag matches by marker *name* only, not argument value, so
`pytest -m "figure(1)"` does not work. Filename glob is the way.

### Run one panel only

```bash
pytest article_aware/extracted_data/test_figure_4C.py
```

### Run one specific test

```bash
pytest article_aware/extracted_data/test_figure_4C.py::test_some_name
```

### Run all figures

```bash
pytest article_aware/extracted_data/
```

### Run implementation-only tests

```bash
pytest implementation/tests/
```

### Run everything (both layers)

```bash
pytest
```

(With the model's `pytest.ini` setting `testpaths`, this picks up both.)

---

## The log

Every pytest invocation appends one row per test to
`logs/test_runs.jsonl`. Each row carries: `run_id`, `session_id`,
`timestamp`, `test_id`, `figure`, `status` (pass/fail/skipped/error),
`commit_hash` (model repo HEAD), `spec_commit_hash` (tree hash of
`article_aware/` at HEAD), `failure_message` (last line of pytest's
longrepr), and `agent_rationale` (null for now).

### When to skip logging

For exploratory runs you don't want polluting the history (e.g., poking at
a single test while debugging, or quickly verifying an idea before
committing):

```bash
pytest article_aware/extracted_data/test_figure_3C.py --neuromodels-log-path disabled
```

### Inspecting the log

```bash
tail -n 20 logs/test_runs.jsonl | python -m json.tool
```

Or aggregate by figure:

```bash
python -c "import json; from collections import Counter; \
  rows=[json.loads(l) for l in open('logs/test_runs.jsonl')]; \
  print(Counter((r['figure'], r['status']) for r in rows))"
```

---

## Useful pytest flags

- **`-v`** — verbose: show each test name and pass/fail status
- **`-x`** — stop at first failure (saves time during iteration)
- **`-q --tb=line`** — compact output with one-line tracebacks (good when
  many tests fail and you want to see all the failure messages at once)
- **`-k <expr>`** — keyword filter on test names (e.g., `-k attended` runs
  every test whose name contains "attended")
- **`--lf`** — only re-run tests that failed last time
- **`-s`** — don't capture stdout (useful when a test prints diagnostics)

---

## Iteration recipe

During debugging, run the **narrowest relevant test** first:

1. Single failing test (`pytest path::test_name`) → fast feedback loop
2. Once it passes, run the file (`pytest path/test_figure_NX.py`)
3. Once the file passes, run the figure (`pytest path/test_figure_N*.py`)
4. Once the figure passes, run the full article-aware suite
5. Before declaring a milestone, run everything (`pytest`)

This mirrors the principle in WORKFLOW Step 5: expand the test scope only
after the narrow one passes.

---

## After tests pass

Once all article-aware tests pass and the implementation generates the
figure PNG, run the visual reproducibility check — see
[`skills/compare-figure/SKILL.md`](../compare-figure/SKILL.md).

---

## Common gotchas

- **Running pytest from the parent directory.** Logs land at the framework
  level (`/Users/.../model_agent/logs/test_runs.jsonl`), test_ids get a
  long `models/<name>/...` prefix, and the spec_commit_hash is wrong (it
  reads the framework repo's HEAD, not the model's). Always `cd` into the
  model first.

- **Log grows quickly.** Every test run appends, so a CI loop or many
  iterations produce many rows. The `update-state` skill queries "latest
  row per `test_id`" to get current state — older rows aren't pruned, they
  document attempt history.

- **`figure: null` in rows.** Means the test isn't tagged with
  `@deterministic_test(figure=N)` (or `@pytest.mark.figure(N)` directly).
  Add the marker so the test is countable in the per-figure aggregation.

- **Editing `article_aware/` to make a test pass.** Don't. The article-aware
  test is the contract; if it's wrong, append to `logs/spec_questions.md`
  per the WORKFLOW escalation channels — don't silently rewrite the contract
  from Phase B.
