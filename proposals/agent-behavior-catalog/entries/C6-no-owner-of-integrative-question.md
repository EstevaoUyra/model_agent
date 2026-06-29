# C6 — No agent owns the integrative question: a cross-cutting defect falls between per-figure agents

> **Thread card** (queryable fields; prose below)
> | field | value |
> |---|---|
> | Domain · Kind | Coordination · agent-behavior (multi-agent decomposition gap) |
> | Behavior | a decomposition into per-figure / per-spec / per-repo agents leaves the **whole-model, cross-figure question unowned**; a defect shared across several figures (or several models) is in no single agent's scope and is asked by no one |
> | Symptom | a normalization inversion shared across pestilli / heeger / doostani falls *between* the per-figure checklist, the per-spec completeness check, and the git-state check — "the integrative question was asked by no one" |
> | Agent role | the ensemble of narrow auditors (per-figure checklist · per-spec completeness · git-state) — and the missing standing Faithfulness Auditor |
> | Trigger | work is sharded into local scopes (one figure / one spec / one repo per agent) with no agent scoped to "does the whole model read like the paper?"; the defect's support set spans shards |
> | Cause (evidence) | structural decomposition gap — *intervention-tracked* (the fix is a new role, the standing Faithfulness Auditor, explicitly tasked with "the integrative … question E3 names") |
> | Detector | **human post-mortem** (the 2026-06-02 faithfulness-enforcement audit, cluster E3) |
> | Lever(s) | structural/role — create the standing Faithfulness Auditor that *holds both* the full paper and the finished implementation and owns the integrative question |
> | Flags | `inverse-of S2` · fills the INDEX "emergent multi-agent dynamics" blind spot |
> | Status | mitigated (role proposed/added; cross-model integrative coverage not independently confirmed in this slice) |

## The behaviour

The pipeline was sharded for parallelism and for the paper-blind boundary: one agent checks a
figure's visual checklist, another checks a spec's completeness, another checks git state. Each shard
is locally competent. But a class of defect has a **support set that spans shards** — the same wrong
decision shows up a little in figure A, a little in figure B, across two or three models — and no
shard is scoped to look across them. So the defect is not *missed* by a responsible agent; it is
**owned by no agent at all**. The whole-model, "does this read like the paper end-to-end?" question
is structurally homeless.

The smoking gun is the normalization inversion that ran across three models:

> "**E3. No agent owns the integrative question.** Per-figure checklist + per-spec completeness +
> git-state checks; the cross-cutting defect (normalization inversion shared across
> pestilli/heeger/doostani) falls between them." — faithfulness-enforcement, cluster E

and the post-mortem's blunt summary of the same gap: the cross-cutting defect "falls between" the
narrow checkers, and the integrative question was asked by no one. The proposed remedy names the
missing owner directly — a standing Faithfulness Auditor that "holds both the full paper AND the
finished implementation" and whose checks include "the integrative 'does the whole model read like
the paper?' question E3 names."

## Why C6 is the **inverse** of S2 (the distinction that makes it a separate thread)

C6 and S2 are mirror images of the same coordination axis — *who owns a decision that spans several
sites?* — and the catalog needs both poles:

- **S2 — a shared decision owned by *everyone*.** One underdetermined mechanism (R&H normalization
  saturation) is encountered at three sites and each loop, in isolation, treats it as *its own* local
  bug — N redundant resolutions of one decision. The risk is fragmentation: the same call litigated
  N times.
- **C6 — a shared defect owned by *no one*.** A cross-cutting defect spans three models and *no*
  agent is scoped to the span — zero resolutions, because the integrative question is in no shard.
  The risk is omission: the call litigated zero times.

Same structural feature (a concern whose scope crosses the per-model/per-figure decomposition);
opposite failure (over-attention that fragments vs. under-attention that drops). That is exactly why
they are linked `inverse-of` rather than merged: a fix that tightens ownership to avoid C6's
no-owner gap (a single integrative auditor) is the *same dial* whose other extreme produces S2-style
redundant local resolution, and vice versa. This pair is what the INDEX flags as the unfilled
"emergent multi-agent dynamics" blind spot — a defect's fate determined by the *shape of the
decomposition*, not by any one agent's judgment.

## How it responded to intervention

The lever is **structural/role**: stand up a Faithfulness Auditor that runs *after* the build (so it
cannot corrupt the paper-blind construction), holds the paper and the implementation together, and is
explicitly charged with the integrative whole-model question that no per-figure shard covered.
Because it sees the model as a whole rather than one figure at a time, a defect whose support set
spans figures is now inside *someone's* scope. C6 is filed **mitigated**: the missing owner is named
and the role is the documented fix, but whether the new auditor actually catches a *cross-model*
inversion (the pestilli/heeger/doostani span, not just a within-model one) is `[to-verify-on-deeper-
dig]` — the auditor as specified runs per-model, so the across-model span may still need the
corpus-level Process-Auditor pass to be fully owned.

## Confidence & threats to validity

Moderate. One named, concrete cross-cutting defect (the normalization inversion across three named
models) is strong evidence the gap is real and not hypothetical. Threats:

- **Anecdote ≠ rate.** One cross-cutting defect across three models shows the no-owner gap happened;
  it does not establish how often shard-spanning defects arise or how many slip.
- **Detector is human.** The gap was found by a human reading the audit, by construction — a narrow
  shard *cannot* report a defect outside its own scope, so only a cross-cutting reader (here, a human)
  could see it. This is the catalog's selection bias in its purest coordination form.
- **Outcome partly unconfirmed.** "Mitigated" rests on the role being the documented fix; the
  per-model Faithfulness Auditor may still leave the *across-model* span (the actual pestilli/heeger/
  doostani case) to the corpus-level pass — so the precise defect that motivated C6 is not provably
  owned end-to-end by the named fix.

## Scope / generality

Descriptive. The mechanism — sharding work into local scopes with no agent owning the cross-scope
integrative question, so span-crossing defects are unowned — is generic to any divide-and-conquer
multi-agent (or multi-reviewer) system. Setup-specific in the particular shards (per-figure checklist
/ per-spec completeness / git-state) and the normalization-inversion instance.

## Links
- `inverse-of S2` — **same axis, opposite pole.** S2 = one shared decision owned by everyone
  (resolved N×, fragmentation); C6 = one shared defect owned by no one (resolved 0×, omission).
- `connects-to E3` (tool/VLM rubber-stamp) is *not* this E3 — note the source proposal's internal
  label "E3" is the faithfulness-enforcement cluster item, not the catalog's E3 thread; C6 is the
  catalog home for that proposal finding.
- `connects-to C7` — both are multi-agent independence/coverage failures surfaced in the same audit
  cluster: C7 = two reviewers correlated (no independent second look); C6 = no reviewer scoped to the
  whole (no integrative look at all).

## Deeper-dig hook
(1) Confirm whether the standing Faithfulness Auditor (or the corpus-level Process-Auditor pass)
actually flags a *cross-model* shared defect, not just within-model — slice the auditor narration for
pestilli/heeger/doostani and look for any agent naming the shared inversion across all three. (2)
Enumerate other cross-cutting defects (shared knobs, shared equations, reused protocols) and check
which shard, if any, owns each — denominator for "how often is the integrative question homeless."
Data: `faithfulness-enforcement-2026-06-02` (Part 2 §1 Faithfulness Auditor; §1b Process Auditor),
per-model audit narration under `evidence/corpus-snapshot/`.

## Status
**mitigated** — the no-owner gap is named and the integrative-owner role is the documented fix;
cross-model coverage by that role is not independently confirmed in this slice.

## Refs
- Proposal (PRIMARY): `proposals/faithfulness-enforcement-2026-06-02.md` (cluster E3, l.110-112; Part
  2 §1 the standing Faithfulness Auditor; §1b the Process Auditor for corpus-level systemic drift).
- Sibling/inverse: **S2** (shared decision resolved N×). Cousin: **C7** (correlated reviewers).

---

### Evidence layer (for verification, not reading)
- **Grounding:** the committed faithfulness-enforcement post-mortem (cluster E3 + the Part-2 remedy).
  **No quote ledger produced** — the Detector is, by construction, a human cross-cutting reader (no
  shard could report a defect outside its scope), and the diagnosis lives verbatim in the proposal, a
  stronger citable source than workflow-agent narration. Per the brief, proposal-grounded → no ledger
  expected.
- **`[to-verify-on-deeper-dig]`:** the per-model audit transcripts for pestilli/heeger/doostani are in
  `evidence/corpus-snapshot/`, but a *within-shard* transcript cannot contain the cross-cutting
  observation by definition; the integrative finding lives only in the human audit. Not promoted.
