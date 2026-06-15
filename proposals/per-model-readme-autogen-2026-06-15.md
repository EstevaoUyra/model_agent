# Per-model README auto-generation — design + artifact gap analysis

_2026-06-15. Companion to `tools/build_readme.py` (which generates the **parent**
roadmap table). This proposal covers the **per-model** READMEs under
`models/<name>/README.md`._

## Problem

Today each model's README is hand-authored by the full-pass **finalize** agent.
Consequences:

- **Structure drifts.** The `reynolds_heeger_2009` README is the intended shape
  (7 sections); most other models only loosely follow it, and two
  (`spratling_2012`, `karklin_lewicki_2009`) are freeform prose with no exit-JSON
  line at all (so the parent `build_readme.py` can't read their state).
- **Deterministic facts go stale by hand.** Test counts, VLM verdicts, the cost
  table, the changelog one-liners are all re-typed by an agent each pass — the
  exact failure mode the parent table was built to remove.
- **The exit JSON is its own single source of truth, embedded in the prose it
  describes.** Nothing else can read it without regex-scraping the README.

Goal: **one generator, run per model, that assembles all 7 sections from
artifacts.** The generator renders artifacts; it never invents prose.

## The 7 sections and where each comes from

| # | Section | Source | Derivable? |
|---|---|---|---|
| 1 | Current exit | `logs/exit.json` *(NEW)* | ✅ fully |
| 2 | Status | `logs/exit.json` + `test_runs.jsonl` + `figure_comparisons/` + narrative in `logs/readme_meta.yaml` *(NEW prose field)* | ◑ data + 1 prose field |
| 3 | Model | `article_aware/spec/model_spec.yaml` + `citations.yaml` | ✅ fully |
| 4 | Reproduced figures | `figure_N_layout.yaml` + files on disk + `test_runs.jsonl` (tier/check) + `figure_comparisons/` + `digitization_audit` + per-figure headline in `readme_meta.yaml` | ◑ data + headlines |
| 5 | Potential sources | `logs/issues.yaml` *(NEW)* | ✅ once authored |
| 6 | Changelog | `logs/changelog.md` `## DATE — summary` headers | ✅ fully |
| 7 | Reproduction cost | `tools/repro_cost.py --markdown` | ✅ already done |

"Fully derivable" = the generator computes it from existing machine data.
"◑" = the generator renders structured data, but a human/agent authored the
irreducible analytical prose **once** into a versioned artifact.

## Missing artifacts — and how to add them

### A. `logs/exit.json` — the standalone exit/state file (feeds §1, §2, and the parent table)

The exit JSON must stop living only inside the README. Schema:

```json
{
  "overall": "reproduced",
  "trajectory": "toward_paper",
  "flagged_count": 0,
  "blocked": [],
  "audit": "hardened",
  "figures_in_scope": [1, 2, 3, 4, 5, 6, 7],
  "figures_rerendered": 7,
  "updated_at": "2026-06-10",
  "headline": "Figures re-rendered and certified; model independently verified faithful."
}
```

Two free wins:
- It adds the `"audit"` field the parent `build_readme.py` already wants and today
  has to default to `self-reported` (it logs a warning for every model).
- The parent table can read `models/<m>/logs/exit.json` directly instead of
  regex-scraping the README prose.

**Who writes it:** the full-pass **finalize** / **update-state** step, replacing
the manual exit block. Backfillable from the current README's embedded JSON.

### B. `logs/issues.yaml` — "Potential sources of the issues" (§5)

The only section with no artifact at all today. Schema:

```yaml
preamble: |
  The forward model (model.py, Eqs 5-6) is FAITHFUL operator-for-operator ...
issues:
  - id: F1
    category: FIGURE        # FIGURE | CONTRACT | MODEL | GEOMETRY | DECISION | MAGNITUDE
    status: resolved        # open | resolved
    title: "The Figure 6 render is now FRESH"
    body: |
      All 7 figures were re-rendered with matplotlib 3.10.9 ...
    sources: ["model.py:284", "protocols.py run_figure_6C", "code_refs.yaml CODE-018"]
```

**Who writes it:** the **faithfulness/spec auditors** already produce this reasoning
in their audit logs; the finalize step distils it here (one entry per open or
recently-resolved divergence) instead of into prose.

### C. tier + check metadata in `test_runs.jsonl` (feeds the §4 per-figure check tables)

The RH tests carry `@pytest.mark.tier("hard"|"qualitative"|"soft")` and
`@pytest.mark.soft`, but `neuromodels/framework/testing/plugin.py` drops them — so
the per-figure **Tier / Check / Result** tables in §4 cannot be generated and are
hand-typed today.

Fix (additive, low-risk — implemented in this change):
- `plugin.py` captures the closest `tier` marker and an optional human-readable
  `check` description (from a new `@pytest.mark.check("...")` marker, else the test
  docstring's first line) into two new columns: `tier`, `check`.
- Old rows lack the columns → the generator treats them as `tier=None` and falls
  back to the prose check table in `readme_meta.yaml`. Once a model re-runs its
  suite, the tables populate themselves.
- **Adoption:** only RH uses tier markers today. Other models keep working
  (tables come out empty / from `readme_meta.yaml`) until they adopt the markers.

### D. `logs/readme_meta.yaml` — the irreducible prose (§2 narrative, §3 summary, §4 headlines)

Some content cannot be computed: the Status narrative, the one-paragraph model
summary, each figure's headline sentence. These are authored **once** here, keyed
by section/figure, so the generator stays a pure renderer:

```yaml
title: "Reynolds & Heeger 2009 — The Normalization Model of Attention"
status_narrative: |
  **Figures re-rendered and certified.** All 7 figure PNGs were regenerated ...
model_summary: |
  The foundational **normalization model of attention**: one divisive-normalization ...
figures:
  6:
    headline: "Feature-based attention sharpening — author 'cross' field, peak ratio 1.109"
    status_badge: "✅ FAITHFUL (det all-pass · fresh render)"
    note: |
      The 6C CONTRACT_BUG (2026-06-10) is RESOLVED via lineage rung 1 ...
```

### E. Re-persist VLM verdicts after every re-render (found by the RH dry-run)

Regenerating the RH README surfaced a real gap: the live per-figure VLM roll-up
(§2) reads the latest `figure_comparisons/figure_N_*.json`, whose newest RH
verdicts are `fail` at the **pre-fix** commit `c8ea505` (2026-06-04). The
2026-06-10 render-and-certify pass verified the figures by **direct image read but
never wrote a fresh verdict JSON** — so the hand-authored README asserts "VLM pass"
while the only persisted artifact says `fail`. The generator (correctly) refuses to
invent the pass and shows the stale `fail` + its commit.

Fix: the VLM/render-certify step must **persist a verdict JSON for every figure it
re-checks** (the schema `neuromodels.framework.test_table` already reads:
`figure_number`, `model_commit_hash`, `evaluated_at`, `verdict.passes`). Until it
does, a stale-commit verdict is the honest signal — and a reader can see the commit
mismatch. This is the cut-over blocker for migrating RH: re-run the VLM compare so
the live data matches the prose before the generated README replaces the curated one.

### F. `logs/adjudications.yaml` — documented organizer audit-overrides (never paperless)

The organizer may overturn an audit/test verdict by direct judgement that a change is small and
safe — the RH Fig-1 "→ faithful" call (flagged_count 1→0) is the canonical case. That power is
legitimate but must **never be paperless**: an audit RED can be overcome **only** by an entry in
`logs/adjudications.yaml`, recording the finding overridden, the reasoning, the change scope, and
the evidence the organizer checked **against the diff**. Schema:

```yaml
adjudications:
  - id: ADJ-001
    date: 2026-06-10
    decided_by: organizer
    verdict: "override → faithful (flagged_count 1 → 0)"
    finding: "Fig-1 R-asymmetry ≥1.10 tripwire carried as a flagged divergence"
    audit_ref: "logs/faithfulness_audit/2026-06-10-...md; SQ-010"
    change_scope: "small — test-contract correction only; model.py + calibration UNTOUCHED (vs diff)"
    reasoning: |
      The ≥1.10 tripwire was an ungrounded over-claim; an independent author-code port gives ~1.01 ...
    evidence: ["independent author-code port", "model.py unchanged vs diff", "159 pass / 0 fail"]
```

The generator renders these prominently in §2 Status (⚖️ block) and flags the count in the §1 exit
table (`Audit overrides: N`), so an override is always visible — the README stays script-generated
while the human-judgement override is on the record. This keeps the project's separate-builder/critic
discipline intact: the organizer can move, but only in writing, and only with the diff checked.
**Workflow rule:** the finalize / audit-faithfulness flow may downgrade an audit RED to a non-block
exit ONLY when a matching `adjudications.yaml` entry exists; otherwise the RED stands.

## Generator: `tools/build_model_readme.py`

One script, one model arg, seven section renderers, each **fault-tolerant** (a
missing artifact degrades that section to a stub + a stderr warning rather than
crashing — so freeform models can be migrated incrementally):

```
python3 tools/build_model_readme.py models/<name>            # write README.md
python3 tools/build_model_readme.py models/<name> --check    # CI: non-zero if stale
python3 tools/build_model_readme.py models/<name> --stdout   # preview, write nothing
```

Reuses `neuromodels.framework.test_table` for the test/VLM roll-up and shells
`tools/repro_cost.py --markdown` for §7. Wired into the full-pass finalize step
(replacing the hand-write) and into the submodule pre-commit hook, exactly like the
parent generator.

## Validation (heeger_1992 dry-run, 2026-06-15)

A subagent authored the three artifacts for `heeger_1992` purely by transcribing its existing
README, then ran the generator: **all 7 sections populated, zero stub warnings, first try.** The
extraction mapped cleanly because the README was already in the 7-section shape. Three schema
refinements it surfaced:

1. **Check-table headers.** Models that predate `@pytest.mark.tier` have check tables shaped
   *Dimension/Status/Note* rather than *Tier/Check/Result*; the `checks` fallback renders them under
   the `Tier|Check|Result` header. Acceptable, but a per-figure column-label override (or a generic
   `Check|Result`) would read more honestly for non-tiered models.
2. **Decisions ≠ issues.** READMEs with a "Queued human-decisions" / 👉 DECISION block have no
   dedicated field. Convention: fold them into `readme_meta.status_narrative` as the leading
   👉 DECISION NEEDED block (the generator renders the narrative verbatim) — keep them out of
   `issues.yaml`, which is for divergence sources.
3. **Issue categories.** Widen the guidance enum to include `DIVERGENCE` / `UNDERDETERMINATION` for
   genuine paper-underdetermination cases (the `category` field is rendered as free text, so this is
   guidance, not a code change).

## Rollout

1. Land the generator + plugin change + RH reference artifacts (this change).
2. Backfill `exit.json` for every started model (cheap regex from the current
   README) so the parent table reads it.
3. Teach finalize to write `exit.json` / `issues.yaml` / `readme_meta.yaml` and
   call the generator — migrating models from hand-authored to generated one pass
   at a time. Freeform models (`spratling`, `karklin`) convert when next touched.
