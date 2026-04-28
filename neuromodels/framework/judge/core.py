from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

import neuromodels.framework.llm as llm
from neuromodels.framework.judge.prompts import build_attacker_prompt, build_defender_prompt


@dataclass(frozen=True)
class JudgeInput:
    """The only material sent to the attacker and defender."""

    rubric: str
    context: str
    under_review: str

    def __post_init__(self) -> None:
        missing = [
            name
            for name, value in {
                "rubric": self.rubric,
                "context": self.context,
                "under_review": self.under_review,
            }.items()
            if not value.strip()
        ]
        if missing:
            raise ValueError(f"missing required judge input(s): {', '.join(missing)}")


@dataclass(frozen=True)
class JudgeResult:
    run_id: str
    attacker_response: str
    defender_response: str
    created_at: datetime
    attacker_metadata: dict[str, str]
    defender_metadata: dict[str, str]


def run_judge(
    judge_input: JudgeInput,
    *,
    run_id: str | None = None,
    model: str | None = None,
) -> JudgeResult:
    """Run attacker and defender reviews and return responses with metadata."""

    attacker = llm.get_llm_response(build_attacker_prompt(judge_input), model=model)
    defender = llm.get_llm_response(build_defender_prompt(judge_input), model=model)

    return JudgeResult(
        run_id=run_id or str(uuid4()),
        attacker_response=attacker.content,
        defender_response=defender.content,
        created_at=datetime.now(timezone.utc),
        attacker_metadata={"model": attacker.model, "provider": attacker.provider},
        defender_metadata={"model": defender.model, "provider": defender.provider},
    )
