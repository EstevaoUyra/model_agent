"""Test the log_freshness.py helper script used by skills/update-state."""

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
    / "log_freshness.py"
)


def _write_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _run(log_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--log-path", str(log_path), *extra_args],
        capture_output=True,
        text=True,
    )


def test_log_freshness_emits_one_line_per_figure(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "a", "figure": 1, "status": "pass",
             "timestamp": "2026-05-12T10:00:00Z", "commit_hash": "abc12345" + "0"*32},
            {"test_id": "b", "figure": 1, "status": "pass",
             "timestamp": "2026-05-12T10:01:00Z", "commit_hash": "abc12345" + "0"*32},
            {"test_id": "c", "figure": 2, "status": "pass",
             "timestamp": "2026-05-12T10:02:00Z", "commit_hash": "def67890" + "0"*32},
        ],
    )
    result = _run(log)
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    assert lines[0].startswith("Figure 1: 2 rows, 2 distinct test_ids, latest commit abc12345")
    assert lines[1].startswith("Figure 2: 1 rows, 1 distinct test_ids, latest commit def67890")


def test_log_freshness_picks_latest_commit_by_timestamp(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "a", "figure": 1, "status": "pass",
             "timestamp": "2026-05-12T09:00:00Z", "commit_hash": "old1" + "0"*36},
            {"test_id": "a", "figure": 1, "status": "pass",
             "timestamp": "2026-05-12T10:00:00Z", "commit_hash": "new2" + "0"*36},
        ],
    )
    result = _run(log)
    assert "latest commit new20000" in result.stdout
    assert "old10000" not in result.stdout


def test_log_freshness_unassigned_bucket_last(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "x", "figure": None, "status": "pass",
             "timestamp": "z", "commit_hash": "c"},
            {"test_id": "y", "figure": 3, "status": "pass",
             "timestamp": "z", "commit_hash": "c"},
        ],
    )
    result = _run(log)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].startswith("Figure 3:")
    assert lines[1].startswith("Unassigned:")


def test_log_freshness_verbose_lists_test_ids(tmp_path: Path) -> None:
    log = tmp_path / "test_runs.jsonl"
    _write_log(
        log,
        [
            {"test_id": "alpha", "figure": 1, "status": "pass",
             "timestamp": "z", "commit_hash": "c"},
            {"test_id": "beta", "figure": 1, "status": "pass",
             "timestamp": "z", "commit_hash": "c"},
        ],
    )
    result = _run(log, "--verbose")
    assert "  - alpha" in result.stdout
    assert "  - beta" in result.stdout


def test_log_freshness_handles_missing_log(tmp_path: Path) -> None:
    result = _run(tmp_path / "nope.jsonl")
    assert result.returncode == 0
    assert "no rows" in result.stderr
