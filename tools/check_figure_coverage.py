#!/usr/bin/env python3
"""Coverage gate — assert every target figure carries its committed three views + a fresh verdict.

This is the keystone gate the full-pass workflow was missing: every other check judges the
*content* of artifacts that happen to exist, so a run could silently stop producing the original
crop / the implemented render / the digitization, and still exit `faithful`. This check judges
EXISTENCE, of COMMITTED files (the README can only show committed files), so a required step that
silently didn't run becomes a hard BLOCK instead of a footnote.

Per target figure N, three views must be committed:
  - original    : article_aware/figures/figure_N.{png,jpg,jpeg}      (the paper crop)
  - implemented : figures_reproduced/figure_N.{png,jpg}              (the model render, committed)
  - digitized   : article_aware/figures/figure_N/ with >=1 *digiti*/*overlay* file
                  OR a committed article_aware/figures/figure_N.nodigitize marker
                  (for a genuinely non-digitizable / schematic panel — honest, not skipped)
And the faithfulness audit must have run this model at least once:
  - verdict     : >=1 logs/faithfulness_audit/* file committed

Render-only panels (no paper counterpart): some target "figures" are MODEL-GENERATED
explanatory panels with NO figure in the paper at all — e.g. a `mechanism`/`dynamics`
dissociation panel the model produces to illustrate its own behaviour. These can never
carry an `original` (paper crop) or `digitized` (overlay) view, because there is nothing
in the paper to crop or digitize against. A committed
  - article_aware/figures/figure_N.nopaper   marker (with a one-line reason inside)
declares exactly this and EXEMPTS the original + digitized views for figure N. The
`implemented` render is STILL required — a render-only panel must show its committed
render, so .nopaper waives the (nonexistent) paper comparison, never the model output
itself. Use .nopaper ONLY for a panel with no paper source; a real paper figure that is
merely hard to obtain (paywalled, lost) stays blocked and routes to a human — never mask
it with .nopaper.

Committed status is read with `git ls-files` inside the submodule.

Usage:
    python3 tools/check_figure_coverage.py models/<name> --figures 1,2,3   # JSON verdict, exit 1 if incomplete
"""
import sys, json, subprocess, os, re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked(model_dir):
    out = subprocess.run(["git", "-C", model_dir, "ls-files"],
                         capture_output=True, text=True)
    return out.stdout.splitlines()


def classify_figures(files, figures):
    """Pure classification: given the committed file paths and the target figure list,
    return (rows, faith_ran). Free of any git/IO so it is unit-testable."""
    files = set(files)

    def has(pattern):
        rx = re.compile(pattern)
        return any(rx.search(f) for f in files)

    faith_ran = has(r"^logs/faithfulness_audit/.+")
    rows = []
    for n in figures:
        n = str(n)
        # A .nopaper marker = a model-generated panel with NO paper counterpart: it exempts
        # the paper-crop + digitization views (which cannot exist), but NOT the render.
        nopaper = has(rf"^article_aware/figures/figure_{re.escape(n)}\.nopaper$")
        original = has(rf"^article_aware/figures/figure_{re.escape(n)}\.(png|jpg|jpeg)$") or nopaper
        implemented = has(rf"^figures_reproduced/figure_{re.escape(n)}\.(png|jpg|jpeg)$")
        digitized = (has(rf"^article_aware/figures/figure_{re.escape(n)}/.*(digiti|overlay).*")
                     or has(rf"^article_aware/figures/figure_{re.escape(n)}\.nodigitize$")
                     or nopaper)
        missing = [k for k, v in (("original", original), ("implemented", implemented),
                                  ("digitized", digitized)) if not v]
        rows.append({"figure": n, "original": original, "implemented": implemented,
                     "digitized": digitized, "nopaper": nopaper,
                     "complete": not missing, "missing": missing})
    return rows, faith_ran


def check(model, figures):
    model_dir = os.path.join(REPO_ROOT, model) if not os.path.isabs(model) else model
    rows, faith_ran = classify_figures(tracked(model_dir), figures)
    all_complete = faith_ran and all(r["complete"] for r in rows)
    return {"model": model, "faithfulness_audit_ran": faith_ran,
            "figures": rows, "all_complete": all_complete,
            "summary": _summary(rows, faith_ran)}


def _summary(rows, faith_ran):
    bad = [f"figure {r['figure']} missing {'+'.join(r['missing'])}" for r in rows if not r["complete"]]
    if not faith_ran:
        bad.insert(0, "no committed faithfulness audit")
    return "coverage complete" if not bad else "INCOMPLETE: " + "; ".join(bad)


def main():
    argv = sys.argv[1:]
    figures = []
    if "--figures" in argv:
        i = argv.index("--figures")
        figures = [x for x in argv[i + 1].split(",") if x.strip()]
        del argv[i:i + 2]
    if not argv:
        print("usage: check_figure_coverage.py models/<name> --figures 1,2,3", file=sys.stderr)
        sys.exit(2)
    model = argv[0]
    if not figures:
        # An empty figure list would report "coverage complete" vacuously — a
        # silent false green. Require an explicit, non-empty --figures.
        print("error: --figures is required and must be non-empty (e.g. --figures 1,2,3); "
              "an empty list reports a vacuous 'complete'.", file=sys.stderr)
        sys.exit(2)
    result = check(model, figures)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_complete"] else 1)


if __name__ == "__main__":
    main()
