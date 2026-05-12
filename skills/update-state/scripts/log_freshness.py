#!/usr/bin/env python3
"""Summarize per-figure freshness of logs/test_runs.jsonl.

For each figure (including the "Unassigned" bucket for rows with figure=None),
prints: row count, distinct test_id count, latest commit_hash, latest timestamp.

This is the data needed to diagnose stale-metadata (commit_hash older than
HEAD but test surface still matches) vs stale-data (test surface has changed
since the latest run).

Usage (from model directory):
    python skills/update-state/scripts/log_freshness.py
    python skills/update-state/scripts/log_freshness.py --verbose
    python skills/update-state/scripts/log_freshness.py --log-path <path>
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from neuromodels.framework.test_table import load_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("logs/test_runs.jsonl"),
        help="Path to test_runs.jsonl (default: logs/test_runs.jsonl)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also list the distinct test_ids in each figure's rows",
    )
    args = parser.parse_args(argv)

    rows = load_rows(args.log_path)
    if not rows:
        print(f"(no rows in {args.log_path})", file=sys.stderr)
        return 0

    by_figure: dict[object, list[dict]] = defaultdict(list)
    for row in rows:
        by_figure[row.get("figure")].append(row)

    for figure in sorted(by_figure, key=_sort_key):
        figure_rows = by_figure[figure]
        label = "Unassigned" if figure is None else f"Figure {figure}"
        distinct_ids = sorted({r.get("test_id") for r in figure_rows if r.get("test_id")})
        latest = max(figure_rows, key=lambda r: r.get("timestamp", ""))
        commit = (latest.get("commit_hash") or "<none>")[:8]
        ts = latest.get("timestamp", "<none>")
        print(
            f"{label}: {len(figure_rows)} rows, {len(distinct_ids)} distinct test_ids, "
            f"latest commit {commit} at {ts}"
        )
        if args.verbose:
            for test_id in distinct_ids:
                print(f"  - {test_id}")
    return 0


def _sort_key(figure: object) -> tuple[int, object]:
    if figure is None:
        return (1, 0)
    if isinstance(figure, int):
        return (0, figure)
    return (0, str(figure))


if __name__ == "__main__":
    raise SystemExit(main())
