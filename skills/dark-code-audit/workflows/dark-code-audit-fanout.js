export const meta = {
  name: 'dark-code-audit-fanout',
  description: 'Fan-out of /dark-code-audit: one worker per module scores the four darkness dimensions (authorship, decision-trail, behavioral-contracts, dependency-awareness) in a clean context, a 3-vote adversarial panel verifies each DARK-tier module before it lands on the TODO list, and a barrier synthesis builds the heat map + drill-down TODO. Read-only; produces a report, never edits code.',
  phases: [
    { title: 'Score' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

// Same Fan-out-and-Synthesize + grafted multi-vote Adversarial-Verify spine as
// model-audit-fanout.js. Unit of fan-out here is a MODULE, not a provider.
// args = {
//   repo: string,                                  // repo path (label + where workers read)
//   threshold: number,                             // DARK tier cutoff (default 80)
//   votes: number,                                 // skeptics per DARK module (default 3)
//   modules: [ { path, loc, lang }, ... ]          // module inventory (Phase 2 discovery output)
// }
// The harness may deliver `args` as a JSON string; parse it so the script is delivery-agnostic.
let A = args
if (typeof A === 'string') {
  try {
    A = JSON.parse(A)
  } catch (e) {
    A = {}
  }
}
A = A || {}
const repo = A.repo || '(unspecified repo)'
const threshold = A.threshold || 80
const votes = A.votes || 3
const modules = A.modules || []
// Fail LOUD on an empty fan-out rather than synthesizing a clean-looking report over 0 modules
// (same silent-no-op class as the model-audit args-string bug).
if (modules.length === 0) {
  log(
    `RED: 0 modules to score (repo=${repo}). Check that args.modules is a non-empty inventory ` +
      `from a Phase-2 module-discovery pass and not an empty/mis-shaped payload. Aborting.`,
  )
  return {
    status: 'error',
    error: 'empty-fanout',
    repo,
    reason: 'No modules supplied; nothing to score. Not a clean repo — a missing/mis-shaped args.modules.',
  }
}
log(`dark-code fan-out on ${repo} | ${modules.length} modules | DARK>=${threshold} | votes=${votes}`)

const DIM = { type: 'number', minimum: 0, maximum: 100 }
const MODULE_SCORE_SCHEMA = {
  type: 'object',
  properties: {
    path: { type: 'string' },
    loc: { type: 'number' },
    authorship: DIM,
    decision_trail: DIM,
    behavioral_contracts: DIM,
    dependency_awareness: DIM,
    darkness_score: DIM,
    tier: { type: 'string', enum: ['DARK', 'DIM', 'UNDERSTOOD'] },
    why: { type: 'string', description: 'the specific gaps that drove the score' },
    actions: {
      type: 'array',
      items: { type: 'string' },
      description: 'highest-impact darkness-reducing actions, most impactful first',
    },
  },
  required: ['path', 'darkness_score', 'tier', 'why'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    suggestedScore: { type: 'number', description: 'the score the skeptic would assign' },
  },
  required: ['refuted', 'reason'],
}

// Phase Score: one worker per module, clean context each. Four dimensions, 25% weight each,
// 0-100 where 100 = maximum darkness. Worker measures via git log, ADR/CLAUDE.md search,
// tests, and import graph exactly as the /dark-code-audit skill specifies.
const scored = await parallel(
  modules.map((m) => () =>
    agent(
      `You are a /dark-code-audit module-worker. Score ONE module for "dark code" (code that works but that no human ` +
        `ever built a mental model of). Module: ${m.path} in repo ${repo} (${m.loc || '?'} LOC, ${m.lang || 'unknown'}).\n\n` +
        `Score four dimensions 0-100 (100 = maximum darkness / worst), 25% weight each:\n` +
        `1. Authorship signal: git log author diversity + commit-message quality + AI-generation markers + PR/review trail. ` +
        `Measure with: git -C ${repo} log --format='%an' -- ${m.path} | sort | uniq -c; git -C ${repo} log --oneline -- ${m.path}; grep for generation markers.\n` +
        `2. Decision trail: ADRs, CLAUDE.md/README rationale, why-not-what commit messages, inline comments on non-obvious choices.\n` +
        `3. Behavioral contracts: tests (behavioral vs mock-heavy), type annotations + docstrings on public interfaces, schema/contract validation.\n` +
        `4. Dependency awareness: referenced in arch docs, import-graph visibility, CODEOWNERS, bottleneck-but-undocumented.\n\n` +
        `darkness_score = mean of the four (each clamped 0-100). tier: DARK 80-100 | DIM 50-79 | UNDERSTOOD 0-49. ` +
        `In "why", cite the specific gaps. In "actions", give the highest-impact darkness-reducing steps, most impactful first, ` +
        `each specific to THIS module (not generic advice). Read-only: never edit code.`,
      { label: `score:${m.path}`, phase: 'Score', schema: MODULE_SCORE_SCHEMA },
    ),
  ),
)

const allScores = scored.filter(Boolean)
const dark = allScores.filter((m) => m.darkness_score >= threshold)
const notDark = allScores.filter((m) => m.darkness_score < threshold)
log(`score: ${allScores.length} modules, ${dark.length} DARK (>=${threshold}) go to the verify panel`)

// Phase Verify: before a module lands on the DARK TODO list, N skeptics try to REFUTE the
// DARK rating (maybe there ARE tests / an ADR / a clear owner the scorer missed). Majority
// refute demotes it out of the DARK TODO. Prevents a false DARK from generating make-work.
const verified = await parallel(
  dark.map((m) => () =>
    parallel(
      Array.from({ length: votes }, (_unused, i) => () =>
        agent(
          `Adversarially verify a /dark-code-audit DARK rating for module ${m.path} in ${repo} ` +
            `(scored ${m.darkness_score}/100; why: ${m.why}). Try to REFUTE the DARK rating: actually go look for tests, ` +
            `ADRs/design docs, CLAUDE.md rules, type annotations/docstrings, CODEOWNERS, or arch-doc references the scorer ` +
            `may have MISSED. Use git -C ${repo} log and grep against the real files. ` +
            `Set refuted=true if you find enough comprehension evidence that this module is not truly DARK; false if the DARK rating holds.`,
          { label: `verify:${m.path}#${i}`, phase: 'Verify', schema: VERDICT_SCHEMA },
        ),
      ),
    ).then((raw) => {
      const v = raw.filter(Boolean)
      const refutes = v.filter((x) => x.refuted).length
      return {
        ...m,
        confirmedDark: refutes <= v.length / 2,
        refutes,
        votes: v.length,
        refuteReasons: v.filter((x) => x.refuted).map((x) => x.reason),
      }
    }),
  ),
)

const confirmedDark = verified.filter(Boolean).filter((m) => m.confirmedDark)
const demoted = verified.filter(Boolean).filter((m) => !m.confirmedDark)
log(`verify: ${confirmedDark.length} DARK confirmed, ${demoted.length} demoted by the panel`)

// Phase Synthesize: barrier over all scores -> heat map + drill-down TODO + honest routing.
const report = await agent(
  `Synthesize a /dark-code-audit report for ${repo}. Build (a) the summary heat map: module count and % of LOC per ` +
    `tier (DARK/DIM/UNDERSTOOD), an aggregate darkness score weighted by LOC, and the module score table ` +
    `(Module | Darkness | Authorship | Decision Trail | Contracts | Dependencies | LOC) sorted by darkness desc; ` +
    `(b) a drill-down TODO section for each CONFIRMED-DARK module (why it's dark + highest-impact actions + effort); ` +
    `(c) a Phase-4.5 routing line per confirmed-DARK module (Fix now | File as bounded work via goal-maker with ` +
    `owner/sink/kill | Escalate to gemini-rescue/codex | Accept-no-action, said explicitly). ` +
    `If NOTHING is confirmed DARK, do not end on a green heat map: route the top few highest-scoring modules with ` +
    `honest verdicts anyway. Also list modules the verify panel DEMOTED out of DARK, with the reason, so the reader ` +
    `sees what was challenged. Confirmed DARK: ${JSON.stringify(confirmedDark)}. Demoted by panel: ${JSON.stringify(demoted)}. ` +
    `Below threshold: ${JSON.stringify(notDark)}. Read-only: recommend, never change code.`,
  { label: 'synthesize', phase: 'Synthesize' },
)

return {
  repo,
  threshold,
  moduleCount: allScores.length,
  confirmedDark,
  demoted,
  belowThreshold: notDark.length,
  report,
}
