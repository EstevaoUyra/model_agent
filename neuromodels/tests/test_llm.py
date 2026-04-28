from neuromodels.framework.llm import get_llm_response


def test_fake_llm_provider_returns_without_network(monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")

    response = get_llm_response("Review this.", model="fake-model")

    assert response.provider == "fake"
    assert response.model == "fake-model"
    assert response.content.startswith("[fake llm]")


def test_llm_rejects_empty_prompt(monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")

    try:
        get_llm_response(" ")
    except ValueError as exc:
        assert "prompt must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")
