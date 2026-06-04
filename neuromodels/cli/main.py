from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from neuromodels.framework.compare_figures import (
    FigureComparison,
    build_model_figure_packet,
    compare_model_figure,
    write_model_figure_packet,
)
from neuromodels.framework.judge import JudgeInput, JudgeResult, run_judge
from neuromodels.framework.provenance import build_provenance, render_markdown as render_provenance
from neuromodels.framework.test_table import render_table


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="neuromodels")
    subparsers = parser.add_subparsers(dest="command")

    judge_parser = subparsers.add_parser("judge", help="Adversarial judge tools")
    judge_subparsers = judge_parser.add_subparsers(dest="judge_command")

    run_parser = judge_subparsers.add_parser("run", help="Run a basic adversarial judge")
    run_parser.add_argument("--rubric-file", required=True, type=Path)
    run_parser.add_argument("--context-file", required=True, type=Path)
    run_parser.add_argument("--under-review-file", required=True, type=Path)
    run_parser.add_argument("--run-id")
    run_parser.add_argument("--model")
    run_parser.add_argument("--output", choices=["json", "markdown"], default="json")
    run_parser.set_defaults(func=run_judge_command)

    compare_parser = subparsers.add_parser(
        "compare-figure",
        help="Compare an original article figure against a generated model figure",
    )
    compare_parser.add_argument("figure_number", help="Figure number, e.g. 1 or 7")
    compare_parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path.cwd(),
        help="Model directory containing article_aware/ and implementation/",
    )
    compare_parser.add_argument("--model", help="Optional VLM model override")
    compare_parser.add_argument("--output", choices=["json", "markdown"], default="json")
    compare_parser.set_defaults(func=run_compare_figure_command)

    packet_parser = subparsers.add_parser(
        "compare-figure-packet",
        help="Write or print a path-only packet for isolated figure comparison",
    )
    packet_parser.add_argument("figure_number", help="Figure number, e.g. 1 or 7")
    packet_parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path.cwd(),
        help="Model directory containing article_aware/ and implementation/",
    )
    packet_parser.add_argument(
        "--output-file",
        type=Path,
        help="Write packet JSON to this path instead of stdout",
    )
    packet_parser.set_defaults(func=run_compare_figure_packet_command)

    table_parser = subparsers.add_parser(
        "test-table",
        help="Render the per-figure test status table from logs/test_runs.jsonl",
    )
    table_parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path.cwd(),
        help="Model directory containing logs/test_runs.jsonl",
    )
    table_parser.add_argument(
        "--log-path",
        type=Path,
        help="Override path to test_runs.jsonl (default: <model-dir>/logs/test_runs.jsonl)",
    )
    table_parser.add_argument(
        "--comparisons-dir",
        type=Path,
        help=(
            "Override path to the VLM figure-comparison verdicts directory "
            "(default: <log-path parent>/figure_comparisons)"
        ),
    )
    table_parser.set_defaults(func=run_test_table_command)

    prov_parser = subparsers.add_parser(
        "provenance",
        help="Bucket calibrated values by source (paper / paper+code / code-alone / assumption)",
    )
    prov_parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path.cwd(),
        help="Model directory containing article_aware/spec/calibration.yaml",
    )
    prov_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    prov_parser.set_defaults(func=run_provenance_command)

    return parser


def run_judge_command(args: argparse.Namespace) -> int:
    try:
        judge_input = JudgeInput(
            rubric=_read_required(args.rubric_file),
            context=_read_required(args.context_file),
            under_review=_read_required(args.under_review_file),
        )
        result = run_judge(judge_input, run_id=args.run_id, model=args.model)
    except Exception as exc:
        print(f"neuromodels judge run: error: {exc}", file=sys.stderr)
        return 1

    if args.output == "markdown":
        print(_render_markdown(result))
    else:
        print(json.dumps(_result_to_dict(result), indent=2))
    return 0


def run_compare_figure_command(args: argparse.Namespace) -> int:
    try:
        result = compare_model_figure(
            args.model_dir,
            args.figure_number,
            model=args.model,
        )
    except Exception as exc:
        print(f"neuromodels compare-figure: error: {exc}", file=sys.stderr)
        return 1

    if args.output == "markdown":
        print(_render_figure_comparison_markdown(result))
    else:
        print(json.dumps(asdict(result), indent=2))
    return 0


def run_compare_figure_packet_command(args: argparse.Namespace) -> int:
    try:
        if args.output_file:
            path = write_model_figure_packet(
                args.model_dir,
                args.figure_number,
                args.output_file,
            )
            print(path)
        else:
            packet = build_model_figure_packet(args.model_dir, args.figure_number)
            print(json.dumps(packet.to_dict(), indent=2))
    except Exception as exc:
        print(f"neuromodels compare-figure-packet: error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_test_table_command(args: argparse.Namespace) -> int:
    log_path = args.log_path or (args.model_dir / "logs" / "test_runs.jsonl")
    try:
        print(render_table(log_path, args.comparisons_dir))
    except Exception as exc:
        print(f"neuromodels test-table: error: {exc}", file=sys.stderr)
        return 1
    return 0


def run_provenance_command(args: argparse.Namespace) -> int:
    try:
        report = build_provenance(args.model_dir)
    except Exception as exc:
        print(f"neuromodels provenance: error: {exc}", file=sys.stderr)
        return 1
    if args.output == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_provenance(report))
    return 0


def _read_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _result_to_dict(result: JudgeResult) -> dict[str, object]:
    data = asdict(result)
    created_at = data["created_at"]
    if isinstance(created_at, datetime):
        data["created_at"] = created_at.isoformat()
    return data


def _render_markdown(result: JudgeResult) -> str:
    return "\n".join(
        [
            f"# Judge Run {result.run_id}",
            "",
            "## Attacker",
            "",
            result.attacker_response.rstrip(),
            "",
            "## Defender",
            "",
            result.defender_response.rstrip(),
            "",
            "## Metadata",
            "",
            f"- Created at: {result.created_at.isoformat()}",
            f"- Attacker model: {result.attacker_metadata['model']}",
            f"- Attacker provider: {result.attacker_metadata['provider']}",
            f"- Defender model: {result.defender_metadata['model']}",
            f"- Defender provider: {result.defender_metadata['provider']}",
        ]
    )


def _render_figure_comparison_markdown(result: FigureComparison) -> str:
    verdict = "needs_review" if result.passes is None else ("pass" if result.passes else "fail")
    lines = [
        f"# Figure Comparison: {verdict}",
        "",
        result.summary.rstrip(),
        "",
    ]

    if result.checklist_results:
        lines.extend(["## Checklist Results", ""])
        for item in result.checklist_results:
            prefix = item.split(":")[0].upper()
            marker = {"PASS": "✓", "FAIL": "✗", "UNSURE": "?"}.get(prefix, "-")
            lines.append(f"- [{marker}] {item}")
        lines.append("")

    lines.extend(["## Issues", ""])
    lines.extend(f"- {item}" for item in result.issues)
    if not result.issues:
        lines.append("- <none reported>")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            result.recommendation,
            "",
            "## Metadata",
            "",
            f"- Model: {result.model}",
            f"- Provider: {result.provider}",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
