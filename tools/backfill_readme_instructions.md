# Backfill instructions — regenerate one model's README from artifacts

You are backfilling ONE model so its `README.md` becomes generated output of
`tools/build_model_readme.py` instead of hand-written prose. Repo root:
`/Users/estevaouyra/dev/model_agent`. You will be told the target `models/<name>`.

The generator renders 7 sections (Current exit · Status · Model · Reproduced figures ·
Potential sources · Changelog · Reproduction cost) from artifacts and **never invents prose**.
Most sections derive from artifacts that already exist (`logs/test_runs.jsonl`,
`logs/figure_comparisons/`, `logs/changelog.md`, `article_aware/spec/*.yaml`, `repro_cost.py`).
Three artifacts hold the irreducible prose and you must author them by faithfully transcribing
the model's CURRENT hand-written README:

- `logs/exit.json`
- `logs/readme_meta.yaml`
- `logs/issues.yaml`

## References (read first)

- Schemas + design: `proposals/per-model-readme-autogen-2026-06-15.md`
- **Worked example — copy its shape exactly:** `models/reynolds_heeger_2009/logs/exit.json`,
  `readme_meta.yaml`, `issues.yaml`
- Authoritative field behaviour: `tools/build_model_readme.py` (read the section renderers)

## Steps

1. **Read** `models/<name>/README.md` (your PRIMARY prose source) and skim its artifacts:
   `logs/changelog.md`, the audit dirs under `logs/`, `article_aware/spec/model_spec.yaml` +
   `citations.yaml`, any `article_aware/figures/figure_*_layout.yaml`, and which figures exist on
   disk (`figures_reproduced/*.png`, `article_aware/figures/figure_*.{png,jpg}`).

2. **Author the three artifacts** into `models/<name>/logs/`, transcribing the existing README:
   - **exit.json** — extract the exit JSON embedded in the current README (if the README is
     freeform with no exit block, synthesise honestly from its state: `overall` ∈
     reproduced|faithful|partial|blocked, `trajectory`, `flagged_count`, `blocked`). Add `audit`
     (hardened|vlm|self-reported — default `self-reported` unless the README evidences an
     independent audit), `updated_at` (today), `figures_in_scope`, `figures_rerendered`, `headline`.
   - **readme_meta.yaml** — `title`, `status_narrative` (the current README's status/current-state
     prose; if the README leads with a 👉 DECISION NEEDED / 👉 UNBLOCKER block, put it at the TOP of
     this field), `model_summary` (the Model section), `model_equation_refs` (governing-equation
     citation IDs from citations.yaml), and `figures: {N: {headline, status_badge, note, checks:
     [{tier, check, result}]}}` for every in-scope figure (transcribe the per-figure headings,
     badges, notes, and check tables). The `checks` list is the fallback table; fine for models
     without `@pytest.mark.tier`.
   - **issues.yaml** — `preamble` + `issues: [{id, category, status, title, body, sources}]` from the
     README's "Potential sources" section. If the model has NO open divergences, still write a
     `preamble` stating the model is faithful plus a short resolved-issues list — **never an empty
     file** (no empty sections). `category` is free text (FIGURE|CONTRACT|MODEL|GEOMETRY|DECISION|
     MAGNITUDE|DIVERGENCE).

   - **`logs/adjudications.yaml`** *(ONLY if the current README evidences an organizer overriding an
     audit/test failure on the judgement that the change was small/safe — e.g. a "→ faithful" call
     that overturned a flagged tripwire)*. Record `adjudications: [{id, date, decided_by, verdict,
     finding, audit_ref, change_scope, reasoning, evidence}]`. Most models have NO override — skip the
     file entirely if so. See `models/reynolds_heeger_2009/logs/adjudications.yaml` for the shape.

3. **Generate + iterate.** Run `python3 tools/build_model_readme.py models/<name>` (it overwrites
   `README.md`). It prints a warning per stubbed section on stderr. If any IN-SCOPE section came out
   a stub/empty, FIX THE ARTIFACT and re-run until
   `python3 tools/build_model_readme.py models/<name> --check` is clean and no in-scope section is a
   `_No ..._` placeholder. **Never hand-edit `README.md`.** (A genuinely-absent section — e.g. no
   recoverable cost transcripts, or no figure_comparisons → VLM column `—` — is fine; only fix
   sections whose source artifact you are responsible for.)

## Commit (in the SUBMODULE only — NEVER the parent)

Work only inside `models/<name>` (its own git repo). **Do not touch the parent `model_agent` repo.**

1. Stage ONLY these paths (never `git add -A` — do not sweep unrelated files):
   `README.md logs/exit.json logs/readme_meta.yaml logs/issues.yaml`, plus `logs/adjudications.yaml`
   if you wrote one, and `logs/changelog.md` if you appended to it.
2. Determine the branch:
   - If the submodule is **on `main`**: commit on `main`.
   - If it is on a **feature branch** or has **unrelated uncommitted changes** (anything other than
     the files you touched): do NOT switch branches and do NOT clobber that work — commit your staged
     files on the **current branch** and note in your report that main was not directly updated and why.
3. Commit message: `readme: auto-generate from artifacts (build_model_readme.py)`. Do NOT push.
4. If anything looks risky (detached HEAD, merge in progress, the README's claims contradict the
   artifacts in a way you cannot reconcile), STOP and report instead of committing.

## Report back (concise)

`model | committed-branch | short-sha (or "not committed: <why>") | sections populated (7/7 or which
are stubs) | remaining stderr warnings | 1-line extraction-quality note (did the README map cleanly?
anything that didn't fit the schema?)`
