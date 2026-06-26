---
name: workflow-sandbox-lacks-matplotlib
description: "FIXED 2026-06-10 — figure rendering needs matplotlib; agents now pinned to the .venv (which has it) + matplotlib is a core dep. If render fails again, the interpreter isn't the .venv."
metadata: 
  node_type: memory
  type: project
  originSessionId: e9688977-51dd-450f-937d-15bb966604d9
---

**Resolved 2026-06-10.** Symptom was: `full-pass` agents ran bare `python`/`pytest`
→ the system **Homebrew** interpreter (`/usr/local/bin`, PEP-668 externally-managed,
no matplotlib), so figure rendering + render-dependent tests (`test_panel_axes.py`)
failed with `ModuleNotFoundError`, and figure passes **blocked on stale renders**
(R&H blocked twice this way). The complete env was the project `.venv`
(`/Users/estevaouyra/dev/model_agent/.venv`, py3.10.9) — nothing pointed agents at it,
and matplotlib was an optional `[sanity]` extra so envs installed without it.

**Fix (all landed):**
- `pyproject.toml` — matplotlib moved from `[sanity]` to **core `dependencies`**
  (rendering is a core deliverable, not a sanity extra).
- `.claude/workflows/full-pass.js` — `const PY = `${ROOT}/.venv/bin/python``; `SK()`
  instructs every agent to use `PY` for ALL Python (`PY -m pytest …`,
  `PYTHONPATH=implementation/src PY -m <pkg>.views`).
- `skills/run-tests/SKILL.md` + `AGENTS.md` — use `.venv/bin/python -m pytest`, not the
  PATH `pytest`.

**If a figure render/test fails with no-matplotlib again:** the interpreter in use is
NOT the `.venv` (someone ran bare `pytest`/`python`). Don't pollute the Homebrew python
(PEP 668 blocks it anyway) — use `<repo>/.venv/bin/python`, or `pip install -e .` into a
fresh venv (matplotlib comes as a core dep now). Always **audit the shipping image**
after rendering ([[vlm-eye-is-arbiter-over-tools]],
[[rendered-output-panels-are-reproduction-targets]]).
