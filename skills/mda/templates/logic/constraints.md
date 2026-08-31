# Constraints — blind protocol + falsification standard

## Blind protocol (the seal)
- A verdict is written with its one-line **Why** BEFORE any model prediction, Top Picks
  badge, rank, or judge verdict is seen. A grade without a why is half a label.
- Once written, a disposal is **sealed**: provenance `user`, timestamped. The reveal is
  **appended, never overwritten**. The model prediction is frozen at digest time, BEFORE
  the grade (soundwave `predictions/<batch>.json`, write-once). That ordering is the
  blind-test guarantee. `stamp.mjs` refuses to emit a label whose model prediction was
  committed AFTER its verdict (the model may have seen the grade).
- Blind-count floor for the 2026-07-23 gate: `ts >= 2026-07-12` (post blind-protocol fix
  in `soundwave_discover.py`, `TOP_PICKS_DISPLAY="banner"`).

## Provenance vocabulary (ARA)
`user` (I said it) · `ai-suggested` (model inferred) · `ai-executed` (model acted / predicted)
· `user-revised` (I refined a model suggestion). Sealed disposals are always `user`.
Only `rules.md` entries may be `user-revised`.

## Falsification standard
- Standing: if a pasted prompt plus the interest model's own analytics reproduces a
  disposal without my reasoning, that disposal is not aligned, it is emulated.
- Per-rule (name-deletion test, ARA D3): strike the reasoning from a rule; if no
  transferable judgment survives, it is a league table, not a claim.

## Reading discipline
- Agreement is not alignment. A batch with zero deviations means the model already agrees,
  which is no signal, not success (ARA D5: a tree with zero dead-ends is suspicious).
- The deviations are the product.
