"""Utilities for VLM-based comparison of reproduced scientific figures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import neuromodels.framework.llm as llm


SYSTEM_PROMPT = (
    "You are evaluating whether a generated scientific model figure reproduces "
    "the key visual features of the original paper figure. "
    "You will be given: (1) the original figure image, (2) the generated figure "
    "image, (3) a figure description explaining expected behavior, and (4) a "
    "visual checklist of specific pass/fail criteria. "
    "Work through the checklist systematically. Focus on whether the model "
    "simulation output shows the correct qualitative scientific relationships, "
    "not on matching colors, fonts, exact panel layout, or publication styling."
)

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp", ".webp"}


@dataclass(frozen=True)
class FigureComparison:
    """Structured output from a figure reproducibility comparison."""

    passes: bool | None
    summary: str
    checklist_results: tuple[str, ...]
    issues: tuple[str, ...]
    recommendation: str
    raw_response: str
    model: str
    provider: str


@dataclass(frozen=True)
class FigureComparisonInputs:
    """Resolved paths for one model figure comparison."""

    original_figure: Path
    generated_figure: Path
    figure_description: Path
    figure_checklist: Path


@dataclass(frozen=True)
class FigureComparisonPacket:
    """Serializable packet for an isolated figure-review context."""

    figure_number: str
    model_dir: Path
    original_figure: Path
    generated_figure: Path
    figure_description: Path
    figure_checklist: Path

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable packet."""
        return {
            "figure_number": self.figure_number,
            "model_dir": str(self.model_dir),
            "original_figure": str(self.original_figure),
            "generated_figure": str(self.generated_figure),
            "figure_description": str(self.figure_description),
            "figure_checklist": str(self.figure_checklist),
        }


def compare_figures(
    original_figure: str | Path,
    generated_figure: str | Path,
    figure_description: str | Path,
    figure_checklist: str | Path,
    *,
    model: str | None = None,
) -> FigureComparison:
    """Compare an original article figure against a generated reproduction.

    Args:
        original_figure: Path to the article figure image.
        generated_figure: Path to the generated model-output figure image.
        figure_description: Path to figure_N.md — overpowered caption with
            expected behavior, parameters, and inter-panel relationships.
        figure_checklist: Path to figure_N_visual_checklist.md — per-item
            pass/fail criteria written from the original figure.
        model: Optional model override for the configured VLM provider.

    Returns:
        Structured pass/fail comparison with per-item checklist results.
        ``passes`` is ``None`` when the VLM response could not be parsed as JSON.
    """
    original_path = _require_file(original_figure, "original_figure")
    generated_path = _require_file(generated_figure, "generated_figure")
    description_text = _read_file(figure_description, "figure_description")
    checklist_text = _read_file(figure_checklist, "figure_checklist")

    prompt = build_comparison_prompt(
        original_path=original_path,
        generated_path=generated_path,
        figure_description=description_text,
        figure_checklist=checklist_text,
    )
    response = llm.get_vision_response(
        prompt,
        [original_path, generated_path],
        system_prompt=SYSTEM_PROMPT,
        model=model,
    )
    return parse_comparison_response(
        response.content,
        model=response.model,
        provider=response.provider,
    )


def compare_model_figure(
    model_dir: str | Path,
    figure_number: str | int,
    *,
    model: str | None = None,
) -> FigureComparison:
    """Resolve conventional model paths for a figure number and compare them."""
    inputs = resolve_figure_inputs(model_dir, figure_number)
    return compare_figures(
        inputs.original_figure,
        inputs.generated_figure,
        inputs.figure_description,
        inputs.figure_checklist,
        model=model,
    )


def build_model_figure_packet(
    model_dir: str | Path,
    figure_number: str | int,
) -> FigureComparisonPacket:
    """Build a path-only packet for isolated figure comparison."""
    normalized_number = _normalize_figure_number(figure_number)
    root = Path(model_dir)
    inputs = resolve_figure_inputs(root, normalized_number)
    return FigureComparisonPacket(
        figure_number=normalized_number,
        model_dir=root,
        original_figure=inputs.original_figure,
        generated_figure=inputs.generated_figure,
        figure_description=inputs.figure_description,
        figure_checklist=inputs.figure_checklist,
    )


def write_model_figure_packet(
    model_dir: str | Path,
    figure_number: str | int,
    output_path: str | Path,
) -> Path:
    """Write a figure comparison packet JSON file."""
    packet = build_model_figure_packet(model_dir, figure_number)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def resolve_figure_inputs(
    model_dir: str | Path,
    figure_number: str | int,
) -> FigureComparisonInputs:
    """Resolve original/generated/description/checklist paths for a figure."""
    root = Path(model_dir)
    number = _normalize_figure_number(figure_number)
    original = _resolve_original_figure(root, number)
    generated = root / "implementation" / "figure_outputs" / f"figure_{number}.png"
    description = root / "article_aware" / "figures" / f"figure_{number}.md"
    checklist = root / "article_aware" / "figures" / f"figure_{number}_visual_checklist.md"

    return FigureComparisonInputs(
        original_figure=_require_file(original, "original_figure"),
        generated_figure=_require_file(generated, "generated_figure"),
        figure_description=_require_file(description, "figure_description"),
        figure_checklist=_require_file(checklist, "figure_checklist"),
    )


def build_comparison_prompt(
    *,
    original_path: Path,
    generated_path: Path,
    figure_description: str,
    figure_checklist: str,
) -> str:
    """Build the VLM prompt for one figure comparison."""
    if not figure_description.strip():
        raise ValueError("figure_description must not be empty")
    if not figure_checklist.strip():
        raise ValueError("figure_checklist must not be empty")

    return f"""You are given two figures and must evaluate how well the generated figure reproduces the original.

IMAGE 1 — Original article figure: {original_path}
IMAGE 2 — Generated model-output figure: {generated_path}

---

## Figure Description

The following description explains what the figure should show, grounded in the model equations and simulation parameters. Use it as context when evaluating the checklist.

{figure_description.strip()}

---

## Visual Checklist

Each item below is a specific visual criterion derived from reading the original figure. Evaluate each one against IMAGE 2 (the generated figure). Items tagged `<!-- UNSURE: ... -->` were genuinely ambiguous in the original — pay extra attention to these.

{figure_checklist.strip()}

---

## Task

Go through every checkbox item in the checklist above. For each one, decide:
- **pass** — the generated figure clearly satisfies this criterion
- **fail** — the generated figure clearly does not satisfy this criterion
- **unsure** — you cannot determine from the images whether this criterion is met

Return valid JSON with exactly this schema:
{{
  "passes": true,
  "summary": "one short paragraph overall assessment",
  "checklist_results": [
    {{"item": "exact item text from checklist", "result": "pass", "note": ""}},
    {{"item": "exact item text from checklist", "result": "fail", "note": "brief reason"}},
    {{"item": "exact item text from checklist", "result": "unsure", "note": "why unclear"}}
  ],
  "issues": ["human-readable description of each failed item"],
  "recommendation": "pass, fail, or needs_review with a short reason"
}}

Set `passes` to true only if no checklist items fail (unsure items are allowed).
Set `passes` to false if one or more items fail.
Set `passes` to null if the images could not be compared at all.
"""


def parse_comparison_response(
    content: str,
    *,
    model: str,
    provider: str,
) -> FigureComparison:
    """Parse the VLM response into a FigureComparison."""
    try:
        data = json.loads(_strip_json_fence(content))
    except json.JSONDecodeError:
        return FigureComparison(
            passes=None,
            summary=content.strip(),
            checklist_results=(),
            issues=("VLM response was not valid JSON.",),
            recommendation="needs_review",
            raw_response=content,
            model=model,
            provider=provider,
        )

    passes = data.get("passes")
    if not isinstance(passes, bool):
        passes = None

    checklist_results = tuple(
        _format_checklist_result(r)
        for r in (data.get("checklist_results") or [])
        if isinstance(r, dict)
    )

    return FigureComparison(
        passes=passes,
        summary=str(data.get("summary", "")).strip(),
        checklist_results=checklist_results,
        issues=tuple(str(item) for item in data.get("issues", []) or []),
        recommendation=str(data.get("recommendation", "")).strip(),
        raw_response=content,
        model=model,
        provider=provider,
    )


def _format_checklist_result(r: dict) -> str:
    result = str(r.get("result", "unsure")).upper()
    item = str(r.get("item", "")).strip()
    note = str(r.get("note", "")).strip()
    if note:
        return f"{result}: {item} — {note}"
    return f"{result}: {item}"


def _require_file(path: str | Path, name: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"{name} does not exist: {file_path}")
    return file_path


def _read_file(path: str | Path, name: str) -> str:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"{name} does not exist: {file_path}")
    return file_path.read_text(encoding="utf-8")


def _resolve_original_figure(model_dir: Path, number: str) -> Path:
    figures_dir = model_dir / "article_aware" / "figures"
    matches = sorted(
        p for p in figures_dir.glob(f"figure_{number}.*")
        if p.suffix.lower() in _IMAGE_SUFFIXES
    )
    if not matches:
        raise FileNotFoundError(
            f"original_figure does not exist: {figures_dir / f'figure_{number}.<image>'}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"multiple original figures matched figure {number}: "
            + ", ".join(str(path) for path in matches)
        )
    return matches[0]


def _normalize_figure_number(figure_number: str | int) -> str:
    text = str(figure_number).strip()
    if text.lower().startswith("figure_"):
        text = text[7:]
    elif text.lower().startswith("figure"):
        text = text[6:].strip("_ -")
    if not text:
        raise ValueError("figure_number must not be empty")
    return text


def _strip_json_fence(content: str) -> str:
    text = content.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


__all__ = [
    "FigureComparison",
    "FigureComparisonInputs",
    "FigureComparisonPacket",
    "SYSTEM_PROMPT",
    "build_comparison_prompt",
    "build_model_figure_packet",
    "compare_figures",
    "compare_model_figure",
    "parse_comparison_response",
    "resolve_figure_inputs",
    "write_model_figure_packet",
]
