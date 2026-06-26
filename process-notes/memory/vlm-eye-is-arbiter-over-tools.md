---
name: vlm-eye-is-arbiter-over-tools
description: "When agents have digitization/measurement tools, they rubber-stamp the visual check and trust tool output over their own eyes — the overlay check must be adversarial and the eye must override the tool"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

Giving an agent good tools (axis calibration, curve tracer, PCHIP, overlay) creates a
new leniency mode: the agent treats the tool output as authoritative and uses the
visual overlay step to **confirm** rather than to **find** mismatches. Obvious
visual artifacts then survive — a curve shifted off the axis (calibration drift), an
apex overshooting into a spike (PCHIP on a sharp peak), a non-monotone wiggle where two
curves cross (tracer with no colour/style channel). The human catches them at a glance;
the agents did not, because "VIEW it, confirm it tracks" invites a rubber-stamp.

**The user's framing (2026-06-03):** *"It seems to be due to overly relying on the
tools. Aren't the agents doing VLM? Shouldn't it be obvious these don't match?"* — Yes,
and that's the point: the eye is in the loop but is being used to bless the tool, not to
judge it.

**Why:** the tools are *approximate exactly where the scan is hard* (fitting an axis
frame, smoothing an apex, separating curves at a crossing). The agent's visual judgement
is the only thing that can catch the tool being wrong there. Same root as
[[faithfulness-critics-want-to-find-issues]]: confirmation-framing → leniency.

**How to apply** (now encoded in `digitize-figure` step 5 + `audit-digitization` step 1):
- The overlay check is **adversarial**: look for every place the line leaves the ink;
  "it tracks well" is not an acceptable conclusion — enumerate axis alignment, each
  curve's worst residual, apex overshoot, crossing wiggles.
- **The eye outranks the tool.** If the rendered curve doesn't sit on the paper, the
  tool output is wrong — re-anchor / hand-place, don't trust calibration/tracer/PCHIP.
- **Audit the overlay that *ships*** (the README image), not just a clean re-trace of
  the data — the render can drift from faithful data through its own calibration/PCHIP.
  A numeric match does not clear a visually-mismatched picture.
- Don't re-render the shipping overlay later with a different calibration than was
  validated (that broke Fig 2A — the data was fine, the re-render drifted).

Generalizes beyond digitization: whenever you hand an agent a tool, make the agent's
own judgement the arbiter *over* the tool, and frame the check to find faults, not bless.
Relates to [[capture-discovered-knowledge-in-artifacts]].
