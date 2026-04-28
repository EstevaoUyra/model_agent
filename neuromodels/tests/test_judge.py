from neuromodels.framework.judge import (
    JudgeInput,
    build_attacker_prompt,
    build_defender_prompt,
    run_judge,
)
from neuromodels.framework.llm import LLMResponse


def test_prompts_include_only_the_three_review_inputs():
    judge_input = JudgeInput(
        rubric="The object must be monotonic.",
        context="Simulation output from figure 4.",
        under_review="values = [1, 2, 3]",
    )

    attacker = build_attacker_prompt(judge_input)
    defender = build_defender_prompt(judge_input)

    for prompt in (attacker, defender):
        assert prompt.count("The object must be monotonic.") == 1
        assert prompt.count("Simulation output from figure 4.") == 1
        assert prompt.count("values = [1, 2, 3]") == 1
        assert "## Rubric" in prompt
        assert "## Context" in prompt
        assert "## Under Review" in prompt
        assert "run_id" not in prompt
        assert "test_id" not in prompt
        assert "spec_ref" not in prompt
        assert "review_queue" not in prompt
        assert "citation" not in prompt.lower()

    assert "fails the rubric" in attacker
    assert "passes the rubric" in defender


def test_run_judge_calls_llm_twice_and_preserves_run_id(monkeypatch):
    calls = []

    def fake_get_llm_response(prompt, *, system_prompt=None, model=None):
        calls.append({"prompt": prompt, "system_prompt": system_prompt, "model": model})
        role = "attacker" if "fails the rubric" in prompt else "defender"
        return LLMResponse(content=f"{role} response", model=model or "fake-model", provider="fake")

    monkeypatch.setattr(
        "neuromodels.framework.llm.get_llm_response",
        fake_get_llm_response,
    )

    result = run_judge(
        JudgeInput(
            rubric="Rubric",
            context="Context",
            under_review="Object",
        ),
        run_id="run-123",
        model="chosen-model",
    )

    assert result.run_id == "run-123"
    assert result.attacker_response == "attacker response"
    assert result.defender_response == "defender response"
    assert result.attacker_metadata == {"model": "chosen-model", "provider": "fake"}
    assert result.defender_metadata == {"model": "chosen-model", "provider": "fake"}
    assert len(calls) == 2
    assert all(call["model"] == "chosen-model" for call in calls)


def test_run_judge_generates_run_id(monkeypatch):
    def fake_get_llm_response(prompt, *, system_prompt=None, model=None):
        return LLMResponse(content="response", model="fake-model", provider="fake")

    monkeypatch.setattr(
        "neuromodels.framework.llm.get_llm_response",
        fake_get_llm_response,
    )

    result = run_judge(JudgeInput(rubric="Rubric", context="Context", under_review="Object"))

    assert result.run_id
    assert result.run_id != "run-123"
