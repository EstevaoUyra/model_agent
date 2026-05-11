"""Utilities for VLM-based comparison of reproduced scientific figures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import neuromodels.framework.llm as llm


DEFAULT_COMPARISON_RUBRIC = (
    "Compare the generated model-output figure against the original article "
    "figure using the referenced protocol. Passing means the generated figure "
    "uses the same relevant plot type(s), shows the same expected qualitative "
    "relationships/trends, and would let a human recognize the intended "
    "article figure. Do not require matching colors, fonts, exact panel layout, "
    "or publication artwork. Return only valid JSON with keys: passes, summary, "
    "strengths, issues, recommendation."
)

SYSTEM_PROMPT = (
    "You are comparing scientific figures for computational model "
    "reproducibility. Use only the supplied protocol text and the two images. "
    "Focus on whether the generated figure reproduces the original figure's "
    "plot types and expected qualitative behavior, not on exact colors, fonts, "
    "or publication styling."
)


@dataclass(frozen=True)
class FigureComparison:
    """Structured output from a figure reproducibility comparison."""

    passes: bool | None
    summary: str
    strengths: tuple[str, ...]
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
    figure_protocol: Path


@dataclass(frozen=True)
class FigureComparisonPacket:
    """Serializable packet for an isolated Codex figure-review context."""

    figure_number: str
    model_dir: Path
    original_figure: Path
    generated_figure: Path
    figure_protocol: Path
    rubric: str = DEFAULT_COMPARISON_RUBRIC

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable packet."""
        return {
            "figure_number": self.figure_number,
            "model_dir": str(self.model_dir),
            "original_figure": str(self.original_figure),
            "generated_figure": str(self.generated_figure),
            "figure_protocol": str(self.figure_protocol),
            "rubric": self.rubric,
        }


def compare_figures(
    original_figure: str | Path,
    generated_figure: str | Path,
    figure_protocol: str | Path,
    *,
    model: str | None = None,
) -> FigureComparison:
    """Compare an original article figure against a generated reproduction.

    Args:
        original_figure: Path to the article figure image.
        generated_figure: Path to the generated model-output figure image.
        figure_protocol: Protocol text, or a path to a protocol/spec document
            that includes the expected qualitative behavior.
        model: Optional model override for the configured VLM provider.

    Returns:
        Structured pass/fail comparison. ``passes`` is ``None`` when the VLM
        response could not be parsed as JSON.
    """
    original_path = _require_file(original_figure, "original_figure")
    generated_path = _require_file(generated_figure, "generated_figure")
    protocol_text = _protocol_text(figure_protocol)

    prompt = build_comparison_prompt(
        original_path=original_path,
        generated_path=generated_path,
        figure_protocol=protocol_text,
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
        inputs.figure_protocol,
        model=model,
    )


def build_model_figure_packet(
    model_dir: str | Path,
    figure_number: str | int,
    *,
    rubric: str = DEFAULT_COMPARISON_RUBRIC,
) -> FigureComparisonPacket:
    """Build a path-only packet for isolated figure comparison."""
    if not rubric.strip():
        raise ValueError("rubric must not be empty")
    normalized_number = _normalize_figure_number(figure_number)
    root = Path(model_dir)
    inputs = resolve_figure_inputs(root, normalized_number)
    return FigureComparisonPacket(
        figure_number=normalized_number,
        model_dir=root,
        original_figure=inputs.original_figure,
        generated_figure=inputs.generated_figure,
        figure_protocol=inputs.figure_protocol,
        rubric=rubric,
    )


def write_model_figure_packet(
    model_dir: str | Path,
    figure_number: str | int,
    output_path: str | Path,
    *,
    rubric: str = DEFAULT_COMPARISON_RUBRIC,
) -> Path:
    """Write a figure comparison packet JSON file."""
    packet = build_model_figure_packet(model_dir, figure_number, rubric=rubric)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def resolve_figure_inputs(
    model_dir: str | Path,
    figure_number: str | int,
) -> FigureComparisonInputs:
    """Resolve original/generated/protocol paths for a model figure number."""
    root = Path(model_dir)
    number = _normalize_figure_number(figure_number)
    original = _resolve_original_figure(root, number)
    generated = root / "implementation" / "figure_outputs" / f"figure_{number}.png"
    protocol = root / "article_aware" / "pseudocode" / f"figure_{number}_protocol.md"

    return FigureComparisonInputs(
        original_figure=_require_file(original, "original_figure"),
        generated_figure=_require_file(generated, "generated_figure"),
        figure_protocol=_require_file(protocol, "figure_protocol"),
    )


def build_comparison_prompt(
    *,
    original_path: Path,
    generated_path: Path,
    figure_protocol: str,
) -> str:
    """Build the VLM prompt for one figure comparison."""
    if not figure_protocol.strip():
        raise ValueError("figure_protocol must not be empty")

    return f"""Compare the generated figure to the original article figure.

The first attached image is the original article figure:
{original_path}

The second attached image is the generated model-output figure:
{generated_path}

Figure protocol and expected behavior:
{figure_protocol.strip()}

Decide whether the generated figure passes the reproducibility test. Passing
means it uses the same relevant plot type(s), shows the same qualitative
relationships/trends required by the protocol, and would let a human recognize
the intended article figure. Do not require matching colors, fonts, exact panel
layout, or publication artwork.

Return only valid JSON with this schema:
{{
  "passes": true,
  "summary": "one short paragraph",
  "strengths": ["what matches"],
  "issues": ["important mismatches or missing pieces"],
  "recommendation": "pass, fail, or needs_review with a short reason"
}}
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
            strengths=(),
            issues=("VLM response was not valid JSON.",),
            recommendation="needs_review",
            raw_response=content,
            model=model,
            provider=provider,
        )

    passes = data.get("passes")
    if not isinstance(passes, bool):
        passes = None

    return FigureComparison(
        passes=passes,
        summary=str(data.get("summary", "")).strip(),
        strengths=tuple(str(item) for item in data.get("strengths", []) or []),
        issues=tuple(str(item) for item in data.get("issues", []) or []),
        recommendation=str(data.get("recommendation", "")).strip(),
        raw_response=content,
        model=model,
        provider=provider,
    )


def _require_file(path: str | Path, name: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"{name} does not exist: {file_path}")
    return file_path


def _resolve_original_figure(model_dir: Path, number: str) -> Path:
    figures_dir = model_dir / "article_aware" / "figures"
    matches = sorted(figures_dir.glob(f"figure_{number}_original.*"))
    if not matches:
        raise FileNotFoundError(
            f"original_figure does not exist: {figures_dir / f'figure_{number}_original.*'}"
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


def _protocol_text(protocol: str | Path) -> str:
    if isinstance(protocol, Path):
        if not protocol.is_file():
            raise FileNotFoundError(f"figure_protocol does not exist: {protocol}")
        return protocol.read_text(encoding="utf-8")

    maybe_path = Path(protocol)
    if "\n" not in protocol and maybe_path.is_file():
        return maybe_path.read_text(encoding="utf-8")
    if not protocol.strip():
        raise ValueError("figure_protocol must not be empty")
    return protocol


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
    "DEFAULT_COMPARISON_RUBRIC",
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
