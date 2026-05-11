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
        figure_description="Expected behavior: generated curve is monotonic.",
        figure_checklist="- [ ] The curve is monotonically increasing.",
    )

    assert str(original) in prompt
    assert str(generated) in prompt
    assert "Expected behavior" in prompt
    assert "monotonically increasing" in prompt
    assert "Return valid JSON" in prompt


def test_parse_comparison_response_accepts_json_fence():
    raw = '''```json
{"passes": true, "summary": "Matches.", "checklist_results": [{"item": "curve present", "result": "pass", "note": ""}], "issues": [], "recommendation": "pass"}
```'''
    parsed = parse_comparison_response(raw, model="m", provider="p")

    assert parsed.passes is True
    assert parsed.summary == "Matches."
    assert parsed.checklist_results == ("PASS: curve present",)
    assert parsed.issues == ()
    assert parsed.recommendation == "pass"


def test_parse_comparison_response_checklist_result_with_note():
    raw = '{"passes": false, "summary": "Bad.", "checklist_results": [{"item": "curve shifted left", "result": "fail", "note": "no shift visible"}], "issues": ["curve shifted left"], "recommendation": "fail"}'
    parsed = parse_comparison_response(raw, model="m", provider="p")

    assert parsed.passes is False
    assert parsed.checklist_results == ("FAIL: curve shifted left — no shift visible",)


def test_parse_comparison_response_handles_non_json():
    parsed = parse_comparison_response("looks okay", model="m", provider="p")

    assert parsed.passes is None
    assert parsed.summary == "looks okay"
    assert parsed.recommendation == "needs_review"
    assert parsed.issues == ("VLM response was not valid JSON.",)
    assert parsed.checklist_results == ()


def test_compare_figures_delegates_to_llm(tmp_path, monkeypatch):
    original = tmp_path / "original.png"
    generated = tmp_path / "generated.png"
    description = tmp_path / "figure_2.md"
    checklist = tmp_path / "figure_2_visual_checklist.md"
    original.write_bytes(b"original")
    generated.write_bytes(b"generated")
    description.write_text("Expected behavior: generated curve is monotonic.", encoding="utf-8")
    checklist.write_text("- [ ] The curve is monotonically increasing.", encoding="utf-8")
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
            content='{"passes": false, "summary": "Missing panel.", "checklist_results": [], "issues": ["missing panel"], "recommendation": "fail"}',
            model=model or "fake-vlm",
            provider="fake",
        )

    monkeypatch.setattr(
        "neuromodels.framework.llm.get_vision_response",
        fake_get_vision_response,
    )

    result = compare_figures(original, generated, description, checklist, model="chosen-vlm")

    assert result.passes is False
    assert result.issues == ("missing panel",)
    assert result.model == "chosen-vlm"
    assert len(calls) == 1
    assert calls[0]["image_paths"] == [original, generated]
    assert calls[0]["model"] == "chosen-vlm"


def test_resolve_figure_inputs_uses_model_conventions(tmp_path):
    model_dir = _write_model_figure_files(tmp_path)

    inputs = resolve_figure_inputs(model_dir, "figure_2")

    assert inputs.original_figure == model_dir / "article_aware" / "figures" / "figure_2.jpg"
    assert inputs.generated_figure == model_dir / "implementation" / "figure_outputs" / "figure_2.png"
    assert inputs.figure_description == model_dir / "article_aware" / "figures" / "figure_2.md"
    assert inputs.figure_checklist == model_dir / "article_aware" / "figures" / "figure_2_visual_checklist.md"


def test_build_and_write_model_figure_packet(tmp_path):
    model_dir = _write_model_figure_files(tmp_path)

    packet = build_model_figure_packet(model_dir, "2")

    assert packet.figure_number == "2"
    assert packet.to_dict()["original_figure"].endswith("figure_2.jpg")
    assert packet.to_dict()["figure_description"].endswith("figure_2.md")
    assert packet.to_dict()["figure_checklist"].endswith("figure_2_visual_checklist.md")

    output_path = tmp_path / "packets" / "figure_2.json"
    written = write_model_figure_packet(model_dir, 2, output_path)

    assert written == output_path
    assert '"figure_number": "2"' in output_path.read_text(encoding="utf-8")


def _write_model_figure_files(tmp_path):
    model_dir = tmp_path / "demo_model"
    figures_dir = model_dir / "article_aware" / "figures"
    generated_dir = model_dir / "implementation" / "figure_outputs"
    figures_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (figures_dir / "figure_2.jpg").write_bytes(b"original")
    (generated_dir / "figure_2.png").write_bytes(b"generated")
    (figures_dir / "figure_2.md").write_text("Figure description.", encoding="utf-8")
    (figures_dir / "figure_2_visual_checklist.md").write_text("- [ ] Curve is present.", encoding="utf-8")
    return model_dir
