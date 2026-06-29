# D2 — The generated README kept being re-fixed because the fix belonged at the source

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Process-maintenance · process/delivery |
> | Behavior | generated-artifact quality drift — a deliverable rendered from a single template + artifacts repeatedly produced wrong/unreadable output and was corrected in a run of patches, because the defect lived in the source (skill prompt / path convention), not the output |
> | Symptom | per-model README figure tables had wrong/missing views and drifting paths, and the prose was opaque insider audit shorthand — across a cluster of PRs (#61–#65, #70, #72) |
> | Agent role | README-gen / finalize (the `update-state` agent authors `exit.json` / `readme_meta.yaml` / `issues.yaml`, then `tools/build_model_readme.py` renders) |
> | Trigger | the README is auto-generated for every model from shared artifacts + one renderer; whenever a path convention drifts or the authoring prompt under-specifies, the defect appears in *every* model's README at once |
> | Cause (evidence) | (a) figure-artifact paths not pinned → corpus-wide README drift; (b) the authoring agent wrote for an auditor, not a scientist → jargon — both *intervention-tracked* (fixed at source, PR #64 and PR #72) |
> | Detector | human (user feedback 2026-06-27: the generated READMEs are unreadable, "for ALL models"); figure-path drift caught in self/orchestrator review |
> | Lever(s) | code (the renderer) + doc/skill (pin canonical paths; "write for a scientist" rule) + structural (single generator = single fix point) |
> | Flags | ⟳ recurred (multiple corrective rounds; readability backfill left open) |
> | Status | mitigated (fixed at source); existing models get it on next finalize |

## The behaviour

Each model's `README.md` is **generated**, never hand-written: `tools/build_model_readme.py`
renders fixed sections from three authored artifacts (`exit.json`, `readme_meta.yaml`,
`issues.yaml`); hand-editing a generated README is explicitly forbidden. Over roughly two weeks the
generated READMEs were corrected in a **run of patches** — first the figure tables (wrong/missing
views, then path drift), then the prose readability — rather than in a single change. The repeated
re-fix is itself the signal: it shows the locus of the defect was the *source* (the renderer, the
artifact path conventions, the authoring prompt), and surface patches kept treating symptoms until
the fix was moved to the source.

Two distinct defects rode this thread:

1. **Figure-table / path drift.** The README's three-view figure tables (paper crop · digitized ·
   implemented render) discovered figures by convention; when the artifact path conventions weren't
   pinned, the tables drifted (missing columns, wrong discovery). Patched across #62–#65, then
   fixed at source by **pinning the canonical figure-artifact paths in the skills** (PR #64,
   `f1fe951` — literally "fix README drift at the source").
2. **Insider-jargon prose.** The generated prose was full of audit shorthand — `xfail-tripwire`,
   `GENUINE_DIVERGENCE`, bare IDs (`F3`, `A-009`), `coverage gate`, `toward_paper`,
   `.nodigitize` — readable only to someone who had read the process docs. To the working
   scientist who is the actual reader, audit shorthand "verifies nothing." Fixed at source in
   PR #72 (a "Write for a scientist" rule in `skills/update-state`, reinforced in the
   `full-pass.js` `update-state` prompt, plus enum-value humanization in the renderer, e.g.
   `toward_paper` → "moving toward the paper (`toward_paper`)").

## Why it recurred (the corpus-wide fan-out property)

This is the structural fact that makes D2 a thread and not a one-off bug: because every README is
rendered from **one** template + shared artifacts, **a defect in the source is a defect in every
model's README simultaneously**, and conversely a fix at the source repairs them all at once. So
the drift fans out across the corpus, and the temptation each round is to patch the visible output;
the durable move is to fix the *generator or the skill prompt that authors the artifacts*. The
PR chain shows exactly this progression: several output-shaped corrective rounds (#62 generator +
backfill, #63 3-view tables/broader discovery, #65 figure remediation) before the fixes that
actually closed the classes were source-level (#64 pin paths, #72 authoring rule). *Cause is
intervention-tracked* — the source fixes are what stopped each class.

## The Detector

The readability defect was caught by **human feedback** (the user, 2026-06-27), not by any gate —
there is no automated check that generated prose is plain-language. The figure-path drift was
caught in self/orchestrator review of the rendered tables. So both faces of D2 were human-detected;
nothing in the pipeline asserts deliverable readability or table-completeness, which is the same
"no coverage-style gate for the *output's quality*" gap that D1/D3 show for the process.

## How it responded to intervention

- **PR #61 (`c395d99`):** auto-generated README roadmap + pre-commit refresh — the generated-README
  regime begins.
- **PR #62 (`61724fb`):** per-model README generator + backfill all submodules.
- **PR #63 (`a90d76e`):** 3-view figure tables, broader figure discovery, open-issues-only §5.
- **PR #64 (`0ca672e`):** **pin canonical figure-artifact paths in skills — fix the drift at the
  source.**
- **PR #65 (`2c0194a`):** figure remediation.
- **PR #70 (`d9f2601`):** reconcile + surface off-corpus started models.
- **PR #72 (`e603c23`):** **"Write for a scientist" readability rule + enum humanization — fix the
  jargon at the source.**

**Which lever held.** The fix-at-source levers (skill path-pinning #64; authoring rule + renderer
humanization #72) are the durable ones — they convert a recurring per-README patch into a single
generator/prompt change. The per-output patches did not hold (each was followed by another round).
A caveat on completeness: PR #72's readability fix is **forward-looking** — existing models only
pick it up on their next finalize; a full backfill (re-finalize every model) was left as an open
option. So the *source* is fixed but the *already-shipped corpus* is not uniformly remediated.

## Confidence & threats to validity

High that the repeated re-fixes happened — the PR chain is the artifact, and the memory notes both
the figure-path and readability fixes with their source-level PRs. Threats: (a) **anecdote ≠ rate**
— "repeatedly re-fixed" means a *visible cluster of ~5–7 PRs over ~two weeks*, not a measured
regression rate; I did not count how many model READMEs were actually wrong per round; (b) the two
defects (path drift, jargon) are bundled into one thread because they share the
*generated-from-a-single-source* mechanism, but they were detected and fixed independently — a
splitter could file them as D2a/D2b; (c) the "forward-looking, not backfilled" status is from
the 2026-06-27 memory and should be re-checked against whether a backfill later ran.

## Scope / generality

Descriptive. The mechanism is generic to any "single generator, many rendered deliverables"
setup: defects and fixes both fan out, and the lasting fix is always at the source, never the
rendered output. Setup-specific in the particular artifacts (per-model neuroscience-reproduction
READMEs) and the particular reader (a domain scientist).

## Links
- `shared-root → D1, D3` — same family: a quality property (here, deliverable correctness/
  readability) with no gate asserting it, so defects accumulate until a human notices.
- `connects-to → E4` (sycophancy/flattery in output) and the `dont-flatter-be-plain` rule — both
  are "human-facing output quality" controls; D2's readability fix generalizes that principle to
  any human-facing artifact.

## Deeper-dig hook
Count, per corrective round, how many model READMEs actually carried the defect (denominator =
models with a generated README at that commit) to convert the PR-cluster anecdote into a rate.
Also check whether a readability **backfill** (re-finalize all models) ever ran after PR #72.
Data: `git log --oneline tools/build_model_readme.py skills/update-state`; the per-model READMEs
at each tagged commit.

## Status
mitigated — both defect classes fixed at source. `open` sub-item: full readability backfill of
already-shipped model READMEs.

## Refs
- Memory: `readable-human-facing-output`, `per-model-readme-autogen`.
- PRs: #61 (`c395d99`), #62 (`61724fb`), #63 (`a90d76e`), #64 (`0ca672e`), #65 (`2c0194a`),
  #70 (`d9f2601`), #72 (`e603c23`); source fixes #64, #72.
- Proposal: `proposals/per-model-readme-autogen-2026-06-15.md` (design + schemas).

---

### Evidence layer (for verification, not reading)
- **Grounding source:** git PR chain + distilled memory + the autogen design proposal. **No quote
  ledger produced** — no verbatim *workflow-agent* corpus quotes were promoted; the thread is a
  delivery/tooling thread whose Detector is human feedback (captured in memory) and whose evidence
  is the commit history (a stronger, citable artifact than session narration).
- **Corpus note `[to-verify-on-deeper-dig]`:** `build_model_readme` appears ≈2.9K times across
  orchestrator-session transcripts in `evidence/corpus-snapshot/`, but those are human-led
  orchestration logs (the renderer being invoked), not agent-behavior narration; not promoted.
