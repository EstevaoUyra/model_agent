#!/usr/bin/env python3
"""Generate a model's README.md from its artifacts — the per-model companion to
`tools/build_readme.py` (which builds the *parent* roadmap table).

A model README has seven sections; each is rendered by one fault-tolerant function
that reads artifacts and NEVER invents prose (irreducible prose is authored once
into `logs/readme_meta.yaml` and rendered verbatim):

  1. Current exit          logs/exit.json
  2. Status                logs/exit.json + test_runs.jsonl + figure_comparisons/ + meta.status_narrative
  3. Model                 article_aware/spec/model_spec.yaml + citations.yaml + meta.model_summary
  4. Reproduced figures    figure_N_layout.yaml + files on disk + test_runs (tier/check) + figure_comparisons + meta.figures
  5. Potential sources     logs/issues.yaml
  6. Changelog             logs/changelog.md  (## DATE — summary headers)
  7. Reproduction cost     tools/repro_cost.py --markdown

A missing artifact degrades its section to a stub + a stderr warning rather than
crashing — so freeform models can be migrated one section at a time. See
`proposals/per-model-readme-autogen-2026-06-15.md` for the design + artifact schemas.

Usage:
    python3 tools/build_model_readme.py models/<name>            # write models/<name>/README.md
    python3 tools/build_model_readme.py models/<name> --check    # CI: exit 1 if it would change
    python3 tools/build_model_readme.py models/<name> --stdout   # print, write nothing
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(ROOT))

# Reuse the framework's test/VLM roll-up where it fits (§2).
try:
    from neuromodels.framework.test_table import (
        load_latest_verdicts,
        load_rows,
        latest_per_test,
    )
except Exception:  # pragma: no cover - framework not importable in some shells
    load_rows = latest_per_test = load_latest_verdicts = None


WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------- IO

def _load_yaml(path: Path):
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        warn(f"unreadable YAML {path}: {e}")
        return None


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        warn(f"unreadable JSON {path}: {e}")
        return None


# --------------------------------------------------------------------- §1 exit

EXIT_KEYS = ["overall", "trajectory", "flagged_count", "blocked",
             "figures_rerendered"]
EXIT_LABEL = {
    "overall": "Overall", "trajectory": "Trajectory",
    "flagged_count": "Flagged (human must confirm)", "blocked": "Blocked",
    "audit": "Audit", "audit_overrides": "Audit overrides",
    "figures_rerendered": "Figures re-rendered", "updated_at": "Updated",
}


def section_exit(exit_data: dict | None, n_adjudications: int = 0) -> str:
    if not exit_data:
        warn("no logs/exit.json — §1 Current exit is a stub")
        return "## Current exit\n\n_No `logs/exit.json` yet (run finalize)._"
    if n_adjudications:
        exit_data = {**exit_data,
                     "audit_overrides": f"{n_adjudications} (see Status ⚖️)"}
    # Canonical machine line — kept so the parent build_readme.py can scrape it.
    line = {k: exit_data[k] for k in
            ["overall", "trajectory", "flagged_count", "blocked"] if k in exit_data}
    for k in ("audit", "figures_rerendered"):
        if k in exit_data:
            line[k] = exit_data[k]
    rows = ["| Field | Value |", "|---|---|"]
    order = ["overall", "trajectory", "audit", "audit_overrides", "flagged_count",
             "figures_rerendered", "blocked", "updated_at"]
    for k in order:
        if k not in exit_data:
            continue
        v = exit_data[k]
        if isinstance(v, list):
            v = ", ".join(map(str, v)) if v else "—"
        rows.append(f"| {EXIT_LABEL.get(k, k)} | {v} |")
    headline = exit_data.get("headline", "")
    parts = ["## Current exit", ""]
    if headline:
        parts += [f"**{headline}**", ""]
    parts += ["\n".join(rows), "",
              "```json", json.dumps(line), "```"]
    return "\n".join(parts)


# ------------------------------------------------------------------- §2 status

PASSING = {"pass"}


def _figure_rollup(rows: list[dict], verdicts) -> str:
    """Per-figure deterministic-test + VLM roll-up table, computed live."""
    if not rows:
        return ""
    totals: dict = defaultdict(int)
    passing: dict = defaultdict(int)
    for r in rows:
        fig = r.get("figure")
        totals[fig] += 1
        if r.get("status") in PASSING:
            passing[fig] += 1

    def key(f):
        if f is None:
            return (2, 0.0, "")
        try:
            return (0, float(f), "")
        except (TypeError, ValueError):
            return (1, 0.0, str(f))

    out = ["| Figure | Deterministic tests | VLM |", "|---|---|---|"]
    for fig in sorted(totals, key=key):
        label = "Unassigned" if fig is None else f"Figure {fig}"
        t, p = totals[fig], passing[fig]
        pct = round(100 * p / t) if t else 0
        vcell = "—"
        if verdicts and fig is not None:
            v = verdicts.get(str(fig))
            if v is not None:
                vcell = v.cell()
        out.append(f"| {label} | {t} total, {p} ({pct}%) passing | {vcell} |")
    return "\n".join(out)


def _adjudications_block(adj_data) -> list[str]:
    """Render organizer audit-overrides. An audit failure can be overcome ONLY by
    a documented entry here (never paperless) — so it is shown prominently."""
    items = (adj_data or {}).get("adjudications") or []
    if not items:
        return []
    out = ["### ⚖️ Organizer adjudications (documented audit overrides)", "",
           "An audit verdict was overturned by the organizer's direct judgement that the "
           "change is small/safe. Each override is on the record with its reasoning — never "
           "silent. Source: `logs/adjudications.yaml`.", ""]
    for a in items:
        head = f"**{a.get('id', 'ADJ')}** ({a.get('date', '')}, {a.get('decided_by', 'organizer')}) — " \
               f"{a.get('verdict', 'override')}"
        out.append(head)
        if a.get("finding"):
            out += ["", f"- _Audit finding overridden:_ {a['finding']}"]
        if a.get("audit_ref"):
            out.append(f"- _Audit on record:_ `{a['audit_ref']}`")
        if a.get("change_scope"):
            out.append(f"- _Change scope:_ {a['change_scope']}")
        if a.get("reasoning"):
            out += ["", "   " + a["reasoning"].rstrip().replace("\n", "\n   ")]
        if a.get("evidence"):
            out += ["", "   _Evidence:_ " + ", ".join(f"`{e}`" for e in a["evidence"])]
        out.append("")
    return out


def section_status(exit_data, meta, rows, verdicts, adj_data) -> str:
    parts = ["## Status", ""]
    narrative = (meta or {}).get("status_narrative")
    if narrative:
        parts += [narrative.rstrip(), ""]
    else:
        warn("no meta.status_narrative — §2 Status narrative omitted")
    blocked = (exit_data or {}).get("blocked") or []
    if blocked:
        parts += ["**Blocked:** " + ", ".join(f"`{b}`" for b in blocked), ""]
    parts += _adjudications_block(adj_data)
    table = _figure_rollup(rows, verdicts)
    if table:
        parts += ["**Per-figure test + VLM roll-up** (computed live from "
                  "`logs/test_runs.jsonl` and `logs/figure_comparisons/`):", "",
                  table]
    return "\n".join(parts).rstrip()


# -------------------------------------------------------------------- §3 model

def section_model(spec, cites, meta) -> str:
    parts = ["## Model", ""]
    citation = (spec or {}).get("paper_citation")
    if citation:
        parts += [citation, ""]
    else:
        warn("no model_spec.paper_citation — §3 citation omitted")
    summary = (meta or {}).get("model_summary")
    if summary:
        parts += [summary.rstrip(), ""]
    else:
        warn("no meta.model_summary — §3 summary omitted")
    # Key equations: pull the cited equation lines from citations.yaml by id.
    eq_ids = (meta or {}).get("model_equation_refs")
    if eq_ids and cites:
        by_id = {c.get("id"): c for c in cites if isinstance(c, dict)}
        eqs = []
        for cid in eq_ids:
            c = by_id.get(cid)
            if c and c.get("text"):
                eqs.append(f"- `{c['text']}`  ({c.get('location', cid)})")
        if eqs:
            parts += ["**Governing equations** (from `citations.yaml`):", "",
                      "\n".join(eqs), ""]
    return "\n".join(parts).rstrip()


# ------------------------------------------------------------------ §4 figures

IMG_EXT = (".png", ".jpg", ".jpeg")


def _committed_pool(model_dir: Path) -> list[str]:
    """Committed image files (git ls-files) — so the README never links an
    uncommitted/gitignored render. Falls back to an on-disk scan outside git."""
    try:
        out = subprocess.run(["git", "-C", str(model_dir), "ls-files"],
                             capture_output=True, text=True, timeout=20)
        if out.returncode == 0:
            return [f for f in out.stdout.splitlines() if f.lower().endswith(IMG_EXT)]
    except Exception:
        pass
    return [str(p.relative_to(model_dir)) for p in model_dir.rglob("*")
            if p.suffix.lower() in IMG_EXT]


# Where each view lives. Models follow one of two committed conventions: the
# canonical `figures_reproduced/figure_N.png` (+ flat `article_aware/figures/figure_N.png`),
# or the older `figure_outputs/` layout (renders in figure_outputs/, paper crops at
# figure_N/figure_N_source.png, overlays under the figure_N/ subdir). Both are discovered.

def _paper_view(pool, n) -> list[str]:
    nr = re.escape(str(n))
    flat = [f for f in pool
            if re.fullmatch(rf"article_aware/figures/figure_{nr}\.(png|jpg|jpeg)", f)]
    if flat:
        return flat[:1]
    src = sorted(f for f in pool
                 if re.match(rf"article_aware/figures/figure_{nr}/figure_{nr}_source\.", f))
    return src[:1]


def _impl_views(pool, n) -> list[str]:
    nr = re.escape(str(n))
    single = [f for f in pool
              if re.fullmatch(rf"figures_reproduced/figure_{nr}\.(png|jpg|jpeg)", f)]
    if single:
        return single[:1]
    # figure_outputs convention — may carry several panels per figure (e.g. weights + activity)
    return sorted(
        f for f in pool
        if re.match(rf"(implementation/)?figure_outputs/figure_{nr}(\.|_)", f)
        and not any(x in f.lower() for x in ("reference", "source", "overlay")))


def _digitized_views(pool, n) -> list[str]:
    nr = re.escape(str(n))
    return sorted(
        f for f in pool
        if re.match(rf"(article_aware/figures|(implementation/)?figure_outputs)/figure_{nr}/", f)
        and "overlay" in f.lower())


def _image_table(pool, n) -> str:
    paper, digi, impl = _paper_view(pool, n), _digitized_views(pool, n), _impl_views(pool, n)
    cols, cells = [], []
    if paper:
        cols.append("Paper")
        cells.append("".join(f'<img src="{p}" width="300">' for p in paper))
    if digi:
        cols.append("Digitized")
        cells.append("".join(f'<img src="{d}" width="150">' for d in digi))
    if impl:
        cols.append("Implementation")
        cells.append("".join(f'<img src="{p}" width="300">' for p in impl))
    if not cells:
        warn(f"figure {n}: no committed views on disk")
        return "_No committed figure views._"
    head = "<tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>"
    body = "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
    return f"<table>{head}{body}</table>"


def _tier_table(rows_for_fig: list[dict], fallback) -> str:
    """Tier | Check | Result table from tier-tagged test rows; else the
    meta-authored fallback list."""
    tiered = [r for r in rows_for_fig if r.get("tier")]
    if tiered:
        out = ["| Tier | Check | Result |", "|---|---|---|"]
        for r in sorted(tiered, key=lambda r: str(r.get("tier"))):
            res = {"pass": "✅ pass", "fail": "❌ fail",
                   "skipped": "⚠️ skipped"}.get(r.get("status"), r.get("status"))
            out.append(f"| {r['tier']} | {r.get('check') or r['test_id'].split('::')[-1]} | {res} |")
        return "\n".join(out)
    if fallback:
        out = ["| Tier | Check | Result |", "|---|---|---|"]
        for c in fallback:
            out.append(f"| {c.get('tier', '')} | {c.get('check', '')} | {c.get('result', '')} |")
        return "\n".join(out)
    return ""


def _figure_sort_key(f):
    """Order figures numeric-first (1, 2, 10), then letter/string ids (A, B)."""
    s = str(f)
    if s.isdigit():
        return (0, int(s), "")
    return (1, 0, s)


def _discover_figure_nums(pool, layouts, fig_meta) -> list:
    """Every figure with a layout, a meta entry, or any committed view in the
    pool (figures_reproduced/, article_aware/figures/, or the figure_outputs/
    convention). Ids may be integers or digit-prefixed (2a) — both render; a
    purely non-numeric token from disk (e.g. figure_table_1) is ignored to avoid
    spurious sections, but meta.figures may still name one explicitly."""
    keys: set = set(layouts.keys())
    keys |= {int(k) if str(k).isdigit() else str(k) for k in fig_meta}
    fig_re = re.compile(
        r"^(?:figures_reproduced|(?:implementation/)?figure_outputs|article_aware/figures)/"
        r"figure_([0-9][0-9A-Za-z]*)(?=[._/])")
    for f in pool:
        m = fig_re.match(f)
        if m:
            tok = m.group(1)
            keys.add(int(tok) if tok.isdigit() else tok)
    return sorted(keys, key=_figure_sort_key)


def section_figures(model_dir: Path, meta, layouts, rows, verdicts, pool) -> str:
    fig_meta = (meta or {}).get("figures") or {}
    nums = _discover_figure_nums(pool, layouts, fig_meta)
    if not nums:
        warn("no figures on disk, no layout, no meta.figures — §4 is a stub")
        return ("## Reproduced figures — paper · digitized · implementation\n\n"
                "_No committed figures in scope._")
    rows_by_fig: dict = defaultdict(list)
    for r in rows or []:
        rows_by_fig[str(r.get("figure"))].append(r)

    parts = [
        "## Reproduced figures — paper · digitized · implementation", "",
        "Each figure is shown up to three ways — **paper** (original crop), "
        "**digitized** (tool-grounded curves the tests grade against), and "
        "**implementation** (the live model through the pinned-axis view). The "
        "check table is the deterministic test tiers; the VLM verdict is the "
        "latest figure-comparison.", "",
    ]
    for n in nums:
        fm = fig_meta.get(n, fig_meta.get(str(n), {})) or {}
        badge = fm.get("status_badge", "")
        headline = fm.get("headline", "")
        title = f"### Figure {n}"
        if headline:
            title += f" — {headline}"
        if badge:
            title += f"  {badge}"
        parts += [title, "", _image_table(pool, n), ""]
        if fm.get("note"):
            parts += [fm["note"].rstrip(), ""]
        # not-reproduced panels, from the layout
        layout = layouts.get(n) or {}
        nr = [c.get("panel") for c in layout.get("cells", [])
              if c.get("reproduced") is False and c.get("role") != "legend"]
        if nr:
            parts += [f"_Not reproduced (explicit placeholders): panels "
                      f"{', '.join(map(str, nr))}._", ""]
        tier = _tier_table(rows_by_fig.get(str(n), []), fm.get("checks"))
        if tier:
            parts += [tier, ""]
    return "\n".join(parts).rstrip()


# ------------------------------------------------------------------- §5 issues

def section_issues(issues_data) -> str:
    parts = ["## Potential sources of the issues", ""]
    if not issues_data:
        warn("no logs/issues.yaml — §5 is a stub")
        return ("## Potential sources of the issues\n\n"
                "_No `logs/issues.yaml` yet (distil from the audit logs at finalize)._")
    if issues_data.get("preamble"):
        parts += [issues_data["preamble"].rstrip(), ""]
    for i, item in enumerate(issues_data.get("issues", []), 1):
        status = item.get("status", "open").upper()
        cat = item.get("category", "")
        tag = " · ".join(x for x in (cat, status) if x)
        head = f"{i}. **{item.get('title', 'untitled')}**"
        if tag:
            head += f" — _{tag}_"
        parts.append(head)
        if item.get("body"):
            parts += ["", "   " + item["body"].rstrip().replace("\n", "\n   ")]
        srcs = item.get("sources")
        if srcs:
            parts += ["", "   *Source:* " + ", ".join(f"`{s}`" for s in srcs)]
        parts.append("")
    return "\n".join(parts).rstrip()


# ---------------------------------------------------------------- §6 changelog

CL_HEADER = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s+[—-]\s+(.*)$")


def _git_changelog(model_dir: Path) -> str:
    """Fallback when there is no logs/changelog.md: the last commit subjects."""
    try:
        out = subprocess.run(["git", "-C", str(model_dir), "log", "-40",
                              "--pretty=%ad\t%s", "--date=short"],
                             capture_output=True, text=True, timeout=10)
    except Exception:
        return ""
    rows = ["| Date | Change |", "|---|---|"]
    for line in out.stdout.splitlines():
        if "\t" not in line:
            continue
        date, subj = line.split("\t", 1)
        # Skip the generator's own commit so the table is stable across regen/commit
        # cycles (else each autogen commit adds a self-referential row → never --check clean).
        if subj.startswith("readme: auto-generate from artifacts"):
            continue
        rows.append(f"| {date} | {subj.replace('|', chr(92) + '|')} |")
        if len(rows) >= 17:  # header(2) + 15 entries
            break
    return "\n".join(rows) if len(rows) > 2 else ""


def section_changelog(model_dir: Path) -> str:
    path = model_dir / "logs" / "changelog.md"
    parts = ["## Changelog", "",
             "One line per pass; full detail in "
             "[`logs/changelog.md`](logs/changelog.md).", ""]
    if not path.exists():
        warn("no logs/changelog.md — §6 falls back to git log")
        table = _git_changelog(model_dir)
        if not table:
            return "## Changelog\n\n_No changelog or git history._"
        return ("## Changelog\n\n_No `logs/changelog.md` yet — showing recent "
                "commits._\n\n" + table)
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = CL_HEADER.match(line.strip())
        if m:
            entries.append((m.group(1), m.group(2).strip()))
    if not entries:
        warn("logs/changelog.md has no '## DATE — summary' headers")
        return "## Changelog\n\n_No parseable changelog headers._"
    parts += ["| Date | Change |", "|---|---|"]
    for date, summary in entries:
        parts.append(f"| {date} | {summary} |")
    return "\n".join(parts)


# --------------------------------------------------------------------- §7 cost

def section_cost(model_rel: str) -> str:
    try:
        out = subprocess.run(
            [sys.executable, str(TOOLS / "repro_cost.py"), model_rel, "--markdown"],
            capture_output=True, text=True, timeout=300)
    except Exception as e:  # pragma: no cover
        warn(f"repro_cost.py failed: {e}")
        return ""
    text = out.stdout.strip()
    if not text:
        warn(f"no recoverable cost transcripts for {model_rel} — §7 omitted")
    return text


# ------------------------------------------------------------------- assembly

def build(model_rel: str) -> str:
    model_dir = (ROOT / model_rel).resolve()
    logs = model_dir / "logs"
    spec_dir = model_dir / "article_aware" / "spec"

    exit_data = _load_json(logs / "exit.json")
    meta = _load_yaml(logs / "readme_meta.yaml") or {}
    issues_data = _load_yaml(logs / "issues.yaml")
    adj_data = _load_yaml(logs / "adjudications.yaml")
    spec = _load_yaml(spec_dir / "model_spec.yaml")
    cites = _load_yaml(spec_dir / "citations.yaml")

    layouts = {}
    for p in sorted((model_dir / "article_aware" / "figures").glob("figure_*_layout.yaml")
                    if (model_dir / "article_aware" / "figures").is_dir() else []):
        m = re.search(r"figure_(\d+)_layout", p.name)
        if m:
            layouts[int(m.group(1))] = _load_yaml(p)

    rows, verdicts = [], {}
    if load_rows is not None:
        rows = latest_per_test(load_rows(logs / "test_runs.jsonl"))
        verdicts = load_latest_verdicts(logs / "figure_comparisons")
    else:
        warn("neuromodels.framework.test_table not importable — live test/VLM data skipped")

    pool = _committed_pool(model_dir)

    title = (meta.get("title") or spec and spec.get("name")
             or model_dir.name.replace("_", " ").title())

    n_adj = len((adj_data or {}).get("adjudications") or [])
    sections = [
        f"# {title}",
        section_exit(exit_data, n_adj),
        section_status(exit_data, meta, rows, verdicts, adj_data),
        section_model(spec, cites, meta),
        section_figures(model_dir, meta, layouts, rows, verdicts, pool),
        section_issues(issues_data),
        section_changelog(model_dir),
        section_cost(model_rel),
    ]
    body = "\n\n---\n\n".join(s for s in sections if s and s.strip())
    return body.rstrip() + "\n"


def main() -> None:
    argv = sys.argv[1:]
    flags = {a for a in argv if a.startswith("--")}
    positional = [a for a in argv if not a.startswith("--")]
    if not positional:
        print("usage: build_model_readme.py models/<name> [--check|--stdout]",
              file=sys.stderr)
        sys.exit(2)
    model_rel = positional[0].rstrip("/")
    if not (ROOT / model_rel).is_dir():
        print(f"no such model dir: {model_rel}", file=sys.stderr)
        sys.exit(2)

    content = build(model_rel)
    readme = ROOT / model_rel / "README.md"

    if WARNINGS:
        print(f"build_model_readme {model_rel}: {len(WARNINGS)} warning(s):",
              file=sys.stderr)
        for w in WARNINGS:
            print(f"  - {w}", file=sys.stderr)

    if "--stdout" in flags:
        print(content)
        return
    old = readme.read_text(encoding="utf-8") if readme.exists() else None
    if "--check" in flags:
        if old != content:
            print(f"{readme} is out of date — run: "
                  f"python3 tools/build_model_readme.py {model_rel}", file=sys.stderr)
            sys.exit(1)
        print(f"{readme} is up to date.")
        return
    readme.write_text(content, encoding="utf-8")
    print(f"Wrote {readme} ({len(content.splitlines())} lines).")


if __name__ == "__main__":
    main()
