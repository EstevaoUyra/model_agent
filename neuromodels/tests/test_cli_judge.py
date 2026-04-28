import json

from neuromodels.cli.main import main


def test_cli_outputs_json_for_three_input_files(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")
    rubric = tmp_path / "rubric.txt"
    context = tmp_path / "context.txt"
    under_review = tmp_path / "under_review.txt"
    rubric.write_text("Must be monotonic.", encoding="utf-8")
    context.write_text("Figure output.", encoding="utf-8")
    under_review.write_text("[1, 2, 3]", encoding="utf-8")

    exit_code = main(
        [
            "judge",
            "run",
            "--rubric-file",
            str(rubric),
            "--context-file",
            str(context),
            "--under-review-file",
            str(under_review),
            "--run-id",
            "cli-run",
            "--model",
            "fake-model",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["run_id"] == "cli-run"
    assert payload["attacker_metadata"] == {"model": "fake-model", "provider": "fake"}
    assert payload["defender_metadata"] == {"model": "fake-model", "provider": "fake"}
    assert payload["attacker_response"].startswith("[fake llm]")
    assert payload["defender_response"].startswith("[fake llm]")


def test_cli_outputs_markdown(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")
    rubric = tmp_path / "rubric.txt"
    context = tmp_path / "context.txt"
    under_review = tmp_path / "under_review.txt"
    rubric.write_text("Must be monotonic.", encoding="utf-8")
    context.write_text("Figure output.", encoding="utf-8")
    under_review.write_text("[1, 2, 3]", encoding="utf-8")

    exit_code = main(
        [
            "judge",
            "run",
            "--rubric-file",
            str(rubric),
            "--context-file",
            str(context),
            "--under-review-file",
            str(under_review),
            "--run-id",
            "cli-run",
            "--output",
            "markdown",
        ]
    )

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "# Judge Run cli-run" in out
    assert "## Attacker" in out
    assert "## Defender" in out
    assert "## Metadata" in out


def test_cli_reports_missing_input_file(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("NEUROMODELS_LLM_PROVIDER", "fake")
    context = tmp_path / "context.txt"
    under_review = tmp_path / "under_review.txt"
    context.write_text("Figure output.", encoding="utf-8")
    under_review.write_text("[1, 2, 3]", encoding="utf-8")

    exit_code = main(
        [
            "judge",
            "run",
            "--rubric-file",
            str(tmp_path / "missing.txt"),
            "--context-file",
            str(context),
            "--under-review-file",
            str(under_review),
        ]
    )

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "neuromodels judge run: error:" in err
    assert "missing.txt" in err
