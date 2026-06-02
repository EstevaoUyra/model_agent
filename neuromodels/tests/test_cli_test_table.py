from __future__ import annotations

import json
from pathlib import Path

from neuromodels.cli.main import main


def _write_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_cli_test_table_default_log_path(tmp_path: Path, capsys) -> None:
    log = tmp_path / "logs" / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "a", "figure": 1, "status": "pass", "timestamp": "z"},
            {"test_id": "b", "figure": 1, "status": "fail", "timestamp": "z"},
        ],
    )
    exit_code = main(["test-table", "--model-dir", str(tmp_path)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "| Figure 1 | 2 total, 1 (50%) passing | — |" in out


def test_cli_test_table_missing_log_emits_placeholder(tmp_path: Path, capsys) -> None:
    exit_code = main(["test-table", "--model-dir", str(tmp_path)])
    assert exit_code == 0
    assert "_No test runs recorded yet._" in capsys.readouterr().out


def test_cli_test_table_log_path_override(tmp_path: Path, capsys) -> None:
    custom = tmp_path / "elsewhere" / "runs.jsonl"
    _write_log(
        custom,
        [{"test_id": "a", "figure": 7, "status": "pass", "timestamp": "z"}],
    )
    exit_code = main(["test-table", "--log-path", str(custom)])
    assert exit_code == 0
    assert "| Figure 7 | 1 total, 1 (100%) passing | — |" in capsys.readouterr().out


def test_cli_test_table_populates_vlm_column(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    _write_log(
        logs / "test_runs.jsonl",
        [{"test_id": "a", "figure": 5, "status": "pass", "timestamp": "z"}],
    )
    comparisons = logs / "figure_comparisons"
    comparisons.mkdir(parents=True, exist_ok=True)
    (comparisons / "figure_5_20260518T115946Z.json").write_text(
        json.dumps(
            {
                "figure_number": "5",
                "model_commit_hash": "dc4f8382998be0fd850219d3457965c63ad1e6d7",
                "evaluated_at": "2026-05-18T11:59:46Z",
                "verdict": {"passes": True, "recommendation": "pass - scaling"},
            }
        ),
        encoding="utf-8",
    )
    exit_code = main(["test-table", "--model-dir", str(tmp_path)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "| Figure 5 | 1 total, 1 (100%) passing | pass (dc4f838) |" in out


def test_cli_test_table_comparisons_dir_override(tmp_path: Path, capsys) -> None:
    log = tmp_path / "logs" / "test_runs.jsonl"
    _write_log(log, [{"test_id": "a", "figure": 1, "status": "pass", "timestamp": "z"}])
    custom = tmp_path / "verdicts"
    custom.mkdir(parents=True, exist_ok=True)
    (custom / "figure_1_20260518T115946Z.json").write_text(
        json.dumps(
            {
                "figure_number": "1",
                "model_commit_hash": "dc4f8382998be0fd850219d3457965c63ad1e6d7",
                "evaluated_at": "2026-05-18T11:59:46Z",
                "verdict": {"passes": False, "recommendation": "fail - blob"},
            }
        ),
        encoding="utf-8",
    )
    exit_code = main(
        ["test-table", "--model-dir", str(tmp_path), "--comparisons-dir", str(custom)]
    )
    assert exit_code == 0
    assert "| Figure 1 | 1 total, 1 (100%) passing | fail (dc4f838) |" in capsys.readouterr().out
