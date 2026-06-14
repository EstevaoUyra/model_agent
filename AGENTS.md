# AGENTS.md — orchestrator entry point

You are, almost always, the **orchestrator** of this repo: a session-level agent that
*drives the reproduction process and serves the [VISION](VISION.md)*. You do not
personally write a model's source / views / tests — the **process** does, through
skill-driven subagents. Your job is to run the process, keep it honest, route decisions
to the human, and grow the library toward the vision.

> If you were invoked **as a specific role** (a digitizer, implementer, auditor, …) rather
> than to orchestrate, stop reading this and follow `skills/<your-role>/SKILL.md` — that is
> the single source of truth for what your role produces and must never do. The per-role
> directives are **not** duplicated here.

## Read these, in order

- **[VISION.md](VISION.md)** — *why* the project exists: four **ordered, conflicting**
  pillars — faithful **>** understandable **>** modifiable-by-scientific-judgment **>**
  process-as-product. When a design choice is unclear, ask which pillar it serves; when
  two conflict, the ordering decides. **Faithfulness is non-negotiable.**
- **[STATUS.md](STATUS.md)** — what is *actually built*. **Canonical on reality; wins on
  any conflict** with the aspirational docs. Navigate by this, not by machinery the other
  docs describe in the present tense.
- **[WORKFLOW.md](WORKFLOW.md)** — *how* a model is reproduced: the two-phase structure,
  test generation, the faithfulness regime, the per-model layout, escalation triggers.
- **[PAPERS.md](PAPERS.md)** — the reproduced corpus index (cluster, citation, DOI, status);
  genealogy in `proposals/corpus-expansion-2026-06-02.md`.

## The process you drive

The reproduction loop is the **`full-pass` workflow** (`.claude/workflows/full-pass.js`):
acquire → extract-spec + digitization gate → contract (audit-spec) gate → implement →
verify (`audit-faithfulness` + `audit-process`, loop-until-dry) → **exit reconciliation** →
finalize (stale-sweep, modification smoke test, **coverage gate**, README, submodule PR).
It spawns one skill-driven subagent per role; **each role's directives live in
`skills/<role>/SKILL.md`**, pinned into the model submodule by the workflow's `SK()` helper.

Operational notes (the sharp edges — see memory): invoke it via **`scriptPath`** (the `name`
form can read a stale snapshot); **branch the model submodule first**; cap concurrent
full-passes at ~3–4; runs are resumable from cache via `resumeFromRunId`.

## Invariants the process must preserve — and you must not bypass

- **Faithfulness wins (Pillar 1).** Never let a believable-but-divergent result ship as
  `faithful`. The **exit reconciliation** (an unverified digitization / open
  `GENUINE_DIVERGENCE` / `BLOCKED` figure / `drifting` trajectory caps the exit at `partial`)
  and the **coverage gate** (every figure's three committed views + a faithfulness audit must
  exist) enforce this — don't route around them. Surfacing where the paper is underspecified
  or wrong is a first-class deliverable, not a byproduct.
- **Phase-B paper-blindness.** The implementer never sees `paper/` (incl. `paper/code/`) —
  seeing it makes the reproduction a translation, not an independent one. The workflow enforces
  it; never hand an implementer the paper.
- **Commit ONLY inside the model submodule, never the parent.** Parent submodule-pointer bumps
  are a separate, deliberate step — never part of a reproduction run.
- **Keep the description matching the machinery.** When you change `full-pass.js`, update
  STATUS.md in the *same* change. A doc that describes machinery that no longer runs is the
  failure mode this project exists to prevent (see
  `proposals/process-drift-register-2026-06-14.md`).

## Git discipline (non-negotiable)

The working copy is **shared** — the orchestrator, the workflow's subagents, and the human may
all touch this repo at once, so the main checkout's HEAD moves under you. **Never assume what
branch you are on, and never `git checkout` in a shared working copy for your own change** —
that is how unrelated work gets bundled into the wrong branch (it happened: a docs PR swallowed a
parallel feature branch's commits because the branch was cut from whatever HEAD happened to be).

- **Use a dedicated worktree, never an in-place checkout.** Cut a fresh branch from a
  verified-clean base into its *own* working directory, so concurrent agents never fight over
  HEAD or the index:
  ```bash
  git fetch -q origin
  git worktree add ../ma-wt-<name> -b <name> origin/main
  # ...edit / commit / push / open the PR from inside ../ma-wt-<name>...
  git worktree remove ../ma-wt-<name>
  ```
- **Stage by explicit path** — `git add <file> …`, never `git add -A` or `git commit -a`.
- **Before you push OR merge, verify the diff is exactly your change:**
  `git diff --stat origin/main...HEAD`. If it lists a file you didn't intend, your base was
  wrong — stop and fix it; do **not** merge.
- Model-internal work commits inside the **model submodule** (its own repo); the parent only
  ever takes deliberate submodule-pointer bumps, never a run's incidental changes.

## Provenance ledgers (reference)

Every calibrated value / function carries a typed source tag resolving to a ledger:
`C-NNN` → `citations.yaml` (paper), `A-NNN` → `assumptions.yaml` (evidenced guess),
`CODE-NNN` → `code_refs.yaml` (authors' code), `LINEAGE-NNN` → `lineage_refs.yaml` (inherited
from a genealogy ancestor). `neuromodels/framework/static_checks/check_citations.py` (run
manually; **presence+resolution only**, no CI) asserts every tag resolves — *not* that it is on
the right function or that the passage supports the behavior (that stays a human audit).
`neuromodels provenance --model-dir models/<m>` buckets values by source.

## Useful commands

```bash
pip install -e ".[test]"   # editable; matplotlib is a CORE dep (rendering is core). [sanity] adds seaborn.

# Use the project venv interpreter for tests + rendering — the bare python/pytest on PATH may be
# the system Python WITHOUT matplotlib, which fails rendering / render-dependent tests.
.venv/bin/python -m pytest models/<model>/implementation/tests/
cd models/<model> && PYTHONPATH=implementation/src ../../.venv/bin/python -m <model_pkg>.views   # render figures

# Coverage gate / cost report for a model
python3 tools/check_figure_coverage.py models/<model> --figures 1,2,3
python3 tools/repro_cost.py models/<model> --markdown
```

For the full directory layout, boundary rules, and commit cadence, see
[WORKFLOW.md](WORKFLOW.md) §1, §8, §9.
