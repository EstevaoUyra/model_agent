# D3 — A required step silently stopped running, and nothing was built to notice

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · process/delivery (cognitive root in Evaluation via E5) |
> | Behavior | silent omission of a mandated step with no detector — the process can stop performing a required step and still report success, because every gate judges the *content of artifacts that exist*, not *whether the step ran*; "absence reads as innocence" |
> | Symptom | `full-pass.js` could stop committing the original figure crop / implemented render / visual checklist / VLM verdict and still exit `faithful` |
> | Agent role | process / gate (the workflow as a whole; the process auditor is artifact-blind by design) |
> | Trigger | any gate that validates artifact *content* but never asserts artifact *presence*; no coverage assertion over required steps |
> | Cause (evidence) | structural — there was no coverage gate — *intervention-tracked* (PR #56 added `tools/check_figure_coverage.py`, which blocks the exit unless required artifacts exist) |
> | Detector | **not a gate** — surfaced 2026-06-14 by a figure-render note, not by any control. The defining property is that *nothing could detect it* |
> | Lever(s) | structural/gate (coverage gate) — held for the silent-omission failure, but introduced a new false-block failure (PR #66 marker + a human-rule to mitigate) |
> | Flags | ↔ E5 (cognitive root); silent-omission mitigated, difficulty partially migrated to false-blocks |
> | Status | mitigated |

## The behaviour

Every gate in the pipeline judged **the content of whatever artifacts happened to exist** — or an
auditor re-rendered its own transient copy and judged that. **Nothing asserted that the required
steps had actually run and committed their outputs.** The process auditor is paper-blind and
artifact-blind by design and, in the register's phrase, "reads absence as innocence." So the
workflow could silently stop producing a required output — the original paper crop, the committed
implemented render, the per-figure visual checklist, the VLM verdict — and **still exit
`faithful`.** A step quietly dropping out of the pipeline produced no failing signal; it simply
stopped happening, and the success report rode along unchanged.

This is the keystone behind D1: it is *why* the docs could go stale silently (D1) and *why* a
required step could vanish silently (D3) — the same blind spot, that the system checks
content-of-what-exists but never presence/currency.

## The Detector *is* the finding

The whole point of D3 is that **no control caught it.** The gap surfaced on 2026-06-14 only
because a figure-render note (izhikevich) tripped over a missing/retired step — a side effect a
human noticed, not a gate firing. The register is explicit that the guardrail *could not* have
caught it: there was no coverage assertion. This is the catalog's selection-bias signal made
literal. It also names the catalog's blind class directly: the **`U#` never-caught failures** are
exactly this behaviour *without* the lucky human catch — figures that exited `faithful` with a
silently-skipped step and were never re-checked. The map cannot see its own false-negatives here;
D3 is the visible tip of that class.

## Cognitive root: self-certification (↔ E5)

D3 is the process-level face of **E5 — self-certification ("green tests / clean exit ⇒ done").**
At the *agent* level (E5), an agent treats passing its own checks as proof of correctness without
an independent confirmation that the right work was done. At the *process* level (D3), the pipeline
treats "no gate complained" as proof the required steps ran — when in fact no gate was even
*looking* at whether they ran. Same move, two scales: success is inferred from the absence of a
complaint by a checker that does not cover the thing in question. The `E5 ↔ D3` edge in INDEX is
this identity; hardening one without the other leaves the loophole open at the other scale.

## How it responded to intervention

- **PR #55 (`cf2b39d`, 2026-06-14):** the drift register names D0 — "No gate asserts that required
  steps ran / artifacts exist; absence reads as innocence" — as the structural enabler of every
  other drift row.
- **PR #56 (`6ab2b1f`, 2026-06-14):** the **coverage gate** lands — `tools/check_figure_coverage.py`.
  Per target figure it requires the three *committed* views (paper crop · digitized · reproduced
  render) plus a committed faithfulness verdict, else the exit **blocks**. The keystone fix: a
  required step that silently didn't run now blocks instead of riding along. Validated by re-running
  izhikevich (coverage passed; crop + render committed; verdict preserved).

**The second face — the gate over-corrected into false-blocks.** Once the gate existed, it began
**false-blocking sound models.** `full-pass from="fix"` skips Phase A (extract + digitization), and
the finalize stale-sweep only re-renders the *implemented* view — so fix mode can never create a
missing `original` (paper crop) or `digitized` artifact. Any in-scope figure lacking those
committed artifacts therefore blocks at the coverage gate *even when the reproduction is sound*.
This hit **4 of 6** fix passes on 2026-06-15 (round 2), in three flavors: derived/synthetic panels
with no paper figure (unsatisfiable `original`), never-digitized real figures (need a `from=extract`
pass), and a paywalled paper (a genuine human/acquisition block).

- **PR #66 (`8e9a4a2`/`4778e0a`, merged):** coverage gate gains a `.nopaper` marker for render-only
  panels + a testable `classify_figures`, so render-only panels stop being false-blocked.
- **Human-rule (memory `fix-mode-false-blocks-on-coverage`):** before launching `from=fix`, run the
  coverage check first and pass *only* real paper figures with existing artifacts (drop
  `mechanism`/`dynamics`-type derived labels); route the three flavors differently (derived →
  marker/exclude; never-digitized → `from=extract`; paywalled → human).

**Which lever held.** The structural coverage gate solved the original silent-omission failure
(a skipped step now blocks). But the gate's blunt presence-check **migrated the difficulty** into a
new failure mode — false-blocking legitimately-absent paper sources — which then required a
follow-on marker (#66) plus an operating human-rule. So the silent-stop is mitigated; the cost of
the fix is a new false-positive surface that is itself only partly closed by convention.

## Confidence & threats to validity

High: the gate's absence and its addition are both committed (PR #55 register + PR #56 gate), and
the 4/6 false-block count comes from a dated round (2026-06-15, round 2) recorded in memory.
Threats: (a) **anecdote ≠ rate** — "4 of 6" is *one round's* count, not a steady-state false-block
rate; (b) the silent-omission "mitigated" claim is about the *known* surfaces the gate covers
(three views + verdict) — by construction it says nothing about silent omissions of steps the gate
doesn't enumerate (the `U#` hole remains); (c) the detector for the *original* failure was a single
lucky render note, so we have n=1 for "how it was caught," which is itself the selection-bias point,
not a measurement.

## Scope / generality

Descriptive. The mechanism — a success report inferred from "no complaint" by checkers that judge
content but never coverage — is generic to any pipeline with conditional/optional steps and no
"did the required step run?" assertion. The follow-on lesson (a presence gate over-fires on
legitimately-absent inputs unless it can distinguish "missing because skipped" from "missing because
N/A") is equally generic. Setup-specific in the particular artifacts (figure crop / digitized /
render / verdict) and the `from=fix` phase-skipping that exposed the false-block.

## Links
- `↔ E5` — **self-certification is the cognitive root.** D3 is its process-scale instance; the
  same "absence of a complaint ⇒ done" loophole at two scales.
- `shared-root → D1` — "no coverage gate" is the structural enabler of both (stale docs undetected
  / skipped step undetected).
- `connects-to → U#` (never-caught failures) — D3 is the visible tip; the gate bounds it for
  enumerated steps only.

## Deeper-dig hook
(1) Measure the steady-state false-block rate post-#66 across `from=fix` runs (denominator = fix
passes with in-scope figures) to test whether the marker + human-rule actually closed flavor-1/2.
(2) For the `U#` estimate: run the injected-fault calibration probe — deliberately skip a required
step on a model and confirm the coverage gate (not a human) blocks it. Data:
`tools/check_figure_coverage.py`, `logs/exit.json` per model, the `from=fix` round-2 transcripts.

## Status
mitigated — silent-omission is gated for the enumerated artifacts; the false-block side effect is
partly closed (marker #66 + human-rule). Not `solved`: coverage is enumerated (not exhaustive), and
the false-block rate post-fix is unmeasured.

## Refs
- Memory: `process-outran-its-docs`, `fix-mode-false-blocks-on-coverage`.
- Proposal (PRIMARY): `proposals/process-drift-register-2026-06-14.md` (row **D0**, the keystone).
- PRs: #55 (`cf2b39d`), #56 (`6ab2b1f`), #66 (`8e9a4a2` / `4778e0a`).
- Sibling: **E5** (self-certification) — INDEX edge `E5 ↔ D3`.

---

### Evidence layer (for verification, not reading)
- **Grounding source:** the committed drift register (row D0) + git PR chain + two distilled
  memories. **No quote ledger produced** — no verbatim *workflow-agent* corpus quotes were
  promoted; for this thread the Detector is, by definition, *not* an agent (a render note / human),
  and the diagnosis lives in the committed register (a stronger, citable artifact).
- **Corpus note `[to-verify-on-deeper-dig]`:** `check_figure_coverage` / "coverage gate" appear in
  orchestrator-session transcripts under `evidence/corpus-snapshot/` (≈1.2K refs each), but those
  are human-led orchestration logs, not the agent-behavior narration the quote harness targets;
  not promoted.
