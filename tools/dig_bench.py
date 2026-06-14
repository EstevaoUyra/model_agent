#!/usr/bin/env python3
"""Digitization-cost A/B bench: clone a model fixture, grade a re-digitized arm.

The figure-digitization cost levers (L1 batched tooling, L2 diff-scoped audit) are
A/B-tested by re-running ONLY the digitization gate (`full-pass.js` from='digitize')
on a fixture and comparing cost + quality against the frozen committed baseline.

This tool is the harness's filesystem + quality side (the cost side is
`tools/repro_cost.py --json`):

    clone   <model> <arm>   make models/<model>__<arm> (working tree, no git history),
                            strip its *_digitized.json, git-init so agents can commit.
    compare <model> <arm>   grade the arm's re-digitized JSON against the ORIGINAL
                            models/<model> baseline: per-curve max-abs / RMSE on a
                            common x-grid + structural identity. Prints a table + verdict.
    cleanup <model> <arm>   rm -rf the clone.

Quality bar (per curve, in panel y-range units): max-abs <= 0.03 AND rmse <= 0.015,
with structural identity (same panels, same curve names, same x_scale/x_range). The
baseline is the frozen Opus-digitized, FAITHFUL-audited reference already on disk.
"""
import sys
import os
import glob
import json
import shutil
import subprocess

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from neuromodels.framework.figures import resample_pchip  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(REPO, "models")

# quality tolerances, in the panel's y-range units
MAX_ABS_TOL = 0.03
RMSE_TOL = 0.015
N_GRID = 100


# --------------------------------------------------------------------------- #
# clone / cleanup
# --------------------------------------------------------------------------- #

def _arm_dir(model, arm):
    return os.path.join(MODELS, f"{model}__{arm}")


def clone(model, arm):
    src = os.path.join(MODELS, model)
    if not os.path.isdir(src):
        sys.exit(f"no such model: {src}")
    dst = _arm_dir(model, arm)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    # copy the working tree (filesystem copy — brings paper.pdf etc. regardless of
    # gitignore), but NOT the submodule's .git gitlink (would break git in the clone).
    subprocess.run(["rsync", "-a", "--exclude", ".git", "--exclude", ".audittmp",
                    f"{src}/", f"{dst}/"], check=True)
    # strip the digitized JSON so the digitizer actually re-runs (else it just re-audits).
    stripped = glob.glob(os.path.join(dst, "article_aware", "figures", "*",
                                      "panel_*_digitized.json"))
    for f in stripped:
        os.remove(f)
    # a fresh standalone repo so the gate's agents can commit cleanly + leave an honest diff.
    env = {**os.environ, "GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "bench@local",
           "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "bench@local"}
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "commit", "-q", "-m", f"baseline clone of {model} (digitized JSON stripped)"]):
        subprocess.run(cmd, cwd=dst, env=env, check=True)
    print(f"cloned -> models/{model}__{arm}  ({len(stripped)} digitized JSON stripped)")
    print(f"  run: Workflow full-pass.js  args={{model:'models/{model}__{arm}', "
          f"figures:[...], from:'digitize', lever1:<bool>, lever2:<bool>}}")


def cleanup(model, arm):
    dst = _arm_dir(model, arm)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
        print(f"removed models/{model}__{arm}")
    else:
        print(f"nothing to remove at models/{model}__{arm}")


# --------------------------------------------------------------------------- #
# compare
# --------------------------------------------------------------------------- #

def _panels(model_dir):
    """{relpath: loaded_json} for every panel_*_digitized.json under the model."""
    out = {}
    root = os.path.join(model_dir, "article_aware", "figures")
    for f in glob.glob(os.path.join(root, "*", "panel_*_digitized.json")):
        try:
            out[os.path.relpath(f, root)] = json.load(open(f))
        except Exception as e:
            out[os.path.relpath(f, root)] = {"_load_error": str(e)}
    return out


def _curve_points(panel, name):
    c = panel.get("curves", {}).get(name, {})
    pts = np.asarray(c.get("points", []), float)
    return pts if pts.ndim == 2 and pts.shape[0] >= 2 else None


def _yspan(panel, name):
    """Panel y-range for normalising the error; fall back to the curve's own span."""
    c = panel.get("curves", {}).get(name, {})
    yr = c.get("y_range") or panel.get("y_range")
    if yr and len(yr) == 2 and (yr[1] - yr[0]):
        return abs(float(yr[1]) - float(yr[0]))
    pts = _curve_points(panel, name)
    if pts is not None:
        s = float(pts[:, 1].max() - pts[:, 1].min())
        if s:
            return s
    return 1.0


def _compare_curve(base, arm, panel_b, panel_a, name):
    pb, pa = _curve_points(panel_b, name), _curve_points(panel_a, name)
    if pb is None or pa is None:
        return {"curve": name, "status": "NO_POINTS", "max_abs": None, "rmse": None}
    log_x = (panel_b.get("x_scale") == "log")
    xlo = max(pb[:, 0].min(), pa[:, 0].min())
    xhi = min(pb[:, 0].max(), pa[:, 0].max())
    if not (xhi > xlo):
        return {"curve": name, "status": "NO_X_OVERLAP", "max_abs": None, "rmse": None}
    if log_x and xlo > 0:
        grid = np.logspace(np.log10(xlo), np.log10(xhi), N_GRID)
    else:
        grid = np.linspace(xlo, xhi, N_GRID)
    yb = resample_pchip(pb, grid, log_x=log_x)
    ya = resample_pchip(pa, grid, log_x=log_x)
    span = _yspan(panel_b, name)
    err = np.abs(ya - yb) / span
    max_abs, rmse = float(err.max()), float(np.sqrt(np.mean(err ** 2)))
    ok = max_abs <= MAX_ABS_TOL and rmse <= RMSE_TOL
    return {"curve": name, "status": "OK" if ok else "OUT_OF_TOL",
            "max_abs": max_abs, "rmse": rmse}


def compare(model, arm, ref=None):
    # ref=None → grade against the frozen committed baseline models/<model>; ref=<armname> →
    # grade arm vs another arm (e.g. treatment vs baseline-arm: shares describe-variance, so it
    # isolates the levers' effect on the trace).
    base_dir = os.path.join(MODELS, model) if ref is None else _arm_dir(model, ref)
    base_label = f"models/{model}" if ref is None else f"models/{model}__{ref}"
    base = _panels(base_dir)
    armd = _panels(_arm_dir(model, arm))
    if not base:
        sys.exit(f"no digitized panels under {base_label}")

    rows, struct = [], []
    missing = sorted(set(base) - set(armd))   # baseline panel the arm did NOT reproduce
    extra = sorted(set(armd) - set(base))     # panel the arm invented
    for p in missing:
        struct.append(f"MISSING panel (arm dropped a reference): {p}")
    for p in extra:
        struct.append(f"EXTRA panel (arm invented): {p}")

    for p in sorted(set(base) & set(armd)):
        pb, pa = base[p], armd[p]
        # structural identity
        if pb.get("x_scale") != pa.get("x_scale"):
            struct.append(f"{p}: x_scale {pb.get('x_scale')} -> {pa.get('x_scale')}")
        cb, ca = set(pb.get("curves", {})), set(pa.get("curves", {}))
        if cb != ca:
            struct.append(f"{p}: curves {sorted(cb)} -> {sorted(ca)}")
        for name in sorted(cb & ca):
            r = _compare_curve(base, arm, pb, pa, name)
            r["panel"] = p
            rows.append(r)

    # report
    print(f"\n=== quality: models/{model}__{arm}  vs  {base_label} ===")
    print(f"panels: {len(set(base) & set(armd))} compared, "
          f"{len(missing)} missing, {len(extra)} extra")
    print(f"{'panel':<34}{'curve':<22}{'status':<12}{'max_abs':>9}{'rmse':>9}")
    print("-" * 86)
    n_ok = n_bad = 0
    for r in rows:
        ma = f"{r['max_abs']:.4f}" if r['max_abs'] is not None else "-"
        rm = f"{r['rmse']:.4f}" if r['rmse'] is not None else "-"
        print(f"{r['panel'][:33]:<34}{r['curve'][:21]:<22}{r['status']:<12}{ma:>9}{rm:>9}")
        if r["status"] == "OK":
            n_ok += 1
        else:
            n_bad += 1
    if struct:
        print("\nstructural differences:")
        for s in struct:
            print(f"  - {s}")
    passed = (n_bad == 0 and not missing and not struct)
    print(f"\ncurves: {n_ok} within tol, {n_bad} out of tol/▲ ; "
          f"structural issues: {len(struct)}")
    print(f"QUALITY VERDICT: {'PASS — arm matches the frozen baseline' if passed else 'FAIL — review divergences above'}")
    return passed


def main():
    if len(sys.argv) < 4:
        sys.exit("usage: dig_bench.py {clone|compare|cleanup} <model> <arm>")
    cmd, model, arm = sys.argv[1], sys.argv[2].replace("models/", "").rstrip("/"), sys.argv[3]
    if cmd == "clone":
        clone(model, arm)
    elif cmd == "compare":
        ref = sys.argv[4] if len(sys.argv) > 4 else None
        ok = compare(model, arm, ref)
        sys.exit(0 if ok else 1)
    elif cmd == "cleanup":
        cleanup(model, arm)
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
