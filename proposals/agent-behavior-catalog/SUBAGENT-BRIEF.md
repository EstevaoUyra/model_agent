# Fan-out subagent brief — agent-behavior catalog

**Hand this file verbatim to every Pass-2/Pass-3 mining subagent.** One brief = one schema, one
output contract, one rule-set — the defense against rubric drift across a many-agent fan-out.
Read `INDEX.md` (esp. the "Two stages" box, the entry schema, and "Coverage & blind spots") before
starting. You are building a Stage-1 research MAP, not writing a paper.

## Your task
You will be given: (a) a thread (or thread-cluster) to analyze, (b) a pre-sliced narration bundle
and/or a manifest query, (c) the intervention dates for that thread. Produce a filled entry (schema
below) **plus a machine-verifiable quote ledger**. Read-only — never modify repo files.

## Hard rules (non-negotiable — these encode past failures)
1. **No mentalism.** Write "the narration *stated* X," never "the agent *believed/chose/wanted* X."
   Narration is a behavioral proxy, possibly post-hoc.
2. **Causal claims are associations** unless an isolated experiment separated the variables. Name
   bundled treatments and confounds inline (e.g. "PR #5 changed referent AND split builder/critic").
   Reserve "experiment"/"caused" for isolated tests.
3. **Anecdote ≠ rate.** A quote proves "happened ≥ once," nothing more. Any frequency, disappearance,
   or longitudinal claim needs a denominator (count over the manifest stratum) or an explicit
   `[to-verify-on-deeper-dig]`. **Never** write "did not recur" from a low-recall/keyword sample.
4. **For counts, slice by manifest strata (role × period), not keywords.** Keyword filters destroy
   recall and manufacture false negatives.
5. **Quote exactly.** Every quote must be copy-pasted verbatim from source. Altered/paraphrased
   quotes fail the task — they are checked mechanically (see output contract).
6. **Grade every "why"** with `{intervention-tracked | agent-stated | inferred}`.
7. **Record the Detector** (human / agent / gate / blind re-audit / cold-mining). If you can't tell,
   say so — it measures the catalog's own selection bias.
8. **Finding the hypothesis WEAK is a valid, valuable result.** Do not confirm to please. The E1
   proof-of-concept disconfirmed its own headline (leniency did not recur) — that was the win.

## Output 1 — the entry (fill the schema from INDEX; thread card on top)
Identity (ID, behavior, symptom, kind) · Mechanism (trigger; cause+evidence-grade) · Context (role;
detector) · Trajectory (timeline; lever-type per fix + which held; recurred?/failed?/migrated-to?) ·
Evidence (smoking gun; slice; n/denominator; verified count; confidence & threats-to-validity) ·
Scope/generality (descriptive only) · Links (typed edges) · Deeper-dig hook · Status · Refs.
Write the human-facing prose for someone with project context but in plain language (no insider
shorthand without a gloss). Demote dense ledgers to an "Evidence layer."

## Output 2 — the quote ledger (REQUIRED, machine-verified)
Append one JSONL line per quote you used, to `evidence/<thread>.quotes.jsonl`:
```
{"id":"<thread-id>","path":"<path-relative-to-evidence/corpus-snapshot/>","quote":"<exact verbatim substring, 8-30 words, distinctive>"}
```
- `path` = the agent transcript under `evidence/corpus-snapshot/` (e.g.
  `e8552c97-.../subagents/workflows/wf_19edde3c-0d3/agent-aa96fe049887aa0ec.jsonl`).
- `quote` = a distinctive verbatim substring (not the whole paragraph; must grep to a unique hit).
- The orchestrator runs `evidence/verify_quotes.py` over your ledger; any line that does not match
  its source **fails your entry**. Do not promote a quote into the prose unless it's in the ledger.

## Concurrency / cost
Stay within the fan-out wave (≤4 concurrent — server rate-limit cascade past that). Work only from
your pre-sliced bundle; do not re-mine the whole 6M-token corpus. Cap your own reading.
