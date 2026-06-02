from __future__ import annotations

import json
from pathlib import Path

from neuromodels.framework.test_table import (
    FigureStats,
    VlmVerdict,
    aggregate_by_figure,
    format_markdown_table,
    latest_per_test,
    load_latest_verdicts,
    load_rows,
    render_table,
)


def _verdict_record(
    figure: str,
    *,
    passes,
    recommendation="",
    commit="dc4f8382998be0fd850219d3457965c63ad1e6d7",
    evaluated_at="2026-05-18T11:59:46Z",
):
    return {
        "figure_number": figure,
        "model_commit_hash": commit,
        "evaluated_at": evaluated_at,
        "verdict": {"passes": passes, "recommendation": recommendation},
    }


def _write_verdict(comparisons_dir: Path, stamp: str, record: dict) -> None:
    comparisons_dir.mkdir(parents=True, exist_ok=True)
    fig = record["figure_number"]
    path = comparisons_dir / f"figure_{fig}_{stamp}.json"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")


def _row(test_id: str, *, figure=None, status="pass", timestamp="2026-05-12T10:00:00Z"):
    return {
        "test_id": test_id,
        "figure": figure,
        "status": status,
        "timestamp": timestamp,
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_load_rows_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_rows(tmp_path / "does-not-exist.jsonl") == []


def test_load_rows_skips_blank_lines(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    log.write_text(
        json.dumps({"test_id": "a"}) + "\n\n" + json.dumps({"test_id": "b"}) + "\n",
        encoding="utf-8",
    )
    rows = load_rows(log)
    assert [r["test_id"] for r in rows] == ["a", "b"]


def test_latest_per_test_picks_latest_timestamp() -> None:
    rows = [
        _row("a", status="fail", timestamp="2026-05-12T09:00:00Z"),
        _row("a", status="pass", timestamp="2026-05-12T10:00:00Z"),
        _row("b", status="pass", timestamp="2026-05-12T09:30:00Z"),
    ]
    latest = {r["test_id"]: r for r in latest_per_test(rows)}
    assert latest["a"]["status"] == "pass"
    assert latest["b"]["status"] == "pass"


def test_latest_per_test_ignores_rows_without_test_id() -> None:
    rows = [_row("a"), {"figure": 1, "status": "pass", "timestamp": "z"}]
    out = latest_per_test(rows)
    assert len(out) == 1
    assert out[0]["test_id"] == "a"


def test_aggregate_by_figure_counts_pass_only() -> None:
    rows = [
        _row("a", figure=1, status="pass"),
        _row("b", figure=1, status="pass"),
        _row("c", figure=1, status="fail"),
        _row("d", figure=2, status="pass"),
    ]
    stats = {s.figure: s for s in aggregate_by_figure(rows)}
    assert stats[1].total == 3
    assert stats[1].passing == 2
    assert stats[1].percent == 67
    assert stats[2].total == 1
    assert stats[2].passing == 1
    assert stats[2].percent == 100


def test_aggregate_by_figure_skipped_is_not_passing() -> None:
    rows = [
        _row("a", figure=1, status="skipped"),
        _row("b", figure=1, status="pass"),
    ]
    stats = aggregate_by_figure(rows)
    assert stats[0].total == 2
    assert stats[0].passing == 1


def test_aggregate_by_figure_groups_unassigned() -> None:
    rows = [
        _row("a", figure=1, status="pass"),
        _row("b", figure=None, status="pass"),
        _row("c", figure=None, status="fail"),
    ]
    stats = aggregate_by_figure(rows)
    by_label = {s.label: s for s in stats}
    assert by_label["Figure 1"].total == 1
    assert by_label["Unassigned"].total == 2
    assert by_label["Unassigned"].passing == 1


def test_aggregate_by_figure_sort_order() -> None:
    rows = [
        _row("a", figure=3),
        _row("b", figure=1),
        _row("c", figure=2),
        _row("d", figure=None),
    ]
    stats = aggregate_by_figure(rows)
    labels = [s.label for s in stats]
    assert labels == ["Figure 1", "Figure 2", "Figure 3", "Unassigned"]


def test_aggregate_by_figure_mixed_int_and_str_keys() -> None:
    """Mixed int/str figure markers must not raise (carrasco2021 regression).

    Numeric (incl. numeric strings) sort by value, then non-numeric, then
    None last.
    """
    rows = [
        _row("a", figure="Supp4"),
        _row("b", figure=2),
        _row("c", figure="10"),
        _row("d", figure=1),
        _row("e", figure=None),
        _row("f", figure="Supp1"),
    ]
    labels = [s.label for s in aggregate_by_figure(rows)]
    assert labels == [
        "Figure 1",
        "Figure 2",
        "Figure 10",
        "Figure Supp1",
        "Figure Supp4",
        "Unassigned",
    ]


def test_format_markdown_table_basic() -> None:
    stats = [
        FigureStats(figure=1, total=10, passing=10),
        FigureStats(figure=2, total=8, passing=6),
        FigureStats(figure=None, total=3, passing=3),
    ]
    output = format_markdown_table(stats)
    assert "| Figure | Deterministic tests | VLM Test |" in output
    assert "| Figure 1 | 10 total, 10 (100%) passing | — |" in output
    assert "| Figure 2 | 8 total, 6 (75%) passing | — |" in output
    assert "| Unassigned | 3 total, 3 (100%) passing | — |" in output


def test_format_markdown_table_empty_returns_placeholder() -> None:
    assert format_markdown_table([]) == "_No test runs recorded yet._"


def test_render_table_end_to_end(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_jsonl(
        log,
        [
            _row("a", figure=1, status="fail", timestamp="2026-05-12T09:00:00Z"),
            _row("a", figure=1, status="pass", timestamp="2026-05-12T10:00:00Z"),  # latest
            _row("b", figure=1, status="pass"),
            _row("c", figure=2, status="fail"),
        ],
    )
    output = render_table(log)
    assert "| Figure 1 | 2 total, 2 (100%) passing | — |" in output
    assert "| Figure 2 | 1 total, 0 (0%) passing | — |" in output


def test_render_table_missing_log(tmp_path: Path) -> None:
    output = render_table(tmp_path / "logs" / "test_runs.jsonl")
    assert output == "_No test runs recorded yet._"


def test_load_latest_verdicts_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert load_latest_verdicts(tmp_path / "figure_comparisons") == {}


def test_load_latest_verdicts_maps_passes_to_words(tmp_path: Path) -> None:
    comparisons = tmp_path / "figure_comparisons"
    _write_verdict(comparisons, "20260518T100000Z", _verdict_record("5", passes=True))
    _write_verdict(
        comparisons,
        "20260518T100000Z",
        _verdict_record("1", passes=False, recommendation="fail - blob"),
    )
    _write_verdict(
        comparisons,
        "20260518T100000Z",
        _verdict_record("7", passes=False, recommendation="needs_review - scope"),
    )
    _write_verdict(comparisons, "20260518T100000Z", _verdict_record("9", passes=None))

    verdicts = load_latest_verdicts(comparisons)
    assert verdicts["5"].verdict == "pass"
    assert verdicts["1"].verdict == "fail"
    assert verdicts["7"].verdict == "needs review"
    assert verdicts["9"].verdict == "needs review"
    assert verdicts["5"].commit == "dc4f838"


def test_load_latest_verdicts_keeps_latest_per_figure(tmp_path: Path) -> None:
    comparisons = tmp_path / "figure_comparisons"
    _write_verdict(
        comparisons,
        "20260101T000000Z",
        _verdict_record("3", passes=True, evaluated_at="2026-01-01T00:00:00Z"),
    )
    _write_verdict(
        comparisons,
        "20260518T115946Z",
        _verdict_record(
            "3",
            passes=False,
            recommendation="fail - regressed",
            evaluated_at="2026-05-18T11:59:46Z",
        ),
    )
    verdicts = load_latest_verdicts(comparisons)
    assert verdicts["3"].verdict == "fail"
    assert verdicts["3"].evaluated_at == "2026-05-18T11:59:46Z"


def test_format_markdown_table_with_verdicts() -> None:
    stats = [
        FigureStats(figure=1, total=10, passing=10),
        FigureStats(figure=5, total=6, passing=6),
        FigureStats(figure=None, total=3, passing=3),
    ]
    verdicts = {
        "1": VlmVerdict("1", "fail", "dc4f838", "2026-05-18T11:59:46Z"),
        "5": VlmVerdict("5", "pass", "dc4f838", "2026-05-18T11:59:46Z"),
    }
    output = format_markdown_table(stats, verdicts)
    assert "| Figure 1 | 10 total, 10 (100%) passing | fail (dc4f838) |" in output
    assert "| Figure 5 | 6 total, 6 (100%) passing | pass (dc4f838) |" in output
    # No verdict for the Unassigned bucket → still the placeholder dash.
    assert "| Unassigned | 3 total, 3 (100%) passing | — |" in output


def test_render_table_reads_verdicts_next_to_log(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    log = logs / "test_runs.jsonl"
    _write_jsonl(log, [_row("a", figure=1, status="pass")])
    _write_verdict(
        logs / "figure_comparisons",
        "20260518T115946Z",
        _verdict_record("1", passes=False, recommendation="fail - suppressive blob"),
    )
    output = render_table(log)
    assert "| Figure 1 | 1 total, 1 (100%) passing | fail (dc4f838) |" in output
