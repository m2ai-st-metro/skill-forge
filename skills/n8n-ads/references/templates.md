# Templates

## analysis.md

```markdown
# Analysis: <workflow name>
- Source: source/<file>
- Date: <YYYY-MM-DD>

## What it does (business language)
<trigger → transforms → outcome, 3-6 sentences, zero node jargon>

## The pain point
**Without this workflow:** <the one-sentence "what breaks" claim>
Cost of the pain: <time/money/missed leads/burnout — be concrete>

## Audience
`business-owner` | `creator` — <one sentence why>
(creator ads: SFW, "creator business automation" framing only)

## Signal score: N/5
<why. If <3: SKIP verdict + reason, logged to catalog.>

## Proposed ad angle
Hook idea: <the 2-second pain statement>
Reveal: <the outcome we show>

STATUS: awaiting-approval | approved | skipped
```

## script.md

```markdown
# Script: <slug>  (30-60s vertical, pain → agitate → reveal)
Audience: business-owner | creator

| Beat | Time | On screen (Veo shot) | Overlay text | Audio/pacing |
|---|---|---|---|---|
| Hook | 0-3s | shot-01 | "<pain in ≤6 words>" | hard cut in |
| Agitate | 3-15s | shot-02, shot-03 | ... | quickening cuts |
| Reveal | 15-40s | shot-04, shot-05 | ... | breathe, brighten |
| CTA | last 5s | CTA card (hyperframes, no clip) | "<CTA line>" | ... |

## Hyperframes composition brief
- Format: 9:16, target <NN>s
- Caption style / typography: ...
- Brand elements: ...
- CTA card: text, link/handle, style
- Pacing notes: ...
- Compliance check: no adult-adjacent framing, no real-app UI, no unsubstantiated claims

STATUS: awaiting-approval | approved
```

## veo-prompts.md

```markdown
# Veo shot prompts: <slug>
Generate in Flow at 9:16, 8s. Save as clips/shot-NN.mp4 per checklist.

## Shot 01 — <label> (beat: Hook)
```
<prompt, self-contained, 30-80 words, per references/veo-prompting.md>
```
...repeat per shot (4-7 total)
```

## clips/CHECKLIST.md

```markdown
# Clip checklist: <slug>
| Shot | File | Passes if | Status |
|---|---|---|---|
| 01 | shot-01.mp4 | <observable criterion> | pending/pass/regen-1/regen-2/cut |
```

## final/captions.md

```markdown
# Captions: <slug>
## YouTube Shorts
Title: ... / Description: ... / Hashtags: ...
## Instagram Reels
Caption: ... / Hashtags: ...
## TikTok
Caption: ... / Hashtags: ...
## Shared
Hook text: ... / CTA: ...
```
