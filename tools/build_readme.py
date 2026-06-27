#!/usr/bin/env python3
"""Regenerate the root README.md: a ranked reproduction roadmap joined to live submodule state.

One table, one row per paper, sorted by the SAME composite score the corpus ranking uses
(`proposals/corpus-ranking/build_ranking.py`). Each row carries two kinds of information:

  - what the paper IS  — from the corpus data (rank, score, cluster, citations, access, code link)
  - where its reproduction STANDS — from the submodule's own README, if a submodule exists

Rows shown: the top-100 by score PLUS every paper we have actually started (a `models/<dir>`
submodule), even if it ranks below 100. Everything is interleaved by score in one table; the
`State` column distinguishes a reproduced/partial/blocked submodule from a `not started` backlog
entry.

Data sources
------------
- Per-paper facts + score: reused verbatim from `build_ranking.py`. We execute only the
  DATA + scoring half of that file (everything before its `# ---- write` section) so we get its
  canonical `data`/`score`/`CLUSTERS` WITHOUT triggering its four file writes. This keeps a single
  source of truth for the corpus and its scoring — edit the paper list there, not here.
- Live state: the authoritative exit-JSON line near the top of each `models/<dir>/README.md`
  (`{"overall": ..., "trajectory": ..., "flagged_count": ..., "blocked": [...]}`), plus a count of
  committed `figures_reproduced/*.png`.

Dir <-> corpus key
------------------
The submodule directory name usually equals the corpus `key`, with four historical exceptions
(see ALIAS). `flash_hogan_1985-fig11-wt` is a git worktree, not an article, and is skipped.

The Audit column
----------------
`audit` is a PROCESS fact (was this independently/hardened audited, VLM-only checked, or merely
self-reported by the builder?) — `overall:"faithful"` is the builder's own claim, NOT a
certification. It is read from an `"audit"` key in the submodule exit JSON so the submodule README
stays the single source of truth. That key is NOT YET emitted by the full-pass finalizer, so today
it falls back to `self-reported` for every started model (the honest default: "implemented; not
independently audited"). Missing-audit submodules are listed on stderr so the field can be
backfilled into each exit JSON. Allowed values: `hardened` | `vlm` | `self-reported`.

Usage:  python3 tools/build_readme.py [--check]
        --check  exit non-zero if README.md would change (for CI / pre-commit), write nothing.
"""
import json
import os
import re
import glob
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_RANKING = os.path.join(ROOT, "proposals", "corpus-ranking", "build_ranking.py")
README = os.path.join(ROOT, "README.md")

BEGIN = "<!-- BEGIN AUTOGEN: reproduction-table (tools/build_readme.py) -->"
END = "<!-- END AUTOGEN: reproduction-table -->"

# submodule dir -> corpus key, for the dirs whose name differs from the key
ALIAS = {
    "cagly2012": "coen_cagli_2012",
    "carrasco2021": "li_pan_carrasco_2021",
    "hermann2010": "herrmann_2010",
    "hara_gardner_2016": "schwedhelm_2016",  # known misattribution (same DOI); see PAPERS.md
}

AUDIT_LABELS = {"hardened": "hardened", "vlm": "VLM", "self-reported": "self-reported"}


def load_corpus():
    """Return (data, score_fn-less list with d['score'] set, CLUSTERS) from build_ranking.py
    without running its file writes."""
    src = open(BUILD_RANKING, encoding="utf-8").read()
    src = src.split("# ---- write the 200 landscape ----")[0]
    ns = {"__name__": "_norun"}
    exec(compile(src, BUILD_RANKING, "exec"), ns)  # noqa: S102 - trusted in-repo file
    return ns["data"], ns["CLUSTERS"]


def submodule_dirs():
    models = os.path.join(ROOT, "models")
    return [
        d for d in os.listdir(models)
        if os.path.isdir(os.path.join(models, d)) and not d.endswith("-wt")
    ]


def exit_state(mdir):
    """Parse the exit JSON from a submodule README. Returns a dict (possibly partial)."""
    path = os.path.join(ROOT, "models", mdir, "README.md")
    if not os.path.exists(path):
        return {}
    text = open(path, encoding="utf-8", errors="ignore").read()
    # Prefer a clean JSON object that contains "overall".
    for m in re.finditer(r'\{[^{}]*?"overall"[^{}]*?\}', text):
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
    # Fallback: pull individual fields out of a malformed/loose block.
    out = {}
    for key, pat in (
        ("overall", r'"overall"\s*:\s*"?([A-Za-z_]+)'),
        ("trajectory", r'"trajectory"\s*:\s*"?([A-Za-z_/]+)'),
        ("audit", r'"audit"\s*:\s*"?([A-Za-z-]+)'),
    ):
        mm = re.search(pat, text)
        if mm:
            out[key] = mm.group(1)
    mm = re.search(r'"flagged_count"\s*:\s*(\d+)', text)
    if mm:
        out["flagged_count"] = int(mm.group(1))
    return out


def figs_count(mdir):
    return len(glob.glob(os.path.join(ROOT, "models", mdir, "figures_reproduced", "*.png")))


def short_traj(t):
    if not t or t in ("n/a", "—"):
        return "—"
    return {"toward_paper": "toward", "away_from_paper": "away"}.get(t, t)


def build_rows():
    data, clusters = load_corpus()
    dirs = submodule_dirs()
    key2dir = {ALIAS.get(d, d): d for d in dirs}

    warnings = []
    rows = []
    matched_dirs = set()
    for d in data:
        key = d["key"]
        mdir = key2dir.get(key)
        if mdir:
            matched_dirs.add(mdir)
        oa = "closed" if d["oa"].lower() == "closed" else d["oa"]
        row = {
            "score": d["score"],
            "label": d["label"],
            "cluster": clusters[d["cluster"]],
            "cites": d["cites"],
            "oa": oa,
            "link": d["link"],
            "code": d["code"],
            "started": mdir is not None,
        }
        if mdir:
            e = exit_state(mdir)
            if not e.get("overall"):
                warnings.append(
                    f"  no parseable exit-JSON line (prose-only status?): models/{mdir}/README.md")
            row["state"] = e.get("overall", "unknown")
            row["traj"] = short_traj(e.get("trajectory"))
            row["flags"] = e.get("flagged_count", "—")
            row["figs"] = figs_count(mdir)
            audit = e.get("audit")
            if audit is None:
                warnings.append(f"  no \"audit\" field in exit JSON: models/{mdir}/README.md")
                audit = "self-reported"
            row["audit"] = AUDIT_LABELS.get(audit, audit)
        else:
            row.update(state="not started", traj="—", flags="—", figs="—", audit="—")
        rows.append(row)

    # Off-corpus started submodules. The loop above emits one row per CORPUS paper, so a
    # started submodule whose key is NOT in the corpus ranking (a paper added outside the
    # original landscape — e.g. vicente_kinouchi_caticha_1998, fitzhugh_1961) was SILENTLY
    # DROPPED, contradicting this module's promise to show "every paper we have actually
    # started". Surface them as rows with no corpus score, sorted to the end (rank shown as
    # "—"); their live state still comes from the submodule's own exit-JSON.
    for mdir in sorted(d for d in dirs if d not in matched_dirs):
        e = exit_state(mdir)
        if not e.get("overall"):
            warnings.append(
                f"  no parseable exit-JSON line (prose-only status?): models/{mdir}/README.md")
        audit = e.get("audit")
        if audit is None:
            warnings.append(f"  no \"audit\" field in exit JSON: models/{mdir}/README.md")
            audit = "self-reported"
        rows.append({
            "score": None, "label": mdir, "cluster": "—", "cites": 0, "oa": "—",
            "link": f"models/{mdir}", "code": "—", "started": True, "off_corpus": True,
            "state": e.get("overall", "unknown"), "traj": short_traj(e.get("trajectory")),
            "flags": e.get("flagged_count", "—"), "figs": figs_count(mdir),
            "audit": AUDIT_LABELS.get(audit, audit),
        })

    # numeric corpus score sorts high→low first; off-corpus rows (score None) sort to the end.
    rows.sort(key=lambda r: (-(r["score"] if r["score"] is not None else float("-inf")), -r["cites"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    # top-100 by rank UNION every started paper (corpus + off-corpus)
    shown = [r for r in rows if r["rank"] <= 100 or r["started"]]
    return shown, warnings


def render_table(rows):
    head = ("| Rank | Score | Paper | Cluster | Cites | Access | Code | "
            "State | Traj | Figs | Flags | Audit |")
    sep = "|--:|--:|---|---|--:|---|---|---|---|--:|--:|---|"
    lines = [head, sep]
    for r in rows:
        paper = f"[{r['label']}]({r['link']})"
        # off-corpus started models carry no corpus rank/score — show "—" for both.
        rank = "—" if r.get("off_corpus") else r["rank"]
        score = "—" if r.get("off_corpus") else r["score"]
        lines.append(
            f"| {rank} | {score} | {paper} | {r['cluster']} | {r['cites']} | "
            f"{r['oa']} | {r['code']} | {r['state']} | {r['traj']} | {r['figs']} | "
            f"{r['flags']} | {r['audit']} |"
        )
    return "\n".join(lines)


def render_readme(rows):
    n_started = sum(1 for r in rows if r["started"])
    n_total = len(rows)
    table = render_table(rows)
    return f"""# model_agent — reproduction roadmap

An agentic pipeline that reproduces computational-neuroscience models from their
papers, one git submodule per model under [`models/`](models/). See
[VISION.md](VISION.md) for the why, [WORKFLOW.md](WORKFLOW.md) for the full-pass
process, [AGENTS.md](AGENTS.md) for agent instructions, and
[PAPERS.md](PAPERS.md) for the clustered index + phylogeny.

## Reproduction status

The table below is **auto-generated** — do not edit it by hand. A pre-commit hook
(`tools/hooks/pre-commit`, activated with `git config core.hooksPath tools/hooks`)
refreshes it on every commit; run `python3 tools/build_readme.py` to refresh it
manually. It lists the
**top-100 ranked reproduction targets plus every paper already started**
({n_started} of {n_total} rows have a submodule), interleaved by composite score
(same scoring as [`proposals/corpus-top100-ranking.md`](proposals/corpus-top100-ranking.md)).

**Columns.** *Rank/Score/Cluster/Cites/Access/Code* describe the paper (from the
corpus data). *State* is the submodule's own self-reported exit
(`reproduced` › `faithful` › `partial` › `blocked` › `not started`); *Traj* its
trajectory; *Figs* committed reproduced figures; *Flags* open dispositions a human
must confirm.

> **Audit honesty.** `State` is the *builder's claim*, not a certification. The
> **Audit** column is the real trust signal: `hardened` = independent figure +
> digitization audit with build/audit roles separated · `VLM` = independent
> figure-comparison only · `self-reported` = implemented, not independently
> audited. Treat `self-reported` as *"not yet verified."*

{BEGIN}
{table}
{END}
"""


def main():
    args = sys.argv[1:]
    check = "--check" in args
    verbose = "--verbose" in args or "-v" in args
    rows, warnings = build_rows()
    content = render_readme(rows)

    if warnings:
        no_audit = sum(1 for w in warnings if "audit" in w)
        no_exit = sum(1 for w in warnings if "exit-JSON line" in w)
        print(f"build_readme: {no_audit} submodules missing an \"audit\" field, "
              f"{no_exit} with no parseable exit-JSON line"
              f"{'' if verbose else ' (run with --verbose to list them)'}", file=sys.stderr)
        if verbose:
            for w in sorted(set(warnings)):
                print(w, file=sys.stderr)

    old = open(README, encoding="utf-8").read() if os.path.exists(README) else None
    if check:
        if old != content:
            print("README.md is out of date — run: python3 tools/build_readme.py", file=sys.stderr)
            sys.exit(1)
        print("README.md is up to date.")
        return
    open(README, "w", encoding="utf-8").write(content)
    n = sum(1 for r in rows if r["started"])
    print(f"Wrote {README}: {len(rows)} rows ({n} started, {len(rows) - n} backlog).")


if __name__ == "__main__":
    main()
