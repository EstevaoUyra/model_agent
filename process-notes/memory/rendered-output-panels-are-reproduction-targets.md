---
name: rendered-output-panels-are-reproduction-targets
description: "A figure panel that is a rendered MODEL OUTPUT is a reproduction target even inside a schematic and even with no numeric claim; classify per-panel by content, not per-figure"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e8552c97-c722-4643-9557-00815e47fc70
---

When classifying whether a figure is reproducible, **classify per-PANEL by CONTENT, not per-figure by position/role.** A panel that is a *rendered model output* (a population-field heatmap, a simulated curve, any model-computed image) is a reproduction target — even when it is embedded in a flow/schematic diagram and even when it "makes no quantitative gain-regime claim." A model render IS a quantitative output.

The "schematic exemption" (skip digitization/reproduction) applies ONLY to genuinely hand-drawn diagram chrome — nodes, arrows, operators, cartoons. Same figure number can flip: heeger_1992 Fig 1 = true schematic (nodes/arrows) → correctly blocked; reynolds_heeger_2009 Fig 1 = flow diagram whose NODES are rendered E/A/S/R population-field images → wrongly exempted as "schematic, no gain-regime claim."

**Why it matters (the cost of the miss):** RH2009 Fig 1's Suppressive-Drive panel is a direct visual check on the exact quantity the suppression bug broke (S came out far too small — see [[saturation-is-the-genealogy-blocker]]). Reproducing it would have (a) forced the correct 2D `simulate()` pipeline rather than the 1D-reduced CRF protocol, and (b) shown the wrong S field to the eye — likely catching the bug's *direction* early, BEFORE the figure-fitted `suppressive_drive_gain` spiral, possibly without needing the authors' code at all. Discovered 2026-06-04.

**How to apply:** in extract-figure / digitization classification, scope IN any panel that is a model render. Reserve "schematic / not-reproduced" for hand-drawn chrome only. When a figure mixes both (flow diagram + render nodes), reproduce the render nodes. Use the [[vlm-eye-is-arbiter-over-tools]] eye to decide render-vs-sketch, not the caption's framing ("no quantitative claim" ≠ "not a model output").
