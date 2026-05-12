"""Pytest plugin that appends one row per test execution to test_runs.jsonl.

Auto-discovered via the `pytest11` entry point in pyproject.toml, so any pytest
invocation in an environment with neuromodels installed will write rows — no
per-model conftest changes required.

Output path resolution:
- Default: ``<rootdir>/logs/test_runs.jsonl``
- Override: ``--neuromodels-log-path <path>``
- Disable:  ``--neuromodels-log-path disabled``
"""

from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest


_DISABLED = "disabled"
_CONFIG_REF: pytest.Config | None = None  # captured for use in pytest_runtest_logreport


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("neuromodels")
    group.addoption(
        "--neuromodels-log-path",
        default=None,
        help=(
            "Where to write test_runs.jsonl. "
            "Default: <rootdir>/logs/test_runs.jsonl. "
            f"Pass '{_DISABLED}' to skip writing."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    for marker_line in (
        "figure(N): associate this test with figure N for test_runs.jsonl",
        "neuromodels_deterministic: deterministic Neuromodels test metadata",
        "neuromodels_claim(claim_id): qualitative or data claim identifier",
        "neuromodels_paper_issue(paper_issue): linked paper issue identifier",
    ):
        config.addinivalue_line("markers", marker_line)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    global _CONFIG_REF
    _CONFIG_REF = session.config

    rootdir = Path(session.config.rootdir)
    log_option = session.config.getoption("--neuromodels-log-path")
    if log_option == _DISABLED:
        log_path: Path | None = None
    elif log_option:
        log_path = Path(log_option)
    else:
        log_path = rootdir / "logs" / "test_runs.jsonl"

    session.config._neuromodels_state = {
        "session_id": str(uuid.uuid4()),
        "session_started": datetime.now(timezone.utc).isoformat(),
        "commit_hash": _git_head(rootdir),
        "spec_commit_hash": _git_tree_hash(rootdir, "article_aware"),
        "log_path": log_path,
        "nodeid_figure": {},
    }


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    state = getattr(config, "_neuromodels_state", None)
    if state is None:
        return
    figure_by_nodeid = state["nodeid_figure"]
    for item in items:
        marker = item.get_closest_marker("figure")
        if marker is None or not marker.args:
            continue
        figure_by_nodeid[item.nodeid] = marker.args[0]


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if not _should_record(report):
        return
    config = _CONFIG_REF
    state = getattr(config, "_neuromodels_state", None) if config else None
    if state is None or state["log_path"] is None:
        return

    row = {
        "run_id": str(uuid.uuid4()),
        "session_id": state["session_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_id": report.nodeid,
        "figure": state["nodeid_figure"].get(report.nodeid),
        "status": _status_from_report(report),
        "commit_hash": state["commit_hash"],
        "spec_commit_hash": state["spec_commit_hash"],
        "failure_message": _failure_message(report),
        "agent_rationale": None,
    }

    log_path: Path = state["log_path"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _should_record(report: pytest.TestReport) -> bool:
    if report.when == "call":
        return True
    if report.when == "setup" and (report.failed or report.skipped):
        return True
    return False


def _status_from_report(report: pytest.TestReport) -> str:
    if report.when == "setup" and report.failed:
        return "error"
    if report.skipped:
        return "skipped"
    if report.failed:
        return "fail"
    if report.passed:
        return "pass"
    return "unknown"


def _failure_message(report: pytest.TestReport) -> str | None:
    if report.passed or report.skipped:
        return None
    longrepr = report.longrepr
    if longrepr is None:
        return None
    reprcrash = getattr(longrepr, "reprcrash", None)
    if reprcrash is not None and getattr(reprcrash, "message", None):
        return reprcrash.message.splitlines()[0]
    text = str(longrepr).strip()
    if not text:
        return None
    return text.splitlines()[-1]


def _git_head(cwd: Path) -> str | None:
    return _run_git(cwd, ["rev-parse", "HEAD"])


def _git_tree_hash(cwd: Path, subpath: str) -> str | None:
    if not (cwd / subpath).exists():
        return None
    return _run_git(cwd, ["rev-parse", f"HEAD:{subpath}"])


def _run_git(cwd: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None
