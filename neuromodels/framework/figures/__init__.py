"""Figure-digitization tools (Mode-1: quantitative plots).

Design: proposals/figure-digitization-design-2026-06-03.md. These are deterministic
CAPABILITIES a digitizer composes — they do not decide anything. The VLM supplies the
semantic anchors (which pixel is the '1.0' tick, which band holds the attended curve);
the tools do the metric work (calibrate, trace, render, smooth).
"""

from .digitize import (
    AxisCalibration,
    build_calibration,
    detect_plot_box,
    overlay,
    resample_pchip,
    trace_darkest_in_band,
)

__all__ = [
    "AxisCalibration",
    "build_calibration",
    "detect_plot_box",
    "overlay",
    "resample_pchip",
    "trace_darkest_in_band",
]
