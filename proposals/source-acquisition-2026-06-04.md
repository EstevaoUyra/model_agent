# Proposal: Phase-0 Source Acquisition (before spec extraction)

**Date:** 2026-06-04 · **Status:** PROPOSED · **Decision owner:** user (policy below already chosen)

## Motivation
hermann2010 blocked (NF1 saturation) partly because the repo never contained the paper's
**Online Methods + Supplementary Tables 1 & 2** — the natural home for the normalization
parameters we're stuck on. Our `paper/` held only the 8-page printed article. The spec-extractor
therefore built an incomplete contract (saturation deferred to R&H 2009) and we mistook a
**missing-source gap** for a **paper-underdetermination**. RH2009 likewise has only
`extracted_text.md`, no original PDF. No model in the repo has any original author code.

We should never silently build a spec on incomplete sources. Add a Phase-0 acquisition step that
runs **before** Phase A writes any spec.

## Policy (decided)
- **Published paper materials** (main text, Online Methods, Supplementary Information / Tables /
  Figures / Methods) are **part of the paper**. Acquire always. Phase A reads them; **Phase B is
  forbidden them** (unchanged boundary).
- **Original author code** (lab page, ModelDB, OSF, GitHub, journal code) is **acquired and is a
  legitimate spec source for Phase A** (user decision, 2026-06-04). It is **never visible to the
  Phase-B implementer** — that boundary is non-negotiable, else the reproduction stops being
  independent.
- **Code provenance is first-class in the citation system** (not a soft string). Today there are two
  resolved ledgers — `citations.yaml` (`C-NNN`) and `assumptions.yaml` (`A-NNN`) — and
  `check_citations.py` fails any tag that doesn't resolve. Add a **third ledger**
  `article_aware/spec/code_refs.yaml` with `CODE-NNN` entries (id, source = repo/url + commit +
  retrieval date, location = file:line/function, text = code snippet, notes = what it specifies),
  mirroring `citations.yaml`. New docstring tag `Code: CODE-NNN`; `source:` in `calibration.yaml`
  may now be a **list** (e.g. `source: [C-012, CODE-003]`). Extend `check_citations.py` with
  `CODE_ID = \bCODE-\d{3,}\b` resolving against `code_refs.yaml` (same presence+resolution contract).

### Provenance taxonomy — the point of the whole thing
Every spec value / behavior falls into exactly one bucket, queryable from its tags:

| Provenance | Tags | Ledger | Meaning |
|---|---|---|---|
| Paper-specified | `C-NNN` only | `citations.yaml` | paper is self-sufficient here |
| Paper + code | `C-NNN` **and** `CODE-NNN` | + `code_refs.yaml` | paper qualitative, code supplies the number |
| **Code-alone** | `CODE-NNN` only (**no `C-NNN`**) | `code_refs.yaml` | **paper insufficient — exists ONLY because we read the authors' code** |
| **Lineage** | `LINEAGE-NNN` | `lineage_refs.yaml` | **inherited from another genealogy paper** — entry names ancestor `model:` + `ref:`, traced through to the ancestor's own ground (paper/code/assumption) |
| Assumption | `A-NNN` | `assumptions.yaml` | neither paper, code, nor ancestor; we chose it |

The **lineage** class makes cross-paper inheritance traceable instead of buried
in an `A-NNN` note. `check_citations` validates the cross-model link (the
ancestor model exists and the `ref` resolves there); `neuromodels provenance`
follows it through to the ancestor's ultimate ground, so you can ask of any
value: *paper here? code here? inherited — and grounded how in the ancestor?*

The **code-alone** set is the deliverable: it recovers the underdetermination finding that pure
"code as spec source" would otherwise bury — now backed by ground-truth code instead of left
unresolved. A small report (`neuromodels provenance` / a section in the model README + faithfulness
report) buckets all values and surfaces the code-alone list explicitly: *"N parameters in this
reproduction are specified by the authors' code alone and are absent from the published paper."*
That number is a faithfulness metric in its own right.

## Directory layout
Everything Phase-B-forbidden stays under the existing `paper/` root (one forbidden boundary, already
enforced in AGENTS.md — no new rule surface for Phase B to violate):

```
paper/
  paper.pdf                 # main article
  online_methods.{pdf,md}   # if separate (Nature/Science online methods)
  supplementary/            # SI tables, figures, methods
  code/                     # original author code (Phase-A spec source; Phase-B forbidden)
  SOURCES.md                # provenance manifest (see below)
article_aware/              # Phase B's ONLY allowed input (unchanged)
```

`paper/SOURCES.md` — the provenance manifest, written by the acquisition agent:
- **Searched:** lab pages, ModelDB, OSF, GitHub, journal SI, the venues checked.
- **Exists & obtained:** each artifact with URL + retrieval date + sha/size.
- **Exists but NOT obtained:** paywalled/dead-link items — a **known, logged gap** the extractor and
  auditor must see (so a missing SI is never silent again).
- **Confirmed absent:** e.g. "no original code found after checking N venues."

## Mechanism: a new `acquire-sources` skill, run as Phase 0 in full-pass
In `.claude/workflows/full-pass.js`, before `phase('Extract')`:

```
phase('Acquire')   // Phase 0 — only on a fresh (from="extract") pass
const sources = await agent(`${SK('acquire-sources')} Inventory + fetch all published materials and
  original code for ${MODEL} into paper/; write paper/SOURCES.md.`, { phase: 'Acquire', model: OPUS,
  schema: SOURCES_VERDICT })   // {obtained:[], missing:[], code_found:bool}
```

The spec-extractor (⑤ unchanged) then consumes the **complete** `paper/` + reads `SOURCES.md` so it
knows what is genuinely missing vs genuinely underspecified — the distinction we just conflated.

- Gate: if SI / Online Methods **exist but couldn't be obtained**, flag a provenance gap on the
  exit report (not a hard block — we can still proceed, but the underdetermination findings are then
  provisional pending the missing source).
- `from="fix"` passes skip Phase 0 (sources already present).

## Doc changes
- **AGENTS.md / WORKFLOW.md:** add Phase 0; clarify `paper/code/` is a Phase-A spec source and
  Phase-B-forbidden; add the `code_sourced` ledger kind to the citation/assumption section.
- **STATUS.md:** record the new skill + manifest as built once wired.

## Immediate payoff (independent of wiring)
Run `acquire-sources` (or fold the in-flight web digger's results) on **hermann2010 now** to obtain
the Online Methods + Supplementary Tables 1 & 2 (+ code if it exists). If Table 1/2 or the code pins
the normalization gain, **Q1 unblocks as an extraction gap, not a human judgment call** — and the
`proposals/saturation-spec-review-2026-06-04.md` Q1 recommendation is rewritten accordingly.
```
```
