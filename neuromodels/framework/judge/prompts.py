from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neuromodels.framework.judge.core import JudgeInput


ATTACKER_INSTRUCTION = (
    "Find concrete reasons why the under-review object fails the rubric. "
    "If you cannot find a substantive failure, say so."
)

DEFENDER_INSTRUCTION = (
    "Find concrete reasons why the under-review object passes the rubric. "
    "Acknowledge genuine ambiguities."
)


def build_attacker_prompt(judge_input: JudgeInput) -> str:
    return _build_prompt(ATTACKER_INSTRUCTION, judge_input)


def build_defender_prompt(judge_input: JudgeInput) -> str:
    return _build_prompt(DEFENDER_INSTRUCTION, judge_input)


def _build_prompt(instruction: str, judge_input: JudgeInput) -> str:
    return "\n\n".join(
        [
            instruction,
            "## Rubric",
            judge_input.rubric.strip(),
            "## Context",
            judge_input.context.strip(),
            "## Under Review",
            judge_input.under_review.strip(),
        ]
    )
