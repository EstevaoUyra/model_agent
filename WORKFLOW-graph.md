# full-pass — the agent graph

The `full-pass` reproduction workflow (`.claude/workflows/full-pass.js`) as a
directed graph: **every agent appears exactly once**, and the caps/retries are
drawn as **loops** (back-edges). It is the visual companion to
[WORKFLOW.md](WORKFLOW.md).

> **Keep this in sync.** Any change to the workflow — to [WORKFLOW.md](WORKFLOW.md)
> *or* to `.claude/workflows/full-pass.js` (a node, an edge, a loop, a cap, a
> routing rule) — **must be reflected in the graph below.** The graph and the prose
> are two views of one process; if they disagree, that is a bug to fix, not a
> nuance to leave.

Green = build/author agents · red = independent auditors (an auditor never audits
its own output). The reused agents collapse to a single node each: `extract-spec`
(extractor **and** the paper-fix *resolver*), `audit-spec` (the Phase-A *gate*
**and** the paper-fix *verifier*), and `implement` (initial build **and** the
verify-loop fix).

```mermaid
flowchart TD
  E0([from = extract]):::entry
  B0([from = build]):::entry
  F0([from = fix]):::entry

  ACQ([acquire-sources]):::build
  XSPEC([extract-spec]):::build
  XFIG([extract-figure]):::build
  DIG([digitize-figure]):::build
  IMPL([implement]):::build
  ATEST([author-tests]):::build
  SWEEP([stale-artifact sweep]):::build
  SMOKE([modification smoke test]):::audit
  COV([coverage gate]):::audit
  UPD([update-state]):::build
  PR([commit + push + PR]):::build

  ADIG([audit-digitization]):::audit
  ASPEC([audit-spec]):::audit
  AUTEST([audit-tests]):::audit
  AFAITH([audit-faithfulness]):::audit
  APROC([audit-process]):::audit

  BLOCK([BLOCKED]):::term
  DONE([DONE / PARTIAL]):::term

  E0 --> ACQ
  ACQ -->|paper not fetchable| BLOCK
  ACQ --> XSPEC
  ACQ --> DIG
  DIG --> ADIG
  ADIG -->|defect, loop up to 3| DIG
  ADIG -->|crops committed| XFIG
  XFIG -->|describe contract recorded| ASPEC
  XSPEC -->|gate / verify the contract| ASPEC
  ASPEC -->|DIVERGENT: resolve, loop up to 2| XSPEC
  ASPEC -->|cap reached| BLOCK
  ASPEC -->|FAITHFUL| IMPL

  B0 -->|skip Phase A; full build| IMPL
  F0 -->|round 1: test-first| ATEST

  IMPL --> AFAITH
  IMPL --> APROC
  AFAITH -->|transient audit failure| BLOCK
  AFAITH -->|no actionable findings| DONE
  AFAITH -->|findings, rounds remain| ATEST
  AFAITH -->|findings at cap: no unaudited mutation| DONE
  ATEST --> AUTEST
  AUTEST -->|not paper-grounded: re-author| ATEST
  AUTEST -->|CONTRACT_BUG / PAPER_ISSUE| XSPEC
  AUTEST -->|CODE_BUG| IMPL
  XSPEC -->|paper-fix verify cap in Verify| BLOCK

  DONE --> SWEEP
  BLOCK --> SWEEP
  APROC --> SWEEP
  SWEEP --> SMOKE
  SMOKE --> COV
  COV -->|complete| UPD
  COV -->|incomplete: downgrade to blocked| UPD
  UPD --> PR

  classDef build fill:#d6f5e0,stroke:#1b7a44,color:#0c3d22;
  classDef audit fill:#ffe0db,stroke:#c0392b,color:#641a12;
  classDef entry fill:#e8eef7,stroke:#33506e,color:#1b2c40;
  classDef term fill:#2b2b33,stroke:#000,color:#fff;
```

## The loops (caps guarantee termination)
- `digitize-figure ⇄ audit-digitization` — re-digitize on defect (≤ 3).
- `extract-spec ⇄ audit-spec` — the **paper-fix**: resolve from ground truth
  (code → lineage → human), then independently verify (≤ 2). Still divergent at the
  cap → **BLOCKED**.
- `author-tests ⇄ audit-tests` — re-author until the tests are paper-grounded (not
  tautologies).
- `implement → audit-faithfulness → author-tests → audit-tests → implement` — the
  verify loop (≤ 3 rounds); `audit-faithfulness` is **comprehensive — everything vs
  the paper**. If the final audit round still has actionable findings, the workflow
  records them and exits without applying an unaudited final-round mutation.

Every finalized exit — `DONE`, `PARTIAL`, `BLOCKED`, or an error — funnels through the
stale-artifact sweep → modification smoke test → coverage gate → `update-state`
(README + a "👉 DECISION NEEDED" human entrypoint when blocked/flagged) → `commit +
push + PR`, without exception.
