export const meta = {
  name: 'full-pass',
  description: 'A pass over a paper. from="extract" (default): full fresh pass extract → digitization gate → implement → verify → report. from="fix" (built+audited model): skip Phase A + digitization, enter at the test-writer using the existing audit → fix → re-audit → report. EVERY exit finalizes: README human-entrypoint + commit + push + PR, without exception.',
  phases: [
    { title: 'Acquire' },
    { title: 'Extract' },
    { title: 'Digitization gate' },
    { title: 'Implement' },
    { title: 'Verify' },
    { title: 'Report' },
  ],
}

// args: { model: 'models/<name>', figures: ['2',...], from?: 'extract' | 'fix' }
// Robust to args arriving as either a parsed object or a JSON-encoded string.
const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
const MODEL = A.model
const FIGURES = A.figures || []
const FROM = A.from || 'extract' // 'extract' = fresh full pass | 'fix' = built+audited: enter at the test-writer
const MAX_ROUNDS = 3
const MAX_PAPERFIX = 2 // paper-fix ↔ implement iterations per contract fault before honest BLOCKED
const SK = (name) => `Read and FOLLOW /Users/estevaouyra/dev/model_agent/skills/${name}/SKILL.md.`
const ROOT = '/Users/estevaouyra/dev/model_agent'

// Model policy: the implementer needs the 1M window (it holds the whole codebase + suite
// while iterating); every other role runs plain opus. Pin BOTH as EXPLICIT model IDs —
// the tier enum ('opus') only sets the tier and the agent then INHERITS this session's 1M
// window, so every agent ends up on opus[1m]. Full IDs are the only lever that strips 1M.
const OPUS = 'claude-opus-4-8'     // non-implementer roles: opus, NO 1M
const IMPL = 'claude-opus-4-8[1m]' // implementer only: opus + 1M

// ── structured verdicts that drive the routing (so the script branches on data, not prose) ──
const DIG_VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    status: { enum: ['FAITHFUL', 'DIVERGENT', 'TOOL_MISUSE', 'BLOCKED'] },
    worst_defect: { type: 'string' },          // what the next re-digitize must fix
  },
  required: ['status', 'worst_defect'],
}
const FAITH_VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    overall: { enum: ['faithful', 'partial', 'blocked'] },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          figure: { type: 'string' },
          tag: { enum: ['CONTRACT_BUG', 'CODE_BUG', 'GENUINE_DIVERGENCE', 'PAPER_ISSUE', 'FAITHFUL'] },
          scope: { enum: ['model', 'figure'] }, // model-fault blocks ALL figures; figure-fault blocks one
          detail: { type: 'string' },
          fix: { type: 'string' },             // spec-level fix (for the *_BUG tags)
          source_hint: { type: 'string' },     // "potential source", for the README
        },
        required: ['figure', 'tag', 'detail'],
      },
    },
  },
  required: ['overall', 'findings'],
}
const PROC_VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    trajectory: { enum: ['toward_paper', 'drifting', 'mixed'] },
    concerns: { type: 'array', items: { type: 'string' } },
  },
  required: ['trajectory'],
}
// audit-spec verdict — drives the Phase-A gate and the paper-fix verify step.
const SPEC_VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    status: { enum: ['FAITHFUL', 'DIVERGENT', 'BLOCKED'] },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          scope: { enum: ['model', 'figure'] }, // model-fault blocks ALL figures; figure-fault blocks one
          detail: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['scope', 'detail'],
      },
    },
  },
  required: ['status', 'findings'],
}

// audit-tests verdict — are the authored tests themselves paper-grounded?
const TESTS_VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    status: { enum: ['FAITHFUL', 'DIVERGENT'] },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          test: { type: 'string' },
          issue: { type: 'string' }, // tautology / unsourced threshold / wrong referent / too loose
          fix: { type: 'string' },
        },
        required: ['test', 'issue'],
      },
    },
  },
  required: ['status', 'findings'],
}

// ── shared run state — read by finalize() on EVERY exit path ──
let figResults = []
let digBlocked = []
let faith = null
let proc = null
const flagged = []
let exit = { overall: 'unknown', trajectory: 'unknown', flagged_count: 0, blocked: [] }
let openFindings = []
let humanEntrypoint = null // { kind, reason, findings } — set when the exit needs a human
let finalized = false

// paper-fix subroutine: resolve a CONTRACT/PAPER fault via a RESOLUTION LADDER from
// already-acquired ground truth, then INDEPENDENTLY verify with audit-spec (builder ≠
// resolver ≠ auditor). Caller bounds retries with MAX_PAPERFIX; returns the spec verdict.
const paperFix = async (findings, label, phaseName) => {
  await agent(
    `${SK('extract-spec')} Phase-A RESOLVER for ${MODEL}. Resolve each finding via this LADDER, in ` +
    `order, stopping at the first that resolves it — do NOT re-acquire (use what is on disk; re-fetch ` +
    `only an item listed in paper/SOURCES.md "exists-but-not-obtained"):\n` +
    `  (1) this paper's own code/supplement (paper/code + SOURCES.md) → author CODE-NNN;\n` +
    `  (2) RELATED genealogy papers via lineage → author LINEAGE-NNN pointing at the ancestor's entry;\n` +
    `  (3) a HUMAN decision — LAST RESORT ONLY.\n` +
    `Correct article_aware/ ONLY; tag code-alone honestly; NEVER tune a per-figure knob to fit a ` +
    `model-level fault. A CONTRACT_BUG you cannot resolve via (1)/(2) → leave an OPEN SQ ` +
    `(owner+expiry), BLOCKED. A PAPER_ISSUE you cannot resolve via (1)/(2) → DISPOSITION it as a ` +
    `documented paper defect (red tripwire + human decision-request with owner+expiry); that is a ` +
    `FAITHFUL contract state, not a block. Commit. Findings: ${JSON.stringify(findings)}`,
    { label: `paperfix-resolve ${label}`, phase: phaseName, model: OPUS })
  return await agent(
    `${SK('audit-spec')} Independently audit the CORRECTED ${MODEL} contract vs the paper + ground ` +
    `truth (paper/code + related-paper lineage). You did NOT author it; adversarial. Tag each finding ` +
    `scope=model|figure. Findings just applied: ${JSON.stringify(findings)}`,
    { label: `audit-spec ${label}`, phase: phaseName, model: OPUS, schema: SPEC_VERDICT })
}

// author tests for a change, then INDEPENDENTLY audit (audit-tests) that those tests faithfully
// REPRESENT THE PAPER/REFERENCES — not tautologies, unsourced thresholds, or the implementation's
// own output. Re-ground flagged tests (capped). This is SPECIFIC to the just-authored tests; it is
// NOT the comprehensive implementation audit (that runs after implement, on everything).
const authorTests = async (authorPrompt, label) => {
  await agent(authorPrompt, { label: `test-author ${label}`, phase: 'Verify', model: OPUS })
  for (let i = 1; i <= MAX_PAPERFIX; i++) {
    const tv = await agent(
      `${SK('audit-tests')} Independently audit the tests just added/changed this pass for ${MODEL}. ` +
      `Judge whether EACH faithfully represents something from the paper + references (digitized ` +
      `figures, paper/code, lineage) — not a tautology, not the implementation's own output, not an ` +
      `unsourced threshold, not too loose to discriminate. The motivating audit is CONTEXT ONLY; you ` +
      `judge the TESTS. You did NOT author them; adversarial.`,
      { label: `audit-tests ${label} r${i}`, phase: 'Verify', model: OPUS, schema: TESTS_VERDICT })
    if (tv.status === 'FAITHFUL') return tv
    await agent(
      `${SK('author-tests')} Re-ground these ${MODEL} tests that audit-tests found do NOT represent the ` +
      `paper/references — fix each referent/threshold/assertion so it traces to a real paper or ` +
      `reference quantity (cite it: C-/CODE-/LINEAGE-NNN or a digitized panel point). Findings: ${JSON.stringify(tv.findings)}`,
      { label: `test-reground ${label} r${i}`, phase: 'Verify', model: OPUS })
  }
  log(`audit-tests: ${label} tests still not fully paper-grounded after ${MAX_PAPERFIX} re-grounds — proceeding, flagged`)
  return { status: 'DIVERGENT', findings: [] }
}

// finalize — runs on EVERY exit (normal, blocked, or thrown) via the try/finally below.
// (1) rewrite the README as the current state + a human entrypoint; (2) commit + push + PR.
// Idempotent (runs once). The README and the PR are the human's entrypoint into the run.
const finalize = async () => {
  if (finalized) return
  finalized = true
  phase('Report')
  // (1) README — ALWAYS the per-figure reproduction state + changelog; and when this exit needs
  //     a decision (paper-fix/audit block, or flagged dispositions) a clear entrypoint on top.
  await agent(
    `${SK('update-state')} Rewrite the ${MODEL} README as CURRENT STATE and the human entrypoint. ` +
    `ALWAYS include, in order: (1) a current-exit block at the very top — exit=${JSON.stringify(exit)}; ` +
    (humanEntrypoint
      ? `(1b) directly under it, a clearly-marked "👉 DECISION NEEDED" section — what is blocked/flagged ` +
        `and WHY (${humanEntrypoint.kind}: ${humanEntrypoint.reason}), the specific open findings, and ` +
        `exactly where to look (logs/spec_audit/, logs/faithfulness_audit/, the SQ in logs/spec_questions.md); `
      : ``) +
    `(2) the model description; (3) per figure the three views side by side (paper · digitized · ` +
    `implemented) + the audit/check tables — the figure-reproduction state; (4) a "potential sources" ` +
    `section from the findings' source_hints; (5) a changelog — append ONE succinct line, full detail to ` +
    `logs/changelog.md. Findings: ${JSON.stringify(openFindings)}. Process: ${JSON.stringify(proc ?? {})}.`,
    { label: 'state-update', phase: 'Report', model: OPUS })
  // (2) Commit + push + PR — WITHOUT EXCEPTION, every exit. The PR IS the human entrypoint.
  await agent(
    `Finalize ${MODEL} for human review — leave NOTHING uncommitted (this runs on EVERY exit). ` +
    `In the model repo (${ROOT}/${MODEL}): stage and commit ALL remaining changes on the current branch ` +
    `(one honest commit whose message matches the diff), then push the branch if it has a remote. Then in ` +
    `the PARENT repo (${ROOT}): on a branch, bump ONLY the ${MODEL} submodule pointer (git add ${MODEL}; do ` +
    `NOT stage unrelated parent changes), commit, push, and open OR update a PR (use gh; if one already ` +
    `exists for the branch, update it). PR title summarizes the exit ("${exit.overall}"); PR body = the ` +
    `README's DECISION-NEEDED / state summary so the PR is the human entrypoint. Report the PR URL.`,
    { label: 'finalize: commit+push+PR', phase: 'Report', model: OPUS })
}

// Phase-A audit failed within the cap → the WHOLE workflow EXITS, BLOCKED (point 2). Sets the
// shared blocked state + human entrypoint; the try/finally runs finalize (README + commit + PR).
const blockedExit = (reason, findings) => {
  log(`WORKFLOW EXIT — Phase-A contract BLOCKED: ${reason}`)
  exit = { overall: 'blocked', trajectory: proc?.trajectory ?? 'n/a', flagged_count: flagged.length, blocked: ['model:contract'] }
  openFindings = findings
  humanEntrypoint = { kind: 'contract-blocked (paper-fix/audit-spec)', reason, findings }
  return { from: FROM, exit, blocked: ['model:contract'], spec: findings }
}

try {
  // ════════════════ PHASE A + initial implement — only on a FRESH pass ════════════════
  if (FROM === 'extract') {
    // ⓪ acquire-sources — Phase 0, BLOCKS Phase A: gather all paper materials + original code
    // into paper/ and write paper/SOURCES.md, so the extractor never builds on incomplete sources.
    phase('Acquire')
    await agent(
      `${SK('acquire-sources')} Acquire all upstream sources for ${MODEL}: published materials ` +
      `(main, Online Methods, Supplementary) into paper/, original author code into paper/code/ ` +
      `(Phase-A spec source, Phase-B forbidden, gitignored), and write paper/SOURCES.md accounting for ` +
      `every artifact (obtained / exists-but-not-obtained / confirmed-absent). Seed code_refs.yaml if code found.`,
      { label: 'acquire-sources', phase: 'Acquire', model: OPUS })

    // ① spec-extractor — runs concurrently with the figure pipeline; joined before the gate
    phase('Extract')
    const specDone = agent(
      `${SK('extract-spec')} Extract the article-aware contract for ${MODEL} (equations, parameters with evidenced/lineage-grounded assumptions, calibration ledger, citations, spec-questions).`,
      { label: 'spec-extract', phase: 'Extract', model: OPUS })

    // ②→③↔④ per figure, concurrent across figures (the 3↔4 loop lives inside each lane)
    figResults = await pipeline(FIGURES,
      (fig) => agent(
        `${SK('extract-figure')} Describe figure ${fig} of ${MODEL}: panels, axis limits, model-panels-only scope. A panel that is a RENDERED MODEL OUTPUT is a reproduction target even inside a schematic. If the paper image is missing, return BLOCKED.`,
        { label: `fig-extract:${fig}`, phase: 'Extract', model: OPUS }),
      async (_extracted, fig) => {
        let verdict = null
        for (let round = 1; round <= MAX_ROUNDS; round++) {
          const fixNote = verdict ? `Fix the prior audit defect: ${verdict.worst_defect}` : 'First digitization.'
          await agent(
            `${SK('digitize-figure')} Digitize figure ${fig} of ${MODEL} (all panels). ${fixNote}`,
            { label: `digitize:${fig} r${round}`, phase: 'Digitization gate', model: OPUS })
          verdict = await agent(
            `${SK('audit-digitization')} Audit the digitization of figure ${fig} of ${MODEL} against the paper (adversarial overlay + crop_region). You are NOT the digitizer.`,
            { label: `dig-audit:${fig} r${round}`, phase: 'Digitization gate', model: OPUS, schema: DIG_VERDICT })
          if (verdict.status === 'FAITHFUL' || verdict.status === 'BLOCKED') break
        }
        return { fig, status: verdict.status, defect: verdict.worst_defect }
      })

    await specDone
    digBlocked = figResults.filter((r) => r.status !== 'FAITHFUL') // flagged, surfaced; does not gate the gate
    log(`Digitization gate: ${figResults.filter(r => r.status === 'FAITHFUL').length}/${FIGURES.length} faithful; ${digBlocked.length} flagged`)

    // audit-spec GATE — the CONTRACT itself is audited before any implementation (the safeguard
    // that was missing). A divergence is resolved via paper-fix (≤MAX_PAPERFIX) BEFORE Phase B, so
    // the implementer never builds against a known-wrong contract and can't paper a bug with a knob.
    let specGate = await agent(
      `${SK('audit-spec')} Audit the freshly-extracted ${MODEL} contract vs the paper + acquired ground truth (paper/code). Adversarial; you did NOT author it. Tag each finding scope=model|figure.`,
      { label: 'audit-spec (gate)', phase: 'Extract', model: OPUS, schema: SPEC_VERDICT })
    for (let i = 1; i <= MAX_PAPERFIX && specGate.status !== 'FAITHFUL'; i++) {
      specGate = await paperFix(specGate.findings, `gate r${i}`, 'Extract')
    }
    // point 2: if the contract can't be made faithful within the cap, EXIT — never implement
    // against a known-wrong contract. (finalize still runs via finally.)
    if (specGate.status !== 'FAITHFUL') return blockedExit('Phase-A spec gate did not pass within MAX_PAPERFIX', specGate.findings)

    // BARRIER ── PHASE B implement (paper-blind, opus[1m])
    phase('Implement')
    await agent(
      `${SK('implement')} Build ${MODEL} from the contract — model + protocols + measurements — iterating locally against the test suite until green or stuck; render the figures.`,
      { label: 'implement', phase: 'Implement', model: IMPL })
  } else {
    log(`from='${FROM}': skipping extract + digitization gate + initial implement — reusing the existing contract, binding references, and audit.`)
  }

  // ════════════════ VERIFY ── ⑥∥⑦, route+fix, loop-until-dry capped at MAX_ROUNDS ════════════════
  // from='fix' enters HERE at the test-writer: round 1 encodes the EXISTING audit and fixes,
  // without an initial ⑥ (we trust the on-disk audit as current); round 2+ re-audits normally.
  phase('Verify')
  let paperFixIters = 0
  for (let round = 1; round <= MAX_ROUNDS; round++) {
    if (FROM === 'fix' && round === 1) {
      // TEST-FIRST, sourced from the MOST RECENT change (NOT a stale audit). If a paper-fix
      // just corrected the contract, encode WHAT THAT CHANGE REQUIRES — the freshly-resolved
      // SQ's must-pass targets + the corrected mechanism's expected behaviour. Then implement
      // to pass them. Round 2 audits the freshly-built implementation.
      await authorTests(
        `${SK('author-tests')} Encode as deterministic tests the requirements of the MOST RECENT change to ${MODEL}. If the contract was just corrected by a paper-fix (recent commits / a freshly-RESOLVED SQ in logs/spec_questions.md carrying a must-pass target), encode THAT — the corrected mechanism's expected behaviour and its new must-pass targets (BUG → must-pass; disposition → red tripwire). Fall back to the latest faithfulness audit's OPEN findings ONLY if there is no recent contract change. Do NOT re-encode stale or already-passing audits.`,
        'r1 (recent change)')
      await agent(
        `${SK('implement')} Build/repair ${MODEL} to PASS the just-authored tests and match the current contract — DELETE any implementation-side knobs the contract no longer sanctions. Iterate locally against the full suite until green or stuck. Escalate any genuine contract-level gap via logs/spec_questions.md.`,
        { label: 'phaseB-fix r1', phase: 'Verify', model: IMPL })
      continue
    }

    ;[faith, proc] = await parallel([
      () => agent(
        `${SK('audit-faithfulness')} Re-render and audit the CURRENT ${MODEL} implementation vs the paper + the digitized references. Tag each divergence CONTRACT_BUG | CODE_BUG | GENUINE_DIVERGENCE | PAPER_ISSUE (a paper-issue only after the lineage ladder), and scope=model|figure (a forward-model/mechanism fault blocks ALL figures; a per-figure issue blocks one). You are NOT the builder. Give a fix (spec-level) for every *_BUG and a source_hint for every divergence.`,
        { label: `faith-audit r${round}`, phase: 'Verify', model: OPUS, schema: FAITH_VERDICT }),
      () => agent(
        `${SK('audit-process')} Read the ${MODEL} change-trail this pass: is the trajectory toward-paper or toward-green? You are paper-blind.`,
        { label: `proc-audit r${round}`, phase: 'Verify', model: OPUS, schema: PROC_VERDICT }),
    ])
    flagged.push(...faith.findings.filter((f) => f.tag === 'GENUINE_DIVERGENCE'))
    // CONTRACT_BUG and PAPER_ISSUE are both SPEC faults → the paper-fix ladder (point 1:
    // PAPER_ISSUE is resolvable from related papers; human is last resort).
    const specFaults = faith.findings.filter((f) => f.tag === 'CONTRACT_BUG' || f.tag === 'PAPER_ISSUE')
    const codeBugs = faith.findings.filter((f) => f.tag === 'CODE_BUG')
    if (specFaults.length === 0 && codeBugs.length === 0) break // dry & contract-clean

    await authorTests(
      `${SK('author-tests')} Encode these ${MODEL} audit findings as deterministic tests (BUG → must-pass; GENUINE_DIVERGENCE/PAPER_ISSUE → red tripwire). Findings: ${JSON.stringify(faith.findings)}`,
      `r${round}`)

    // PRIORITY (point 3): an open SPEC fault / SQ BLOCKS implementation — we NEVER implement
    // against an open SQ. Resolve the contract first via the paper-fix ladder, re-audit, and
    // only build CODE bugs once the contract is clean.
    if (specFaults.length) {
      paperFixIters++
      const sv = await paperFix(specFaults, `r${round}`, 'Verify')
      if (sv.status !== 'FAITHFUL') {
        // audit-spec (the ARBITER, not the figure-auditor's tag) confirms the contract is
        // GENUINELY still faulted → never implement against an open SQ; re-audit, or BLOCK at cap.
        if (paperFixIters >= MAX_PAPERFIX) return blockedExit('paper-fix verify did not pass within MAX_PAPERFIX', sv.findings)
        continue
      }
      // audit-spec says the contract is now FAITHFUL → NO open SQ. A figure that still diverges is
      // an IMPLEMENTATION issue (the figure-auditor's CONTRACT_BUG tag was a hypothesis audit-spec
      // just refuted) → fall through and IMPLEMENT; do NOT spin re-auditing an un-fixed build.
    }

    // contract is clean (no open SQ) → build the implementation to match it + fix CODE bugs
    await agent(
      `${SK('implement')} Build ${MODEL} to match the current contract and apply these CODE findings, iterating locally against the full suite (including the audit-derived tests) until green or stuck. Code findings: ${JSON.stringify(codeBugs)}`,
      { label: `phaseB-fix r${round}`, phase: 'Verify', model: IMPL })
  }

  // ── normal completion — set the shared exit state for finalize() ──
  exit = { overall: faith?.overall ?? 'unknown', trajectory: proc?.trajectory ?? 'unknown', flagged_count: flagged.length, blocked: digBlocked.map(b => b.fig) }
  openFindings = faith?.findings ?? []
  if (flagged.length) humanEntrypoint = { kind: 'review', reason: `${flagged.length} flagged disposition(s) to confirm`, findings: flagged }
} finally {
  // README human-entrypoint + commit + push + PR — on EVERY exit, without exception.
  await finalize()
}

return { from: FROM, exit, flagged, blocked: exit.blocked, process: proc }
