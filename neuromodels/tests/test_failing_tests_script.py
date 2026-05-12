"""Test the failing_tests.py helper script used by skills/update-state."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).parent.parent.parent
    / "skills"
    / "update-state"
    / "scripts"
    / "failing_tests.py"
)


def _write_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _run(log_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--log-path", str(log_path)],
        capture_output=True,
        text=True,
    )


def test_failing_tests_emits_only_failing_rows(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "a", "figure": 1, "status": "pass", "timestamp": "z",
             "failure_message": None},
            {"test_id": "b", "figure": 2, "status": "fail", "timestamp": "z",
             "failure_message": "assert x > y"},
        ],
    )
    result = _run(log)
    assert result.returncode == 0
    assert "test_id" not in result.stdout or "::a" not in result.stdout
    assert "fail: b" in result.stdout
    assert "assert x > y" in result.stdout


def test_failing_tests_keeps_only_latest_per_id(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "a", "figure": 1, "status": "fail",
             "timestamp": "2026-05-12T09:00:00Z", "failure_message": "old"},
            {"test_id": "a", "figure": 1, "status": "pass",
             "timestamp": "2026-05-12T10:00:00Z", "failure_message": None},
        ],
    )
    result = _run(log)
    assert result.returncode == 0
    assert "(no failing tests)" in result.stdout


def test_failing_tests_handles_missing_log(tmp_path: Path) -> None:
    result = _run(tmp_path / "missing.jsonl")
    assert result.returncode == 0
    assert "no rows" in result.stderr


def test_failing_tests_sorts_by_figure_then_test_id(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "c_test", "figure": 1, "status": "fail",
             "timestamp": "z", "failure_message": "x"},
            {"test_id": "a_test", "figure": 2, "status": "fail",
             "timestamp": "z", "failure_message": "x"},
            {"test_id": "b_test", "figure": 1, "status": "fail",
             "timestamp": "z", "failure_message": "x"},
        ],
    )
    result = _run(log)
    lines = [line for line in result.stdout.splitlines() if line.startswith("fail:")]
    # figure=1 before figure=2; within figure=1, alphabetical
    assert lines[0].startswith("fail: b_test")
    assert lines[1].startswith("fail: c_test")
    assert lines[2].startswith("fail: a_test")
