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


def check(model, figures):
    model_dir = os.path.join(REPO_ROOT, model) if not os.path.isabs(model) else model
    files = set(tracked(model_dir))

    def has(pattern):
        rx = re.compile(pattern)
        return any(rx.search(f) for f in files)

    faith_ran = has(r"^logs/faithfulness_audit/.+")
    rows = []
    for n in figures:
        n = str(n)
        original = has(rf"^article_aware/figures/figure_{re.escape(n)}\.(png|jpg|jpeg)$")
        implemented = has(rf"^figures_reproduced/figure_{re.escape(n)}\.(png|jpg|jpeg)$")
        digitized = (has(rf"^article_aware/figures/figure_{re.escape(n)}/.*(digiti|overlay).*")
                     or has(rf"^article_aware/figures/figure_{re.escape(n)}\.nodigitize$"))
        missing = [k for k, v in (("original", original), ("implemented", implemented),
                                  ("digitized", digitized)) if not v]
        rows.append({"figure": n, "original": original, "implemented": implemented,
                     "digitized": digitized, "complete": not missing, "missing": missing})

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
    result = check(model, figures)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_complete"] else 1)


if __name__ == "__main__":
    main()
