# Skill: Update State

## Purpose

Refresh the model's README to reflect the current state of the reproduction
so that a returning human or a cold-start agent can pick up the work without
re-reading the entire history.

This is **not** a status snapshot — it's a planning artifact. The agent
gathers concrete data (including a fresh VLM pass over the figures), reflects
on what's working and what's broken, then writes a README that names the next
correction specifically enough to act on.

The skill writes `models/<model>/README.md` and appends new verdict files
under `models/<model>/logs/figure_comparisons/` (the persistent home for VLM
figure-comparison results). It does **not** mutate `logs/test_runs.jsonl`,
`logs/changelog.yaml`, or any other source, and it does **not** regenerate
figures or edit model code.

---

## Trigger

Human-invoked. Typically at the end of a working session or at the start of a
new one. Not tied to commits or test runs.

---

## Inputs (sources the agent reads)

Read everything available. Sources marked **(may not exist yet)** are part of
the long-term design but not all are implemented — degrade gracefully.

1. **Test table** — `neuromodels test-table` from the model directory. Returns
   the markdown table the README embeds verbatim. Its VLM column is populated
   from the persisted verdicts in `logs/figure_comparisons/` (source #6), so
   run the VLM step (Process Step 1b) **before** capturing this table or the
   column will read `—`.

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

6. **VLM verdicts** — `logs/figure_comparisons/figure_<N>_<UTCstamp>.json`.
   This skill **produces** these in Step 1b and then **reads them back** for
   the reflection. Each file is a provenance wrapper around the subagent's
   FigureComparison-shaped verdict:

   ```json
   {
     "figure_number": "1",
     "model_commit_hash": "<full model HEAD when evaluated>",
     "evaluated_at": "<UTC ISO8601>",
     "evaluator": "<who/what produced it>",
     "packet_path": "<the compare-figure-packet used>",
     "n_subagents": 3,
     "parent_adjudication": "<set only when a det/VLM disagreement was cross-checked>",
     "verdict": { "passes": true, "summary": "...",
                  "checklist_results": [...], "issues": [...],
                  "recommendation": "..." }
   }
   ```

   `neuromodels test-table` already picks the latest verdict per figure for
   the VLM column. For the reflection, run
   `scripts/verdict_status.py --model-dir models/<model>` — it reports each
   figure's latest verdict, whether it is **stale** (recorded against a commit
   older than the model's current HEAD → no longer trustworthy), which figures
   are **uncovered** (deterministic data but no verdict), and any parent
   adjudications on record.

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

- `scripts/persist_verdict.py` — wrap one subagent verdict (file or stdin)
  with provenance (model HEAD, UTC time, packet path, n_subagents, optional
  `--adjudication`) and write it to `logs/figure_comparisons/`. Used once per
  figure in Step 1b.

- `scripts/verdict_status.py` — per-figure latest VLM verdict with a
  `stale` flag (verdict commit vs current model HEAD), the list of uncovered
  figures (deterministic data but no verdict), and any parent adjudications
  on record. The reflection's primary VLM-side diagnostic.

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

# Failing test details (for "next correction")
python <repo-root>/skills/update-state/scripts/failing_tests.py

# Per-figure log freshness (for stale-metadata vs stale-data diagnosis)
python <repo-root>/skills/update-state/scripts/log_freshness.py

# Recent activity
git log --oneline -20

# Outstanding spec questions
cat logs/spec_questions.md 2>/dev/null || echo "(none)"
```

Do **not** capture `neuromodels test-table` yet — its VLM column reads the
verdicts produced in Step 1b. Run it in Step 1c.

If `logs/changelog.yaml` exists, read it.

### Step 1b — Run the VLM over the figures (subagents)

Deterministic green is **not** a finished figure — a figure is only green
when a fresh VLM verdict also passes. Refresh the VLM verdicts every run for
figures whose latest verdict is missing or **stale** (recorded against a
commit older than the model's current HEAD — check with
`scripts/verdict_status.py`). A still-fresh verdict (its `model_commit_hash`
== current model HEAD) can be reused without re-running.

For each figure needing a verdict:

1. **Draft the subagent context with the lib** (do not hand-assemble it):

   ```bash
   neuromodels compare-figure-packet <N> \
     --model-dir models/<model> \
     --output-file /tmp/<model>_figure_packets/figure_<N>.json
   ```

   The packet is a path-only JSON pointing at the original figure, the
   generated figure, the figure description, and the visual checklist.

2. **Spawn VLM subagents.** The subagent *is* the VLM — it reads the two
   images directly with its own vision; no API/CLI. Give it only the packet
   path and require a strict JSON verdict with this exact schema (it is what
   `persist_verdict.py` and `neuromodels test-table` consume):

   ```json
   {"passes": true,
    "summary": "...",
    "checklist_results": [{"item": "...", "result": "pass|fail|unsure", "note": "..."}],
    "issues": ["..."],
    "recommendation": "pass|fail|needs_review - short reason"}
   ```

   Spawn **2–3 independent subagents per figure**, in parallel across
   figures. VLM subagents have documented failure modes (hallucinating absent
   structure, inventing failures, reasoning from equations instead of reading
   the image, and — observed here — over-passing quantitative saturation /
   convergence criteria). Treat unanimous FAIL as strong; a lone PASS on a
   figure that is deterministically red is weak and must **not** be trusted
   (see the conflict rule). Where subagents disagree, or a verdict disagrees
   with the deterministic signal in a consequential way, **the parent agent
   reads the image itself** and records the call in `parent_adjudication`.

3. **Persist each verdict** with provenance:

   ```bash
   python <repo-root>/skills/update-state/scripts/persist_verdict.py \
     --model-dir models/<model> --figure <N> \
     --packet /tmp/<model>_figure_packets/figure_<N>.json \
     --verdict-file /tmp/figure_<N>_verdict.json \
     --n-subagents 3 \
     --adjudication "<only if the parent cross-checked a disagreement>"
   ```

   This stamps the verdict with the model's current commit and UTC time and
   writes `logs/figure_comparisons/figure_<N>_<stamp>.json`. Verdict files are
   append-only history; never edit or delete an old one.

### Step 1c — Capture the test table

Now run `neuromodels test-table` from the model directory and capture it
verbatim. Its VLM column reflects the verdicts just persisted.

### Step 2 — Reflect (agent reasoning)

Synthesize a **specific** picture. The reflection section must answer:

**The conflict rule (decides figure color — apply it literally):**

- **Any deterministic red is a loss.** A figure with even one failing
  deterministic test is broken, full stop. A VLM `pass` does **not** redeem
  it — a lone VLM-pass on a deterministically-red figure is the known
  over-lenient failure mode, not evidence of correctness.
- **Deterministic green + VLM red is also a loss.** Passing every
  deterministic test but failing (or `needs_review` with real issues) the VLM
  means the figure is broken — not green.
- **Green requires both:** all deterministic tests pass **and** a *fresh*
  VLM verdict (`model_commit_hash` == current HEAD) says `pass`.
- **Deterministic green + no/stale VLM = unknown**, never green.

With that rule:

- **What's working?** Only figures that are green by **both** signals
  (deterministic all-pass AND fresh VLM `pass`). Cite the figure numbers.
- **What's broken?** Two groups, named separately: (a) deterministic-red
  figures — name the failing test_ids, group by likely common cause; (b)
  deterministic-green-but-VLM-red figures — name the figure and the specific
  VLM issue. Distinguish a model-equation failure from a figure-generation /
  scope failure (e.g. a `needs_review` whose only issues are missing context
  panels) — both are "not green", but they route to different fixes.
- **What's unknown?** Deterministic-green figures with no VLM verdict or only
  a **stale** one (`scripts/verdict_status.py` reports `stale=yes`) are
  *uncovered* — not validated visually, not green. Name them explicitly.
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
| Green | all pass | fresh `pass` | "complete" |
| Red | **any fail** | anything (incl. `pass`) | "broken" — concrete deterministic failure mode |
| Red | all pass | `fail` / `needs_review` w/ issues | "broken" — concrete VLM failure mode |
| Unknown | all pass | none / stale | "uncovered" — surface as work-to-do |

Do not call a figure "done" without a fresh VLM-`pass` verdict. "Fresh" means
the verdict's recorded `model_commit_hash` matches current model HEAD (or is
at least newer than the most recent change to figure-relevant code). A stale
verdict is treated as no verdict.

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
3. **Uncovered figures.** Since this skill runs the VLM every invocation
   (Step 1b), broad "go run the VLM" is no longer a valid next correction —
   it's already done. Uncovered should only remain for a figure whose verdict
   genuinely could not be produced this run (e.g. missing generated figure).
   If so, name the figure and the blocker.
4. Open **spec question** that's blocking implementation work
5. A figure with a high % of failures (broad problem)

A deterministic-red figure outranks a deterministic-green-but-VLM-red figure
as the next correction: the deterministic failure message is the more
actionable signal. A lone VLM-pass on a deterministically-red figure is never
the reason to skip that figure — the conflict rule says red wins.

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
      hand-edited. Its VLM column is non-`—` for every figure that has a
      generated output (Step 1b ran).
- [ ] Every figure called "green" in "Current state" has both all
      deterministic tests passing AND a fresh VLM `pass`. No figure is called
      green on a stale or absent verdict.
- [ ] Any deterministic-red figure is called broken regardless of its VLM
      verdict; any det-green-but-VLM-red figure is called broken too. The
      conflict rule was applied literally.
- [ ] Each parent adjudication (where a det/VLM disagreement was
      cross-checked by reading the image) is recorded in the verdict file's
      `parent_adjudication` and reflected in "Current state".
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

- **VLM verdict commit vs model HEAD.** `scripts/verdict_status.py` reports
  `stale=yes` when a figure's latest verdict was recorded against an older
  commit than the model's current HEAD. A stale verdict is treated as **no
  verdict** (the figure is uncovered, not green) — and Step 1b should have
  refreshed it this run, so a remaining `stale=yes` means the VLM step was
  skipped or failed for that figure. Call that out.
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
  `logs/test_runs.jsonl` first if the data is stale. This skill reads
  `test_runs.jsonl`; it never writes it.
- **Regenerate figures or edit model code.** Step 1b compares whatever
  generated figures exist; it does not fix them. A VLM failure becomes the
  "next correction" for a later implementation pass, not an edit made here.
- **Add changelog entries.** That's a separate operation — the human or
  another skill records a new version when a meaningful state change is
  worth checkpointing.
- **Mutate test/changelog logs.** `test_runs.jsonl` and `changelog.yaml` are
  read-only inputs. The skill *does* write new (append-only) verdict files
  under `logs/figure_comparisons/`; it never edits or deletes existing ones.

Note: this skill now **does** run figure comparisons itself (Step 1b), via
`compare-figure-packet` + VLM subagents. `skills/compare-figure/SKILL.md`
remains the reference for the subagent protocol and the catalogue of VLM
failure modes; this skill is where that protocol is invoked on a schedule.

## Commit when done

When your work is complete, **commit your output** on the working branch — your changes, or (for a report-only role) your report — with a message that matches the diff. The process-auditor reads commit messages against diffs, so every agent must leave an atomic, honestly-described commit.
