---
name: mda
description: >
  Stamp a MATS Disposal Artifact (MDA) from the blind-disposal label store. An MDA is an
  ARA-derived (Agent-Native Research Artifact) directory that wraps me2me-feedback.json
  losslessly: sealed blind rulings (immutable), crystallized judgment rules (evolving),
  and a disposal tree where deviations are dead_end nodes. Use when Matthew says "/mda",
  "stamp a disposal artifact", "make an MDA", "wrap this batch of blind grades", "package
  the disposals for the gate", or wants the me2me blind-disposal labels in an auditable,
  reviewable ARA shape (for the 2026-07-23 MATS gate, or to feed the same rigor reviewer
  that grades AutoResearch runs). Deterministic stamp; the seal (no model prediction
  postdates its blind verdict) is enforced by the tool, not by trust.
---

# MDA — MATS Disposal Artifact

Turns the live blind-disposal label store (`~/vault/me2me-feedback.json`) into an
ARA-shaped, auditable artifact. Same substrate MATS and AutoResearch share: provenance
keeps `user` judgment separable from `ai-executed` prediction, deviations are preserved as
the product, and the two-tier ARA Seal can later grade it (the L2 semantic review = the
MATS orthogonal judge / Rung B).

## How to run

The stamp is deterministic. From this skill's directory:

```bash
node ~/.claude/skills/mda/stamp.mjs --list                 # what batches exist
node ~/.claude/skills/mda/stamp.mjs --since 2026-07-12      # the gate slice (blind-count floor)
node ~/.claude/skills/mda/stamp.mjs --batch 2026-07-12      # one batch by its `batch` field
# score one batch against the model's frozen predictions:
node ~/.claude/skills/mda/soundwave-reveals.mjs 2026-07-11 > /tmp/reveals.json
node ~/.claude/skills/mda/stamp.mjs --batch 2026-07-11 \
     --reveals /tmp/reveals.json --out ~/vault/mats-disposals/2026-07-11
```

- Output defaults to `~/vault/mats-disposals/<batch-or-since>/` with `PAPER.md`,
  `logic/{disposals,rules,constraints}.md`, `trace/disposal_tree.yaml`, `evidence/README.md`.
- `--reveals` is an optional `{ "<id>": { rank, picked, ts } }` map. Build it from a frozen
  soundwave prediction snapshot with `soundwave-reveals.mjs <batch>` (reads
  `~/.claude/soundwave-discover/predictions/<batch>.json`). Without it, every Status is
  `pending-reveal` (honest: the reveal has not been scored yet).
- **The seal is enforced**: the model prediction is committed at digest time, before the blind
  grade. If any supplied prediction `ts > verdict ts` (generated AFTER the grade, so the model
  may have seen it), the run exits non-zero with the offending ids and writes nothing.

## What it does NOT do (deliberately, default down a tier)

- It does not judge. Promoting a deviation into a `rules.md` entry, and the L2 semantic
  review, need judgment: that is Rung B (post-vacation), the orthogonal judge, not this tool.
- It does not touch `me2me-feedback.json` or the digest. Read-only except the output dir.

## Field mapping (me2me-feedback.json -> MDA)

`verdict` (up/down) -> **Verdict** · `notes` -> **Why** · `ts` -> **Sealed-at** ·
`batch` -> **Batch** · `id` -> **Item-id** · provenance always `user`. The model prediction
(rank-watch) enters only via `--reveals`, tagged `ai-executed`.

## Reference

Blank skeletons of every file live in `templates/`. The design rationale (ARA-to-MATS
mapping, the seal, the graduation gate) is on the CCOS Bunker: "ARA -> MATS: Blind-Disposal
Artifact".
