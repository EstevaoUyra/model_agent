#!/usr/bin/env python3
"""Print the latest failing tests from logs/test_runs.jsonl.

For each test_id, only the latest row (by timestamp) is considered.
Rows with status != "pass" are printed, one per line:

    <status>: <test_id> | figure=<N or None> | <failure_message>

Usage (from model directory):
    python skills/update-state/scripts/failing_tests.py
    python skills/update-state/scripts/failing_tests.py --log-path <path>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from neuromodels.framework.test_table import latest_per_test, load_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("logs/test_runs.jsonl"),
        help="Path to test_runs.jsonl (default: logs/test_runs.jsonl relative to cwd)",
    )
    args = parser.parse_args(argv)

    rows = load_rows(args.log_path)
    if not rows:
        print(f"(no rows in {args.log_path})", file=sys.stderr)
        return 0

    failing = [r for r in latest_per_test(rows) if r.get("status") != "pass"]
    if not failing:
        print("(no failing tests)")
        return 0

    for row in sorted(failing, key=lambda r: (r.get("figure") or 0, r.get("test_id", ""))):
        status = row.get("status", "?")
        test_id = row.get("test_id", "?")
        figure = row.get("figure")
        message = row.get("failure_message") or ""
        print(f"{status}: {test_id} | figure={figure} | {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
