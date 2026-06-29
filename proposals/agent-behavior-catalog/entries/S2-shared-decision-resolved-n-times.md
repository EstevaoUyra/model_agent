# S2 — One shared decision gets re-litigated independently at every site

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · agent-behavior (multi-agent / orchestrator) |
> | Behavior | failure to recognize a *shared root*: one underdetermined decision is encountered and worked as N independent local bugs |
> | Symptom | three models (RH2009, heeger_1992, hermann2010) each block/drift on divisive-normalization **saturation** and each treats it as its own model bug |
> | Agent role | builder + faithfulness/process auditors + orchestrator (the consolidation is the organizer's) |
> | Trigger | a paper-underdetermined mechanism is reused across a model genealogy; each model's loop hits it locally with no view of the others |
> | Cause (evidence) | shared reuse surface (R&H normalization) + per-model isolation of the workflow loop — *intervention-tracked structurally (calibration.yaml routes the fix cross-model)*; underdetermination is *paper-grounded* |
> | Detector | another agent (per-model audits each flag it) + human/orchestrator (recognized it as ONE decision, 2026-06-04) |
> | Lever(s) | doc (consolidated human spec-review packet) — **not yet resolved** |
> | Flags | ⟳ recurs at each genealogy level · `shared-root` |
> | Status | **open** |

## The behaviour

The attention-normalization model genealogy shares one mechanism — **divisive-normalization
saturation** (whether contrast-response curves reach the paper's high-contrast plateau). The
mechanism is **underdetermined by the papers** (the reachable plateau depends on an unaudited
saturation/width choice). Because the mechanism is *reused* across models (hermann2010 and the
others consume the Reynolds & Heeger normalization surface), the same decision surfaces in **three
different model reproductions** — RH2009 (`SQ-005`), heeger_1992 (`Vₑ` width), hermann2010 (`NF1`
Fig-1a response-gain) — and each workflow loop, running in isolation on one model, encounters it as
*its own* local bug to fix.

The structural tell is that the agents working hermann2010 correctly observe the root is **not
local**: the saturation is owned by another model's frozen knob, not hermann's:

> *"A-008 (Fig 1a saturation) remains broken via a cross-model R&H knob."* — hermann2010 audit
> *"saturation is owned by R&H's regime.response_gain.\* which is [frozen]"* — hermann2010 update-state
> *"This is the same under-saturation issue that was flagged in R&H but for [the response_gain]"* — hermann2010 audit

So the *shared root* is visible from inside a single model's loop — but the loop has no mechanism to
**consolidate** it into one decision; absent the organizer doing that, it would be resolved once per
model (three times), each time as a separate fix, each time tempted toward "just raise the gain."

## Why it happens (graded)

- **Structural / intervention-tracked (strong):** the coupling is explicit in committed artifacts —
  hermann2010's `calibration.yaml` *routes its fix back* to "reynolds_heeger_2009 / raise the R&H
  saturation gain," i.e. the fix isn't in the model that's red. The reuse surface
  (`rh_model.crf_protocol.run_crf`, `regime.response_gain.*`) is shared, so one mechanism decision
  has three downstream consumers. This is a property of the dependency graph, not a stated belief.
- **Paper-grounded underdetermination (strong):** the decision is genuinely unsettled by the
  sources — e.g. heeger p.184 "filter orientation range 60°" vs "cell tuning widths" cannot both
  hold once response ∝ Vₑ² (squaring narrows FWHM by √2); RH2009's 2D→1D suppression reduction
  makes S *smaller*, not larger, so it cannot deliver saturation. So there is a real human choice,
  not just a bug.
- **Isolation of the loop (inferred):** each full-pass runs one model with no cross-model view, so
  the default is N local resolutions. Inferred from the per-model structure, not separately tested.

## Why it's still OPEN (the important part)

This thread is **open by design, correctly.** The right move was *recognized* — RH2009-SQ-005,
hermann-NF1, and heeger-Vₑ are facets of **one human spec-review decision** about the R&H
normalization-saturation mechanism, to be consolidated and decided **once**, not three times. The
consolidation was written up as a human spec-review packet (`saturation-spec-review-2026-06-04`,
status OPEN) offering three mutually-exclusive resolutions (audited saturation constant /
mechanism-is-wrong / stimulus geometry). But the **decision itself** — which clause binds, whether
the 1D mechanism is the defect — is reserved for human spec-review and **has not been made.** Until
it is, the models stay honestly red rather than force-green:

> *"the three NF1 response-gain saturation tests are RED at the latest commit"* — hermann2010 audit-process

Critically, the builder/auditors did **not** paper over it: hermann's last commit was a "STUCK
escalation, no force-green," and the response-gain twin was left RED. The forbidden shortcut —
"just raise the gain" to make one model green — is exactly the over-reach S1 names (and the
saturation packet explicitly bans: *"Do NOT let the organizer or a builder 'just raise the
gain'"*). So the open status is a **correct refusal to resolve a shared decision locally**, not a
stall.

## How it responded to intervention

The lever applied is a **doc**: consolidate the three sites into one human-owned decision packet so
it is decided once. That lever has held in the sense that no site unilaterally resolved it — but the
underlying decision is unmade, so the thread is **mitigated-against-fragmentation, unresolved-on-substance.**
No gate/test or structural lever has been applied (and arguably none can resolve it — it needs a
human spec call). Recurrence ("recurs at each genealogy level") is asserted from the three named
sites, which is an enumerated set, not a sampled rate.

## Confidence & threats-to-validity

**Moderate-to-high on the structure, by design unresolved on outcome.** Threats:
- **The "N independent resolutions" counterfactual is partly averted, not observed** — the
  organizer recognized the shared root *before* three separate fixes shipped, so we mostly see the
  *avoidance* of fragmentation, plus the artifacts (calibration routing) that would have caused it.
  The pure failure mode (three divergent local fixes merged) was not allowed to run to completion.
- **Three sites is an anecdote-set, not a rate** — it shows the shared-root pattern happened across
  ≥3 models in one genealogy; it does not establish a frequency across the corpus.
- **Corpus quotes are from hermann2010's loop** (one model, one full-pass `wf_7f2034c2-c60`); they
  ground "the agents saw the cross-model root," not the heeger/RH2009 sites (those rest on
  git + the spec packet). `[to-verify-on-deeper-dig]`: pull the RH2009 (`wf_246026d2-440`) and
  heeger audit narration for the same cross-model framing.
- `claude_model` constant (`claude-opus-4-8`) — model-version confound ruled out corpus-wide.

## Timeline

| Date | Event | Ref |
|------|-------|-----|
| 2026-06-04 | RH2009 blocks on SQ-005; hardened full-passes on heeger + hermann surface the SAME saturation theme | `saturation-is-the-genealogy-blocker`; PR-era `7a9e76f` |
| 2026-06-04 | Recognized as ONE shared human decision; consolidated spec-review packet (status OPEN) | `saturation-spec-review-2026-06-04.md` |
| 2026-06-04 | hermann NF1 left RED ("STUCK escalation, no force-green"); fix routed to R&H surface | corpus `wf_7f2034c2-c60`; `calibration.yaml` |
| (open) | Human spec-review decision (a/b/c) not yet made | `saturation-spec-review-2026-06-04.md` |

## Links
- `shared-root` — RH2009 `SQ-005` ⋈ heeger `Vₑ` ⋈ hermann `NF1`: three sites, one R&H
  normalization-saturation decision (the catalog's canonical shared-root edge, per INDEX).
- `connects-to S1` — "just raise the gain" is the organizer-over-reach reflex (S1) aimed at this
  shared decision; S2 is the place the catalog says explicitly *do not* resolve it unilaterally.
- `connects-to X2` — escalation-to-human is the *correct* disposition here (paper-underdetermined),
  the inverse case to X1's over-routing of paper-resolvable findings.

## Deeper-dig hook
`grep -ril "reuse surface\|saturation" corpus-snapshot/<rh2009 wf_246026d2-440>/ <heeger wf>/` and
extract message-text narration framing the saturation as cross-model vs local, to confirm all three
sites independently named the shared root. Spec packet: `saturation-spec-review-2026-06-04.md`.

## Status
**Open.** Mitigated against *fragmented* resolution (consolidated to one packet, no force-green);
the substantive human spec decision is outstanding. `Refs:` memory
`saturation-is-the-genealogy-blocker`, `re-audit-after-every-model-change`,
`organizer-doesnt-implement-trust-the-process`; proposal `saturation-spec-review-2026-06-04`;
corpus `wf_7f2034c2-c60` (hermann2010).

## Evidence layer
**Corpus-grounded (hermann2010 loop) + git/proposals.** Ledger: `../evidence/S2.quotes.jsonl`
— 4 quotes, all verified verbatim by `../evidence/verify_quotes.py S2` (4/4, exit 0), drawn from
four distinct hermann2010 workflow agents (audit-faithfulness `ac41…`, update-state `a518…`,
audit-faithfulness `a01e…`, audit-process `a9af…`) in full-pass `wf_7f2034c2-c60`. The heeger and
RH2009 sites are git/proposal-grounded, not yet quote-backed (`[to-verify-on-deeper-dig]`).
