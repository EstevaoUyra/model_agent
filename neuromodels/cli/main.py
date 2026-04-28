from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from neuromodels.framework.judge import JudgeInput, JudgeResult, run_judge


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


if __name__ == "__main__":
    raise SystemExit(main())
