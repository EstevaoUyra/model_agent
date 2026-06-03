"""Simplest Mode-1 figure-digitization tools.

Design: proposals/figure-digitization-design-2026-06-03.md.

The two biggest sources of error in eyeball digitization are (1) the axis mapping
done in the head, and (2) connect-the-dots representation between sparse points.
These tools remove both, and add an overlay so a SEPARATE critic
(skills/audit-digitization) can judge the extraction against the paper image rather
than the digitizer grading its own work.

Conventions
-----------
- Images are read as grayscale; pixel coordinates are ``(col, row)`` with ``row``
  increasing DOWNWARD (PIL/numpy), while data ``y`` increases UPWARD. The
  calibration handles the flip — callers always work in data coordinates.
- A "band" is a row range ``(row_lo, row_hi)`` the caller (the VLM) supplies to
  isolate ONE curve from others that overlap it; the tool then finds the precise
  curve pixel inside the band. The VLM does the semantic disambiguation it is good
  at; the tool does the metric read it is good at.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy.interpolate import PchipInterpolator


# --------------------------------------------------------------------------- #
# Axis calibration: pixel <-> data, linear or log, from VLM-supplied anchors.
# --------------------------------------------------------------------------- #

def _fit_1d(pixels: np.ndarray, values: np.ndarray, scale: str):
    """Fit a 1-D pixel->data map. Returns (slope, intercept, scale).

    For ``log`` scale the fit is pixel -> log10(data); ``to_data`` exponentiates.
    Two anchors give an exact line; more are least-squares (robust to a mis-click).
    """
    pixels = np.asarray(pixels, float)
    values = np.asarray(values, float)
    if scale not in ("linear", "log"):
        raise ValueError(f"scale must be 'linear' or 'log', got {scale!r}")
    y = np.log10(values) if scale == "log" else values
    if pixels.size < 2:
        raise ValueError("need >= 2 anchors per axis")
    slope, intercept = np.polyfit(pixels, y, 1)
    return float(slope), float(intercept), scale


@dataclass
class AxisCalibration:
    """Independent pixel<->data maps for the x (col) and y (row) axes."""

    x: tuple  # (slope, intercept, scale) on columns
    y: tuple  # (slope, intercept, scale) on rows

    def to_data(self, cols, rows):
        cols = np.asarray(cols, float)
        rows = np.asarray(rows, float)
        xs = self._apply(cols, self.x)
        ys = self._apply(rows, self.y)
        return xs, ys

    def to_pixels(self, xs, ys):
        xs = np.asarray(xs, float)
        ys = np.asarray(ys, float)
        cols = self._invert(xs, self.x)
        rows = self._invert(ys, self.y)
        return cols, rows

    @staticmethod
    def _apply(pix, fit):
        slope, intercept, scale = fit
        v = slope * pix + intercept
        return np.power(10.0, v) if scale == "log" else v

    @staticmethod
    def _invert(val, fit):
        slope, intercept, scale = fit
        v = np.log10(np.asarray(val, float)) if scale == "log" else np.asarray(val, float)
        return (v - intercept) / slope


def build_calibration(x_anchors, y_anchors, x_scale="linear", y_scale="linear") -> AxisCalibration:
    """Build a calibration from anchor points the VLM read off the panel.

    Parameters
    ----------
    x_anchors : list of (pixel_col, data_value)  — e.g. [(40, 0.01), (300, 1.0)]
    y_anchors : list of (pixel_row, data_value)  — e.g. [(360, 0.0), (20, 1.0)]
    x_scale, y_scale : "linear" | "log"

    The anchors are tick positions whose DATA values are labelled on the axis —
    the thing the VLM reads reliably. Two per axis suffice; pass more for safety.
    """
    xa = np.asarray(x_anchors, float)
    ya = np.asarray(y_anchors, float)
    return AxisCalibration(
        x=_fit_1d(xa[:, 0], xa[:, 1], x_scale),
        y=_fit_1d(ya[:, 0], ya[:, 1], y_scale),
    )


# --------------------------------------------------------------------------- #
# Image helpers.
# --------------------------------------------------------------------------- #

def _load_gray(image_path) -> np.ndarray:
    """Load an image as a float grayscale array in [0, 1] (0 = black)."""
    return np.asarray(Image.open(image_path).convert("L"), float) / 255.0


def detect_plot_box(image_path, *, dark_below: float = 0.5, frac: float = 0.5):
    """Find the axis rectangle as a convenience for placing anchors.

    Returns ``(col0, row0, col1, row1)`` of the densest dark rows/cols (the axis
    frame). Heuristic: the plot's left/bottom axes are long dark lines, so the
    row/column dark-pixel profiles spike there. The VLM should sanity-check the
    box (and still supply DATA values for the edges); this only saves it from
    eyeballing pixel positions.
    """
    g = _load_gray(image_path)
    dark = g < dark_below
    col_profile = dark.mean(axis=0)
    row_profile = dark.mean(axis=1)
    cols = np.flatnonzero(col_profile > frac * col_profile.max())
    rows = np.flatnonzero(row_profile > frac * row_profile.max())
    if cols.size == 0 or rows.size == 0:
        h, w = g.shape
        return (0, 0, w - 1, h - 1)
    return (int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max()))


def trace_darkest_in_band(image_path, cols, row_lo, row_hi, *, calibration=None,
                          min_darkness: float = 0.35):
    """Trace one curve: per column, the darkest row within a VLM-supplied band.

    The band ``(row_lo, row_hi)`` isolates ONE curve where several overlap — the
    semantic call the VLM makes. The tool returns the precise pixel (darkness-
    weighted centroid of the darkest cluster), which is far more accurate than
    eyeballing the value. Columns with no pixel darker than ``min_darkness`` are
    dropped (a gap, e.g. a dashed segment) and reported.

    Returns dict: ``cols``, ``rows`` (pixel), and if ``calibration`` given, ``x``,
    ``y`` (data), plus ``coverage`` (fraction of requested cols that had a curve).

    LIMITATION — monochrome / overlapping curves (READ THIS before using on a
    scanned paper panel). This tool separates curves only by *where they are*
    (the band) and *how dark they are* — it has **no colour or line-style
    channel**. On a grayscale scan, two curves of the same colour that run within
    a few pixels of each other (e.g. a contrast-gain pair: a small leftward shift
    keeps attended and ignored nearly coincident) **cannot be told apart** — the
    darkest-pixel read returns their merged blob, not "the attended one". So:

    - It is reliable for: a single curve in the band; **well-separated** curves
      (give each its own band); the **envelope / plateau / overall shape** of a
      bundle; and curves you can isolate by region.
    - It is NOT reliable for: splitting two same-colour curves where they overlap.
      There, trace the **envelope** and accept the pair is ~identical in that
      region, then pin their offset only in the x-range where they **do** visibly
      separate (e.g. mid-contrast, where a leftward shift opens a gap), and check
      the result with ``overlay``.
    - The dashed curve (e.g. % modulation) is separable by its gaps + its distinct
      region; trace it in its own band.

    This is a VLM-guided tool, not push-button extraction: the agent must choose
    bands and decide where separation is even possible. If a panel's curves cannot
    be separated by any band, say so (a digitization caveat) rather than reporting
    a confident split the pixels do not support.
    """
    g = _load_gray(image_path)
    row_lo, row_hi = int(min(row_lo, row_hi)), int(max(row_lo, row_hi))
    out_c, out_r = [], []
    for c in np.asarray(cols, int):
        strip = 1.0 - g[row_lo:row_hi + 1, c]  # darkness, 0..1
        if strip.size == 0 or strip.max() < min_darkness:
            continue
        # darkness-weighted centroid of the darkest contiguous cluster
        thresh = max(min_darkness, 0.6 * strip.max())
        idx = np.flatnonzero(strip >= thresh)
        w = strip[idx]
        row = row_lo + float(np.sum(idx * w) / np.sum(w))
        out_c.append(int(c))
        out_r.append(row)
    res = {"cols": np.asarray(out_c, float), "rows": np.asarray(out_r, float),
           "coverage": (len(out_c) / max(1, len(np.asarray(cols, int))))}
    if calibration is not None and out_c:
        xs, ys = calibration.to_data(res["cols"], res["rows"])
        res["x"], res["y"] = xs, ys
    return res


# --------------------------------------------------------------------------- #
# Representation: smooth, plateau-respecting resampling (fixes "pointy" peaks).
# --------------------------------------------------------------------------- #

def resample_pchip(points, x_grid, *, log_x: bool = False) -> np.ndarray:
    """Monotone-cubic (PCHIP) resample of digitized points onto ``x_grid``.

    PCHIP rounds peaks and respects plateaus without overshoot — the fix for the
    pointy apexes and soft plateaus that linear ``np.interp`` produces between
    sparse points. ``log_x`` interpolates in log-x for log-scaled panels.
    """
    pts = np.asarray(points, float)
    xs, ys = pts[:, 0], pts[:, 1]
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    gx = np.asarray(x_grid, float)
    if log_x:
        f = PchipInterpolator(np.log(xs), ys, extrapolate=True)
        return f(np.log(gx))
    return PchipInterpolator(xs, ys, extrapolate=True)(gx)


# --------------------------------------------------------------------------- #
# Overlay: render extracted data back on the paper panel for the critic.
# --------------------------------------------------------------------------- #

_OVERLAY_COLORS = ["#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4"]


def overlay(image_path, calibration: AxisCalibration, curves: dict, out_path, *,
            log_x: bool = False, n: int = 200):
    """Render data curves over the paper panel, mapped back through calibration.

    ``curves`` maps name -> (xs, ys) in DATA coordinates. Each is PCHIP-smoothed,
    mapped to pixels, and drawn as a coloured line on the original image. The
    output PNG is what the audit-digitization critic compares against the paper —
    a curve drawn on the actual paper pixels, far more sensitive than two
    separately-rendered plots.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    g = np.asarray(Image.open(image_path).convert("RGB"))
    fig, ax = plt.subplots(figsize=(g.shape[1] / 80, g.shape[0] / 80), dpi=80)
    ax.imshow(g)
    for i, (name, (xs, ys)) in enumerate(curves.items()):
        xs = np.asarray(xs, float)
        ys = np.asarray(ys, float)
        if log_x:
            gx = np.logspace(np.log10(xs.min()), np.log10(xs.max()), n)
        else:
            gx = np.linspace(xs.min(), xs.max(), n)
        gy = resample_pchip(np.column_stack([xs, ys]), gx, log_x=log_x)
        cols, rows = calibration.to_pixels(gx, gy)
        ax.plot(cols, rows, "-", lw=2.5, color=_OVERLAY_COLORS[i % len(_OVERLAY_COLORS)],
                label=name, alpha=0.85)
    ax.set_xlim(0, g.shape[1])
    ax.set_ylim(g.shape[0], 0)
    ax.axis("off")
    ax.legend(fontsize=6, loc="upper left", framealpha=0.6)
    fig.tight_layout(pad=0)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path
