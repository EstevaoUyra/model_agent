---
name: process-outran-its-docs
description: full-pass.js drifted ahead of VISION/WORKFLOW/STATUS; no coverage gate means a required step can silently stop running
metadata: 
  node_type: memory
  type: project
  originSessionId: a6fd7e82-9088-4e49-8e88-9c0c3e990d90
---

The `full-pass.js` workflow (the de-facto process) **drifted ahead of every description doc**.
WORKFLOW.md and even STATUS.md (whose ONE job is canonical-on-reality) describe a process the
workflow no longer runs — e.g. STATUS.md's "real loop" is the retired `compare-figure-packet`
VLM loop; full-pass.js uses paper-aware `audit-faithfulness` instead. This is the VISION's own
named failure mode (docs "masquerading as machinery that exists") recurring on the doc stack.

**Root cause = no coverage gate.** Every gate judges the *content* of artifacts that exist (or
re-renders its own copy); nothing asserts required steps RAN and committed outputs. The process
auditor is paper- and artifact-blind by design and "reads absence as innocence." So the workflow
could silently stop committing the original figure crop, the implemented render, the visual
checklist — and still exit `faithful`. Surfaced 2026-06-14 by a figure-render note, not a gate.

Full adjudication (opinionated, by pillar ordering) in
**proposals/process-drift-register-2026-06-14.md**. **RESOLVED 2026-06-14 (PR #56, merged + validated):**
- **Coverage gate** `tools/check_figure_coverage.py` — per target figure the three COMMITTED views
  (paper crop `article_aware/figures/figure_N.png` · digitized · `figures_reproduced/figure_N.png`)
  + a committed faithfulness audit must exist, else the exit blocks. The keystone: a required step
  that silently didn't run now blocks instead of riding along.
- **Exit reconciliation** in full-pass.js: unverified digitization / open GENUINE_DIVERGENCE /
  BLOCKED figure / `drifting` trajectory all cap the exit at `partial`.
- digitization commits the crop (+ `.nodigitize` marker for schematics); stale-sweep commits the
  render; per-panel digitization restored; minimal scalar modification smoke test (Pillar 3).
- Docs (WORKFLOW/STATUS/skills) reconciled to reality. Validated by re-running izhikevich: coverage
  passed, crop+render committed, smoke test perturb→respond→revert, verdict preserved.

The deterministic test layer and audit-faithfulness were always sound — the models are fine; the
*process-as-product* had been running on stale docs.

**Apply:** when changing full-pass.js, update STATUS.md in the same change; treat "a required
step silently not running" as the failure class to gate against. Comparing a render to the
**digitized** reference (not the paper PDF) is the *preferred* design — the paper-grounding lives
in the separate digitization audit. Related: [[re-audit-after-every-model-change]],
[[faithfulness-critics-want-to-find-issues]], [[reproduction-cost-tooling]].
