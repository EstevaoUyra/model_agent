"""Generate the README test status table from logs/test_runs.jsonl.

For each test_id, only the latest row (by timestamp) is counted. Rows are
grouped by figure; tests without a figure marker land in an "Unassigned"
row.

The VLM column is a placeholder until figure-comparison verdicts have a
persistent home (currently they're ephemeral CLI output).
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_PASSING_STATUSES = {"pass"}


@dataclass(frozen=True)
class FigureStats:
    """Per-figure deterministic test counts."""

    figure: int | str | None
    total: int
    passing: int

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return round(100 * self.passing / self.total)

    @property
    def label(self) -> str:
        if self.figure is None:
            return "Unassigned"
        return f"Figure {self.figure}"

    def cell(self) -> str:
        return f"{self.total} total, {self.passing} ({self.percent}%) passing"


def load_rows(jsonl_path: Path) -> list[dict]:
    """Read every row from a JSONL test log. Missing file → empty list."""
    if not jsonl_path.exists():
        return []
    rows: list[dict] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            rows.append(json.loads(stripped))
    return rows


def latest_per_test(rows: Iterable[dict]) -> list[dict]:
    """Keep one row per test_id — whichever has the latest timestamp."""
    by_test: dict[str, dict] = {}
    for row in rows:
        test_id = row.get("test_id")
        if not test_id:
            continue
        existing = by_test.get(test_id)
        if existing is None or row.get("timestamp", "") > existing.get("timestamp", ""):
            by_test[test_id] = row
    return list(by_test.values())


def aggregate_by_figure(rows: Iterable[dict]) -> list[FigureStats]:
    """Group rows by figure and count totals/passing.

    Returned list is sorted by figure number; ``None`` goes last as "Unassigned".
    """
    totals: dict[int | str | None, int] = defaultdict(int)
    passing: dict[int | str | None, int] = defaultdict(int)
    for row in rows:
        figure = row.get("figure")
        totals[figure] += 1
        if row.get("status") in _PASSING_STATUSES:
            passing[figure] += 1

    stats = [
        FigureStats(figure=fig, total=totals[fig], passing=passing[fig])
        for fig in totals
    ]
    return sorted(stats, key=_sort_key)


def _sort_key(stat: FigureStats) -> tuple[int, int | str]:
    """Sort numeric figures ascending; None last."""
    if stat.figure is None:
        return (1, 0)
    if isinstance(stat.figure, int):
        return (0, stat.figure)
    return (0, str(stat.figure))


def format_markdown_table(stats: list[FigureStats]) -> str:
    """Render the test status table as a markdown table.

    The VLM column is a placeholder ("—") until figure comparison verdicts
    have a persistent on-disk source.
    """
    if not stats:
        return "_No test runs recorded yet._"

    lines = [
        "| Figure | Deterministic tests | VLM Test |",
        "|---|---|---|",
    ]
    for stat in stats:
        lines.append(f"| {stat.label} | {stat.cell()} | — |")
    return "\n".join(lines)


def render_table(jsonl_path: Path) -> str:
    """End-to-end: read JSONL → latest per test → aggregate → render markdown."""
    rows = load_rows(jsonl_path)
    latest = latest_per_test(rows)
    stats = aggregate_by_figure(latest)
    return format_markdown_table(stats)


__all__ = [
    "FigureStats",
    "aggregate_by_figure",
    "format_markdown_table",
    "latest_per_test",
    "load_rows",
    "render_table",
]
