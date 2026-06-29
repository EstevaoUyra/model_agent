# U1 — Never-caught failures: a measured floor (injected-fault probe)

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · measurement (the `U#` floor — not a single behavior) |
> | Behavior class | a required step silently doesn't run / produces nothing, and **no control notices** — the never-caught (false-negative) class that no intervention-surface sweep can enumerate (see [[D3]]) |
> | Detector | by definition **none** for the un-probed residue — which is exactly why this thread *measures* detection with a deliberate fault instead of waiting for a lucky human catch |
> | Status | open (bounded, not closed) — one sub-class measured-as-caught; residue named + unmeasured |

## Why this thread exists

Every other thread, and every sweep that built this catalog (memory, workflow, skills, the drift
register, `issues.yaml`), **indexes on fixes** — so it can only ever find behaviors someone
*noticed*. The never-noticed / never-caught class leaves no trace in any of those surfaces. You
cannot enumerate it; you can only **measure detection for a deliberately injected fault** and report
the rate. `U1` is that measurement, so "what are we still missing?" has a numeric floor instead of a
shrug.

## The probe (reproducible: `../evidence/u1_coverage_probe.sh`)

Fault class tested: **a silently-skipped required step** (the [[D3]] behavior — the workflow stops
producing a mandated artifact and still exits `faithful`). Method: take a throwaway copy of a
complete model (`boynton_2009`, figs 1–2, both `complete` at baseline), delete figure 1's *committed
render* (simulating a skipped render step), and ask whether `tools/check_figure_coverage.py` — a
gate, not a human — blocks it.

```
baseline (nothing removed):          gate exit 0   → complete
after fault (fig 1 render removed):   gate exit 1   → BLOCKED;  fig 1 missing: ['implemented'], fig 2 complete
```

**Result (measured 2026-06-29): caught.** For a silently-skipped *enumerated* artifact
(original / implemented / digitized / described / verdict), the coverage gate detects the omission
deterministically and blocks — no human required. So this sub-class is **not** in the never-caught
hole post-#56; D3's fix demonstrably holds against it.

## The residue this does NOT cover (the honest, still-open `U#` floor)

The gate checks **existence of enumerated, committed artifacts**. By construction it cannot catch:

1. **Wrong-but-present content.** A committed render that *exists* but is unfaithful passes coverage
   — coverage is existence, not correctness. (Correctness is E1's job, itself imperfect.)
2. **A figure missing from the target list.** Coverage only checks the `--figures` it's given; if the
   target-figure list itself silently omits a paper figure, the whole figure is invisible to the gate.
3. **Non-enumerated steps.** Any required step whose output isn't one of the five enumerated views
   (e.g. the Pillar-3 modifiability smoke test, [[D3]]/drift-row D6) is uncovered.

These three are the genuine `U#` residue. They are **named but unmeasured**: a fuller floor would
inject one fault of each type (a correct-looking but wrong render; a dropped target figure; a skipped
non-enumerated step) and report how many are caught by *any* control vs only by a human. That is the
next measurement, not a claim we can make now.

## What this buys the catalog's completeness claim

The defensible statement becomes: *"we swept every intervention surface (Tier 1), sampled the raw
narration (Tier 2 — Method C, pending), and put a **measured bound** on the never-caught class (Tier
3): silently-skipped enumerated artifacts are caught by the coverage gate; wrong-content,
dropped-target-figure, and non-enumerated-step faults remain the open residue."* That is a real floor,
not "we listed a lot."

## Links
- `measures → D3` (silent-step-stops; the gate is D3's fix — U1 confirms it holds for enumerated views)
- `bounds → the P#/U# coverage classes` in `INDEX.md` "Coverage & blind spots"
- `residue-1 connects-to → E1` (existence ≠ correctness; wrong-but-present content is E1's imperfect domain)

## Deeper-dig hook
Extend the probe to the three residue fault types (wrong-content / dropped-target-figure /
non-enumerated-step); report a per-fault-class detection table. Also run a Method-C random-narration
sample (Tier 2) for behaviors fixed inline but never written to any artifact.

## Refs
Tool: `tools/check_figure_coverage.py` · probe: `../evidence/u1_coverage_probe.sh` · sibling [[D3]]
(`process-outran-its-docs`, `fix-mode-false-blocks-on-coverage`) · drift register row D0/D6.
