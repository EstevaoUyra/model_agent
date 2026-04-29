"""Minimal pytest-facing test metadata API for Neuromodels.

The full runner and logging layer is intentionally deferred. These decorators
give Phase B tests stable metadata that the future runner can consume.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

import pytest

F = TypeVar("F", bound=Callable[..., Any])


def deterministic_test(
    *,
    spec_ref: str,
    claim_id: str | None = None,
    paper_issue: str | None = None,
) -> Callable[[F], F]:
    """Attach deterministic-test metadata and pytest marks to a test function."""
    if not spec_ref:
        raise ValueError("spec_ref is required")

    metadata = {
        "kind": "deterministic",
        "spec_ref": spec_ref,
        "claim_id": claim_id,
        "paper_issue": paper_issue,
    }

    def decorate(func: F) -> F:
        setattr(func, "__neuromodels_test__", metadata)
        setattr(func, "__neuromodels_spec_ref__", spec_ref)
        setattr(func, "__neuromodels_claim_id__", claim_id)
        setattr(func, "__neuromodels_paper_issue__", paper_issue)
        marked = pytest.mark.neuromodels_deterministic(**metadata)(func)
        if claim_id is not None:
            marked = pytest.mark.neuromodels_claim(claim_id)(marked)
        if paper_issue is not None:
            marked = pytest.mark.neuromodels_paper_issue(paper_issue)(marked)
        return marked

    return decorate


__all__ = ["deterministic_test"]
