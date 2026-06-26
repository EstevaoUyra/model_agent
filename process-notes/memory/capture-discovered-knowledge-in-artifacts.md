---
name: capture-discovered-knowledge-in-artifacts
description: "Process knowledge you discover while working must go into the durable artifact (docstring/skill) at point of use, not stay in your context"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b2b7a60-da9d-4ae5-bb82-a3a5b9885198
---

When you discover process knowledge while working — a tool's limitation, the right
way to use it, a gotcha (e.g. "the curve tracer can't separate two same-colour curves
that overlap on a grayscale scan; trace the envelope instead"), or a sharpened rule —
**write it into the durable artifact where the next agent will hit it**: the function
docstring (point of use), the relevant SKILL, or the spec. Do NOT just apply the fix
from your own context.

**Why:** the user's words — *"It doesn't make sense for us to have you going there and
doing with your own context, otherwise we don't learn the process."* If the knowledge
lives only in the organizer's head, the process hasn't learned: the next agent
rediscovers the same limitation, burns the same cycles, or repeats the same error.
Pillar 4 (process is the deliverable) made literal. This is the same reason critics are
separate and report-only — knowledge and judgement must be externalized into the
system, not carried by one privileged context.

**How to apply:**
- Tool limitation / usage pattern → the **function docstring** (the agent reads it when
  it reaches for the tool), plus a check in the consuming skill if a critic should
  enforce it.
- A rule the case sharpened (e.g. normalization: "if the paper's curves don't reach 1.0,
  yours must not either — never per-panel auto-normalize") → the **skill / spec** where
  the rule already lived, made un-missable.
- Before "fixing it myself," ask: where would an agent need to already know this to not
  repeat my discovery? Put it there.

Relates to [[organizer-operating-model]], [[project-vision-four-pillars]], and the
separate-critic principle in [[faithfulness-critics-want-to-find-issues]].
