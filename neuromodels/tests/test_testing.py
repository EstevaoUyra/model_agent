import pytest

from neuromodels.framework.testing import deterministic_test


def test_deterministic_test_attaches_metadata_and_marks():
    @deterministic_test(
        spec_ref="simulation_protocols.figure_2A",
        claim_id="Q-004",
        figure=2,
        paper_issue="PI-001",
    )
    def sample_test():
        pass

    assert sample_test.__neuromodels_test__ == {
        "kind": "deterministic",
        "spec_ref": "simulation_protocols.figure_2A",
        "claim_id": "Q-004",
        "paper_issue": "PI-001",
        "figure": 2,
    }
    assert sample_test.__neuromodels_spec_ref__ == "simulation_protocols.figure_2A"
    assert sample_test.__neuromodels_claim_id__ == "Q-004"
    assert sample_test.__neuromodels_paper_issue__ == "PI-001"
    assert sample_test.__neuromodels_figure__ == 2

    marks = {mark.name for mark in sample_test.pytestmark}
    assert "neuromodels_deterministic" in marks
    assert "neuromodels_claim" in marks
    assert "neuromodels_paper_issue" in marks
    assert "figure" in marks


def test_deterministic_test_attaches_figure_mark():
    @deterministic_test(
        spec_ref="simulation_protocols.figure_1",
        claim_id="Q-001",
        figure=1,
    )
    def sample_test():
        pass

    assert sample_test.__neuromodels_figure__ == 1
    marks = {mark.name: mark for mark in sample_test.pytestmark}
    assert "figure" in marks
    assert marks["figure"].args == (1,)


def test_deterministic_test_requires_spec_ref():
    with pytest.raises(ValueError, match="spec_ref is required"):
        deterministic_test(spec_ref="", claim_id="Q-001", figure=1)


def test_deterministic_test_requires_figure():
    with pytest.raises(TypeError, match="figure"):
        deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-001")


def test_deterministic_test_requires_claim_id():
    with pytest.raises(TypeError, match="claim_id"):
        deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1)
