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


def _longest_dark_run(dark: np.ndarray, along_columns: bool) -> np.ndarray:
    """Longest consecutive run of True along each column (or row)."""
    lines = dark.T if along_columns else dark
    out = np.zeros(lines.shape[0], dtype=int)
    for i, line in enumerate(lines):
        best = cur = 0
        for v in line:
            cur = cur + 1 if v else 0
            if cur > best:
                best = cur
        out[i] = best
    return out


def detect_plot_box(image_path, *, dark_below: float = 0.5, frac: float = 0.5):
    """Find the axis rectangle as a *starting hint* for placing anchors.

    Returns ``(col0, row0, col1, row1)``. Heuristic: an axis is a **long
    continuous** dark line, so each column/row is scored by its *longest
    consecutive* dark run (NOT dark-pixel density — density is fooled by axis
    labels and tick text, which are dark but short; that was the reported
    mis-detection). A line qualifies when its longest run spans >= ``frac`` of the
    dimension; the box is the outermost qualifying lines, with a fall-back to the
    full extent on any side that collapses.

    KNOWN LIMITS — verify the box, do not trust it blindly:
    - The **bottom-left origin** (the x-axis row and y-axis column) is usually
      reliable. The **top is often open** on scanned panels (no top frame line),
      so ``row0`` may fall back to the image top — read the y-max tick (e.g. the
      "1" label) position yourself.
    - A crop that includes a sliver of a **neighbouring panel** (a second long
      vertical line) or a **caption / legend / "Stimuli" box below the panel** (a
      second long horizontal line — this fooled Fig 4E, where the real x-axis is
      ~27% higher than the legend-box edge the detector grabbed) can capture the
      wrong frame. Verify ``col0``/``col1``/``row0``/``row1`` against the visible
      plot — a wrong frame silently rescales every value.
    In both cases, read the tick pixel positions by viewing and pass anchors to
    ``build_calibration`` directly — this tool only saves you the common case.
    """
    g = _load_gray(image_path)
    dark = g < dark_below
    h, w = dark.shape
    col_run = _longest_dark_run(dark, along_columns=True)   # len w
    row_run = _longest_dark_run(dark, along_columns=False)  # len h
    # An axis line spans a large fraction of its dimension. ABSOLUTE threshold
    # (fraction of dimension), not relative-to-max — so BOTH the left and right
    # vertical lines (and top + bottom) qualify even when one is a little shorter.
    vcols = np.flatnonzero(col_run >= frac * h)
    hrows = np.flatnonzero(row_run >= frac * w)
    c0, c1 = (int(vcols.min()), int(vcols.max())) if vcols.size else (0, w - 1)
    r0, r1 = (int(hrows.min()), int(hrows.max())) if hrows.size else (0, h - 1)
    # Degeneracy guard: if a side collapsed (only one strong line found), fall
    # back to the full extent on that axis rather than returning a sliver box.
    if c1 - c0 < 0.3 * w:
        c0, c1 = 0, w - 1
    if r1 - r0 < 0.3 * h:
        r0, r1 = 0, h - 1
    return (c0, r0, c1, r1)


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
# Region crop: zoom a part of an image, defined in AXIS coordinates, for the eye.
# --------------------------------------------------------------------------- #

def _offset_upscale_calibration(cal: AxisCalibration, col_off, row_off, upscale):
    """A calibration valid for a crop taken at (col_off, row_off) and upscaled."""
    u = float(upscale or 1)
    sx, ix, scx = cal.x
    sy, iy, scy = cal.y
    return AxisCalibration(x=(sx / u, sx * col_off + ix, scx),
                           y=(sy / u, sy * row_off + iy, scy))


def crop_region(image_path, x_range, y_range, *, calibration=None, plot_box=None,
                as_fraction=False, out_path=None, upscale=3, pad_px=6):
    """Crop a region defined in **axis coordinates** and upscale it for detailed inspection.

    A magnifying glass for the VLM: name a region in the plot's own units and get a
    zoomed-in image, so a suspected problem (an apex overshoot, a crossing wiggle, an
    axis-edge misalignment) can be *looked at* up close instead of squinting at the whole
    small panel. Works on **any** image — paper panel, digitized reference render,
    implementation render, or overlay — as long as the calibration matches THAT image
    (run `detect_plot_box` + `build_calibration` on the specific image you are cropping;
    an overlay PNG has a different pixel frame than the paper crop it was drawn from).

    Two ways to specify the region:
    - **data coords** (default): pass ``calibration``; ``x_range``/``y_range`` are DATA
      values, e.g. ``x_range=(0.01, 0.1)`` contrast, ``y_range=(0.0, 0.2)`` response.
    - **axis fraction**: pass ``as_fraction=True`` (``plot_box`` auto-detected if omitted);
      ``x_range``/``y_range`` are fractions [0,1] of the plot box from the LEFT (x) and the
      BOTTOM (y) — e.g. ``x_range=(0, 0.5), y_range=(0, 0.2)`` is the bottom-left
      "0–50% of x, 0–20% of y".

    Returns ``{path, pixel_box, [calibration]}`` — and when a calibration is available, a
    ``calibration`` valid for the CROP, so `trace_darkest_in_band` (etc.) can run on the
    zoom and return correct data coordinates.
    """
    img = Image.open(image_path).convert("RGB")
    W, H = img.size
    if as_fraction:
        c0, r0, c1, r1 = plot_box if plot_box is not None else detect_plot_box(image_path)
        col_lo = c0 + x_range[0] * (c1 - c0)
        col_hi = c0 + x_range[1] * (c1 - c0)
        row_lo = r1 - y_range[1] * (r1 - r0)   # y fraction measured from the bottom
        row_hi = r1 - y_range[0] * (r1 - r0)
    else:
        if calibration is None:
            raise ValueError("data-coord crop needs a calibration (or pass as_fraction=True)")
        cols, rows = calibration.to_pixels(list(x_range), list(y_range))
        col_lo, col_hi = sorted(float(c) for c in cols)
        row_lo, row_hi = sorted(float(r) for r in rows)
    col_lo = max(0, int(round(col_lo - pad_px)))
    col_hi = min(W - 1, int(round(col_hi + pad_px)))
    row_lo = max(0, int(round(row_lo - pad_px)))
    row_hi = min(H - 1, int(round(row_hi + pad_px)))
    crop = img.crop((col_lo, row_lo, col_hi + 1, row_hi + 1))
    if upscale and upscale != 1:
        crop = crop.resize((crop.width * int(upscale), crop.height * int(upscale)), Image.LANCZOS)
    out = str(out_path) if out_path else (str(image_path).rsplit(".", 1)[0] + "_crop.png")
    crop.save(out)
    res = {"path": out, "pixel_box": (col_lo, row_lo, col_hi, row_hi)}
    if calibration is not None:
        res["calibration"] = _offset_upscale_calibration(calibration, col_lo, row_lo, upscale)
    return res


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


# --------------------------------------------------------------------------- #
# Batched helpers — collapse the multi-turn trace / inspect loop into ONE call.
#
# The digitizer's validate step and the auditor's overlay+crop loop are each many
# tool round-trips (trace one band, crop one region, view it, crop the next, …),
# and EVERY round-trip re-reads the agent's whole context — the dominant cost of
# these roles. These two helpers do the SAME work the docstrings above describe,
# but return all artefacts in a single call so the agent reasons over them in one
# turn instead of ~20. They COMPOSE the primitives above (no new digitization
# logic) and change nothing about what gets measured — only how many turns it takes.
# --------------------------------------------------------------------------- #

def _curves_xy(curves: dict):
    """Normalise a curves mapping to ``{name: (xs, ys)}`` float arrays.

    Accepts either the ``overlay()`` form ``{name: (xs, ys)}`` or the digitized-JSON
    form ``{name: {"points": [[x, y], ...]}}`` so callers can pass a loaded panel JSON
    straight through.
    """
    out = {}
    for name, c in curves.items():
        if isinstance(c, dict):
            pts = np.asarray(c.get("points", []), float)
            if pts.size == 0:
                continue
            out[name] = (pts[:, 0], pts[:, 1])
        else:
            xs, ys = c
            out[name] = (np.asarray(xs, float), np.asarray(ys, float))
    return out


def _auto_regions(curves_xy: dict):
    """Derive a default diagnostic-crop battery (apex + endpoints) from the curves.

    The regions the digitize/audit docstrings call out as the usual defect sites:
    each curve's **apex** (peak/plateau — PCHIP overshoot, rounded saturation) and
    the shared **left / right endpoints** (foot alignment, axis-edge calibration).
    Index-fraction windows, so it is scale-agnostic (works on log-x without log math);
    the caller passes explicit ``regions`` for crossings or anything bespoke.
    """
    regions = []
    all_x = np.concatenate([xs for xs, _ in curves_xy.values()]) if curves_xy else np.array([])
    if all_x.size:
        xlo, xhi = float(all_x.min()), float(all_x.max())
        span = (xhi - xlo) or abs(xhi) or 1.0
        edge = 0.18 * span
        regions.append({"name": "left_edge", "x_range": (xlo, xlo + edge), "y_range": None})
        regions.append({"name": "right_edge", "x_range": (xhi - edge, xhi), "y_range": None})
    for name, (xs, ys) in curves_xy.items():
        if xs.size == 0:
            continue
        k = int(np.argmax(ys))
        ax_, ay = float(xs[k]), float(ys[k])
        span = (float(xs.max()) - float(xs.min())) or abs(ax_) or 1.0
        yspan = (float(ys.max()) - float(ys.min())) or abs(ay) or 1.0
        regions.append({
            "name": f"{name}_apex",
            "x_range": (ax_ - 0.18 * span, ax_ + 0.18 * span),
            "y_range": (ay - 0.45 * yspan, ay + 0.12 * yspan),
        })
    return regions


def overlay_with_crops(image_path, calibration: AxisCalibration, curves: dict, out_dir, *,
                       regions=None, log_x: bool = False, n: int = 300, upscale: int = 3,
                       pad_px: int = 6):
    """Shipping overlay PLUS a battery of zoomed overlays, in ONE call.

    Collapses the inspect loop (``overlay`` → ``crop_region`` → view → ``crop_region``
    → view …, often dozens of turns) into a single call whose result the agent views in
    one turn. Each crop is a *zoomed overlay* — the digitized curve drawn on the cropped
    paper pixels (via ``crop_region``'s crop-local calibration), so what the agent
    inspects up close is exactly the line-on-ink the full overlay shows, not a bare zoom.

    Parameters
    ----------
    image_path : the paper panel (the same image ``overlay`` draws on).
    calibration : the panel's ``AxisCalibration``.
    curves : ``{name: (xs, ys)}`` in DATA coords, or a digitized-JSON ``{name: {"points": ...}}``.
    out_dir : directory for the output PNGs (created if absent).
    regions : list of ``{name, x_range, y_range}`` in DATA coords to zoom into; ``y_range``
        may be ``None`` (auto from the crop). If omitted, a default apex+endpoints battery is
        derived from the curves (pass explicit regions for a crossing or a custom locus).

    Returns ``{"overlay": <path>, "crops": {name: <path>}, "regions": [...]}``. The agent
    views the overlay and every crop together and writes its verdict in one turn.
    """
    import os
    os.makedirs(out_dir, exist_ok=True)
    cxy = _curves_xy(curves)
    full = overlay(image_path, calibration, cxy,
                   os.path.join(out_dir, "overlay.png"), log_x=log_x, n=n)
    if regions is None:
        regions = _auto_regions(cxy)
    crops = {}
    for r in regions:
        name = r["name"]
        xr = r["x_range"]
        yr = r.get("y_range")
        try:
            if yr is None:
                # crop by x only — derive a y window covering the curves in that x-band
                xs_all, ys_all = [], []
                for xs, ys in cxy.values():
                    m = (xs >= min(xr)) & (xs <= max(xr))
                    xs_all.append(xs[m]); ys_all.append(ys[m])
                yall = np.concatenate(ys_all) if ys_all else np.array([0.0, 1.0])
                if yall.size == 0:
                    yall = np.concatenate([ys for _, ys in cxy.values()]) if cxy else np.array([0.0, 1.0])
                pad = 0.12 * ((yall.max() - yall.min()) or abs(float(yall.max())) or 1.0)
                yr = (float(yall.min()) - pad, float(yall.max()) + pad)
            cr = crop_region(image_path, xr, yr, calibration=calibration,
                             upscale=upscale, pad_px=pad_px,
                             out_path=os.path.join(out_dir, f"_crop_{name}.png"))
            crops[name] = overlay(cr["path"], cr["calibration"], cxy,
                                  os.path.join(out_dir, f"crop_{name}.png"), log_x=log_x, n=n)
        except Exception as e:  # a degenerate region must not sink the whole battery
            crops[name] = f"SKIPPED ({type(e).__name__}: {e})"
    return {"overlay": full, "crops": crops, "regions": regions}


def trace_bands(image_path, bands: dict, calibration: AxisCalibration, *,
                min_darkness: float = 0.35, resample_n: int = None, log_x: bool = False):
    """Trace several curves (one VLM-supplied band each) in ONE call.

    Wraps ``trace_darkest_in_band`` over a dict of bands so a multi-curve panel is
    digitized in a single call instead of one round-trip per curve. The same documented
    limitation applies (no colour/style channel — band-separation only; trace the
    envelope where same-colour curves coincide and say so).

    Parameters
    ----------
    bands : ``{name: (cols, row_lo, row_hi)}`` — ``cols`` is the iterable of columns to
        sample (e.g. ``range(c0, c1)``), ``row_lo/row_hi`` the band isolating that curve.
    resample_n : if given, also return a PCHIP-resampled curve on a dense grid of this
        many points across the traced x-range (rounds peaks, keeps plateaus flat).

    Returns ``{name: {"points": [[x, y], ...], "coverage": float,
                      ["resampled": [[x, y], ...]]}}`` in DATA coords, ready to drop
    into the digitized JSON's ``curves``.
    """
    out = {}
    for name, (cols, row_lo, row_hi) in bands.items():
        res = trace_darkest_in_band(image_path, cols, row_lo, row_hi,
                                    calibration=calibration, min_darkness=min_darkness)
        if "x" not in res or len(res["x"]) == 0:
            out[name] = {"points": [], "coverage": float(res.get("coverage", 0.0))}
            continue
        pts = np.column_stack([res["x"], res["y"]])
        entry = {"points": [[float(x), float(y)] for x, y in pts],
                 "coverage": float(res["coverage"])}
        if resample_n:
            xs = pts[:, 0]
            if log_x:
                gx = np.logspace(np.log10(xs.min()), np.log10(xs.max()), resample_n)
            else:
                gx = np.linspace(xs.min(), xs.max(), resample_n)
            gy = resample_pchip(pts, gx, log_x=log_x)
            entry["resampled"] = [[float(x), float(y)] for x, y in zip(gx, gy)]
        out[name] = entry
    return out
