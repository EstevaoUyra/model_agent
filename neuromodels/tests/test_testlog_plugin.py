"""Tests for the test_runs.jsonl logging plugin.

Each test invokes pytest as a subprocess in an isolated tmp dir, then reads
the JSONL output and asserts on the row contents.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_pytest(cwd: Path, *args: str, log_path: Path | None = None) -> subprocess.CompletedProcess:
    cli = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args]
    if log_path is not None:
        cli.extend(["--neuromodels-log-path", str(log_path)])
    return subprocess.run(cli, cwd=cwd, capture_output=True, text=True)


def _read_rows(log_path: Path) -> list[dict]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_plugin_writes_one_row_per_test(tmp_path: Path) -> None:
    test_file = tmp_path / "test_dummy.py"
    test_file.write_text("def test_a(): pass\ndef test_b(): pass\n", encoding="utf-8")
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=log_path)
    assert result.returncode == 0, result.stdout + result.stderr

    rows = _read_rows(log_path)
    assert len(rows) == 2
    statuses = sorted(r["status"] for r in rows)
    assert statuses == ["pass", "pass"]
    test_ids = sorted(r["test_id"] for r in rows)
    assert test_ids == ["test_dummy.py::test_a", "test_dummy.py::test_b"]


def test_plugin_records_failure_message(tmp_path: Path) -> None:
    test_file = tmp_path / "test_fail.py"
    test_file.write_text(
        "def test_fails():\n    assert 1 + 1 == 3, 'arithmetic broke'\n",
        encoding="utf-8",
    )
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=log_path)
    assert result.returncode == 1, result.stdout + result.stderr

    rows = _read_rows(log_path)
    assert len(rows) == 1
    assert rows[0]["status"] == "fail"
    assert rows[0]["failure_message"] is not None
    assert "arithmetic broke" in rows[0]["failure_message"]


def test_plugin_reads_figure_marker(tmp_path: Path) -> None:
    test_file = tmp_path / "test_marked.py"
    test_file.write_text(
        "import pytest\n"
        "@pytest.mark.figure(4)\n"
        "def test_marked(): pass\n"
        "def test_unmarked(): pass\n",
        encoding="utf-8",
    )
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=log_path)
    assert result.returncode == 0, result.stdout + result.stderr

    rows = {r["test_id"]: r for r in _read_rows(log_path)}
    assert rows["test_marked.py::test_marked"]["figure"] == 4
    assert rows["test_marked.py::test_unmarked"]["figure"] is None


def test_plugin_disable_via_option(tmp_path: Path) -> None:
    test_file = tmp_path / "test_off.py"
    test_file.write_text("def test_ok(): pass\n", encoding="utf-8")
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=Path("disabled"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert not log_path.exists()


def test_plugin_default_log_path_uses_rootdir(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    test_file = tmp_path / "test_default.py"
    test_file.write_text("def test_ok(): pass\n", encoding="utf-8")

    result = _run_pytest(tmp_path, str(test_file))
    assert result.returncode == 0, result.stdout + result.stderr

    default_log = tmp_path / "logs" / "test_runs.jsonl"
    assert default_log.exists(), f"expected default log at {default_log}, stdout={result.stdout}"
    rows = _read_rows(default_log)
    assert len(rows) == 1
    assert rows[0]["test_id"] == "test_default.py::test_ok"


def test_plugin_row_has_required_fields(tmp_path: Path) -> None:
    test_file = tmp_path / "test_fields.py"
    test_file.write_text("def test_ok(): pass\n", encoding="utf-8")
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=log_path)
    assert result.returncode == 0, result.stdout + result.stderr

    rows = _read_rows(log_path)
    assert len(rows) == 1
    row = rows[0]
    required_fields = {
        "run_id",
        "session_id",
        "timestamp",
        "test_id",
        "figure",
        "status",
        "commit_hash",
        "spec_commit_hash",
        "failure_message",
        "agent_rationale",
    }
    assert required_fields.issubset(row.keys()), f"missing: {required_fields - row.keys()}"


def test_plugin_session_id_shared_across_rows(tmp_path: Path) -> None:
    test_file = tmp_path / "test_session.py"
    test_file.write_text("def test_a(): pass\ndef test_b(): pass\n", encoding="utf-8")
    log_path = tmp_path / "logs" / "test_runs.jsonl"

    result = _run_pytest(tmp_path, str(test_file), log_path=log_path)
    assert result.returncode == 0, result.stdout + result.stderr

    rows = _read_rows(log_path)
    assert len({r["session_id"] for r in rows}) == 1
    assert len({r["run_id"] for r in rows}) == 2  # run_id unique per test
