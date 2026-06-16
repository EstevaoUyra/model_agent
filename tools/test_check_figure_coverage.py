"""Unit tests for the coverage gate's pure classification logic (classify_figures)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_figure_coverage import classify_figures  # noqa: E402


def _by_fig(rows):
    return {r["figure"]: r for r in rows}


def test_complete_figure_with_all_three_views():
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "article_aware/figures/figure_5.png",
        "figures_reproduced/figure_5.png",
        "article_aware/figures/figure_5/panel_a_digitized.json",
    ]
    rows, faith = classify_figures(files, ["5"])
    assert faith is True
    assert rows[0]["complete"] is True
    assert rows[0]["missing"] == []


def test_missing_digitized_blocks():
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "article_aware/figures/figure_6.png",
        "figures_reproduced/figure_6.png",
    ]
    rows, _ = classify_figures(files, ["6"])
    assert rows[0]["complete"] is False
    assert rows[0]["missing"] == ["digitized"]


def test_nodigitize_marker_satisfies_digitized_only():
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "article_aware/figures/figure_3.png",
        "figures_reproduced/figure_3.png",
        "article_aware/figures/figure_3.nodigitize",
    ]
    rows, _ = classify_figures(files, ["3"])
    assert rows[0]["complete"] is True
    # .nodigitize does NOT waive the paper crop.
    rows2, _ = classify_figures(
        ["logs/faithfulness_audit/x.md", "figures_reproduced/figure_3.png",
         "article_aware/figures/figure_3.nodigitize"], ["3"])
    assert rows2[0]["missing"] == ["original"]


def test_nopaper_marker_exempts_original_and_digitized_but_not_render():
    # A render-only derived panel: only the committed render + the .nopaper marker exist.
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "figures_reproduced/figure_mechanism.png",
        "article_aware/figures/figure_mechanism.nopaper",
    ]
    rows, _ = classify_figures(files, ["mechanism"])
    row = rows[0]
    assert row["nopaper"] is True
    assert row["complete"] is True
    assert row["missing"] == []


def test_nopaper_still_requires_the_render():
    # .nopaper waives the paper comparison, never the model output itself.
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "article_aware/figures/figure_dynamics.nopaper",
    ]
    rows, _ = classify_figures(files, ["dynamics"])
    assert rows[0]["nopaper"] is True
    assert rows[0]["complete"] is False
    assert rows[0]["missing"] == ["implemented"]


def test_no_faithfulness_audit_fails_overall_even_if_figures_complete():
    files = [
        "article_aware/figures/figure_2.png",
        "figures_reproduced/figure_2.png",
        "article_aware/figures/figure_2.nodigitize",
    ]
    rows, faith = classify_figures(files, ["2"])
    assert faith is False
    assert rows[0]["complete"] is True  # the figure itself is complete
    # all_complete folds in faith_ran at the check() layer; here we assert faith is the gate.


def test_paywalled_real_figure_without_nopaper_stays_blocked():
    # A real paper figure that is merely unavailable must NOT silently pass — no .nopaper.
    files = [
        "logs/faithfulness_audit/2026-06-15.md",
        "figures_reproduced/figure_1.png",
        "article_aware/figures/figure_1.nodigitize",
    ]
    rows, _ = classify_figures(files, ["1"])
    assert rows[0]["complete"] is False
    assert rows[0]["missing"] == ["original"]
