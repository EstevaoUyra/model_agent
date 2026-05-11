from __future__ import annotations

import json

from neuromodels.cli.main import main
from neuromodels.framework.compare_figures import FigureComparison


def test_cli_compare_figure_outputs_json(tmp_path, capsys, monkeypatch):
    calls = []

    def fake_compare_model_figure(model_dir, figure_number, *, model=None):
        calls.append({"model_dir": model_dir, "figure_number": figure_number, "model": model})
        return FigureComparison(
            passes=True,
            summary="Generated figure matches.",
            strengths=("same plot type",),
            issues=(),
            recommendation="pass",
            raw_response="{}",
            model=model or "fake-vlm",
            provider="fake",
        )

    monkeypatch.setattr("neuromodels.cli.main.compare_model_figure", fake_compare_model_figure)

    exit_code = main(
        [
            "compare-figure",
            "2",
            "--model-dir",
            str(tmp_path),
            "--model",
            "chosen-vlm",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passes"] is True
    assert payload["strengths"] == ["same plot type"]
    assert payload["model"] == "chosen-vlm"
    assert calls == [{"model_dir": tmp_path, "figure_number": "2", "model": "chosen-vlm"}]


def test_cli_compare_figure_outputs_markdown(tmp_path, capsys, monkeypatch):
    def fake_compare_model_figure(model_dir, figure_number, *, model=None):
        return FigureComparison(
            passes=False,
            summary="Generated figure is missing a panel.",
            strengths=(),
            issues=("missing panel",),
            recommendation="fail",
            raw_response="{}",
            model="fake-vlm",
            provider="fake",
        )

    monkeypatch.setattr("neuromodels.cli.main.compare_model_figure", fake_compare_model_figure)

    exit_code = main(
        [
            "compare-figure",
            "4",
            "--model-dir",
            str(tmp_path),
            "--output",
            "markdown",
        ]
    )

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "# Figure Comparison: fail" in out
    assert "Generated figure is missing a panel." in out
    assert "- missing panel" in out


def test_cli_compare_figure_reports_errors(tmp_path, capsys, monkeypatch):
    def fake_compare_model_figure(model_dir, figure_number, *, model=None):
        raise FileNotFoundError("figure_9_original.*")

    monkeypatch.setattr("neuromodels.cli.main.compare_model_figure", fake_compare_model_figure)

    exit_code = main(["compare-figure", "9", "--model-dir", str(tmp_path)])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "neuromodels compare-figure: error:" in err
    assert "figure_9_original" in err


def test_cli_compare_figure_packet_outputs_json(tmp_path, capsys):
    model_dir = _write_model_figure_files(tmp_path)

    exit_code = main(["compare-figure-packet", "2", "--model-dir", str(model_dir)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["figure_number"] == "2"
    assert payload["original_figure"].endswith("figure_2_original.jpg")
    assert payload["generated_figure"].endswith("figure_2.png")
    assert payload["figure_protocol"].endswith("figure_2_protocol.md")


def test_cli_compare_figure_packet_writes_file(tmp_path, capsys):
    model_dir = _write_model_figure_files(tmp_path)
    output_file = tmp_path / "figure_2_packet.json"

    exit_code = main(
        [
            "compare-figure-packet",
            "2",
            "--model-dir",
            str(model_dir),
            "--output-file",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert str(output_file) in capsys.readouterr().out
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["figure_number"] == "2"


def _write_model_figure_files(tmp_path):
    model_dir = tmp_path / "demo_model"
    original_dir = model_dir / "article_aware" / "figures"
    generated_dir = model_dir / "implementation" / "figure_outputs"
    protocol_dir = model_dir / "article_aware" / "pseudocode"
    original_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    protocol_dir.mkdir(parents=True)
    (original_dir / "figure_2_original.jpg").write_bytes(b"original")
    (generated_dir / "figure_2.png").write_bytes(b"generated")
    (protocol_dir / "figure_2_protocol.md").write_text("Expected behavior.", encoding="utf-8")
    return model_dir
