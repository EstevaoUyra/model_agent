#!/usr/bin/env python3
"""Citation/Assumption/Code/Lineage presence+resolution check.

Walks every model's ``implementation/src/**/*.py``, extracts each
``Citation: C-NNN`` / ``Assumption: A-NNN`` / ``Code: CODE-NNN`` /
``Lineage: LINEAGE-NNN`` tag from docstrings/comments, and asserts each ID
resolves to an entry in that model's ledger under ``article_aware/spec/``
(``citations.yaml`` / ``assumptions.yaml`` / ``code_refs.yaml`` /
``lineage_refs.yaml``). A dangling tag — one whose ID is absent from the
corresponding ledger — is a failure.

The four first-class provenance classes:
  * ``C-NNN``       — this paper's text/figures (``citations.yaml``).
  * ``A-NNN``       — an assumption we made (``assumptions.yaml``).
  * ``CODE-NNN``    — the original authors' code (``code_refs.yaml``); see the
    acquire-sources skill. The *paper-insufficiency* view (values from code
    ALONE) is produced by ``neuromodels provenance``.
  * ``LINEAGE-NNN`` — a value inherited from ANOTHER paper in the genealogy
    (``lineage_refs.yaml``). Each entry names an ancestor ``model:`` and a
    ``ref:`` into that model's spec; this check additionally validates that the
    ancestor exists and the ref resolves there, so a genealogy link is always
    traceable to a concrete entry, not just a paper name.

Scope of the guarantee (do not over-read it):
  * Presence + resolution only: the tag exists and points at a real ledger ID.
  * It does NOT check that the tag is on the *right* function, that the cited
    passage/code supports the behavior, or that every function carries a tag.
    Those are quality concerns left to a periodic human audit (WORKFLOW.md §4).

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

# Matches "C-001", "A-012", "CODE-003", "LINEAGE-002" (the ledger ID grammar).
# The prefixes don't collide: "C-\d" never matches inside "CODE-"/"LINEAGE-"
# (the C/no-C is not followed by "-"), and "A-\d" never matches inside
# "LINEAGE-" (the A is followed by "G").
CITATION_ID = re.compile(r"\bC-\d{3,}\b")
ASSUMPTION_ID = re.compile(r"\bA-\d{3,}\b")
CODE_ID = re.compile(r"\bCODE-\d{3,}\b")
LINEAGE_ID = re.compile(r"\bLINEAGE-\d{3,}\b")

# Each provenance class: (docstring label, id pattern, ledger filename).
TAG_CLASSES = {
    "citation": (CITATION_ID, "citations.yaml"),
    "assumption": (ASSUMPTION_ID, "assumptions.yaml"),
    "code": (CODE_ID, "code_refs.yaml"),
    "lineage": (LINEAGE_ID, "lineage_refs.yaml"),
}

# A tag line looks like:
#   Citation: C-002, C-009 ; Assumption: A-004 ; Code: CODE-003 ; Lineage: LINEAGE-001
# We split on the labels and harvest IDs from the segment each introduces, so a
# bare "C-009" sitting in prose elsewhere on the line is not miscounted.
TAG_LABEL = re.compile(r"(Citation|Assumption|Code|Lineage)\s*:", re.IGNORECASE)


def _ledger_ids(path: Path) -> set[str]:
    """Return the set of ``id:`` values in a citations/assumptions/code YAML file."""
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


def _extract_tags(text: str) -> dict[str, set[str]]:
    """Extract referenced IDs per provenance class (keys of ``TAG_CLASSES``).

    Only IDs that appear in the segment following a ``Citation:`` /
    ``Assumption:`` / ``Code:`` / ``Lineage:`` label are collected, and each ID is
    attributed to the kind of the *nearest preceding* label on its line.
    """
    found: dict[str, set[str]] = {kind: set() for kind in TAG_CLASSES}
    for line in text.splitlines():
        matches = list(TAG_LABEL.finditer(line))
        if not matches:
            continue
        for i, m in enumerate(matches):
            kind = m.group(1).lower()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
            segment = line[start:end]
            pattern, _ = TAG_CLASSES[kind]
            found[kind].update(pattern.findall(segment))
    return found


def _iter_src_files(model_dir: Path) -> Iterable[Path]:
    src = model_dir / "implementation" / "src"
    if not src.is_dir():
        return []
    return [
        p
        for p in sorted(src.rglob("*.py"))
        if ".claude" not in p.parts and "worktree" not in str(p)
    ]


def _ledger_entries(path: Path) -> list[dict]:
    """Return the list of entry dicts in a ledger YAML file."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    return [e for e in data if isinstance(e, dict)] if isinstance(data, list) else []


def _calibration_keys(model_dir: Path) -> set[str]:
    """Flat + dotted keys of every calibrated value in a model's calibration.yaml."""
    keys: set[str] = set()
    for rel in (Path("article_aware") / "spec" / "calibration.yaml",
                Path("implementation") / "calibration.yaml"):
        path = model_dir / rel
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        def _walk(d, prefix=""):
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                full = f"{prefix}{k}"
                if isinstance(v, dict) and "value" in v:
                    keys.add(full)
                elif isinstance(v, dict):
                    _walk(v, prefix=f"{full}.")

        _walk(data)
    return keys


def _model_known_ids(model_dir: Path) -> set[str]:
    """Everything a lineage ``ref`` may point at in an ancestor model: every
    ledger ID plus every calibration key."""
    spec = model_dir / "article_aware" / "spec"
    ids: set[str] = set()
    for _, fname in TAG_CLASSES.values():
        ids |= _ledger_ids(spec / fname)
    ids |= _calibration_keys(model_dir)
    return ids


def check_model(model_dir: Path) -> list[str]:
    """Check one model. Return a list of human-readable failure strings."""
    failures: list[str] = []
    name = model_dir.name
    spec = model_dir / "article_aware" / "spec"

    # ── 1. presence + resolution of every tag to its own ledger ──
    ledger_ids = {kind: _ledger_ids(spec / fname) for kind, (_, fname) in TAG_CLASSES.items()}
    referenced: dict[str, dict[str, list[Path]]] = {kind: {} for kind in TAG_CLASSES}
    for src_file in _iter_src_files(model_dir):
        found = _extract_tags(src_file.read_text(encoding="utf-8", errors="replace"))
        for kind, ids in found.items():
            for _id in ids:
                referenced[kind].setdefault(_id, []).append(src_file)

    for kind, (_, fname) in TAG_CLASSES.items():
        refs = referenced[kind]
        if refs and not ledger_ids[kind]:
            failures.append(f"{name}: source references {kind} but article_aware/spec/{fname} is missing or empty")
        for _id, files in sorted(refs.items()):
            if _id not in ledger_ids[kind]:
                locs = ", ".join(_rel(f) for f in sorted(set(files)))
                failures.append(f"{name}: dangling {kind.capitalize()} {_id} (not in {fname}) — {locs}")

    # ── 2. lineage entries must resolve cross-model: the named ancestor exists
    #       and the ref points at a real entry/key in THAT model's spec ──
    for entry in _ledger_entries(spec / "lineage_refs.yaml"):
        lid = str(entry.get("id", "?"))
        anc_name = str(entry.get("model", "")).strip()
        ref = str(entry.get("ref", "")).strip()
        if not anc_name or not ref:
            failures.append(f"{name}: lineage {lid} missing 'model' or 'ref' (cannot trace to an ancestor)")
            continue
        anc_dir = MODELS_DIR / anc_name
        if not anc_dir.is_dir():
            failures.append(f"{name}: lineage {lid} names ancestor model '{anc_name}' which is not in models/")
            continue
        if ref not in _model_known_ids(anc_dir):
            failures.append(
                f"{name}: lineage {lid} ref '{ref}' does not resolve in {anc_name} "
                f"(no such ledger ID or calibration key) — the genealogy link is untraceable"
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
        print("Citation/Assumption/Code/Lineage presence check: FAIL")
        print(f"  checked {n_models} model(s); {len(all_failures)} dangling tag(s):")
        for f in all_failures:
            print(f"  - {f}")
        return 1

    print(
        f"Citation/Assumption/Code/Lineage presence check: OK "
        f"({n_models} model(s); every tag resolves to a ledger entry)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
