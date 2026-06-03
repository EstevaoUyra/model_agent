# Full-pass reproduction workflow — agent diagram (design, 2026-06-03)

Goal: a **dynamic workflow that does one full pass over a paper** — extract → gate →
implement → verify → route/report — so the orchestration is *encoded*, not hand-driven
agent-by-agent. This is the agent map to plan it from. (Not built yet; this is the design.)

A "pass" = one trip through the pipeline, including **one fix-cycle for clear bugs**.
Genuine divergences and paper-issues *exit* the pass (flagged / to the human); closing
them is the *next* pass.

```
                                ┌───────────┐
                                │  paper/   │   only paper-AWARE roles may read this
                                └─────┬─────┘
 PHASE A · extract the contract       │            (paper-aware → writes article_aware/)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  ① spec-extractor        ② figure-extractor          ③ digitizer               │
 │  [extract-spec]          [extract-figure]            [digitize-figure]          │
 │  equations · params ·    per-figure description ·    classify mode/type ·       │
 │  calibration ledger      panels · axis limits ·      calibrate · trace ·        │
 │  (EVIDENCED assumptions· model-panels-only scope ·   overlay · pchip ·          │
 │  lineage) · citations ·  (no paper image ⇒ BLOCKED)  provenance · the VIEW ·    │
 │  spec-questions                                      adversarial self-overlay   │
 └──────────────────────────────────┬─────────────────────────────────────────────┘
                       references (the "ruler") + spec + Phase-A-owned view
                                    ▼
 GATE · is the ruler faithful?      (a SEPARATE critic — never the digitizer ③)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  ④ digitization-auditor   [audit-digitization]   (paper-aware)                 │
 │     references vs the paper: adversarial overlay + crop_region zoom; were the  │
 │     right TOOLS used?                                                           │
 │     ─► FAITHFUL = refs become BINDING   |  DIVERGENT / TOOL-MISUSE ─► back to ③ │
 │                                          |  BLOCKED (no image)      ─► HUMAN     │
 └──────────────────────────────────┬─────────────────────────────────────────────┘
 ═════════════════ PHASE WALL · Phase B never reads paper/ ═══════════════════════
                          binding references + the contract
                                    ▼
 PHASE B · implement                (paper-BLIND → writes implementation/)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  ⑤ implementer    model · protocols · measurements · view-record               │
 │     from article_aware/ ONLY · every fn carries a Citation:/Assumption:         │
 │     ─► renders figures · deterministic tripwire tests · three-tier figure tests │
 └──────────────────────────────────┬─────────────────────────────────────────────┘
                       implementation + rendered figures + the change-trail
                                    ▼
 VERIFY · three independent critics (none is the builder ⑤)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  ⑥ faithfulness-auditor  [audit-faithfulness]  (paper-aware, re-renders)       │
 │     impl ↔ paper ↔ refs · per-figure divergence, CLASSIFIED:                   │
 │       IMPLEMENTATION-BUG ─► fix   |   GENUINE-DIVERGENCE ─► flag (never fit)    │
 │       SUSPECTED-PAPER-ISSUE ─► only after the ladder: paper → lineage → HUMAN   │
 │                                                                                │
 │  ⑦ process-auditor  [audit-process]  (paper-BLIND, reads the change-trail)     │
 │     is the trajectory toward-paper or toward-GREEN? (laundering, goalpost-move)│
 │                                                                                │
 │  ⑧ adversarial-judge  (paper-blind, on demand) — adjudicate one resisting claim│
 └──────────────────────────────────┬─────────────────────────────────────────────┘
            findings ────────────────┤
 ┌───────────────────────────┐       │   BUG ─► Phase A (contract) and/or Phase B (impl)
 │ FIX (same pass, clear bugs │◄──────┤        ─► re-render ─► RE-AUDIT ⑥ (mandatory:
 │ only): re-run ③ / ⑤        │       │           the builder never self-certifies)
 │ ─► re-verify ⑥             │       │
 └───────────────────────────┘       ▼
 ROUTE + REPORT  (the workflow / organizer — routes, never implements)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  ⑨ state-updater  [update-state]  ─►  README = the UP-TO-DATE AUDIT of record   │
 │     GENUINE divergences → flagged · PAPER-ISSUES + BLOCKED + DRIFT → HUMAN      │
 └──────────────────────────────────────────────────────────────────────────────┘
                                    ▼
                    HUMAN · dispositions paper-issues / blocked figures / drift
```

## The agents

| # | Role | Phase / paper | Skill | Reads | Writes | Its separate check |
|---|---|---|---|---|---|---|
| ① | spec-extractor | A · aware | `extract-spec` | paper, lineage | `article_aware/spec/` | ⑥ faithfulness-auditor |
| ② | figure-extractor | A · aware | `extract-figure` | paper figures | `article_aware/figures/*.md` | ⑥ |
| ③ | digitizer | A · aware | `digitize-figure` | paper panels | `…/panel_*_digitized.json`, overlays, view | ④ digitization-auditor |
| ④ | digitization-auditor | gate · aware | `audit-digitization` | paper + refs | `logs/digitization_audit/` | — (it *is* a check) |
| ⑤ | implementer | B · **blind** | `implement` | `article_aware/` only | `implementation/src/` | ⑥ + ⑦ |
| ⑥ | faithfulness-auditor | verify · aware | `audit-faithfulness` | paper + impl + refs + lineage | `logs/faithfulness_audit/` | — |
| ⑦ | process-auditor | verify · **blind** | `audit-process` | the change-trail | `logs/process_audit/` | — |
| ⑨ | state-updater | report | `update-state` | the audits | `README.md` (current state) + `logs/changelog.md` (detail) | — |
| ⑩ | test-author | verify · A · blind-ok | `author-tests` | ⑥'s findings | `article_aware/extracted_data/` tests | — |

(The **adversarial-judge** is *not* spawned by the pass — it is invoked on demand, by an
auditor or the human, to settle one resisting claim paper-blind. Out of the standard flow.)

## What ⑨ writes — the README *is* the current state

⑨ rewrites the README to show the model **as it stands now** (a state, not a history):
- **The current exit/status at the very top** — *before* the model description and the
  figures: the pass outcome (faithful / partial / blocked) and the queued human-decisions.
- **Per figure, three views side by side** — original (paper panel) · digitized reference ·
  implementation render — plus its **audit/check tables** (the current verdict of record).
- **A "potential sources of the issues" section** — for each open divergence, where it
  likely originates (e.g. the `audited:false` suppressive-gain tuning, a specific
  parameter/convention) so the next pass and the human know where to dig.
- **A changelog** — ⑨ appends **one succinct line** per pass (a sentence or two: what
  improved, what now passes). The full per-pass detail goes to `logs/changelog.md`; the
  README carries only the running one-line overview.

## Invariants the pipeline must hold (the lessons, encoded)

1. **The phase wall.** Phase B (⑤) never reads `paper/` — it builds from `article_aware/`
   only. The faithfulness reasoning is done by paper-aware roles; the builder implements the
   *mechanism* and reports what emerges. This is what prevents laundering (the wrong Fig-4C
   sign was a builder bending the model to a convenient prose quote).
2. **Separation of powers — no self-grading.** digitizer ③ ≠ digitization-auditor ④;
   implementer ⑤ ≠ faithfulness-auditor ⑥. The organizer/workflow **routes, never implements
   and never certifies**.
3. **Guard the ruler before measuring.** ④ audits the digitized references *before* the
   tiers grade anything against them — a wrong ruler silently mis-calibrates every test.
4. **The eye is arbiter over the tools.** ③ and ④ validate **adversarially** against the
   overlay-on-paper, zooming suspect regions (`crop_region`); a tool result the eye sees is
   wrong *is* wrong. "It tracks well" is not a verdict.
5. **Paper-issue is a last resort.** ⑥ resolves an apparent contradiction within the paper,
   then via the **lineage/sibling papers**, and only then declares a `SUSPECTED-PAPER-ISSUE`
   for the human.
6. **Re-audit after every change; the README is the audit, not the self-report.** A fix is
   not done until a *fresh separate* ⑥ re-audits the changed model and ⑨ writes that verdict.
7. **Flag, never fit.** A genuine divergence (faithful mechanism, wrong magnitude) stays red;
   no parameter is tuned to match a figure. Watch `audited:false` knobs especially — only ⑥
   catches those.
8. **No paper image ⇒ BLOCKED ⇒ human.** No fallback, no paper-blind checklist substitute.
9. **Every agent commits its own output when done** — changes, or (report-only roles) the
   report — with a message matching the diff. The change-trail is atomic and honestly
   described, which is exactly what ⑦ the process-auditor reads.

## Loops & routing (the "dynamic" part)

The pass has **two bounded loops** plus terminal exits. Both auditors emit a **structured
verdict with a loop-target tag**, so the workflow routes deterministically (not by the
organizer reading prose).

- **Digitization loop `③↔④`.** ④ returns per panel `FAITHFUL` | `DIVERGENT`/`TOOL-MISUSE` |
  `BLOCKED`. A divergence routes its *specific* defect back to ③ for a **targeted re-digitize
  of that panel**; ④ re-audits. Bounded — after N rounds (or `BLOCKED`) it exits to the human.
- **Implement/verify loop `⑤↔⑥`, routed by where the break is.** ⑥ localizes each divergence
  along `paper → contract → code` and tags it:
  - `CONTRACT-BUG` (the spec/pseudocode/tests encode the wrong thing) → loop to **Phase A**
    (re-author the contract: ①/②/③) → then ⑤.
  - `CODE-BUG` (code diverges from a correct contract) → loop straight to **⑤**.
  - `GENUINE-DIVERGENCE` → **flag** (no loop; never fit).
  - `SUSPECTED-PAPER-ISSUE` (only after the lineage ladder) → **human**.
  Bounded the same way; every loop end re-runs ⑥ (no self-certification).
- **⑩ test-author closes the VLM-cost gap (nested loop).** Before each fix, a Phase-A
  test-author encodes the audit findings as deterministic tests — BUG → **must-pass**;
  GENUINE/PAPER-ISSUE → **intended-failure tripwire** (red; flips only if the model genuinely
  improves). The implementer then runs an **inner loop** — edit → `pytest` → repeat, *no
  VLM* — and only returns to ⑥ (the outer, capped loop) when the local suite is green. So the
  expensive VLM pass runs **per fix-round, not per edit**, and the implementer can only chase
  paper-grounded must-pass tests — it cannot iterate itself into overfitting.
- **Terminal exits:** flagged divergences and BLOCKED/paper-issue/drift go to ⑨/the human;
  the pass ends when ⑥ has no open `*-BUG` (only flags/paper-issues remain).

## Resolved decisions (2026-06-03)
- **Fan-out:** per-figure **pipeline** for ②③④ (figures concurrent, the `3↔4` loop inside
  each lane); ①spec-extract in parallel; **barrier before ⑤**; ⑥⑦ in parallel.
- **Loop depth:** **loop-until-dry, capped at 3 rounds** for both `3↔4` and `5↔6`. What
  survives the cap is a genuine divergence / paper-issue / STUCK.
- **Isolation:** **no worktrees** — agents write disjoint paths or run sequentially.
- **Human gates:** **never pause mid-flight** — record, flag, finish, and queue every
  human-decision (BLOCKED / paper-issue / drift / STUCK) in the README current-exit block;
  the human adjudicates between passes.
- **The view:** **moves to `article_aware/`, Phase-A-owned** (generated by ③); Phase B
  produces records the view renders but never edits presentation. Migrating the existing
  `implementation/.../views.py` is an **article-aware (Phase-A) task**.
