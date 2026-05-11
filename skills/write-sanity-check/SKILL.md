# Skill: Write Sanity Check

## Purpose

Sanity checks are **exploratory diagnostics** that build intuition about a
component's behavior. They print summary statistics to stdout (token-friendly,
agent reads) and save PNGs to a gitignored directory (visual, human reads).
They make **no assertions**.

---

## Why sanity checks live alongside tests

Tests answer "does X always satisfy P?" — binary, narrow. They tell you
something is wrong but not what's happening. When debugging, the agent often
needs to *see the shape* of a component's output across a few configurations.

We could write ad-hoc scripts for that, but they get thrown away. Sanity
checks are the version that survives: each one is named, lives in
`implementation/sanity_checks/`, can be re-run, and its outputs (text + PNG)
document the model's current behavior. They make no assertions — that's the
line between sanity check and test, and keeping it sharp prevents the two
surfaces from collapsing into each other.

The dual-output design (token-friendly text for agents, PNG for humans)
acknowledges that the two audiences want different things from the same
diagnostic. Neither is sufficient alone.

---

## Sanity check vs test — the load-bearing distinction

> If you can write `assert P(output)` for a property P that should *always*
> hold → **test**.
>
> If you want to look at the output and form a judgement → **sanity check**.

The moment you write `assert`, it's a test, not a sanity check. Keep this
line sharp.

---

## Where they live

```
implementation/sanity_checks/
  check_<topic>.py                # one file per topic; multiple checks inside
  check_<topic>_outputs/          # GITIGNORED — PNG + text per check
  README.md                       # one-line index of checks (optional)
```

**Naming:** `check_<component_or_question>.py`. Examples:
`check_stimulus_drive.py`, `check_attention_field.py`,
`check_full_pipeline_trace.py`.

---

## Use the framework helpers

Helpers in `neuromodels.framework.explore` enforce consistent style across
models so a human inspecting one model's sanity checks doesn't have to
re-learn idioms.

```python
from neuromodels.framework.explore import (
    require_plotting,
    output_dir,
    matrix_stats,
    matrix_excerpt,
    write_text,
    save_heatmap_grid,
)
```

`require_plotting()` raises with an install hint if matplotlib/seaborn are
missing — they live under the optional `sanity` extra:
`pip install -e ".[sanity]"`.

---

## Token discipline

If an array has more than ~10 elements along a dimension, print **stats**
(use `matrix_stats`) instead of values. Cap stdout per check at ~30 lines.
Push the visual surface to PNGs.

The stdout audience is the agent; the PNG audience is the human. Don't make
the agent wade through a 200-line dump when a 5-line stat summary plus a
linked PNG path covers the same ground.

---

## When to write or extend a sanity check

- After implementing a new pipeline step → exercise it across a few
  configurations.
- When a test fails in a way you don't immediately understand → write or
  extend a sanity check that gives you the intuition.
- Before declaring a component "done" → re-run the relevant sanity check
  and confirm the output looks right.

---

## Lifecycle

Keep, evolve, don't delete. Sanity checks become part of the model's
permanent documentation. If a component changes meaningfully, update the
sanity check; don't remove it.

---

## Citation/Assumption docstrings

- **Yes** for sanity checks that exercise specific equations (cite the equation)
- **No** for full pipeline traces (a citation list would be the whole model;
  a simple docstring describing the purpose is enough)

---

## What sanity checks are NOT

**They don't substitute for understanding.** Sanity checks build intuition;
they don't replace analysis of a failing test. The fix to a failing test is
still the failure description plus reasoning, not "I ran the sanity check and
it looks fine."

**They are not tests.** No `assert`. If a property must always hold, that's a
test — write it in `implementation/tests/` (or in `article_aware/extracted_data/`
if it's a paper-derived claim).
