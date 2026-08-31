#!/usr/bin/env node
// Adapter: build a --reveals map for stamp.mjs from a frozen soundwave prediction snapshot
// (~/.claude/soundwave-discover/predictions/<batch>.json).
//
// The snapshot stores the model's top-5 "up" picks + the whole field (all_ids), committed at
// digest time (generated_at, before the blind grade). Per-item binary = "did the model top-pick
// it", which is exactly the rung-2 signal rank-watch already scores:
//   pick + up   = agreement (model rightly picked it)
//   pick + down = deviation  (model over-valued it)
//   field + down= agreement (model rightly skipped it)
//   field + up  = deviation  (model missed one you valued) <- an agency gap
//
// Usage: node soundwave-reveals.mjs 2026-07-11 > reveals.json
//        node stamp.mjs --batch 2026-07-11 --reveals reveals.json --out ...

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const batch = process.argv[2];
if (!batch) { console.error('usage: soundwave-reveals.mjs <batch-YYYY-MM-DD>'); process.exit(1); }

const snap = path.join(os.homedir(), '.claude', 'soundwave-discover', 'predictions', `${batch}.json`);
if (!fs.existsSync(snap)) {
  console.error(`[reveals] no prediction snapshot: ${snap}`);
  console.error('[reveals] the rank step in soundwave_discover.py did not emit for this batch.');
  process.exit(2);
}
const rec = JSON.parse(fs.readFileSync(snap, 'utf8'));
const ts = rec.generated_at;
const out = {};
(rec.picks || []).forEach((p, i) => { out[p.id] = { picked: true, rank: i + 1, pUp: p.pUp, ts }; });
for (const id of rec.all_ids || []) if (!out[id]) out[id] = { picked: false, ts };

process.stdout.write(JSON.stringify(out, null, 2) + '\n');
console.error(`[reveals] batch ${batch}: ${Object.keys(out).length} items (${(rec.picks || []).length} picks), generated_at ${ts}`);
