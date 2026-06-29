#!/usr/bin/env bash
# U1 injected-fault probe — measure whether the coverage gate (not a human) catches a
# silently-skipped required step. Isolated: operates on a throwaway copy, never touches a real model.
#
# Usage:  bash u1_coverage_probe.sh [models/<name>] [figs]   (default: models/boynton_2009 1,2)
# Result: prints baseline exit (expect 0=complete) and post-fault exit (expect 1=BLOCKED).
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"   # repo root (…/model_agent)
MODEL="${1:-models/boynton_2009}"
FIGS="${2:-1,2}"
FIG1="$(echo "$FIGS" | cut -d, -f1)"
P="$(mktemp -d)/probe_model"
cd "$ROOT" || exit 2

rsync -a --exclude='.git' "$MODEL/" "$P/"
( cd "$P" && git init -q && git add -A && git commit -q -m "probe baseline" )

python3 "$ROOT/tools/check_figure_coverage.py" "$P" --figures "$FIGS" >/dev/null 2>&1
echo "baseline (nothing removed): exit $?  (expect 0 = complete)"

# inject fault: silently drop figure_<FIG1>'s committed render (a skipped render step)
( cd "$P" && git rm -q "figures_reproduced/figure_${FIG1}.png" 2>/dev/null \
            || git rm -q "figures_reproduced/figure_${FIG1}.jpg" 2>/dev/null
  git commit -q -m "simulate silently-skipped render step" )

python3 "$ROOT/tools/check_figure_coverage.py" "$P" --figures "$FIGS" >/dev/null 2>&1
echo "after fault (fig $FIG1 render removed): exit $?  (expect 1 = BLOCKED by the gate, no human)"
rm -rf "$(dirname "$P")"
