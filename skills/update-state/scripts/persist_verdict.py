"""Wrap one VLM subagent verdict with provenance and persist it.

The update-state VLM step spawns a subagent per figure that returns a
FigureComparison-shaped JSON object (passes / summary / checklist_results /
issues / recommendation). This script stamps that object with the metadata
the skill's reflection and `neuromodels test-table` need — most importantly
the model commit the verdict was recorded against, so a later run can tell a
fresh verdict from a stale one — and writes it to the persistent home:

    <model-dir>/logs/figure_comparisons/figure_<N>_<UTCstamp>.json

Usage:
    python persist_verdict.py \
        --model-dir models/<model> \
        --figure 1 \
        --packet /tmp/<model>_figure_packets/figure_1.json \
        --verdict-file /tmp/figure_1_verdict.json \
        [--n-subagents 3] \
        [--adjudication "parent confirmed by direct image read: ..."]

`--verdict-file` may be `-` to read the verdict JSON from stdin. The verdict
JSON must parse; this script does not repair malformed model output.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _git_head(model_dir: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(model_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _load_verdict(verdict_file: str) -> dict:
    raw = sys.stdin.read() if verdict_file == "-" else Path(verdict_file).read_text(
        encoding="utf-8"
    )
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--figure", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--verdict-file", required=True)
    parser.add_argument("--n-subagents", type=int, default=1)
    parser.add_argument(
        "--adjudication",
        default="",
        help="Parent-agent note when a det/VLM disagreement was cross-checked.",
    )
    parser.add_argument(
        "--evaluator",
        default="claude VLM subagent (compare-figure-packet)",
    )
    args = parser.parse_args(argv)

    model_dir = args.model_dir
    figure = str(args.figure).strip()
    verdict = _load_verdict(args.verdict_file)

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    record = {
        "figure_number": figure,
        "model_dir": str(model_dir),
        "model_commit_hash": _git_head(model_dir),
        "evaluated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evaluator": args.evaluator,
        "packet_path": args.packet,
        "n_subagents": args.n_subagents,
        "parent_adjudication": args.adjudication,
        "verdict": verdict,
    }

    out_dir = model_dir / "logs" / "figure_comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"figure_{figure}_{stamp}.json"
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
