from neuromodels.framework.llm import get_llm_response, get_vision_response


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


def test_fake_vision_provider_returns_without_network(tmp_path, monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")
    image = tmp_path / "figure.png"
    image.write_bytes(b"not really an image")

    response = get_vision_response("Compare these.", [image], model="fake-vlm")

    assert response.provider == "fake"
    assert response.model == "fake-vlm"
    assert response.content.startswith("[fake vlm]")
    assert "1 image" in response.content


def test_vision_response_requires_prompt_and_images(tmp_path, monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")
    image = tmp_path / "figure.png"
    image.write_bytes(b"not really an image")

    try:
        get_vision_response(" ", [image])
    except ValueError as exc:
        assert "prompt must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    try:
        get_vision_response("Compare.", [])
    except ValueError as exc:
        assert "at least one image path" in str(exc)
    else:
        raise AssertionError("expected ValueError")
