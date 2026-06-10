# Skill: Acquire Sources

## Purpose

**Phase 0 — runs before spec extraction.** Gather *all* upstream source material
for a paper into the repo, so Phase A never builds a spec on incomplete sources.
This is the step whose absence let `hermann2010` mistake a **missing-source gap**
(the Supplementary Tables / original code we never had) for a **paper
underdetermination**.

Two classes of source, treated differently:

1. **Published paper materials** — main text, Online Methods, Supplementary
   Information / Tables / Figures / Methods. These *are* the paper. Acquire
   always.
2. **Original author code** — lab page, ModelDB, OSF, GitHub, journal code
   archive. A legitimate **spec source for Phase A** (project decision), but it
   is **never** part of the paper and is **never visible to the Phase-B
   implementer**. Acquire when it exists.

The defining output is honesty about what exists vs what we have: a missing
supplement must become a **logged, known gap**, never silent.

---

## Inputs

- The model directory `models/<name>/` with at least a paper reference (DOI /
  title / authors), usually an existing `paper/paper.pdf` or
  `paper/extracted_text.md`.
- Web access (WebSearch / WebFetch).

---

## Outputs

Everything Phase-B-forbidden lives under the existing `paper/` boundary (one
forbidden root — no new rule for Phase B to violate):

```
paper/
  paper.pdf                 # main article
  online_methods.{pdf,md}   # if the venue separates them (Nature/Science)
  supplementary/            # SI: tables, figures, methods (one file each, named)
  code/                     # original author code — GITIGNORED (Phase-A spec source; Phase-B FORBIDDEN)
  SOURCES.md                # provenance manifest (REQUIRED, versioned — see below)
```

**`paper/code/` is gitignored** — original author code is not redistributed
through our history (licensing + bulk). Add `paper/code/` to the model's
`.gitignore` as part of acquisition. Its existence and source stay fully
traceable through the **versioned** `paper/SOURCES.md` (the fetch URL + manifest)
and `article_aware/spec/code_refs.yaml` (`CODE-NNN` entries with file:line), so
anyone can re-fetch and verify. This also reinforces the Phase-B boundary: a
fresh checkout has no code for an implementer to peek at.

`article_aware/spec/code_refs.yaml` is **seeded** here if code was acquired (the
actual `CODE-NNN` entries are authored later, by extract-spec, when it pulls a
value from the code — see Handoff).

---

## Process

### Step 1 — Inventory (search before fetching)

For the paper's authors and venue, check, in roughly this order:
- the **author/lab pages** (e.g. a Heeger-lab `content/software/` page, a
  Carrasco-lab page),
- **ModelDB / SenseLab**, **OSF**, **GitHub**,
- the **journal's** article page for Supplementary Information / Online Methods
  and any "Code availability" statement,
- **PMC** (open author manuscript) as a fallback for SI when the publisher
  gates it.

Record every venue checked — including dead ends — so "confirmed absent" is
distinguishable from "not looked for."

### Step 2 — Fetch what exists

- Download paper materials into `paper/` (and `paper/supplementary/`,
  `paper/online_methods.*`). Prefer the publisher/PMC canonical copy; note the
  URL and retrieval date.
- Download original code into `paper/code/`, and ensure `paper/code/` is in the
  model's `.gitignore` (it is not committed). Record the exact archive URL,
  version/commit or file date, and byte size in `SOURCES.md`. Do **not** modify it.
  **Flag released fitted results.** When the code ships **fitted parameter values**
  (per-observer / per-condition fit files) or the **simulated curves a figure plots**
  (saved model outputs), call that out explicitly in the `SOURCES.md` "Obtained" line —
  it is the difference between a figure that must be stubbed `ILLUSTRATIVE-NOT-REPRODUCED`
  and one that extract-spec can reproduce genuinely from author ground truth (`CODE-NNN`,
  no re-fit). See extract-spec Step 3b.
- If something **exists but cannot be fetched** (paywall, JS wall, dead link),
  do not fake it — record it as a known gap (Step 3) with the URL you found.

### Step 3 — Write `paper/SOURCES.md` (the manifest)

Four sections, every artifact accounted for:

```markdown
# Sources — <Author Year>, "<title>", <venue> · acquired <date>

## Obtained
- main article — paper/paper.pdf — <url> — <date> — <bytes>
- supplementary — paper/supplementary/<file> — <url> — <date> — contains: <tables/figs>
- original code — paper/code/ — <archive url> — <version/date> — <one-line of what it covers>

## Exists but NOT obtained (KNOWN GAP)
- <artifact> — <url> — reason: <paywall / JS wall / 403> — impact: <what the spec may be missing>

## Confirmed absent (searched, none found)
- original code — checked: <lab page, ModelDB, OSF, GitHub> — none found

## Searched
- <venues / queries tried>
```

The "Exists but NOT obtained" section is the one that matters: extract-spec and
the faithfulness auditor read it to know the spec is provisional pending that
source.

### Step 4 — Seed `code_refs.yaml` (only if code was acquired)

Create `article_aware/spec/code_refs.yaml` with a header pointing at
`paper/code/`. Leave it otherwise empty — entries are authored by extract-spec.
Format mirrors `citations.yaml`:

```yaml
# Original-author code provenance for <Author Year>.
# Code lives at paper/code/ (Phase-A spec source; Phase-B FORBIDDEN).
# A value taken from the code is tagged `source: CODE-NNN` in calibration.yaml
# and `Code: CODE-NNN` in the implementing function's docstring.
- id: CODE-001
  source: "paper/code/<file>.m:<line> (fn <name>)"          # file:line in the acquired archive
  version: "<archive url> @ <commit-or-date>"
  text: >-
    <verbatim code snippet the value/behavior comes from>
  notes: <what it specifies, and whether the paper is silent on it>
```

---

## Handoff to Phase A (extract-spec)

extract-spec now consumes the **complete** `paper/` plus `paper/SOURCES.md`, and:

- Treats Online Methods + Supplementary as paper text — cite with `C-NNN`.
- May read `paper/code/` and, when it pulls a value the paper does not specify,
  add a `CODE-NNN` entry and tag the value `source: CODE-NNN` (or
  `source: [C-NNN, CODE-NNN]` when the paper is qualitative and the code is
  numeric).
- Knows that anything in the "Exists but NOT obtained" gap section is a real
  underspecification to flag, not something to invent around.

A value that ends up `CODE-NNN` with **no** `C-NNN` is **code-alone** — the
paper is insufficient there. That is surfaced, per model, by
`neuromodels provenance --model-dir models/<name>` and is a faithfulness metric
in its own right. `check_citations` enforces that every `CODE-NNN` tag resolves
to a `code_refs.yaml` entry, exactly like citations and assumptions.

---

## Boundaries

- **`paper/code/` is Phase-A only.** The Phase-B implementer reads *only*
  `article_aware/`; it must never see the original code, or the reproduction
  stops being independent. The existing "NEVER read `paper/` in Phase B" rule
  already covers `paper/code/` — keep code under `paper/`, do not surface it
  elsewhere.
- Do not edit acquired code or SI. They are immutable upstream artifacts.
- On a `from="fix"` pass, sources are already present — skip this skill.
