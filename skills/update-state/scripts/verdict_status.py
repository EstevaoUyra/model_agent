"""Per-figure VLM verdict status, with staleness against the model's HEAD.

Feeds the update-state reflection. For each figure that has a persisted
verdict, prints the latest one and whether it was recorded against the
current model commit (fresh) or an older one (stale — the figure code may
have changed since, so the verdict can no longer be trusted as-is).

It also lists figures that have deterministic test rows but NO verdict at
all — these are *uncovered*, not green: the conflict rule treats a figure as
green only when deterministic is green AND a fresh VLM verdict passes.

Output line per figure:
    figure=<N> verdict=<pass|fail|needs_review|none> \
        commit=<short> stale=<yes|no|n/a> evaluated_at=<ts>

Usage:
    python verdict_status.py --model-dir models/<model>
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from neuromodels.framework.test_table import (
    aggregate_by_figure,
    latest_per_test,
    load_latest_verdicts,
    load_rows,
)


def _git_head(model_dir: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(model_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    model_dir: Path = args.model_dir
    head = _git_head(model_dir)
    head_short = head[:7]

    comparisons = model_dir / "logs" / "figure_comparisons"
    verdicts = load_latest_verdicts(comparisons)

    rows = latest_per_test(load_rows(model_dir / "logs" / "test_runs.jsonl"))
    figures_with_tests = sorted(
        {str(s.figure) for s in aggregate_by_figure(rows) if s.figure is not None},
        key=lambda f: (len(f), f),
    )

    all_figures = sorted(
        set(figures_with_tests) | set(verdicts),
        key=lambda f: (len(f), f),
    )

    print(f"model HEAD: {head_short}")
    uncovered = []
    for figure in all_figures:
        verdict = verdicts.get(figure)
        if verdict is None:
            uncovered.append(figure)
            print(
                f"figure={figure} verdict=none commit=- stale=n/a evaluated_at=-"
            )
            continue
        stale = "no" if verdict.commit == head_short else "yes"
        print(
            f"figure={figure} verdict={verdict.verdict.replace(' ', '_')} "
            f"commit={verdict.commit or '-'} stale={stale} "
            f"evaluated_at={verdict.evaluated_at or '-'}"
        )

    if uncovered:
        print(
            "uncovered (deterministic data but no VLM verdict — NOT green): "
            + ", ".join(uncovered)
        )

    raw_records = []
    if comparisons.is_dir():
        for path in sorted(comparisons.glob("figure_*.json")):
            try:
                raw_records.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    adjudicated = [
        f"figure={r.get('figure_number')}: {r.get('parent_adjudication')}"
        for r in raw_records
        if str(r.get("parent_adjudication", "")).strip()
    ]
    if adjudicated:
        print("parent adjudications on record:")
        for line in adjudicated:
            print("  " + line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
