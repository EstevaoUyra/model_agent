#!/usr/bin/env python3
"""Provenance taxonomy over a model's calibration ledger.

Every calibrated value carries a ``source:`` tag (or list of tags) pointing at
the citation/assumption/code ledgers. This module buckets each value by where
its support actually comes from, and surfaces the one bucket that matters most
for faithfulness:

    CODE-ALONE — values supported by the authors' original code (``CODE-NNN``)
    with NO supporting paper citation (``C-NNN``). These are the parameters the
    *published paper is insufficient to specify* — they exist in the
    reproduction only because we read the authors' code. The count of code-alone
    values is itself a faithfulness metric: low ⇒ the paper is reproducible from
    its text; high ⇒ it is not, and this report says exactly where.

Buckets (by what supports a value, not by tag count):

    paper        C-NNN present, no CODE-NNN           paper self-sufficient
    paper+code   C-NNN and CODE-NNN both present      paper qualitative, code numeric
    code-alone   CODE-NNN present, NO C-NNN           paper insufficient (the signal)
    assumption   A-NNN only (no C/CODE)               we chose it
    unsourced    no recognizable C/A/CODE tag         flag — provenance gap

CLI: ``neuromodels provenance --model-dir <dir>`` (see neuromodels/cli/main.py).
Dependency-light: stdlib + pyyaml.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CITATION_ID = re.compile(r"\bC-\d{3,}\b")
ASSUMPTION_ID = re.compile(r"\bA-\d{3,}\b")
CODE_ID = re.compile(r"\bCODE-\d{3,}\b")
LINEAGE_ID = re.compile(r"\bLINEAGE-\d{3,}\b")

# Spec calibration is the authoritative parameter ledger. Fall back to the
# implementation copy if a model keeps it there.
_CALIB_CANDIDATES = (
    Path("article_aware") / "spec" / "calibration.yaml",
    Path("implementation") / "calibration.yaml",
)
_MODELS_DIR = Path(__file__).resolve().parents[2] / "models"

BUCKETS = ("paper", "paper+code", "code-alone", "lineage", "assumption", "unsourced")


@dataclass
class ValueProvenance:
    key: str
    value: object
    sources: list[str]
    bucket: str
    note: str = ""
    # Populated for ``lineage`` values: the ancestor paper and where, in that
    # ancestor's spec, this decision ultimately grounds.
    lineage: dict | None = None


@dataclass
class ProvenanceReport:
    model: str
    calibration_path: str | None
    values: list[ValueProvenance] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        out = {b: 0 for b in BUCKETS}
        for v in self.values:
            out[v.bucket] += 1
        return out

    @property
    def code_alone(self) -> list[ValueProvenance]:
        return [v for v in self.values if v.bucket == "code-alone"]

    @property
    def lineage_values(self) -> list[ValueProvenance]:
        return [v for v in self.values if v.bucket == "lineage"]

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "calibration_path": self.calibration_path,
            "counts": self.counts,
            "code_alone": [
                {"key": v.key, "value": v.value, "sources": v.sources, "note": v.note}
                for v in self.code_alone
            ],
            "lineage": [
                {"key": v.key, "value": v.value, "sources": v.sources, "trace": v.lineage}
                for v in self.lineage_values
            ],
            "values": [
                {
                    "key": v.key,
                    "value": v.value,
                    "sources": v.sources,
                    "bucket": v.bucket,
                    "lineage": v.lineage,
                }
                for v in self.values
            ],
        }


def _source_tokens(source) -> list[str]:
    """Normalize a ``source:`` field (str or list) into recognized ledger IDs."""
    if source is None:
        return []
    raw = source if isinstance(source, list) else [source]
    text = " ".join(str(s) for s in raw)
    # Prefixes don't collide (C-\d never matches inside CODE-/LINEAGE-, A-\d never
    # inside LINEAGE-), so collect all four classes independently.
    return (
        LINEAGE_ID.findall(text)
        + CODE_ID.findall(text)
        + CITATION_ID.findall(text)
        + ASSUMPTION_ID.findall(text)
    )


def _classify(tokens: list[str]) -> str:
    has_paper = any(t.startswith("C-") for t in tokens)
    has_code = any(t.startswith("CODE-") for t in tokens)
    has_lineage = any(t.startswith("LINEAGE-") for t in tokens)
    has_assumption = any(t.startswith("A-") for t in tokens)
    if has_code and not has_paper:
        return "code-alone"
    if has_code and has_paper:
        return "paper+code"
    if has_paper:
        return "paper"
    if has_lineage:
        return "lineage"
    if has_assumption:
        return "assumption"
    return "unsourced"


def _find_calibration(model_dir: Path) -> Path | None:
    for rel in _CALIB_CANDIDATES:
        p = model_dir / rel
        if p.exists():
            return p
    return None


def _walk_entries(data, prefix=""):
    """Yield (key, entry-dict) for every mapping that looks like a calibrated
    value (has a ``value`` field). Supports flat and nested calibration files."""
    if not isinstance(data, dict):
        return
    if "value" in data and not isinstance(data["value"], dict):
        # caller handles; this node itself is a value — but we only reach here
        # for nested dicts, so emit at the parent level instead.
        return
    for key, entry in data.items():
        full = f"{prefix}{key}"
        if isinstance(entry, dict) and "value" in entry:
            yield full, entry
        elif isinstance(entry, dict):
            yield from _walk_entries(entry, prefix=f"{full}.")


def _lineage_map(model_dir: Path) -> dict[str, dict]:
    """LINEAGE-NNN -> {model, ref, ...} from article_aware/spec/lineage_refs.yaml."""
    path = model_dir / "article_aware" / "spec" / "lineage_refs.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    out: dict[str, dict] = {}
    if isinstance(data, list):
        for e in data:
            if isinstance(e, dict) and "id" in e:
                out[str(e["id"]).strip()] = e
    return out


_PREFIX_GROUND = {"C-": "paper", "CODE-": "code", "A-": "assumption", "LINEAGE-": "lineage"}


def _resolve_ancestor_ground(ancestor_dir: Path, ref: str, _cache: dict) -> str:
    """Where does ``ref`` ultimately ground in the ancestor model? Returns a
    bucket name (paper/code/assumption/lineage) or a calibration bucket, or
    'unresolved'."""
    for prefix, ground in _PREFIX_GROUND.items():
        if ref.startswith(prefix):
            return ground
    # Otherwise ref is a calibration key in the ancestor — look up its bucket.
    name = ancestor_dir.name
    if name not in _cache:
        _cache[name] = {v.key: v.bucket for v in build_provenance(ancestor_dir).values}
    return _cache[name].get(ref, "unresolved")


def build_provenance(model_dir: Path, _ancestor_cache: dict | None = None) -> ProvenanceReport:
    model_dir = Path(model_dir)
    cache = _ancestor_cache if _ancestor_cache is not None else {}
    report = ProvenanceReport(model=model_dir.name, calibration_path=None)
    calib = _find_calibration(model_dir)
    if calib is None:
        return report
    report.calibration_path = str(calib)
    with calib.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    lineage_refs = _lineage_map(model_dir)
    for key, entry in _walk_entries(data):
        tokens = _source_tokens(entry.get("source"))
        bucket = _classify(tokens)
        vp = ValueProvenance(
            key=key,
            value=entry.get("value"),
            sources=tokens,
            bucket=bucket,
            note=str(entry.get("note", ""))[:200],
        )
        if bucket == "lineage":
            lid = next((t for t in tokens if t.startswith("LINEAGE-")), None)
            ref_entry = lineage_refs.get(lid, {}) if lid else {}
            anc_name = str(ref_entry.get("model", "")).strip()
            ref = str(ref_entry.get("ref", "")).strip()
            ground = "unresolved"
            anc_dir = _MODELS_DIR / anc_name
            if anc_name and ref and anc_dir.is_dir():
                ground = _resolve_ancestor_ground(anc_dir, ref, cache)
            vp.lineage = {"id": lid, "model": anc_name, "ref": ref, "ancestor_ground": ground}
        report.values.append(vp)
    return report


def render_markdown(report: ProvenanceReport) -> str:
    counts = report.counts
    total = sum(counts.values())
    lines = [
        f"# Provenance — {report.model}",
        "",
        f"Calibration ledger: `{report.calibration_path or '(none found)'}`  ·  {total} value(s)",
        "",
        "| Bucket | Count | Meaning |",
        "|---|---:|---|",
        f"| paper | {counts['paper']} | paper self-sufficient (C-NNN only) |",
        f"| paper+code | {counts['paper+code']} | paper qualitative, code supplies the number |",
        f"| **code-alone** | **{counts['code-alone']}** | **paper insufficient — only the authors' code specifies it** |",
        f"| lineage | {counts['lineage']} | inherited from another genealogy paper (LINEAGE-NNN) |",
        f"| assumption | {counts['assumption']} | we chose it (A-NNN) |",
        f"| unsourced | {counts['unsourced']} | provenance gap — flag |",
        "",
    ]
    if report.lineage_values:
        lines += [
            "## Lineage (inherited from genealogy ancestors)",
            "",
            "| Key | Value | Ancestor model | Ancestor ref | Grounds as |",
            "|---|---|---|---|---|",
        ]
        for v in report.lineage_values:
            tr = v.lineage or {}
            lines.append(
                f"| `{v.key}` | {v.value} | {tr.get('model', '?')} | "
                f"`{tr.get('ref', '?')}` | {tr.get('ancestor_ground', '?')} |"
            )
        lines.append("")
    if report.code_alone:
        lines += [
            "## Code-alone values (paper does not specify these)",
            "",
            "| Key | Value | Sources |",
            "|---|---|---|",
        ]
        for v in report.code_alone:
            lines.append(f"| `{v.key}` | {v.value} | {', '.join(v.sources)} |")
        lines.append("")
    else:
        lines += ["_No code-alone values: every calibrated number traces to the paper or an assumption._", ""]
    if counts["unsourced"]:
        lines += [
            "## Unsourced values (provenance gap)",
            "",
        ]
        lines += [f"- `{v.key}` = {v.value}" for v in report.values if v.bucket == "unsourced"]
        lines.append("")
    return "\n".join(lines)
