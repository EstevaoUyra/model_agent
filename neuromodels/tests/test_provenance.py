"""Tests for the provenance taxonomy and the CODE-NNN static-check extension."""

from __future__ import annotations

import textwrap
from pathlib import Path

from neuromodels.framework.provenance import (
    _classify,
    _source_tokens,
    build_provenance,
)
from neuromodels.framework.static_checks.check_citations import check_model


def test_source_tokens_handles_str_list_and_comma():
    assert _source_tokens("C-017") == ["C-017"]
    assert set(_source_tokens("C-016, A-004")) == {"C-016", "A-004"}
    assert set(_source_tokens(["C-012", "CODE-003"])) == {"C-012", "CODE-003"}
    assert _source_tokens(None) == []


def test_classify_buckets():
    assert _classify(["C-001"]) == "paper"
    assert _classify(["A-002"]) == "assumption"
    assert _classify(["CODE-003"]) == "code-alone"               # the signal
    assert _classify(["C-001", "CODE-003"]) == "paper+code"
    assert _classify(["A-002", "CODE-003"]) == "code-alone"       # code support beats assumption
    assert _classify(["LINEAGE-001"]) == "lineage"               # inherited from ancestor
    assert _classify(["LINEAGE-001", "A-002"]) == "lineage"      # lineage beats assumption
    assert _classify([]) == "unsourced"


def test_source_tokens_no_prefix_collision():
    toks = set(_source_tokens("LINEAGE-001, CODE-002, C-003, A-004"))
    assert toks == {"LINEAGE-001", "CODE-002", "C-003", "A-004"}


def _write_model(tmp_path: Path, calibration: str, code_refs: str | None = None,
                 src: str | None = None) -> Path:
    spec = tmp_path / "article_aware" / "spec"
    spec.mkdir(parents=True)
    (spec / "calibration.yaml").write_text(textwrap.dedent(calibration), encoding="utf-8")
    (spec / "citations.yaml").write_text("- id: C-001\n  source: paper\n", encoding="utf-8")
    (spec / "assumptions.yaml").write_text("- id: A-001\n  name: a\n", encoding="utf-8")
    if code_refs is not None:
        (spec / "code_refs.yaml").write_text(textwrap.dedent(code_refs), encoding="utf-8")
    if src is not None:
        srcdir = tmp_path / "implementation" / "src"
        srcdir.mkdir(parents=True)
        (srcdir / "model.py").write_text(textwrap.dedent(src), encoding="utf-8")
    return tmp_path


def test_build_provenance_surfaces_code_alone(tmp_path):
    model = _write_model(
        tmp_path,
        calibration="""
        gain:    { value: 16,   units: x, source: CODE-003 }
        sigma:   { value: 1e-6, units: x, source: [C-001, CODE-004] }
        width:   { value: 60,   units: deg, source: C-001 }
        guess:   { value: 0.5,  units: x, source: A-001 }
        orphan:  { value: 1,    units: x }
        """,
    )
    report = build_provenance(model)
    counts = report.counts
    assert counts["code-alone"] == 1
    assert counts["paper+code"] == 1
    assert counts["paper"] == 1
    assert counts["assumption"] == 1
    assert counts["unsourced"] == 1
    assert [v.key for v in report.code_alone] == ["gain"]


def _make_model(root: Path, name: str, calibration: str,
                lineage_refs: str | None = None, src: str | None = None) -> Path:
    d = root / name
    spec = d / "article_aware" / "spec"
    spec.mkdir(parents=True)
    (spec / "calibration.yaml").write_text(textwrap.dedent(calibration), encoding="utf-8")
    (spec / "citations.yaml").write_text("- id: C-001\n  source: paper\n", encoding="utf-8")
    (spec / "assumptions.yaml").write_text("- id: A-001\n  name: a\n", encoding="utf-8")
    if lineage_refs is not None:
        (spec / "lineage_refs.yaml").write_text(textwrap.dedent(lineage_refs), encoding="utf-8")
    if src is not None:
        srcdir = d / "implementation" / "src"
        srcdir.mkdir(parents=True)
        (srcdir / "model.py").write_text(textwrap.dedent(src), encoding="utf-8")
    return d


def test_lineage_traces_through_to_ancestor_ground(tmp_path, monkeypatch):
    import neuromodels.framework.provenance as prov
    import neuromodels.framework.static_checks.check_citations as cc

    root = tmp_path / "models"
    root.mkdir()
    _make_model(root, "anc", calibration="tuning: { value: 30, source: C-001 }\n")
    kid = _make_model(
        root, "kid",
        calibration="tw: { value: 30, source: LINEAGE-001 }\n",
        lineage_refs="- id: LINEAGE-001\n  model: anc\n  ref: tuning\n",
        src='def f():\n    """Inherited width.\n\n    Lineage: LINEAGE-001\n    """\n    return 30\n',
    )
    monkeypatch.setattr(prov, "_MODELS_DIR", root)
    monkeypatch.setattr(cc, "MODELS_DIR", root)

    report = prov.build_provenance(kid)
    assert report.counts["lineage"] == 1
    trace = report.lineage_values[0].lineage
    assert trace["model"] == "anc"
    assert trace["ref"] == "tuning"
    # `tuning` is paper-specified (C-001) in the ancestor -> grounds as "paper".
    assert trace["ancestor_ground"] == "paper"
    assert cc.check_model(kid) == []  # resolves cleanly across models


def test_lineage_untraceable_link_is_flagged(tmp_path, monkeypatch):
    import neuromodels.framework.static_checks.check_citations as cc

    root = tmp_path / "models"
    root.mkdir()
    _make_model(root, "anc", calibration="tuning: { value: 30, source: C-001 }\n")
    kid = _make_model(
        root, "kid",
        calibration="tw: { value: 30, source: LINEAGE-001 }\n",
        lineage_refs="- id: LINEAGE-001\n  model: anc\n  ref: NOPE\n",
    )
    ghost = _make_model(
        root, "ghost",
        calibration="tw: { value: 30, source: LINEAGE-001 }\n",
        lineage_refs="- id: LINEAGE-001\n  model: missing_model\n  ref: tuning\n",
    )
    monkeypatch.setattr(cc, "MODELS_DIR", root)

    assert any("does not resolve in anc" in f for f in cc.check_model(kid))
    assert any("not in models/" in f for f in cc.check_model(ghost))


def test_check_citations_resolves_and_flags_code_tags(tmp_path):
    # A Code: tag that resolves passes; a dangling one fails.
    model = _write_model(
        tmp_path,
        calibration="gain: { value: 16, source: CODE-003 }\n",
        code_refs="- id: CODE-003\n  source: attentionModel.m:42\n",
        src='''
        def gain():
            """Suppressive gain.

            Code: CODE-003
            """
            return 16
        ''',
    )
    assert check_model(model) == []

    # Now reference a CODE id that is not in the ledger -> dangling failure.
    (model / "implementation" / "src" / "model.py").write_text(
        textwrap.dedent('''
        def gain():
            """Code: CODE-999"""
            return 16
        '''),
        encoding="utf-8",
    )
    failures = check_model(model)
    assert any("dangling Code CODE-999" in f for f in failures)
