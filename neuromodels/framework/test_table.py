"""Generate the README test status table from logs/test_runs.jsonl.

For each test_id, only the latest row (by timestamp) is counted. Rows are
grouped by figure; tests without a figure marker land in an "Unassigned"
row.

The VLM column is populated from persisted figure-comparison verdicts in
``<logs>/figure_comparisons/figure_<N>_*.json`` (written by the update-state
skill's VLM step). For each figure the latest verdict by ``evaluated_at`` is
used; the cell shows ``pass`` / ``fail`` / ``needs review`` plus the model
commit the verdict was recorded against (so a reader can spot a stale
verdict). Figures with no verdict file show ``—``.

This table reports the two signals *separately*. The combined green/red/
unknown classification — including the rule that any deterministic red is a
loss and a deterministic-green + VLM-red figure is also a loss — is the
update-state skill's reflection job, not this renderer's.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


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


@dataclass(frozen=True)
class VlmVerdict:
    """Latest persisted VLM figure-comparison verdict for one figure."""

    figure: str
    verdict: str  # "pass" | "fail" | "needs review"
    commit: str  # short model commit hash the verdict was recorded against
    evaluated_at: str

    def cell(self) -> str:
        return f"{self.verdict} ({self.commit})" if self.commit else self.verdict


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


def _sort_key(stat: FigureStats) -> tuple[int, float, str]:
    """Sort numeric figures ascending, then non-numeric, then None last.

    The key is uniformly typed ``(group:int, value:float, text:str)`` so a
    table mixing int and string figure markers (e.g. ``1`` and ``"Supp4"``)
    sorts without a ``TypeError`` — the previous ``(0, int)`` vs ``(0, str)``
    keys were mutually incomparable in Python 3 and crashed any model that
    mixed marker types (found by the carrasco2021 run).
    """
    figure = stat.figure
    if figure is None:
        return (2, 0.0, "")
    try:
        return (0, float(figure), "")
    except (TypeError, ValueError):
        return (1, 0.0, str(figure))


def _verdict_word(record: dict) -> str:
    """Map a persisted verdict record to one display word.

    ``passes is True`` → ``pass``. ``passes is False`` → ``fail`` unless the
    recommendation flags it ``needs_review`` (e.g. core science correct but a
    scope/structure question remains). ``passes is None`` → ``needs review``.
    """
    verdict = record.get("verdict")
    if not isinstance(verdict, Mapping):
        return "needs review"
    passes = verdict.get("passes")
    recommendation = str(verdict.get("recommendation", "")).strip().lower()
    if passes is True:
        return "pass"
    if passes is False:
        if recommendation.startswith(("needs_review", "needs review")):
            return "needs review"
        return "fail"
    return "needs review"


def load_latest_verdicts(comparisons_dir: Path) -> dict[str, VlmVerdict]:
    """Load the latest persisted VLM verdict per figure.

    Reads ``figure_<N>_*.json`` records, keeps the one with the greatest
    ``evaluated_at`` per ``figure_number`` (filename order breaks ties since
    the filename embeds a sortable UTC stamp). Missing dir → empty mapping;
    unreadable/invalid files are skipped, not fatal.
    """
    if not comparisons_dir.is_dir():
        return {}
    by_figure: dict[str, VlmVerdict] = {}
    for path in sorted(comparisons_dir.glob("figure_*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(record, Mapping):
            continue
        figure = str(record.get("figure_number", "")).strip()
        if not figure:
            continue
        evaluated_at = str(record.get("evaluated_at", ""))
        commit = str(record.get("model_commit_hash", ""))[:7]
        candidate = VlmVerdict(
            figure=figure,
            verdict=_verdict_word(record),
            commit=commit,
            evaluated_at=evaluated_at,
        )
        existing = by_figure.get(figure)
        if existing is None or evaluated_at >= existing.evaluated_at:
            by_figure[figure] = candidate
    return by_figure


def _vlm_cell(stat: FigureStats, verdicts: Mapping[str, VlmVerdict] | None) -> str:
    if not verdicts or stat.figure is None:
        return "—"
    verdict = verdicts.get(str(stat.figure))
    return verdict.cell() if verdict is not None else "—"


def format_markdown_table(
    stats: list[FigureStats],
    verdicts: Mapping[str, VlmVerdict] | None = None,
) -> str:
    """Render the test status table as a markdown table.

    ``verdicts`` maps a figure number (as ``str``) to its latest
    :class:`VlmVerdict`. When omitted, the VLM column is ``—`` for every row
    (back-compatible with callers that have no persisted verdicts).
    """
    if not stats:
        return "_No test runs recorded yet._"

    lines = [
        "| Figure | Deterministic tests | VLM Test |",
        "|---|---|---|",
    ]
    for stat in stats:
        lines.append(
            f"| {stat.label} | {stat.cell()} | {_vlm_cell(stat, verdicts)} |"
        )
    return "\n".join(lines)


def render_table(
    jsonl_path: Path,
    comparisons_dir: Path | None = None,
) -> str:
    """End-to-end: read JSONL + verdicts → aggregate → render markdown.

    ``comparisons_dir`` defaults to ``<jsonl_path parent>/figure_comparisons``,
    which is the conventional location next to ``logs/test_runs.jsonl``.
    """
    rows = load_rows(jsonl_path)
    latest = latest_per_test(rows)
    stats = aggregate_by_figure(latest)
    if comparisons_dir is None:
        comparisons_dir = Path(jsonl_path).parent / "figure_comparisons"
    verdicts = load_latest_verdicts(Path(comparisons_dir))
    return format_markdown_table(stats, verdicts)


__all__ = [
    "FigureStats",
    "VlmVerdict",
    "aggregate_by_figure",
    "format_markdown_table",
    "latest_per_test",
    "load_latest_verdicts",
    "load_rows",
    "render_table",
]
