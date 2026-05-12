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
