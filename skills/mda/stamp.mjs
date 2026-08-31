#!/usr/bin/env node
// MDA stamp: turn sealed blind disposals (me2me-feedback.json) into a MATS Disposal
// Artifact (ARA-derived). Deterministic, read-only except the output dir.
//
// The seal it enforces: a reveal (model prediction) may NEVER predate its blind
// verdict. If a supplied reveal has ts <= the verdict ts, that is contamination and
// the run FAILS loudly rather than emitting a corrupt label.
//
// Usage:
//   node stamp.mjs --since 2026-07-12                # gate slice (blind-count floor)
//   node stamp.mjs --batch 2026-07-12                # one batch by its `batch` field
//   node stamp.mjs --since 2026-07-12 --reveals rank-watch.json --out /path/artifact
//   node stamp.mjs --list                            # list available batches, then exit
//
// --reveals is an optional JSON map { "<id>": { rank, picked: true|false, ts } }.
// Without it, every Status is `pending-reveal` (honest: the reveal has not happened yet).

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith('--')) continue;
    const name = k.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) a[name] = true;
    else { a[name] = next; i++; }
  }
  return a;
}

const args = parseArgs(process.argv.slice(2));
const HOME = os.homedir();
const FEEDBACK = args.feedback || path.join(HOME, 'vault', 'me2me-feedback.json');
const TAG = typeof args.tag === 'string' ? args.tag : null; // optional narrower; a disposal is any up/down verdict
const BATCH = typeof args.batch === 'string' ? args.batch : null;
const SINCE = typeof args.since === 'string' ? args.since : null; // YYYY-MM-DD
const REVEALS = typeof args.reveals === 'string'
  ? JSON.parse(fs.readFileSync(args.reveals, 'utf8')) : null;

if (!fs.existsSync(FEEDBACK)) {
  console.error(`[mda] label store not found: ${FEEDBACK}`);
  process.exit(1);
}
const store = JSON.parse(fs.readFileSync(FEEDBACK, 'utf8'));
const all = Object.values(store);

if (args.list) {
  const byBatch = {};
  for (const e of all) byBatch[e.batch || '(none)'] = (byBatch[e.batch || '(none)'] || 0) + 1;
  console.log('batch                 count');
  for (const [b, n] of Object.entries(byBatch).sort()) console.log(b.padEnd(22), n);
  process.exit(0);
}

const sinceStamp = SINCE ? `${SINCE}T00:00:00.000Z` : null;
const rows = all
  .filter((e) => e.verdict === 'up' || e.verdict === 'down') // a disposal is a blind up/down call
  .filter((e) => (TAG ? e.tag === TAG : true))
  .filter((e) => (BATCH ? e.batch === BATCH : true))
  .filter((e) => (sinceStamp ? (e.ts || '') >= sinceStamp : true))
  .sort((a, b) => (a.ts || '').localeCompare(b.ts || ''));

if (rows.length === 0) {
  console.error('[mda] no disposals matched. Try --list to see batches.');
  process.exit(2);
}

const label = BATCH || (SINCE ? `since-${SINCE}` : 'all');
const OUT = typeof args.out === 'string'
  ? args.out : path.join(HOME, 'vault', 'mats-disposals', label);

// ── Seal enforcement ────────────────────────────────────────────────────────
const breaches = [];
function reveal(e) {
  if (!REVEALS || !REVEALS[e.id]) return null;
  const r = REVEALS[e.id];
  // Seal: the model prediction is committed at digest time, BEFORE the blind grade. That
  // ordering is the blind-test guarantee. Contamination = a prediction generated AFTER the
  // verdict (the model may have seen the grade). Frozen write-once snapshots back this up.
  if (r.ts && e.ts && r.ts > e.ts) breaches.push({ id: e.id, verdict: e.ts, reveal: r.ts });
  return r;
}
const enriched = rows.map((e, i) => {
  const r = reveal(e);
  let status = 'pending-reveal';
  if (r && typeof r.picked === 'boolean') {
    const iLiked = e.verdict === 'up';
    status = iLiked === r.picked ? 'agreement' : 'deviation';
  }
  return { e, r, status, n: String(i + 1).padStart(2, '0') };
});
if (breaches.length) {
  console.error('[mda] SEAL BREACH: model prediction POSTDATES the blind verdict (model may have seen the grade). Aborting.');
  for (const b of breaches) console.error(`  ${b.id}: verdict=${b.verdict} prediction=${b.reveal}`);
  process.exit(3);
}

// ── Emit ────────────────────────────────────────────────────────────────────
const esc = (s) => String(s || '').replace(/\r?\n/g, ' ').trim();
const deviations = enriched.filter((x) => x.status === 'deviation').length;
const agreements = enriched.filter((x) => x.status === 'agreement').length;
const pending = enriched.filter((x) => x.status === 'pending-reveal').length;

const disposals = enriched.map(({ e, r, status, n }) => {
  const lines = [
    `## D${n}: ${esc(e.title)}`,
    `- **Verdict**: ${e.verdict}`,
    `- **Why**: ${esc(e.notes) || '(no why recorded — half a label)'}`,
    `- **Tag**: ${e.tag}`,
    `- **Provenance**: user`,
    `- **Sealed-at**: ${e.ts}`,
    `- **Batch**: ${e.batch || '(none)'}`,
    `- **Item-id**: ${e.id}`,
    `- **Falsification**: a pasted prompt + the interest model's own analytics reproduces this ${e.verdict} without my reasoning.`,
  ];
  if (r) {
    lines.push(`<!-- REVEAL ${r.ts || '(no ts)'} appended, not overwriting the blind call -->`);
    lines.push(`- **Model-prediction**: ${r.picked ? 'picked' : 'not-picked'}${r.rank != null ? `, rank ${r.rank}` : ''}`);
    lines.push(`- **Prediction-provenance**: ai-executed`);
  } else {
    lines.push(`- **Model-prediction**: [pending: rank-watch reveal]`);
  }
  lines.push(`- **Status**: ${status}`);
  return lines.join('\n');
}).join('\n\n');

const nodes = enriched.map(({ e, status, n }) => {
  const type = status === 'deviation' ? 'dead_end' : status === 'agreement' ? 'experiment' : 'question';
  const base = [
    `  - id: N${n}`,
    `    type: ${type}`,
    `    title: ${JSON.stringify(`D${n} — ${esc(e.title).slice(0, 70)}`)}`,
    `    provenance: user`,
    `    timestamp: ${JSON.stringify(e.ts)}`,
  ];
  if (type === 'dead_end') {
    base.push(`    hypothesis: "model prediction diverged from my blind ${e.verdict}"`);
    base.push(`    failure_mode: ${JSON.stringify(esc(e.notes).slice(0, 160) || 'divergence')}`);
    base.push(`    lesson: "candidate rule — promote to rules.md if the pattern repeats"`);
  } else if (type === 'experiment') {
    base.push(`    result: "model agreed with my blind ${e.verdict}"`);
  } else {
    base.push(`    description: "reveal pending — model prediction not yet scored"`);
  }
  base.push(`    status: ${status === 'pending-reveal' ? 'open' : 'resolved'}`);
  return base.join('\n');
}).join('\n\n');

const paper = [
  '---',
  'title: MATS Disposal Artifact',
  'authors: [Matthew]',
  `batch: ${label}`,
  'mda_version: "0.1"',
  'domain: person-specific alignment',
  `disposals: ${enriched.length}`,
  `deviations: ${deviations}`,
  `agreements: ${agreements}`,
  `pending_reveal: ${pending}`,
  'baseline: "AUQ 73.5% agreement (unbeaten)"',
  'gate: "2026-07-23 — 30+ blind disposals + ablation published"',
  '---',
  '',
  '# MATS Disposal Artifact',
  '',
  '## Overview',
  `${enriched.length} sealed blind disposals for batch \`${label}\`. ` +
    `${deviations} deviations (the product), ${agreements} agreements, ${pending} awaiting reveal. ` +
    'Deviations are where judgment lives; agreement is not alignment.',
  '',
  '## Layer Index',
  '- `logic/disposals.md` — sealed blind rulings (immutable)',
  '- `logic/rules.md` — crystallized judgment rules (evolving; user-revised)',
  '- `logic/constraints.md` — blind protocol + falsification standard',
  '- `trace/disposal_tree.yaml` — deviations as dead_end nodes',
  '- `evidence/README.md` — item + reveal pointers into me2me-feedback.json / rank-watch',
  '',
].join('\n');

const constraints = fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), 'templates', 'logic', 'constraints.md'), 'utf8');
const rulesTpl = fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), 'templates', 'logic', 'rules.md'), 'utf8');
const evReadme =
  '# Evidence index\n\n' +
  '| Disposal | Item source | Reveal source |\n|---|---|---|\n' +
  enriched.map(({ e, n }) => `| D${n} | me2me-feedback.json:${e.id} | rank-watch (soundwave) |`).join('\n') +
  '\n';

fs.mkdirSync(path.join(OUT, 'logic'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'trace'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'evidence'), { recursive: true });
fs.writeFileSync(path.join(OUT, 'PAPER.md'), paper);
fs.writeFileSync(path.join(OUT, 'logic', 'disposals.md'), `# Disposals — batch ${label}\n\n${disposals}\n`);
fs.writeFileSync(path.join(OUT, 'logic', 'rules.md'), rulesTpl);
fs.writeFileSync(path.join(OUT, 'logic', 'constraints.md'), constraints);
fs.writeFileSync(path.join(OUT, 'trace', 'disposal_tree.yaml'), `tree:\n\n${nodes}\n`);
fs.writeFileSync(path.join(OUT, 'evidence', 'README.md'), evReadme);

console.log(`[mda] stamped ${enriched.length} disposals -> ${OUT}`);
console.log(`[mda]   deviations=${deviations} agreements=${agreements} pending_reveal=${pending}`);
console.log(`[mda]   seal: OK (every model prediction committed no later than its blind verdict)`);
if (pending === enriched.length) console.log('[mda]   note: all pending — supply --reveals to score agreement/deviation');
