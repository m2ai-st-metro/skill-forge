# Veo Prompting Reference (for Flow / Gemini, HIL generation)

Grounded 2026-08-13 from ai.google.dev/gemini-api/docs/veo and Google Cloud video-gen
prompt guidance. Current generation at grounding time: **Veo 3.1** (models:
veo-3.1-generate-preview / -fast / -lite; Flow uses the same family). If prompts start
behaving oddly or a new Veo generation ships, re-verify before trusting this file.
(Note: "Veo 2.1" does not exist; the project brief's version name was stale.)

## Capabilities that matter for this pipeline

- Durations: 4, 6, or 8 seconds per clip (8s required for 1080p+). Plan shots at 8s, trim in assembly.
- Aspect ratios: 16:9 and **9:16 (use 9:16 for every shot in this pipeline — state it)**.
- Native synchronized audio: dialogue, SFX, ambient. We usually DON'T want dialogue
  (hyperframes owns text/voice); do want ambient/SFX for texture.
- Text rendering in-frame is unreliable — never ask Veo to render readable UI text or
  headlines; overlays are hyperframes' job.

## Prompt structure (in this order, 30-80 words, sweet spot ~50-60)

1. **Subject** — who/what, concrete and sketchable ("a small-business owner in her 40s at a
   cluttered reception desk")
2. **Action** — one clear action per shot, not a sequence
3. **Scene/Setting** — location, time of day, props that sell the story
4. **Camera & composition** — "close-up", "slow dolly in", "eye-level", "handheld", "wide shot"
5. **Style & ambiance** — lighting, palette, mood ("warm morning light", "cool blue late-night
   glow", "cinematic, shallow depth of field")
6. **Audio** — ambient/SFX only, described explicitly ("phone notifications chiming
   relentlessly, low office hum"). Dialogue only if scripted, in quotation marks.

Litmus: if someone else read the prompt, could they sketch the shot? If they'd guess, add detail.

## Rules for this pipeline's shots

- **Self-contained shots, no recurring characters.** Veo cannot hold identity across
  separate generations (known identity-drift failure). Different person per shot, or use
  hands / screens / objects / environments. Never write "the same woman from shot 1".
- One idea per shot. Competing aesthetics or multi-beat actions produce mush.
- State "vertical 9:16" in every prompt (Flow UI setting AND prompt text — belt and braces).
- No brand names, no readable text, no phone-UI mimicry of a real app.
- Pain shots: exaggerate the sensory grind (stacks of paper, 2am screen glow, endless
  scroll). Reveal shots: calm, bright, spacious — the contrast IS the message.
- When regenerating a failed clip, change only the element that failed; don't rewrite.

## Example (pain shot, business-owner audience)

```
Vertical 9:16. A tired cafe owner in his 50s hunched over a laptop at a counter after
closing, surrounded by receipt stacks and sticky notes, manually retyping numbers into a
spreadsheet. Slow dolly in to a tight close-up on his rubbing his eyes. Dim overhead light,
cool blue laptop glow, cinematic, shallow depth of field. Audio: quiet keyboard clicks,
a fridge humming, a long sigh.
```

## Example (reveal shot, creator audience)

```
Vertical 9:16. A young content creator relaxing on a sunny balcony with coffee, glancing at
her phone with a small satisfied smile as notifications roll in, then setting it down and
looking at the view. Handheld medium shot, gentle push in. Golden-hour warm light, airy,
optimistic. Audio: soft city ambience, birds, a light notification chime.
```
