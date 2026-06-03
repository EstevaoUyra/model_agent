#!/usr/bin/env python3
"""Citation/Assumption presence+resolution check.

Walks every model's ``implementation/src/**/*.py``, extracts each
``Citation: C-NNN`` / ``Assumption: A-NNN`` tag from docstrings/comments, and
asserts each ID resolves to an entry in that model's
``article_aware/spec/citations.yaml`` (``C-NNN``) or
``assumptions.yaml`` (``A-NNN``). A dangling tag — one whose ID is absent from
the corresponding ledger — is a failure.

Scope of the guarantee (do not over-read it):
  * Presence + resolution only: the tag exists and points at a real ledger ID.
  * It does NOT check that the tag is on the *right* function, that the cited
    passage supports the behavior, or that every function carries a tag. Those
    are quality concerns left to a periodic human audit (DESIGN.md §8).

Run manually (no CI is wired):

    python -m neuromodels.framework.static_checks.check_citations
    # or restrict to some models:
    python -m neuromodels.framework.static_checks.check_citations reynolds_heeger_2009 spratling_2010

Exit code is non-zero if any dangling tag is found (or any model is missing a
ledger it needs). Dependency-light: stdlib + pyyaml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

# Repo root = three levels up from this file
# (neuromodels/framework/static_checks/check_citations.py -> repo root).
REPO_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = REPO_ROOT / "models"


def _rel(path: Path) -> str:
    """Path relative to the repo root, falling back to the absolute path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)

# Matches "C-001", "A-012" etc. (the ledger ID grammar).
CITATION_ID = re.compile(r"\bC-\d{3,}\b")
ASSUMPTION_ID = re.compile(r"\bA-\d{3,}\b")

# A tag line looks like:  Citation: C-002, C-009 ; Assumption: A-004, A-011
# We split on the "Citation:" / "Assumption:" labels and harvest IDs from the
# segment each label introduces, so a "C-009" sitting in prose elsewhere on the
# line is not miscounted as a citation tag.
TAG_LABEL = re.compile(r"(Citation|Assumption)\s*:", re.IGNORECASE)


def _ledger_ids(path: Path) -> set[str]:
    """Return the set of ``id:`` values in a citations/assumptions YAML file."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    ids: set[str] = set()
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict) and "id" in entry:
                ids.add(str(entry["id"]).strip())
    return ids


def _extract_tags(text: str) -> tuple[set[str], set[str]]:
    """Extract (citation_ids, assumption_ids) referenced by tag labels in text.

    Only IDs that appear in the segment following a ``Citation:`` / ``Assumption:``
    label are collected, and each ID is attributed to the kind of the *nearest
    preceding* label on its line.
    """
    cit_ids: set[str] = set()
    asm_ids: set[str] = set()
    for line in text.splitlines():
        matches = list(TAG_LABEL.finditer(line))
        if not matches:
            continue
        for i, m in enumerate(matches):
            kind = m.group(1).lower()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
            segment = line[start:end]
            if kind == "citation":
                cit_ids.update(CITATION_ID.findall(segment))
                # A "Citation:" segment may still inline-mention assumptions only
                # via an explicit "Assumption:" label, which the loop handles
                # separately; raw A-NNN in a citation segment are ignored.
            else:  # assumption
                asm_ids.update(ASSUMPTION_ID.findall(segment))
    return cit_ids, asm_ids


def _iter_src_files(model_dir: Path) -> Iterable[Path]:
    src = model_dir / "implementation" / "src"
    if not src.is_dir():
        return []
    return [
        p
        for p in sorted(src.rglob("*.py"))
        if ".claude" not in p.parts and "worktree" not in str(p)
    ]


def check_model(model_dir: Path) -> list[str]:
    """Check one model. Return a list of human-readable failure strings."""
    failures: list[str] = []
    name = model_dir.name

    citations = _ledger_ids(model_dir / "article_aware" / "spec" / "citations.yaml")
    assumptions = _ledger_ids(
        model_dir / "article_aware" / "spec" / "assumptions.yaml"
    )

    referenced_c: dict[str, list[Path]] = {}
    referenced_a: dict[str, list[Path]] = {}

    for src_file in _iter_src_files(model_dir):
        text = src_file.read_text(encoding="utf-8", errors="replace")
        cit_ids, asm_ids = _extract_tags(text)
        for cid in cit_ids:
            referenced_c.setdefault(cid, []).append(src_file)
        for aid in asm_ids:
            referenced_a.setdefault(aid, []).append(src_file)

    if (referenced_c and not citations):
        failures.append(
            f"{name}: source references citations but "
            f"article_aware/spec/citations.yaml is missing or empty"
        )
    if (referenced_a and not assumptions):
        failures.append(
            f"{name}: source references assumptions but "
            f"article_aware/spec/assumptions.yaml is missing or empty"
        )

    for cid, files in sorted(referenced_c.items()):
        if cid not in citations:
            locs = ", ".join(_rel(f) for f in sorted(set(files)))
            failures.append(
                f"{name}: dangling Citation {cid} (not in citations.yaml) — {locs}"
            )
    for aid, files in sorted(referenced_a.items()):
        if aid not in assumptions:
            locs = ", ".join(_rel(f) for f in sorted(set(files)))
            failures.append(
                f"{name}: dangling Assumption {aid} (not in assumptions.yaml) — {locs}"
            )

    return failures


def discover_models(selected: list[str]) -> list[Path]:
    if selected:
        return [MODELS_DIR / name for name in selected]
    return [
        p
        for p in sorted(MODELS_DIR.iterdir())
        if p.is_dir() and (p / "implementation" / "src").is_dir()
    ]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    model_dirs = discover_models(argv)

    all_failures: list[str] = []
    n_models = 0
    for model_dir in model_dirs:
        if not model_dir.is_dir():
            all_failures.append(f"{model_dir.name}: model directory not found")
            continue
        n_models += 1
        all_failures.extend(check_model(model_dir))

    if all_failures:
        print("Citation/Assumption presence check: FAIL")
        print(f"  checked {n_models} model(s); {len(all_failures)} dangling tag(s):")
        for f in all_failures:
            print(f"  - {f}")
        return 1

    print(
        f"Citation/Assumption presence check: OK "
        f"({n_models} model(s); every tag resolves to a ledger entry)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
