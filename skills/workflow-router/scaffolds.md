# workflow-router scaffolds

Six parameterized `Workflow()` script templates, one per pattern. In Step 5 of SKILL.md,
copy the chosen template and replace every `{{PLACEHOLDER}}` with the recon'd target, the
task inputs, and the wizard answers. Each is a valid Workflow script: a pure-literal `meta`
block, `phase()` groups, `pipeline()`/`parallel()`, JSON schemas for structured returns, and
`.filter(Boolean)` before using fan-out results.

Common placeholders: `{{TARGET}}` (folder/file/path), `{{OUTPUT}}` (where the deliverable
lands), `{{TOPIC}}` (subject), `{{CRITERIA}}` (rubric text). Pattern-specific ones are noted
per template.

---

## 1. Classify-and-Act

Placeholders: `{{TARGET}}` (the queue dir), `{{HANDLERS}}` (comma list, e.g. `bug, refund,
lead, spam`), `{{TRACKED}}` (path/source of already-handled items for dedup).

```js
export const meta = {
  name: 'classify-and-act',
  description: 'Triage {{TARGET}}: classify each item, dedup against tracked, route to a handler',
  phases: [
    { title: 'Classify' },
    { title: 'Route' },
  ],
}

const ITEM_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    label: { type: 'string', enum: ['{{HANDLERS_AS_ENUM}}'] },
    confidence: { type: 'number' },
    dedupKey: { type: 'string', description: 'stable key to detect duplicates' },
    summary: { type: 'string' },
  },
  required: ['id', 'label', 'dedupKey'],
}

// 1) Read + classify every item in the queue.
const items = await agent(
  `Read every item under {{TARGET}}. For each, classify it into exactly one of: {{HANDLERS}}. ` +
  `Return one object per item with a stable dedupKey (e.g. normalized subject+sender).`,
  { label: 'classify-all', phase: 'Classify', schema: { type: 'object', properties: { items: { type: 'array', items: ITEM_SCHEMA } }, required: ['items'] } },
)

// 2) Dedup against what is already tracked (barrier: needs the whole set + the tracker).
const seen = new Set()  // seed from {{TRACKED}} inside the agent below if it must be read live
const deduped = []
for (const it of items.items) {
  if (seen.has(it.dedupKey)) continue
  seen.add(it.dedupKey)
  deduped.push(it)
}
log(`${deduped.length} unique of ${items.items.length} items after dedup`)

// 3) Route each unique item to its handler, in parallel.
const handled = await parallel(deduped.map(it => () =>
  agent(
    `Handle this {{TARGET}} item as a "${it.label}" case. Item: ${it.summary}. ` +
    `Take the appropriate handler action and return what you did. Dedup source: {{TRACKED}}.`,
    { label: `handle:${it.label}`, phase: 'Route' },
  ).then(text => ({ id: it.id, label: it.label, action: text })),
))

return { routed: handled.filter(Boolean) }
```

---

## 2. Fan-out-and-Synthesize

Placeholders: `{{TARGET}}` (the corpus root), `{{PARTS}}` (how parts are split, usually
subfolders), `{{OUTPUT}}` (memo path), `{{DELIVERABLE}}` (e.g. "due diligence memo").

```js
export const meta = {
  name: 'fan-out-synthesize',
  description: 'Summarize each part of {{TARGET}} in a clean context, then merge into one cited {{DELIVERABLE}}',
  phases: [
    { title: 'Fan-out' },
    { title: 'Synthesize' },
  ],
}

const PART_SUMMARY = {
  type: 'object',
  properties: {
    part: { type: 'string', description: 'which part/folder this came from' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          sourcePath: { type: 'string', description: 'exact file path backing this finding' },
        },
        required: ['claim', 'sourcePath'],
      },
    },
  },
  required: ['part', 'findings'],
}

// Replace this list with the real parts discovered in recon (one entry per {{PARTS}}).
const PARTS = [/* '{{TARGET}}/folderA', '{{TARGET}}/folderB', ... */]

// 1) One agent per part, each in its OWN clean context so files never cross-contaminate.
const summaries = await parallel(PARTS.map(p => () =>
  agent(
    `You see only the files under ${p}. Produce a structured summary of the material facts. ` +
    `Every finding MUST include the exact source file path it came from. Do not reference anything outside ${p}.`,
    { label: `part:${p}`, phase: 'Fan-out', schema: PART_SUMMARY },
  ),
))

// 2) Barrier synthesize: wait for ALL, merge into one cited deliverable.
const clean = summaries.filter(Boolean)
const memo = await agent(
  `Merge these per-part summaries into one {{DELIVERABLE}}. Every claim in the memo MUST link back ` +
  `to the file path it came from. Flag any conflicts between parts. Summaries: ${JSON.stringify(clean)}`,
  { label: 'synthesize', phase: 'Synthesize' },
)

return { output: '{{OUTPUT}}', memo, parts: clean.length }
```

---

## 3. Adversarial-Verification

Placeholders: `{{TARGET}}` (the artifact/draft), `{{N}}` (skeptics per claim, default 3),
`{{SOURCE_HINT}}` (where to check claims, e.g. "the web" or a docs path).

```js
export const meta = {
  name: 'adversarial-verification',
  description: 'Extract each claim in {{TARGET}} and refute it independently; return what failed',
  phases: [
    { title: 'Extract' },
    { title: 'Verify' },
  ],
}

const CLAIMS = {
  type: 'object',
  properties: {
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: { id: { type: 'string' }, text: { type: 'string' } },
        required: ['id', 'text'],
      },
    },
  },
  required: ['claims'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

// 1) Extract each factual/technical claim into its own item.
const extracted = await agent(
  `Read {{TARGET}}. Extract every distinct factual or technical claim as its own item.`,
  { label: 'extract-claims', phase: 'Extract', schema: CLAIMS },
)

// 2) For each claim, spin {{N}} independent skeptics that try to REFUTE it. Majority refute => fail.
const results = await pipeline(
  extracted.claims,
  claim => parallel(Array.from({ length: {{N}} }, (_, i) => () =>
    agent(
      `Try to REFUTE this claim against {{SOURCE_HINT}}: "${claim.text}". ` +
      `Default to refuted=true if you cannot confirm it. Be a skeptic, not a believer.`,
      { label: `verify:${claim.id}#${i}`, phase: 'Verify', schema: VERDICT },
    ),
  )).then(votes => {
    const v = votes.filter(Boolean)
    const refutes = v.filter(x => x.refuted)
    return { claim, failed: refutes.length > v.length / 2, reasons: refutes.map(x => x.reason) }
  }),
)

return { failedClaims: results.filter(Boolean).filter(r => r.failed) }
```

---

## 4. Generate-and-Filter

Placeholders: `{{TOPIC}}`, `{{N}}` (how many to generate, e.g. 40), `{{KIND}}` (e.g. "video
titles and headline angles"), `{{CRITERIA}}` (scoring rubric). Generator and judge are
distinct agents by construction.

```js
export const meta = {
  name: 'generate-and-filter',
  description: 'Over-generate {{N}} {{KIND}} for {{TOPIC}}, then a different judge scores and filters',
  phases: [
    { title: 'Generate' },
    { title: 'Judge' },
  ],
}

const OPTIONS = {
  type: 'object',
  properties: { options: { type: 'array', items: { type: 'string' } } },
  required: ['options'],
}

const SCORE = {
  type: 'object',
  properties: {
    option: { type: 'string' },
    score: { type: 'number' },
    rationale: { type: 'string' },
  },
  required: ['option', 'score'],
}

// 1) Generator over-produces. This agent only generates; it never judges.
const gen = await agent(
  `Brainstorm {{N}} distinct {{KIND}} for: {{TOPIC}}. Maximize variety of angle. Return the raw list.`,
  { label: 'generator', phase: 'Generate', schema: OPTIONS },
)

// 2) A DIFFERENT judge scores every option against the criteria. Separation prevents self-preference.
const scored = await parallel(gen.options.map(opt => () =>
  agent(
    `Score this option against the criteria, 0-10, with a one-line rationale. ` +
    `Criteria: {{CRITERIA}}. Option: "${opt}". You are a judge, not the author.`,
    { label: 'judge', phase: 'Judge', schema: SCORE },
  ),
))

const ranked = scored.filter(Boolean).sort((a, b) => b.score - a.score)
return { top: ranked.slice(0, 10), all: ranked }
```

---

## 5. Tournament

Placeholders: `{{TARGET}}` (candidate pool path), `{{ROLE}}` (what they compete for, e.g.
"back-end engineer"), `{{CRITERIA}}` (rubric for head-to-head).

```js
export const meta = {
  name: 'tournament',
  description: 'Rank the {{TARGET}} candidates for {{ROLE}} via pairwise comparison brackets',
  phases: [
    { title: 'Load' },
    { title: 'Bracket' },
  ],
}

const POOL = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: { type: 'object', properties: { id: { type: 'string' }, summary: { type: 'string' } }, required: ['id', 'summary'] },
    },
  },
  required: ['candidates'],
}

const MATCH = {
  type: 'object',
  properties: {
    winnerId: { type: 'string' },
    reason: { type: 'string' },
  },
  required: ['winnerId'],
}

// 1) Load the candidate pool.
const pool = await agent(
  `Read every candidate under {{TARGET}}. Return one entry per candidate with an id and a short summary.`,
  { label: 'load-pool', phase: 'Load', schema: POOL },
)

// 2) Deterministic single-elimination bracket. Each match is its own comparison agent.
let round = pool.candidates
let r = 0
while (round.length > 1) {
  r++
  const pairs = []
  for (let i = 0; i < round.length; i += 2) pairs.push([round[i], round[i + 1]])
  const winners = await parallel(pairs.map((pair, idx) => () => {
    if (!pair[1]) return Promise.resolve(pair[0])          // odd one out gets a bye
    return agent(
      `Head-to-head for the {{ROLE}} role, judged ONLY on: {{CRITERIA}}. ` +
      `A: ${JSON.stringify(pair[0])}  B: ${JSON.stringify(pair[1])}. Pick the stronger; return its id.`,
      { label: `match:r${r}#${idx}`, phase: 'Bracket', schema: MATCH },
    ).then(m => round.find(c => c.id === m?.winnerId) || pair[0])
  }))
  round = winners.filter(Boolean)
}

return { winner: round[0], rounds: r }
```

---

## 6. Loop-Until-Done

Placeholders: `{{TARGET}}` (e.g. the test dir), `{{CONDITION}}` (the done-state, e.g.
"reproduced and root-caused the flaky test"), `{{MAX}}` (kill cap, e.g. 8).

```js
export const meta = {
  name: 'loop-until-done',
  description: 'Form and test theories about {{TARGET}} until {{CONDITION}}, in isolated worktrees',
  phases: [{ title: 'Hunt' }],
}

const THEORY = {
  type: 'object',
  properties: {
    theory: { type: 'string' },
    tested: { type: 'boolean' },
    confirmed: { type: 'boolean', description: 'true only when {{CONDITION}} is met' },
    evidence: { type: 'string' },
  },
  required: ['theory', 'confirmed'],
}

const tried = []
let attempt = 0
let done = null

while (!done && attempt < {{MAX}}) {
  attempt++
  const r = await agent(
    `Hunt {{TARGET}}. Done condition: {{CONDITION}}. ` +
    `Already-ruled-out theories: ${JSON.stringify(tried)}. ` +
    `Form ONE new theory, test it in an isolated worktree, and report whether the condition is now met.`,
    { label: `attempt-${attempt}`, phase: 'Hunt', schema: THEORY, isolation: 'worktree' },
  )
  if (!r) continue
  tried.push(r.theory)
  if (r.confirmed) done = r
  log(`attempt ${attempt}/{{MAX}}: ${r.confirmed ? 'CONFIRMED' : 'ruled out'} — ${r.theory}`)
}

return done
  ? { status: 'done', attempts: attempt, result: done }
  : { status: 'exhausted', attempts: attempt, ruledOut: tried }
```
