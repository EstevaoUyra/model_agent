"""Helpers for qualitative sanity-check scripts.

These utilities are shared across models. Per-model sanity-check scripts in
`models/<model>/implementation/sanity_checks/` import from this module to
get consistent stat printing and PNG output behavior.

Sanity checks are exploratory — they print summary statistics and save PNGs
for human inspection. They are not tests; they make no assertions. See
WORKFLOW.md for the authoring rules.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


def require_plotting() -> tuple[Any, Any]:
    """Import matplotlib and seaborn or fail with an install hint.

    Configures a temp matplotlib cache and Agg backend so the call works
    in headless CI / agent environments. Raises SystemExit with a useful
    message if the optional `sanity` extra is not installed.
    """
    cache_dir = Path(tempfile.gettempdir()) / "neuromodels_matplotlib_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Plotting dependencies are missing. Install them with: "
            '.venv/bin/python -m pip install -e ".[sanity]"'
        ) from exc
    return plt, sns


def output_dir(script_path: str | Path) -> Path:
    """Return (and create) the conventional `<script>_outputs/` directory
    next to `script_path`. Output dirs are gitignored per repo policy.
    """
    path = Path(script_path)
    out = path.with_name(f"{path.stem}_outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out


def matrix_stats(
    name: str,
    matrix: np.ndarray,
    *,
    x_grid: np.ndarray | None = None,
    theta_grid: np.ndarray | None = None,
) -> list[str]:
    """Compact summary lines for a 1D or 2D array.

    Includes shape, min/max/mean/sum, and the peak index (with grid
    coordinates when provided). Use this instead of dumping the full array.
    """
    arr = np.asarray(matrix)
    lines = [
        f"{name}",
        f"  shape: {arr.shape}",
        f"  min: {arr.min():.6g}",
        f"  max: {arr.max():.6g}",
        f"  mean: {arr.mean():.6g}",
        f"  sum: {arr.sum():.6g}",
    ]
    if arr.ndim == 2:
        peak = np.unravel_index(int(np.argmax(arr)), arr.shape)
        lines.append(f"  peak_index: theta={peak[0]}, x={peak[1]}")
        if theta_grid is not None and x_grid is not None:
            lines.append(
                f"  peak_coords: theta={float(theta_grid[peak[0]]):.6g}, "
                f"x={float(x_grid[peak[1]]):.6g}"
            )
    elif arr.ndim == 1:
        peak = int(np.argmax(arr))
        lines.append(f"  peak_index: {peak}")
    return lines


def matrix_excerpt(matrix: np.ndarray, rows: int = 7, cols: int = 9) -> str:
    """Center-cropped excerpt of a matrix as a printable string."""
    arr = np.asarray(matrix)
    if arr.ndim != 2:
        return np.array2string(arr, precision=3, suppress_small=True)
    r0 = max((arr.shape[0] - rows) // 2, 0)
    c0 = max((arr.shape[1] - cols) // 2, 0)
    excerpt = arr[r0 : r0 + rows, c0 : c0 + cols]
    return np.array2string(excerpt, precision=3, suppress_small=True)


def write_text(path: Path, sections: list[str]) -> None:
    """Write `sections` joined by blank lines to `path` (UTF-8)."""
    path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def save_heatmap_grid(fig, axes, matrices, titles, *, sns, cbar: bool = False) -> None:
    """Render a sequence of matrices as heatmaps across `axes` (raveled).

    Pass the seaborn module via `sns` (returned from `require_plotting`).
    Extra axes beyond `len(matrices)` are turned off.
    """
    for ax, matrix, title in zip(np.ravel(axes), matrices, titles, strict=False):
        sns.heatmap(np.asarray(matrix), ax=ax, cmap="viridis", cbar=cbar)
        ax.set_title(title)
        ax.set_xlabel("x index")
        ax.set_ylabel("theta index")
    for ax in np.ravel(axes)[len(matrices) :]:
        ax.axis("off")


__all__ = [
    "require_plotting",
    "output_dir",
    "matrix_stats",
    "matrix_excerpt",
    "write_text",
    "save_heatmap_grid",
]
