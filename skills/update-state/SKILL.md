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

   **If no README exists**, write the Model section from scratch by reading:
   - `article_aware/spec/citations.yaml` — for the paper title, authors,
     journal/year, and core equation citations
   - `article_aware/spec/model_spec.yaml` — for the pipeline structure and
     which simulation protocols exist
   - `article_aware/figures/figure_*.md` — for the scope (which figures
     are in the reproduction)

   Ground every claim in a citation ID (`C-NNN`) or a structural fact
   (e.g., "pipeline has 4 steps", "7 figures in scope"). Do not invent
   descriptive language the spec doesn't support.

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

## README generation
<List of custom Python (or other ad-hoc commands) the agent ran to answer
questions the existing scripts don't cover. APPEND-ONLY across invocations.
Each entry: date, one-line summary of what was queried, the actual code,
and why it was needed. Patterns that recur should be turned into new
scripts in `skills/update-state/scripts/`.>
```

Total target: ~1000 words including the test table.

---

## Helper scripts

Anything more than a one-line shell command lives in `scripts/` next to this
SKILL.md. The skill itself stays single-line invocations; the logic lives in
the script. Adopt this convention if you extend the skill with new helpers.

Current scripts:

- `scripts/failing_tests.py` — read `logs/test_runs.jsonl`, dedupe to the
  latest row per test_id, and print rows whose status is not `pass`. Output
  format: `<status>: <test_id> | figure=<N> | <failure_message>`.

- `scripts/log_freshness.py` — for each figure (including the "Unassigned"
  bucket for rows with `figure=None`), print row count, distinct test_id
  count, latest `commit_hash`, and latest timestamp. This is the diagnostic
  for distinguishing *stale-metadata* (commit older than HEAD but test
  surface still matches) from *stale-data* (test surface has changed).
  Pass `--verbose` to also list the distinct test_ids.

### When you need a query no script covers

If you find yourself needing custom Python to answer a question the existing
scripts don't, that's fine — run it. But **log it in the README's "README
generation" section** (see Output structure below). Over time those entries
identify patterns worth turning into new scripts. Don't silently run ad-hoc
queries and discard them — they're the most useful signal for what the
helper set is missing.

---

## Process

### Step 1 — Compile (mechanical)

Run these from the model directory. Capture the outputs.

```bash
cd models/<model_name>

# Test status table
neuromodels test-table

# Failing test details (for "next correction")
python <repo-root>/skills/update-state/scripts/failing_tests.py

# Per-figure log freshness (for stale-metadata vs stale-data diagnosis)
python <repo-root>/skills/update-state/scripts/log_freshness.py

# Recent activity
git log --oneline -20

# Outstanding spec questions
cat logs/spec_questions.md 2>/dev/null || echo "(none)"
```

If `logs/changelog.yaml` exists, read it. If `logs/figure_comparisons/` exists,
list the most recent verdict per figure.

### Step 2 — Reflect (agent reasoning)

Synthesize a **specific** picture. The reflection section must answer:

- **What's working?** Which figures are **fully green** — deterministic tests
  pass AND a recent VLM verdict says pass? Cite the counts.
- **What's broken?** Name failing test_ids and the figure they belong to.
  Group by likely common cause. A figure with passing tests but a failing VLM
  verdict counts as broken — not green.
- **What's unknown?** Figures where deterministic tests pass but no VLM
  verdict exists (or the verdict is stale relative to current `commit_hash`)
  are **not green** — they are *uncovered*. The reproduction is not
  validated visually. Name these figures explicitly.
- **What's blocked?** Spec questions, paper issues, STUCK signals.
  - **Hard blockers**: a spec question is open and unresolved AND a test
    failure or VLM mismatch depends on the answer. Test color cannot be
    trusted until a human adjudicates.
  - **Soft blockers (propping-up factors)**: a spec question has a
    `chosen_assumption` resolution AND tests pass under that assumption
    but the resolution wasn't human-audited. The reproduction is held up
    by unaudited calibration. Tests are green but the green is provisional.
    Name these explicitly in "Current state" with the SQ-NNN id and the
    figures affected; do **not** treat them as the next correction (the
    next correction is for a human, not the agent).
- **What's been tried?** Walk through the last 5-10 commits — what was the
  goal, did the test counts change?
- **What hypotheses are live?** What's the agent's current best theory for
  remaining failures?
- **What's been ruled out?** From the changelog or commit messages — what was
  tried and didn't work?

The three states per figure:

| State | Deterministic | VLM | Reflection treatment |
|---|---|---|---|
| Green | all pass | pass (recent) | "complete" |
| Red | any fail OR VLM fail | — | "broken" — concrete failure mode |
| Unknown | all pass | not run / stale | "uncovered" — surface as work-to-do |

Do not call a figure "done" without a recent VLM-pass verdict. "Recent" means
the verdict's recorded model `commit_hash` matches current HEAD (or is at
least newer than the most recent change to figure-relevant code).

Anti-patterns to avoid:
- "Most tests pass; some failures remain." — too vague to be useful.
- "Things look mostly working." — agentic hand-waving. Be specific.
- "All green!" when most figures lack a VLM verdict — that's mostly *unknown*,
  not *green*.
- "Tried X, didn't work, will try Y next." — only if X and Y are real,
  named hypotheses with concrete code paths.

### Step 3 — Identify the next correction

Pick the **single most pressing action**. Usually that's a single fix at a
single test/figure, but it can be a *batch action* (e.g., "run VLM comparison
across figures 1–7") when the bottleneck is missing coverage rather than a
specific identified bug.

Selection criteria, in order:

1. Failing **deterministic test** with a clear failure message that names a
   specific output mismatch — single test, single figure
2. Failing **VLM verdict** with a specific visible discrepancy (e.g.,
   "Figure 1 S panel shows single band") — single figure
3. **Unknown figures (batch action OK).** When deterministic tests pass and
   no VLM verdicts exist, the next action is "run VLM comparison for figures
   X, Y, Z." If many figures are uncovered, this is a legitimate *batch*
   correction — name all affected figures, but still pick one to start with
   (the highest-information one) so the work has a head. A 100%-pass test
   table with no VLM coverage is **not** "we're done"; it is "we don't know
   yet."
4. Open **spec question** that's blocking implementation work
5. A figure with a high % of failures (broad problem)

Skip:
- Failures whose root cause is already an open spec question (call them out
  in "Current state" but don't make them the next correction — the human
  needs to answer the question first)
- Cosmetic figure issues (missing axis labels, font size) when model-level
  failures exist

Format:
- **Target** — single test_id, single figure, OR a batch like "figures 1–7"
- **Action** — what to do (fix code, run VLM, answer spec question)
- **Symptom** — what fails, what the failure message says (omit for batch
  coverage actions where the symptom is "no signal yet")
- **Starting point** — for batch actions, which item to do first and why
- **Likely scope** — which implementation file(s) are involved
- **Hypothesis** — if obvious, a one-sentence falsifiable theory. If not,
  say so.

### Step 4 — Write README

Open `README.md` in the model directory. Replace **Current state**, **Next
correction**, **Test status**, and **Recent changes** entirely. Preserve
**Model** unless its description is clearly stale.

**Append (do not replace) the README generation section.** If a previous run
left entries there, keep them and add new ones below. Format each entry:

```
- <YYYY-MM-DD>: <one-line summary of what you needed to know>.
  Code:
  ```
  <the actual command or python snippet>
  ```
  Why: <one-line reason this wasn't in the existing scripts>.
```

If you didn't need any custom queries this run, write a single line:
`- <YYYY-MM-DD>: no custom queries needed.`

Word counts: Model ≤200, Current state ≤300, Next correction ≤200. The skill
fails if any prose section exceeds its cap — keep the README scannable. The
"README generation" section has no cap (it's evidence-tracking, not reading
material).

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
- [ ] **README generation** section is up to date. Either contains a
      "no custom queries needed" line for this date, or lists every
      custom Python/shell snippet run, with code and reason. Previous
      entries are preserved (append-only).

---

## When to flag stale data

Stale-data signals are **soft**, not binary. Report what you see, don't
collapse to "stale / not stale" — let the reader judge how much weight
each signal deserves.

Things to check and how to report them:

- **`logs/test_runs.jsonl` mtime** > 7 days → "test run is N days old;
  results may be stale"
- **`logs/changelog.yaml` last version** > 14 days old → "no version
  recorded since <date>"
- **Latest row's `commit_hash` vs current HEAD.** These can disagree in
  two ways:
  - *Stale-metadata case:* `commit_hash` is older than HEAD **but** the
    set of test_ids in the log matches the current test surface (same row
    count, same nodeids). The results are likely still trustworthy; just
    say "log was last refreshed at `<short_sha>`; row count still matches
    HEAD's test surface."
  - *Stale-data case:* `commit_hash` is older **and** the test surface has
    changed (new tests since, or tests deleted). Results are not
    trustworthy; recommend a re-run.

  Don't conflate the two. The fix for each is different.

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
