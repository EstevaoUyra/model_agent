export const meta = {
  name: 'full-pass',
  description: 'A pass over a paper. from="extract" (default): full fresh pass extract → digitization gate → implement → verify → report. from="fix" (built+audited model): skip Phase A + digitization, enter at the test-writer using the existing audit → fix → re-audit → report.',
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

let figResults = []
let digBlocked = []

// ════════════════ PHASE A + initial implement — only on a FRESH pass ════════════════
if (FROM === 'extract') {
  // ⓪ acquire-sources — Phase 0, BLOCKS Phase A: gather all paper materials +
  // original code into paper/ and write paper/SOURCES.md, so the extractor never
  // builds the spec on incomplete sources (the hermann2010 missing-SI failure).
  phase('Acquire')
  await agent(
    `${SK('acquire-sources')} Acquire all upstream sources for ${MODEL}: published materials ` +
    `(main, Online Methods, Supplementary) into paper/, original author code into paper/code/ ` +
    `(Phase-A spec source, Phase-B forbidden), and write paper/SOURCES.md accounting for every ` +
    `artifact (obtained / exists-but-not-obtained / confirmed-absent). Seed code_refs.yaml if code was found.`,
    { label: 'acquire-sources', phase: 'Acquire', model: OPUS })

  // ① spec-extractor — runs concurrently with the figure pipeline; joined before ⑤
  phase('Extract')
  const specDone = agent(
    `${SK('extract-spec')} Extract the article-aware contract for ${MODEL} (equations, parameters with evidenced/lineage-grounded assumptions, calibration ledger, citations, spec-questions).`,
    { label: 'spec-extract', phase: 'Extract', model: OPUS })

  // ②→③↔④ per figure, concurrent across figures (the 3↔4 loop lives inside each lane)
  figResults = await pipeline(FIGURES,
    (fig) => agent(
      `${SK('extract-figure')} Describe figure ${fig} of ${MODEL}: panels, axis limits, model-panels-only scope. If the paper image is missing, return BLOCKED.`,
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
  digBlocked = figResults.filter((r) => r.status !== 'FAITHFUL') // flagged, surfaced; does not gate ⑤
  log(`Digitization gate: ${figResults.filter(r => r.status === 'FAITHFUL').length}/${FIGURES.length} faithful; ${digBlocked.length} flagged`)

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
let faith, proc
const flagged = []
for (let round = 1; round <= MAX_ROUNDS; round++) {
  if (FROM === 'fix' && round === 1) {
    await agent(
      `${SK('author-tests')} Read the LATEST existing ${MODEL} faithfulness audit (logs/faithfulness_audit/ + the README current-state) and encode its OPEN findings as deterministic tests (BUG → must-pass; GENUINE_DIVERGENCE/PAPER_ISSUE → red tripwire). Do NOT re-audit; the on-disk audit is your input.`,
      { label: 'test-author r1 (existing audit)', phase: 'Verify', model: OPUS })
    await agent(
      `${SK('implement')} Apply the existing ${MODEL} audit's open findings, iterating locally against the full suite (incl. the new audit-derived tests) until green or stuck. Escalate any contract-level issue via logs/spec_questions.md.`,
      { label: 'phaseB-fix r1', phase: 'Verify', model: IMPL })
    continue // round 2+ runs a FRESH ⑥/⑦ re-audit (the builder never self-certifies)
  }

  ;[faith, proc] = await parallel([
    () => agent(
      `${SK('audit-faithfulness')} Re-render and audit the CURRENT ${MODEL} implementation vs the paper + the digitized references. Tag each divergence CONTRACT_BUG | CODE_BUG | GENUINE_DIVERGENCE | PAPER_ISSUE (a paper-issue only after the lineage ladder). You are NOT the builder. Give a fix (spec-level) for every *_BUG and a source_hint for every divergence.`,
      { label: `faith-audit r${round}`, phase: 'Verify', model: OPUS, schema: FAITH_VERDICT }),
    () => agent(
      `${SK('audit-process')} Read the ${MODEL} change-trail this pass: is the trajectory toward-paper or toward-green? You are paper-blind.`,
      { label: `proc-audit r${round}`, phase: 'Verify', model: OPUS, schema: PROC_VERDICT }),
  ])
  flagged.push(...faith.findings.filter((f) => f.tag === 'GENUINE_DIVERGENCE' || f.tag === 'PAPER_ISSUE'))
  const contractBugs = faith.findings.filter((f) => f.tag === 'CONTRACT_BUG')
  const codeBugs = faith.findings.filter((f) => f.tag === 'CODE_BUG')
  if (contractBugs.length === 0 && codeBugs.length === 0) break // dry

  await agent(
    `${SK('author-tests')} Encode these ${MODEL} audit findings as deterministic tests (BUG → must-pass; GENUINE_DIVERGENCE/PAPER_ISSUE → red tripwire). Findings: ${JSON.stringify(faith.findings)}`,
    { label: `test-author r${round}`, phase: 'Verify', model: OPUS })

  if (contractBugs.length) {
    await agent(
      `Phase-A contract editor for ${MODEL}. Apply these CONTRACT findings to article_aware/ ONLY (spec, pseudocode, tests, citations, assumptions, the view), then state the Phase-B build order. GUARD: specify the paper's mechanism; never tune to fit. COMMIT your changes when done (an atomic commit whose message matches the diff) — do not leave the contract edits uncommitted. Findings: ${JSON.stringify(contractBugs)}`,
      { label: `phaseA-fix r${round}`, phase: 'Verify', model: OPUS })
  }
  await agent(
    `${SK('implement')} Apply the updated contract + these code findings to ${MODEL}, iterating locally against the full suite (including the new audit-derived tests) until green or stuck. Code findings: ${JSON.stringify(codeBugs)}`,
    { label: `phaseB-fix r${round}`, phase: 'Verify', model: IMPL })
}

// ════════════════ REPORT — ⑨ state-updater (README = current state) ════════════════
phase('Report')
const exit = { overall: faith?.overall ?? 'unknown', trajectory: proc?.trajectory ?? 'unknown', flagged_count: flagged.length, blocked: digBlocked.map(b => b.fig) }
await agent(
  `${SK('update-state')} Rewrite the ${MODEL} README as the CURRENT STATE. Order: (1) a current-exit block AT THE TOP (before the model description) — exit=${JSON.stringify(exit)} and the queued human-decisions; (2) model description; (3) per figure the three views side by side (paper · digitized · implemented) + the audit/check tables; (4) a "potential sources of the issues" section built from the findings' source_hints; (5) a changelog — append ONE succinct line here, full detail to logs/changelog.md. Findings: ${JSON.stringify(faith?.findings ?? [])}. Process: ${JSON.stringify(proc ?? {})}.`,
  { label: 'state-update', phase: 'Report', model: OPUS })

return { from: FROM, exit, flagged, blocked: digBlocked, process: proc }
