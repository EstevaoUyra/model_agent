"""Unit tests for build_readme's pure rendering (off-corpus started-model surfacing)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_readme as b  # noqa: E402


def _row(**kw):
    base = dict(label="x", link="models/x", rank=1, score=10, cluster="c", cites=5,
                oa="open", code="—", state="faithful", traj="toward", figs=3,
                flags=0, audit="hardened")
    base.update(kw)
    return base


def test_corpus_row_shows_rank_and_score():
    out = b.render_table([_row(rank=7, score=42, label="paper", link="https://doi/x")])
    assert "| 7 | 42 | [paper](https://doi/x) |" in out


def test_off_corpus_started_row_shows_dashes_for_rank_and_score():
    # A started submodule with no corpus entry: rank + score render as "—", but its live
    # state (from the submodule exit-JSON) is still shown. This is the regression fix —
    # such a row used to be DROPPED entirely.
    out = b.render_table([_row(off_corpus=True, label="vicente_kinouchi_caticha_1998",
                               link="models/vicente_kinouchi_caticha_1998",
                               state="partial", traj="toward", figs=7, flags=4)])
    assert "| — | — | [vicente_kinouchi_caticha_1998](models/vicente_kinouchi_caticha_1998) |" in out
    assert "partial" in out and "toward" in out
