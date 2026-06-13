export const meta = {
  name: 'full-pass',
  description: 'A pass over a paper. from="extract" (default): full fresh pass extract → digitization gate → implement → verify → report. from="build": the contract is already extracted + approved FAITHFUL but Phase B is UNBUILT or PARTIAL (e.g. an earlier extract pass exited BLOCKED at the spec gate before implementation) → skip Phase A, do a FULL Phase-B implement against the existing contract → verify → report. from="fix" (built+audited model): skip Phase A + digitization, enter at the test-writer using the existing audit → fix → re-audit → report. EVERY exit finalizes IN THE MODEL\'S OWN REPO (never the parent): README human-entrypoint + commit + a PR onto the submodule\'s main, without exception.',
  phases: [
    { title: 'Acquire' },
    { title: 'Extract' },
    { title: 'Digitization gate' },
    { title: 'Implement' },
    { title: 'Verify' },
    { title: 'Report' },
  ],
}

// args: { model: 'models/<name>', figures: ['2',...], from?: 'extract' | 'build' | 'fix' }
// Robust to args arriving as either a parsed object or a JSON-encoded string.
const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
const MODEL = A.model
const FIGURES = A.figures || []
// 'extract' = fresh full pass | 'build' = full Phase-B implement on an already-FAITHFUL contract
// (Phase A done/approved, Phase B unbuilt or partial) | 'fix' = built+audited: repair recent change
const FROM = A.from || 'extract'
const MAX_ROUNDS = 3
const MAX_PAPERFIX = 2 // paper-fix ↔ implement iterations per contract fault before honest BLOCKED
const ROOT = '/Users/estevaouyra/dev/model_agent'
// The project venv is the ONLY complete interpreter: it has matplotlib (figure
// rendering + the render-dependent panel-axes tests) plus neuromodels/scipy/numpy.
// The bare `python`/`pytest` on PATH is the system Homebrew interpreter, which LACKS
// matplotlib — running tests/rendering there fails with ModuleNotFoundError and blocks
// figure passes on stale renders. Every agent MUST use this absolute interpreter path.
const PY = `${ROOT}/.venv/bin/python`
// Every skill-based agent works INSIDE its model repo. Skills use model-relative paths
// (logs/, article_aware/, implementation/, figure_outputs/); the agent runs from the parent,
// so without this it writes/commits into the PARENT (model_agent) — the bug that polluted
// model_agent/logs/. This pins every agent to the submodule and forbids parent commits.
const SK = (name) =>
  `Read and FOLLOW ${ROOT}/skills/${name}/SKILL.md. Work ONLY inside the model repo ${ROOT}/${MODEL} ` +
  `(cd into it first): EVERY skill path (logs/, article_aware/, implementation/, figure_outputs/) is ` +
  `relative to ${ROOT}/${MODEL}, and you COMMIT your output INSIDE ${ROOT}/${MODEL}, NEVER in the parent ` +
  `model_agent repo at ${ROOT} (reading other models is fine; committing there is forbidden). ` +
  `Use ${PY} for ALL Python — tests and figure rendering: \`${PY} -m pytest ...\`, ` +
  `\`PYTHONPATH=implementation/src ${PY} -m <model_pkg>.views\`. The bare \`python\`/\`pytest\` on PATH is ` +
  `the system Homebrew interpreter and LACKS matplotlib, so rendering/render-dependent tests FAIL there.`

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
    `point 2 — ADOPT THE ON-DISK GROUND TRUTH, do not punt: a finding whose resolution TRACES TO ` +
    `ALREADY-ACQUIRED ground truth (paper / paper/code / SI / lineage on disk) is CODE-RESOLVABLE — ` +
    `APPLY it (rung 1/2). "Needs a human" is reserved for a GENUINELY FREE or PAPER-CONTRADICTORY ` +
    `choice the acquired sources truly do not settle (rung 3). Most "routed to human" findings are a ` +
    `MAX_PAPERFIX cap artifact: R&H's contract divergences, denison's allocation law, the DR-4C sign ` +
    `were all settled by the on-disk author code and dissolved under one adversarial audit. Open the ` +
    `acquired code/paper and adopt what it says before declaring anything human-only.\n` +
    `Correct article_aware/ ONLY; tag code-alone honestly; NEVER tune a per-figure knob to fit a ` +
    `model-level fault. A CONTRACT_BUG you cannot resolve via (1)/(2) → leave an OPEN SQ ` +
    `(owner+expiry), BLOCKED. A PAPER_ISSUE you cannot resolve via (1)/(2) → DISPOSITION it as a ` +
    `documented paper defect (red tripwire + human decision-request with owner+expiry); that is a ` +
    `FAITHFUL contract state, not a block. Commit. Findings: ${JSON.stringify(findings)}`,
    { label: `paperfix-resolve ${label}`, phase: phaseName, model: OPUS })
  return await agent(
    `${SK('audit-spec')} Independently audit the CORRECTED ${MODEL} contract vs the paper + ground ` +
    `truth (paper/code + related-paper lineage). You did NOT author it; adversarial. Tag each finding ` +
    `scope=model|figure AND code-resolvable|genuinely-human: code-resolvable = the answer is in the ` +
    `acquired paper/code/lineage on disk (the resolver must APPLY it, NOT punt); genuinely-human = a ` +
    `free/paper-contradictory choice the sources truly do not settle. Do NOT call a code-settled ` +
    `question human; "routed to human" is usually a cap artifact. Findings just applied: ${JSON.stringify(findings)}`,
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
// (0) stale-artifact sweep; (1) rewrite the README as the current state + a human entrypoint;
// (2) commit + push + PR. Idempotent (runs once). The README and the PR are the human's entrypoint.
const finalize = async () => {
  if (finalized) return
  finalized = true
  phase('Report')
  // (0) STALE-ARTIFACT SWEEP (point 3): after a model is fixed, the artifacts documenting the OLD
  //     broken state go stale and must be cleaned (recurred in ~every model). (a) RE-RENDER figures
  //     from the current model (the venv has matplotlib — R&H shipped stale renders → false verdicts);
  //     (b) CONVERT RESOLVED TRIPWIRES — an xfail(strict) that now XPASSes because the model was fixed
  //     becomes a must-pass (or an honest relabel), NEVER left to flip the suite RED (R&H 21 xpasses;
  //     ghose leftover xfail decorators that would've reddened main; denison co-finding tripwires);
  //     (c) GREP docstrings/README/spec prose for PRE-FIX NUMBERS that contradict the now-binding
  //     contract and refresh them (olshausen stale docstring). Skip cleanly if nothing changed.
  await agent(
    `${SK('run-tests')} Stale-artifact sweep for ${MODEL} before the README/commit. (a) RE-RENDER every ` +
    `figure from the CURRENT model with ${PY} (never trust a committed snapshot). (b) Find every ` +
    `xfail(strict) that now XPASSes because the model was fixed and CONVERT it to a must-pass (or an ` +
    `honest relabel) — an XPASS-strict left in place flips the suite RED; never leave one. (c) Grep ` +
    `docstrings / README / spec prose for PRE-FIX numbers that contradict the now-binding contract and ` +
    `refresh them. Commit the sweep. If nothing is stale, say so and make no change.`,
    { label: 'stale-artifact sweep', phase: 'Report', model: OPUS })
  // (1) README — ALWAYS the per-figure reproduction state + changelog; and when this exit needs
  //     a decision (paper-fix/audit block, or flagged dispositions) a clear entrypoint on top.
  await agent(
    `${SK('update-state')} Rewrite the ${MODEL} README as CURRENT STATE and the human entrypoint. ` +
    `ALWAYS include, in order: (1) a current-exit block at the very top — exit=${JSON.stringify(exit)}; ` +
    (humanEntrypoint
      ? `(1a) if this exit is BLOCKED on an obtainable-by-human gated source (a login/paywall/` +
        `CRCNS-registration rescue artifact — released fits / learned basis/covariances / ` +
        `figure-generating data per paper/SOURCES.md), LEAD at the very TOP with a clear "👉 UNBLOCKER" ` +
        `banner naming EXACTLY what to fetch and where it goes (e.g. "drop the CRCNS MGSM toolbox in ` +
        `paper/code/ and re-run" — cagly2012); the human's single highest-leverage action must be ` +
        `impossible to miss, above the per-figure state; ` +
        `(1b) directly under it, a clearly-marked "👉 DECISION NEEDED" section — what is blocked/flagged ` +
        `and WHY (${humanEntrypoint.kind}: ${humanEntrypoint.reason}), the specific open findings, and ` +
        `exactly where to look (logs/spec_audit/, logs/faithfulness_audit/, the SQ in logs/spec_questions.md); `
      : ``) +
    `(2) the model description; (3) per figure the three views side by side (paper · digitized · ` +
    `implemented) + the audit/check tables — the figure-reproduction state; (4) a "potential sources" ` +
    `section from the findings' source_hints; (5) a changelog — append ONE succinct line, full detail to ` +
    `logs/changelog.md; (6) a "Reproduction cost" section AS THE FINAL section — run ` +
    `\`${PY} ${ROOT}/tools/repro_cost.py ${MODEL} --markdown\` (it scans THIS model's full-pass agent ` +
    `transcripts across ALL runs and prices them at standard Opus 4.8 API rates) and paste its stdout ` +
    `VERBATIM, replacing any existing "## Reproduction cost" section (idempotent — do not stack copies). ` +
    `If the command prints nothing (no recoverable transcripts), omit the section entirely. ` +
    `Findings: ${JSON.stringify(openFindings)}. Process: ${JSON.stringify(proc ?? {})}.`,
    { label: 'state-update', phase: 'Report', model: OPUS })
  // (2) Land the result IN THE MODEL'S OWN REPO (the submodule) — commit + a PR onto the
  //     submodule's main, every exit (blocked included). NEVER touch the parent (model_agent):
  //     parent submodule-pointer bumps are a separate, deliberate step, not part of a run
  //     (AGENTS.md: "commit only inside the model repo, never the parent").
  await agent(
    `Finalize ${MODEL} and LAND THE RESULT IN ITS OWN REPO — leave NOTHING uncommitted (runs on EVERY exit). ` +
    `Work ONLY inside the submodule ${ROOT}/${MODEL}. DO NOT commit, branch, push, or open a PR in the PARENT ` +
    `(model_agent) repo at ${ROOT} — that is forbidden; parent submodule-pointer bumps are a separate ` +
    `deliberate step, never part of a reproduction run. In the submodule: stage and commit ALL remaining ` +
    `changes on the current feature branch (one honest commit matching the diff; the README — the human ` +
    `entrypoint, with a "DECISION NEEDED" section if blocked — is part of it). Push the feature branch. Then ` +
    `LAND IT ON THE SUBMODULE'S OWN main via a PR IN THE SUBMODULE REPO (cwd = the submodule so gh targets ` +
    `it): gh pr create --base main --head <feature-branch> (title = the exit "${exit.overall}", body = the ` +
    `README entrypoint summary), then gh pr merge --merge --delete-branch (server-side → lands on the ` +
    `submodule's main, blocked included). If the submodule has no remote, commit locally and report. If the ` +
    `merge cannot complete cleanly, leave the PR open and report why — do NOT force, and do NOT fall back to ` +
    `the parent. Report the submodule PR URL and whether the submodule's main was updated.`,
    { label: 'finalize: land in submodule (its own repo)', phase: 'Report', model: OPUS })
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
    // ACQUIRABILITY PRE-FLIGHT (point 6): acquire-sources runs Step 0 first — confirm the PAPER
    // FULL TEXT is genuinely fetchable (open-access / PMC / on-disk). If it is NOT, it returns
    // PAPER_UNFETCHABLE and we BLOCK EARLY with a clear "supply the PDF to paper/" message — never
    // run extract/implement on missing data (several models had no PDF on disk; fail fast & clear).
    const acq = await agent(
      `${SK('acquire-sources')} Acquire all upstream sources for ${MODEL}. FIRST do the Step-0 ` +
      `acquirability pre-flight: confirm the PAPER FULL TEXT is genuinely fetchable (open-access / PMC / ` +
      `already on disk). If it is NOT (hard paywall, no free full text, no PDF supplied), STOP and return ` +
      `{paper_fetchable:false} — do not proceed to partial sources. Otherwise acquire published materials ` +
      `(main, Online Methods, Supplementary) into paper/, original author code into paper/code/ ` +
      `(Phase-A spec source, Phase-B forbidden, gitignored), and write paper/SOURCES.md accounting for ` +
      `every artifact (obtained / exists-but-not-obtained / confirmed-absent). When a gated/login/paywalled ` +
      `item is the LIKELY RESCUE ARTIFACT (released fits / learned basis / figure-generating data), record ` +
      `it PROMINENTLY (exact URL + access method + what it unblocks). Seed code_refs.yaml if code found. ` +
      `Return {paper_fetchable: true|false, reason}.`,
      { label: 'acquire-sources', phase: 'Acquire', model: OPUS,
        schema: { type: 'object', additionalProperties: false,
          properties: { paper_fetchable: { type: 'boolean' }, reason: { type: 'string' } },
          required: ['paper_fetchable'] } })
    // point 6: paper unfetchable → BLOCK EARLY with a clear message; never extract/implement on missing data.
    if (acq && acq.paper_fetchable === false) {
      return blockedExit(`paper not fetchable — supply the PDF to ${MODEL}/paper/ and re-run`, [
        { scope: 'model', detail: `Paper full text is not fetchable (${acq.reason || 'no free full text / no PDF on disk'}). ` +
          `A from=extract pass needs the real paper. Drop the PDF in paper/ and re-run.`, fix: 'supply paper/paper.pdf' }])
    }

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
          // null = the audit agent died on a TRANSIENT API error (e.g. a server-side rate-limit when
          // many passes run at once). Never throw on verdict.status — synthesize a non-faithful
          // verdict and stop retrying this fig. The gate only FLAGS (it never blocks the gate), and a
          // resume re-runs just this fig cheaply.
          if (!verdict) { verdict = { status: 'BLOCKED', worst_defect: 'digitization audit failed transiently (API rate-limit) — resume to retry' }; break }
          if (verdict.status === 'FAITHFUL' || verdict.status === 'BLOCKED') break
        }
        return { fig, status: verdict?.status ?? 'BLOCKED', defect: verdict?.worst_defect ?? 'digitization failed transiently — resume to retry' }
      })

    await specDone
    figResults = figResults.filter(Boolean) // a pipeline stage that threw outright drops to null — never let it crash the gate
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
  } else if (FROM === 'build') {
    // from='build' — the contract is already extracted, audited FAITHFUL, and approved (Phase A
    // complete), but Phase B is UNBUILT or PARTIAL: typically an earlier from=extract pass that
    // exited BLOCKED at the spec gate (so implementation never ran), or a build where only some
    // figures got implemented. Skip Phase A entirely and do a FULL Phase-B implement against the
    // existing contract, then fall through to the SAME verify loop + finalize as extract. This is
    // the reusable entrypoint for "contract is right, now build the whole model" — distinct from
    // from=fix, which only repairs the MOST-RECENT change and assumes a complete prior build.
    log(`from='build': skipping Phase A (contract assumed faithful/approved) — full Phase-B implement against the existing contract.`)
    phase('Implement')
    await agent(
      `${SK('implement')} Build ${MODEL} COMPLETELY from the existing (faithful, approved) contract — the full forward model + protocols + measurements for EVERY figure the contract defines, PLUS the renderer/views (so every figure renders to figure_outputs/). Iterate locally against the FULL test suite until green or genuinely stuck; render the figures. Do NOT re-author the contract — Phase A is done; if you hit a genuine contract-level gap, escalate via logs/spec_questions.md rather than papering it with an implementation-side knob.`,
      { label: 'implement (full Phase-B)', phase: 'Implement', model: IMPL })
  } else {
    log(`from='fix': skipping extract + digitization gate + initial implement — reusing the existing contract, binding references, and audit.`)
  }

  // ════════════════ VERIFY ── ⑥∥⑦, route+fix, loop-until-dry capped at MAX_ROUNDS ════════════════
  // from='fix' enters HERE at the test-writer: round 1 encodes the EXISTING audit and fixes,
  // without an initial ⑥ (we trust the on-disk audit as current); round 2+ re-audits normally.
  // from='build' (and 'extract') skip that round-1 test-writer branch and go straight to the
  // audit below — the implementation was just (fully) built, so round 1 audits it like normal.
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
    // A null faithfulness audit = the auditor died on a TRANSIENT API error (rate-limit). NEVER let
    // that fall through as a clean/dry round (that would false-green); bail honestly to a blocked
    // exit so a resume retries it. (proc is read null-safely below, so only faith must be guarded.)
    if (!faith) return blockedExit('faithfulness audit failed transiently (API rate-limit) — resume to retry', [])
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
