# Skill: Update State

## Purpose

Refresh the model's README to reflect the current state of the reproduction
so that a returning human or a cold-start agent can pick up the work without
re-reading the entire history.

This is **not** a status snapshot — it's a planning artifact. The agent
gathers concrete data, reflects on what's working and what's broken, then
writes a README that names the next correction specifically enough to act on.

The skill writes only `models/<model>/README.md`. It does **not** mutate
`logs/test_runs.jsonl`, `logs/changelog.yaml`, or any other source.

---

## Trigger

Human-invoked. Typically at the end of a working session or at the start of a
new one. Not tied to commits or test runs.

---

## Inputs (sources the agent reads)

Read everything available. Sources marked **(may not exist yet)** are part of
the long-term design but not all are implemented — degrade gracefully.

1. **Test table** — `neuromodels test-table` from the model directory. Returns
   the markdown table the README embeds verbatim.

2. **Failing test details** — `logs/test_runs.jsonl`, filtered to the latest
   row per `test_id` with `status` != `pass`. Carries `failure_message` and
   `test_id` — the specifics that make "next correction" actionable.

3. **Spec questions** — `logs/spec_questions.md` (append-only). Open questions
   block whatever they touch; surface them in the reflection.

4. **Recent commits** — `git log --oneline -20` in the model repo. Names what
   has actually changed since the last update.

5. **Changelog** — `logs/changelog.yaml` **(may not exist yet)**. When present,
   the most recent 3–5 version entries (summary line only — `detailed_notes` is
   not loaded). When absent, the "Recent changes" section is omitted or
   replaced with the git log summary.

6. **VLM verdicts** — `logs/figure_comparisons/figure_N_*.json` **(may not
   exist yet)**. When present, the most recent verdict per figure populates the
   VLM column of the test table and feeds the reflection. When absent, the VLM
   column stays as `—`.

7. **Existing README** — if `README.md` already exists, read the **Model**
   section. Preserve it unless the scope has clearly changed (e.g., the model
   now reproduces figures the description doesn't mention).

---

## Output: README structure

```
# <Model name> Reproduction

## Model
<1-2 paragraphs: paper, scope, what's reproduced so far. ≤200 words.>

## Current state
<reflection: what's working, what's broken, what hypotheses are live, what's
been ruled out. Specific test_ids and figure numbers, not vague summaries.
≤300 words. REPLACED each invocation — not append-only.>

## Next correction
<single most important next fix. Concrete: file paths, the failing test_id,
the failure message, a brief hypothesis if obvious. ≤200 words.>

## Test status
<markdown table from `neuromodels test-table`, verbatim>

## Recent changes
<table of last 3-5 versions from changelog.yaml summaries, OR last 5-10
git commit subjects when no changelog exists>
```

Total target: ~1000 words including the test table.

---

## Process

### Step 1 — Compile (mechanical)

Run these from the model directory. Capture the outputs.

```bash
cd models/<model_name>

# Test status table
neuromodels test-table

# Failing test details (for "next correction")
python -c "import json; \
  rows=[json.loads(l) for l in open('logs/test_runs.jsonl')]; \
  latest={}; \
  [latest.update({r['test_id']: r}) for r in sorted(rows, key=lambda r: r['timestamp'])]; \
  [print(r['test_id'], '|', r.get('figure'), '|', r.get('failure_message')) \
   for r in latest.values() if r['status'] != 'pass']"

# Recent activity
git log --oneline -20

# Outstanding spec questions
cat logs/spec_questions.md 2>/dev/null || echo "(none)"
```

If `logs/changelog.yaml` exists, read it. If `logs/figure_comparisons/` exists,
list the most recent verdict per figure.

### Step 2 — Reflect (agent reasoning)

Synthesize a **specific** picture. The reflection section must answer:

- **What's working?** Which figures are fully green (tests + VLM)? Cite the
  test counts.
- **What's broken?** Name failing test_ids and the figure they belong to.
  Group by likely common cause.
- **What's blocked?** Spec questions, paper issues, STUCK signals.
- **What's been tried?** Walk through the last 5-10 commits — what was the
  goal, did the test counts change?
- **What hypotheses are live?** What's the agent's current best theory for
  remaining failures?
- **What's been ruled out?** From the changelog or commit messages — what was
  tried and didn't work?

Anti-patterns to avoid:
- "Most tests pass; some failures remain." — too vague to be useful.
- "Things look mostly working." — agentic hand-waving. Be specific.
- "Tried X, didn't work, will try Y next." — only if X and Y are real,
  named hypotheses with concrete code paths.

### Step 3 — Identify the next correction

Pick the **single** most pressing fix. Selection criteria, in order:

1. Failing **deterministic test** with a clear failure message that names a
   specific output mismatch
2. Failing **VLM verdict** with a specific visible discrepancy (e.g.,
   "Figure 1 S panel shows single band")
3. Open **spec question** that's blocking implementation work
4. A figure with a high % of failures (broad problem)

Skip:
- Failures whose root cause is already an open spec question (call them out
  in "Current state" but don't make them the next correction — the human
  needs to answer the question first)
- Cosmetic figure issues (missing axis labels, font size) when model-level
  failures exist

Format:
- **Test_id or figure** at the top
- **Symptom** — what fails, what the failure message says
- **Likely scope** — which implementation file(s) are involved
- **Hypothesis** — if obvious, a one-sentence theory. If not, say so.

### Step 4 — Write README

Open `README.md` in the model directory. Replace **Current state**, **Next
correction**, **Test status**, and **Recent changes** entirely. Preserve
**Model** unless its description is clearly stale.

Word counts: Model ≤200, Current state ≤300, Next correction ≤200. The skill
fails if any prose section exceeds its cap — keep the README scannable.

---

## Quality checks before declaring done

- [ ] Every claim in "Current state" cites a specific test_id, figure number,
      or commit hash. No vague "mostly working" language.
- [ ] "Next correction" names a specific test_id or figure and an actionable
      scope (file path or section).
- [ ] The test status table came from `neuromodels test-table` — not
      hand-edited.
- [ ] If a hypothesis is named, it's specific enough that an agent could try
      to falsify it.
- [ ] Length caps respected: Model ≤200, Current state ≤300, Next
      correction ≤200 words.

---

## When to flag stale data

If any source is suspiciously old, note it in the reflection rather than
silently using it:

- `logs/test_runs.jsonl` mtime > 7 days → "test run is N days old; results
  may be stale"
- `logs/changelog.yaml` last version > 14 days old → "no version recorded
  since <date>"
- Failing test where the latest row's `commit_hash` doesn't match current
  HEAD → "this failure is from before the most recent commits"

---

## What this skill does NOT do

- **Run tests.** Use `skills/run-tests/SKILL.md` to refresh
  `logs/test_runs.jsonl` first if the data is stale.
- **Run figure comparisons.** Use `skills/compare-figure/SKILL.md`. The
  verdict files (once they have a persistent home) feed back into update-state.
- **Add changelog entries.** That's a separate operation — the human or
  another skill records a new version when a meaningful state change is
  worth checkpointing.
- **Mutate logs.** All log files are read-only inputs.
