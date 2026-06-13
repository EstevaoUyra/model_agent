# Candidate PDF status — 2026-06-13

After a bulk drop into the gitignored `paper_candidates/`, reconciled against the
200-paper index (`corpus-candidates-200.json`, canonical name = `NNN_<key>.pdf` for
top-100, `<key>.pdf` otherwise) and content-verified (author surname / title vs the
extracted text of every PDF).

**190 / 200 candidates have a verified-correct PDF on disk.** `pdf_saved` in the JSON
and the `saved` column in `corpus-candidates-200.md` / `corpus-top100-ranking.md` are
regenerated from disk, so they are the live index — re-run `build_ranking.py` after any
new drop.

## Still needed (10)

### Wrong content — re-download (2)
The dropped file's name did not match its contents; quarantined to
`paper_candidates/_mismatched/` (gitignored), NOT counted as saved:
- **movshon_thompson_tolhurst_1978** — the file was actually a *laryngeal-receptors*
  paper (J. Physiol. 277:409). Need: Movshon, Thompson & Tolhurst 1978, "Spatial
  summation in the receptive fields of simple cells in the cat's striate cortex"
  (J. Physiol. 283:53–77).
- **zemel_1998** — the file was actually van Vreeswijk & Sompolinsky 1998, "Chaotic
  balanced state in a model of cortical circuits". Need: Zemel, Dayan & Pouget 1998,
  "Probabilistic interpretation of population codes" (Neural Comput. 10:403–430).
  (The quarantined vV&S-1998 PDF is kept in `_mismatched/` in case it is wanted later.)

### Never dropped (8)
- **verhoef_maunsell_2017** · gold OA — fetchable (eLife)
- **doostani_2023** · gold OA — fetchable (eLife)
- barlow_1961 · closed (book chapter, *Sensory Communication*)
- reichardt_1961 · closed
- hassenstein_reichardt_1956 · closed (German original)
- knill_richards_1996 · closed (book, *Perception as Bayesian Inference*)
- tsodyks_sejnowski_1995 · closed
- houk_adams_barto_1995 · closed (book chapter)

## Notes
- `011_wong_wang_2006`: two copies were dropped — kept the full published J. Neurosci.
  PDF (1.58 MB) as the canonical name; removed the 300 KB institutional-repository cover
  version.
- All other 190 PDFs verified: filename author/year matches the paper's own first pages
  (a few old papers — e.g. `olshausen_field_1996`, `okeefe_dostrovsky_1971` — are scanned
  image PDFs with no extractable text; spot-confirmed visually).
