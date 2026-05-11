from __future__ import annotations

from neuromodels.framework.compare_figures import (
    FigureComparison,
    build_model_figure_packet,
    build_comparison_prompt,
    compare_figures,
    parse_comparison_response,
    resolve_figure_inputs,
    write_model_figure_packet,
)
from neuromodels.framework.llm import LLMResponse


def test_build_comparison_prompt_mentions_inputs(tmp_path):
    original = tmp_path / "original.png"
    generated = tmp_path / "generated.png"

    prompt = build_comparison_prompt(
        original_path=original,
        generated_path=generated,
        figure_protocol="Expected behavior: generated curve is monotonic.",
    )

    assert str(original) in prompt
    assert str(generated) in prompt
    assert "Expected behavior" in prompt
    assert "Return only valid JSON" in prompt


def test_parse_comparison_response_accepts_json_fence():
    parsed = parse_comparison_response(
        """```json
{"passes": true, "summary": "Matches.", "strengths": ["same trend"], "issues": [], "recommendation": "pass"}
```""",
        model="m",
        provider="p",
    )

    assert parsed == FigureComparison(
        passes=True,
        summary="Matches.",
        strengths=("same trend",),
        issues=(),
        recommendation="pass",
        raw_response="""```json
{"passes": true, "summary": "Matches.", "strengths": ["same trend"], "issues": [], "recommendation": "pass"}
```""",
        model="m",
        provider="p",
    )


def test_parse_comparison_response_handles_non_json():
    parsed = parse_comparison_response("looks okay", model="m", provider="p")

    assert parsed.passes is None
    assert parsed.summary == "looks okay"
    assert parsed.recommendation == "needs_review"
    assert parsed.issues == ("VLM response was not valid JSON.",)


def test_compare_figures_delegates_to_llm(tmp_path, monkeypatch):
    original = tmp_path / "original.png"
    generated = tmp_path / "generated.png"
    protocol = tmp_path / "protocol.md"
    original.write_bytes(b"original")
    generated.write_bytes(b"generated")
    protocol.write_text("Expected behavior: generated curve is monotonic.", encoding="utf-8")
    calls = []

    def fake_get_vision_response(prompt, image_paths, *, system_prompt=None, model=None):
        calls.append(
            {
                "prompt": prompt,
                "image_paths": image_paths,
                "system_prompt": system_prompt,
                "model": model,
            }
        )
        return LLMResponse(
            content='{"passes": false, "summary": "Missing panel.", "strengths": [], "issues": ["missing panel"], "recommendation": "fail"}',
            model=model or "fake-vlm",
            provider="fake",
        )

    monkeypatch.setattr(
        "neuromodels.framework.llm.get_vision_response",
        fake_get_vision_response,
    )

    result = compare_figures(original, generated, protocol, model="chosen-vlm")

    assert result.passes is False
    assert result.issues == ("missing panel",)
    assert result.model == "chosen-vlm"
    assert len(calls) == 1
    assert calls[0]["image_paths"] == [original, generated]
    assert calls[0]["model"] == "chosen-vlm"


def test_resolve_figure_inputs_uses_model_conventions(tmp_path):
    model_dir = _write_model_figure_files(tmp_path)

    inputs = resolve_figure_inputs(model_dir, "figure_2")

    assert inputs.original_figure == model_dir / "article_aware" / "figures" / "figure_2_original.jpg"
    assert inputs.generated_figure == model_dir / "implementation" / "figure_outputs" / "figure_2.png"
    assert inputs.figure_protocol == model_dir / "article_aware" / "pseudocode" / "figure_2_protocol.md"


def test_build_and_write_model_figure_packet(tmp_path):
    model_dir = _write_model_figure_files(tmp_path)

    packet = build_model_figure_packet(model_dir, "2")

    assert packet.figure_number == "2"
    assert packet.to_dict()["original_figure"].endswith("figure_2_original.jpg")
    assert "Return only valid JSON" in packet.rubric

    output_path = tmp_path / "packets" / "figure_2.json"
    written = write_model_figure_packet(model_dir, 2, output_path)

    assert written == output_path
    assert '"figure_number": "2"' in output_path.read_text(encoding="utf-8")


def _write_model_figure_files(tmp_path):
    model_dir = tmp_path / "demo_model"
    original_dir = model_dir / "article_aware" / "figures"
    generated_dir = model_dir / "implementation" / "figure_outputs"
    protocol_dir = model_dir / "article_aware" / "pseudocode"
    original_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    protocol_dir.mkdir(parents=True)
    original = original_dir / "figure_2_original.jpg"
    generated = generated_dir / "figure_2.png"
    protocol = protocol_dir / "figure_2_protocol.md"
    original.write_bytes(b"original")
    generated.write_bytes(b"generated")
    protocol.write_text("Expected behavior.", encoding="utf-8")
    return model_dir
