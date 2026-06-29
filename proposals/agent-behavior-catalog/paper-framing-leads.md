# Paper-framing leads (Stage 2) — parked, not yet acted on

These are **Stage-2 decisions** (see INDEX "Two stages"). They are *not* instructions to narrow
the catalog. They are captured from a 3-critic adversarial review (conference-fit / rigor /
novelty) of the catalog + the E1 entry on 2026-06-29, so the value isn't lost when we later choose
a framing. Treat as leads to weigh, not settled calls.

## The leading candidate thesis (strongest lead)

> **"Fixes move the bug": targeted interventions suppress the *verbalized* form of an agent bias
> while the underlying failure resurfaces through an uninstrumented channel.**

Evidence already visible in the catalog: E1a leniency → E1b perceptual blind spot (same symptom,
fix didn't cover the new channel); X1 over-routing ↔ X2 under-routing; S2 a decision suppressed in
one model recurring in three. Why it's the best lead: it's non-obvious, transferable, uncomfortable,
and **only obtainable longitudinally / in-the-wild** — a benchmark can't produce it. Inverts E1:
the *migration* is the finding, the leniency is the setup.

Status: hypothesis. Needs the deeper-dig verification below before it's claimable.

## Track / scope leads
- **Benchmark track (1–2pp)** is the deadline-safe option and reframes the work *forward* (a
  designed eval) instead of *backward* (log archaeology), which dissolves the "process-engineering"
  smell. Candidate: a benchmark for **intervention durability** — does fixing a verbalized bias
  remove it or relabel it? — or the narrower **evaluator self-acquittal** probe (does an LLM judge
  pass a discrepancy it has explicitly named?).
- **Paper track (4–9pp)** only viable as a *single-phenomenon case study*, explicitly scoped, after
  the re-analysis. Not 1.5-day-safe.
- For the paper, the critics agree: **cut clusters S/D/T**, de-jargon (no model names), and lead
  with the smoking-gun quote.

## Novelty positioning (for the related-work section, later)
- The biases themselves are **known**: LLM-as-judge leniency, self-preference, sycophancy,
  reward-hacking-the-grader, spec drift. Presenting any as a discovery invites rejection.
- The **only** novel asset is the *longitudinal, intervention-coupled, in-the-wild observational
  design* + the narration corpus. Spend the paper on what that design uniquely yields.
- ⚠️ **Citations from the novelty critic are UNVERIFIED** — it linked two author groups to the same
  arxiv ID and cited 2026 IDs I can't confirm. The *substance* (this is established prior work) is
  right; the specific refs must be checked before use. (Fittingly, the exact hallucination risk this
  project studies — verify, don't relay.)

## Navel-gazing defusers (later)
Reframe from "what broke in our project" → "a natural record of agent behaviour under real
interventions." Foreground generality per retained entry; make one falsifiable, transferable
prediction someone else can test on their pipeline.

---

## Entry-quality guardrails (Stage 1 — APPLY NOW to every entry/template)

These came from the rigor critic but are *catalog-stage*: they make each entry a trustworthy
entry-point, independent of any paper. Now baked into the entry standard.

1. **No mentalism.** Write "the narration *stated* X," not "the agent *chose/anchored/believed* X."
   Narration is a behavioural proxy, possibly post-hoc.
2. **Causal claims are associations unless an experiment isolated them.** Name bundled treatments
   and confounds inline; reserve "experiment"/"caused" for isolated tests.
3. **Anecdote ≠ rate.** A quote is an existence proof ("happened ≥once"). Any frequency,
   disappearance, or longitudinal claim needs a denominator — mark it `[to-verify-on-deeper-dig]`
   if not yet counted. Never assert "did not recur" from a low-recall sample.
4. **Flag selection bias.** The catalog only holds biases we *noticed and fixed*; silent ones are
   excluded by construction. Each prevalence-flavoured statement must carry this caveat.
5. **De-jargon** for the human reader where it doesn't cost precision.
6. **Verify every quote** verbatim against source `.jsonl`; keep the source path in the evidence layer.

## Open `[to-verify-on-deeper-dig]` queue (seeds for the deeper passes)
- E1: full-population verdict-rate counts (BLOCK / PASS / PASS-WITH-CAVEAT) per period, no keyword
  filter — to replace the sampled "not observed" with a measured rate + CI.
- E1: frozen-figure replay (old vs new auditor, pinned model, change only referent) to isolate the
  referent's effect from the builder/critic split.
- All threads: join each agent to its session LLM version (rule out model-upgrade confound).
- Method C (un-distilled bias discovery): a *sampled* sweep to estimate what the fix-driven catalog
  cannot see; ideally one injected-fault probe to get an unbiased detection rate for one bias class.
