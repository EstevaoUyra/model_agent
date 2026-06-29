# T5 — The agent ran the tool it had on an input the tool didn't fit

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Tool / environment · agent-behavior (tool-adjacent) |
> | Behavior | law of the instrument: faced with an input the available tool was not built for, the agent runs the tool anyway (or quietly falls back to eyeballing) instead of declaring a capability gap |
> | Symptom | a curve tracer aimed at a figure that has no curve to trace (a filter dictionary / schematic / image grid); a fabricated "digitized" reference produced by forcing an unfit pipeline |
> | Agent role | digitize-figure; audit-digitization (as the policing role) |
> | Trigger | the panel is not the figure type the toolbox handles (a "Mode-2" dictionary/image or a schematic), but the curve tracer is the capability at hand and the task says "digitize this panel" |
> | Cause (evidence) | tool-selection by availability, not fit ("the tool it has") → *intervention-tracked* (the fix is "no tool ⇒ BLOCKED, never silent fallback") |
> | Detector | human (figure-digitization design retro); the fix installs an agent/gate detector (audit-digitization TOOL-MISUSE/BLOCKED verdicts) |
> | Lever(s) | structural/spec — figure-type taxonomy + "tool selection is a recorded, auditable decision" + "no tool ⇒ BLOCKED" + an auditor verdict category for tool-misuse |
> | Flags | — (corpus is dominated by the post-fix discipline operating) |
> | Status | mitigated · `claude_model` constant `claude-opus-4-8` |

## The behaviour

Give an agent a curve-tracing toolbox and ask it to "digitize this figure," and it tends to reach
for the tracer **even when the panel is not a curve** — the classic *law of the instrument*: the
hammer is in hand, so everything looks like a nail. The design retro names the exact failure to
engineer out: *"the agent reaching for the curve tracer on a filter dictionary because that is the
tool it has."* The two bad outcomes are (1) running the wrong tool and producing a meaningless or
fabricated trace, and (2) silently giving up on the tool and going back to eyeballing — both
disguise a *capability gap* as a completed digitization.

This is distinct from E3. E3 is trusting a tool's *output* (the tracer ran, the overlay "looks
fine," ship it). T5 is mis-*selecting* the tool in the first place — pointing a Mode-1 curve tracer
at a Mode-2 dictionary/image. E3 is about the verdict on a result; T5 is about the choice that
precedes the result.

## Why it did it

**Cause (intervention-tracked): tool selection defaulted to availability rather than fit.** The
toolbox grew curve-first (highest coverage), so the curve tracer was the most-available capability;
an agent told to digitize "all panels" had a path of least resistance through that tool even for
panels it couldn't represent. The fix is structural: register a *figure-type taxonomy* up front so
each type is a named slot and the empty slots are visible holes; make **tool selection a recorded,
auditable decision** (figure type → tools chosen → why) that a reviewer challenges; and enforce
**"no tool ⇒ BLOCKED, never a silent fallback"** — a missing capability must surface as an explicit
gap, exactly like a missing paper image, and must not quietly route to the wrong tool or back to
eyeballing.

## How the behaviour responded to the intervention

The corpus shows the post-fix discipline operating: agents classify the panel's "Mode" first and
**route unfit panels out instead of forcing the tracer.** A digitizer handed a schematic declines
to run the curve tools on it:

> *"…route this schematic through the curve-tracing tools"* — quoted in the negative: the agent
> records that it did **not** do this, citing the skill's "what this is NOT" clause.

Another digitizer, hitting a panel with no extractable curve, names forcing it as the forbidden
move and routes it back rather than fabricating a reference:

> *"The correct outcome is to **not force a curve** and route it back"*

And the audit-digitization role now carries an explicit verdict category that *polices tool
selection* — a reviewer can return TOOL-MISUSE or BLOCKED, and clears it only when the tool set fits
the figure type:

> *"not TOOL-MISUSE** — provenance complete, tool set correct (Mode-1)"*

That auditor category is the structural backstop: tool *choice*, not just tool *output*, is now an
auditable, blockable decision.

## How confident I am, and what could be wrong

Moderate on the behaviour's existence; weak on rate.

- **The raw pre-fix incident (curve tracer on a filter dictionary) is named in the design retro,
  not quoted from role-tagged narration.** The digitize/audit roles in the manifest begin at/after
  the 2026-06-03 hardening, so the corpus is dominated by agents *reciting and applying* the Mode
  taxonomy and the "don't force it, route it" rule — not by the original misuse. I can show the fix
  working (schematic not routed through the tracer; "not force a curve and route it back"; auditor
  TOOL-MISUSE category) but cannot quote a pre-fix "I'll just run the tracer on this dictionary."
- **Confound — recitation ≠ behaviour change.** Every post-fix digitizer cites the Mode taxonomy
  because it's in the prompt; the genuine routing decisions (schematic declined) show it sometimes
  *operates*, but the catalog cannot say how often the routing is real vs ritual.
- **Detector bias:** original detector is the human design retro; the installed detector is the
  audit-digitization role, an agent/gate.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-03 | Design retro names the failure to engineer out ("curve tracer on a filter dictionary because that is the tool it has") and the fix: figure-type taxonomy + recorded tool-selection + "no tool ⇒ BLOCKED, never silent fallback" | `figure-digitization-design-2026-06-03.md` l.56-59 |
| 2026-06-03 | "no-tool ⇒ BLOCKED" + auditor TOOL-MISUSE/BLOCKED verdicts encoded | commit e3dbba3; `digitize-figure` / `audit-digitization` skills |
| 2026-06-03+ | Post-fix: digitizers classify Mode first and route unfit panels (schematics) out; auditors clear "tool set correct (Mode-1)" / can return TOOL-MISUSE | `e8552c97…/wf_af948253-90f`, `…/wf_19edde3c-0d3`, `…/wf_1dbdd4b1-ef4` |

---

## Evidence layer (for verification, not reading)

- **Smoking gun (behaviour):** design retro `figure-digitization-design-2026-06-03.md` l.56-59 —
  "the agent reaching for the curve tracer on a filter dictionary because that is the tool it has …
  must not quietly route to the wrong tool or back to eyeballing." Proposal-grounded; the raw misuse
  is **not** in the role-tagged narration stream.
- **Smoking gun (fix operating, in-corpus):** `e8552c97…/wf_af948253-90f/agent-a566a44b5a8a4c147.jsonl`
  (schematic deliberately not routed through the curve tracer), `…/wf_19edde3c-0d3/agent-acce722ad0640c87e.jsonl`
  ("not force a curve and route it back"), `…/wf_1dbdd4b1-ef4/agent-a43922d74e8dda8e1.jsonl`
  (auditor's "tool set correct (Mode-1)" / TOOL-MISUSE category).
- **Quote ledger:** `../evidence/T5.quotes.jsonl` — 3 quotes, verify with
  `python3 ../evidence/verify_quotes.py T5` (exit 0). The originating tool-misuse incident is
  proposal-grounded only — stated here per the catalog's honesty rule.
- **Refs:** proposal `figure-digitization-design-2026-06-03.md`; commit e3dbba3.

## Links

- `connects-to → E3` — adjacent tool-trust failures: E3 trusts the tool's *output* (rubber-stamps a
  ran trace); T5 mis-selects the tool *input-side* (runs an unfit tool / silently eyeballs). Same
  toolbox, different decision point. Both fixed in the same 2026-06-03 digitize/audit hardening.
- `connects-to → X3` — shared root "reach for the knob/tool you have": X3 forces a curve with the
  nearest *parameter* (a per-figure gain) when the real fault is elsewhere; T5 forces a result with
  the nearest *tool* when no tool fits. Both are law-of-the-instrument; both are fixed by making the
  unfit move structurally impossible (BLOCKED / SQ-blocking) rather than relying on judgment.

## Deeper-dig hook

Sample the `unknown`/older inline-prompt stratum and any pre-2026-06-03 digitization narration (the
spratling/olshausen dictionary work) for the raw "run the tracer on a non-curve" move, to establish
the behaviour existed in narration before the fix and to estimate how often post-fix routing is
genuine vs recited. Data: `evidence/manifest.jsonl` (roles `digitize-figure`, `audit-digitization`,
`unknown`); grep `Mode-2`, `BLOCKED`, `TOOL-MISUSE`, `route it` in text/thinking blocks.

## Status

`mitigated` — figure-type taxonomy + recorded/auditable tool-selection + "no tool ⇒ BLOCKED" +
audit-digitization TOOL-MISUSE/BLOCKED verdicts; post-fix agents route unfit panels out rather than
forcing the tracer. Residual misuse rate uncharacterised; original detector is human.
