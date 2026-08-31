---
name: site-style-audit
description: "Audit one or more website URLs for visual and design patterns, then produce two markdown deliverables: a client-friendly summary of the brand feel, and a structured style guide (color palette, typography, imagery style, layout, tone/voice). Use whenever the user provides website URLs and asks for a brand/style audit, style guide extraction, design pattern analysis, 'what's the vibe', brand consistency review, or wants to match or replicate the look of referenced sites. Trigger even when the user does not explicitly say 'style guide' — any request to understand, describe, or match the design of one or more sites should route here."
argument-hint: "URL [URL ...]"
context: fork
---

# Site Style Audit

You are extracting the visual and design language of one or more websites and producing two deliverables: a non-technical summary for a client, and a structured style guide for a designer or downstream tool (e.g. an image generation prompt, a rebuild brief).

The user gives you 1..N URLs. You fetch each one, look for consistent patterns, and write both documents.

## Inputs

The user provides one or more URLs. Accept:
- Full URLs: `https://example.com/about`
- Bare domains: `example.com` (prepend `https://`)
- A mix of URLs across different domains (you'll look for consistency across them)

Single URL is valid — in that case you're auditing one site, not looking for cross-site consistency. Multiple URLs means the user wants you to call out what's *consistent* across them and what's *divergent*.

## Step 1: Fetch each URL with WebFetch

For each URL, call WebFetch with a prompt like:

> "Extract the visual and editorial signals from this page. Specifically: any CSS color values, font-family declarations, font sizes or weights, imagery (photos, illustrations, icons), layout structure (hero, grid, whitespace), headline and body copy samples, and any visible brand voice cues. Include raw HTML/CSS hints where available."

WebFetch is lossy on JS-heavy sites. If a page returns thin or obviously rendered-empty content (e.g., only a skeleton, no text, no visible styling), note it and proceed — don't fabricate around the gap.

If a URL fails entirely (404, timeout, blocked), record the error and continue with the rest. Mention the failure in the final deliverables.

## Step 2: Extract per-URL signals

For each URL, capture what you can observe or reasonably infer:

- **Colors** — dominant colors, accents, neutrals. Record hex values *only if you can see them in the fetched content* (inline styles, CSS variables, direct color declarations). If you can't, describe qualitatively: "warm terracotta," "deep navy," "muted sage." Never invent a hex code to sound precise.
- **Typography** — heading and body font families if declared. Note weights, approximate size relationships, whether serif/sans/mono/display. If no font-family is visible, describe the character: "geometric sans," "editorial serif," "monospace technical."
- **Imagery style** — photography (studio, candid, editorial), illustration (flat, textured, hand-drawn), abstract (gradients, shapes), or icon-heavy. Capture mood: clinical, warm, playful, cinematic, utilitarian.
- **Layout** — grid vs. asymmetric, whitespace density, hierarchy (bold hero vs. understated), content patterns (card grids, long-form prose, modular sections).
- **Tone of voice** — pull 2-3 short copy samples. Classify: formal, conversational, playful, technical, authoritative, aspirational. Note any consistent voice tics (questions, imperatives, jargon density).
- **Motifs** — anything recurring across the page: a specific shape, an illustration style, a phrase pattern, a repeated UI element.

Keep a working mental (or scratch) table of these per URL. You don't need to output this intermediate data — it feeds the two deliverables.

## Step 3: Cross-site synthesis (only if multiple URLs)

If the user gave you more than one URL, explicitly identify:

- **Consistent** — signals that appear across all or most URLs. These are the strongest brand anchors.
- **Divergent** — signals that differ meaningfully between sites. These either indicate sub-brands, audience segmentation, or brand drift. Name which.
- **Shared vocabulary** — recurring words, phrases, or concepts in the copy.

If a signal is consistent across 3 of 4 sites, say so — don't pretend it's universal.

## Step 4: Write the two deliverables

Output two separate markdown files to a `site-style-audit-output/` directory in the current working directory, timestamped:

```
./site-style-audit-output/<timestamp>-client-summary.md
./site-style-audit-output/<timestamp>-style-guide.md
```

Create the directory if it doesn't exist. Use `YYYY-MM-DD-HHMM` for the timestamp. If auditing a single identifiable brand, include a slug: `2026-04-21-1430-acme-client-summary.md`.

### Deliverable A: Client Summary

Non-technical. No hex codes, no font weights, no CSS jargon. Focused on *feel* and *story*. A client should read this and think "yes, that's us" or "no, that's not us."

Target length: 1 page, max 2. Use short paragraphs. No filler, no marketing puffery — describe what's actually there.

Structure:

```markdown
# [Brand/Site name] — Style Summary

**Sites reviewed:** [list URLs]
**Date:** [today's date]

## The Feeling

[2-4 sentences. What is the overall impression? If someone landed on these pages with no brand context, what would they take away? Example: "These sites feel like a quiet, considered editorial publication rather than a product company. The pace is slow, the imagery is restrained, and the writing assumes the reader is smart."]

## What Stands Out

[3-5 bullets. The signature moves — the things that make this brand recognizable. Example: "Every page opens with a full-bleed photograph, usually a landscape with no people." Not "uses hero images."]

## The Voice

[2-3 sentences describing how the brand talks. Include a short representative quote if you have one.]

## Where It's Consistent / Where It Drifts
[Only include this section if auditing multiple URLs. Be specific about what holds and what doesn't.]

## Who This Reads To
[1-2 sentences. Best guess at the intended audience based on tone, imagery, and complexity. Be explicit that this is inference.]
```

### Deliverable B: Style Guide

Structured, concrete, for a designer or downstream tool. Use the exact section headers below so the document is parseable.

```markdown
# Style Guide — [Brand/Site name]

**Source URLs:** [list]
**Extracted:** [date]
**Confidence notes:** [One line on fetch quality — e.g. "CSS observed directly on 2 of 3 URLs; site 3 was JS-rendered and signals are inferred from visible copy only."]

## Color Palette

[For each color, give: name, hex if observed, qualitative description. Group into primary / accent / neutral if the hierarchy is clear.]

- **Primary:** [hex or description] — used for [where]
- **Accent:** [hex or description] — used for [where]
- **Neutral / background:** [hex or description]
- **Text:** [hex or description]

If a color was inferred rather than observed, mark it `(inferred)`.

## Typography

- **Headings:** [font family if known, else character description] — [weight/size cues]
- **Body:** [font family if known, else character description]
- **Accent / display:** [if any]
- **Notes:** [e.g. "Heading-to-body ratio is roughly 3:1. Tight tracking on headings."]

## Imagery Style

- **Medium:** [photography / illustration / abstract / mixed]
- **Mood:** [e.g. "cinematic, desaturated, human-centered"]
- **Subject patterns:** [what do the images depict — people, objects, landscapes, product, abstract]
- **Treatment:** [any consistent filter, crop, framing, color grade]

## Layout

- **Structure:** [grid / asymmetric / long-form / modular]
- **Density:** [whitespace-heavy / packed / balanced]
- **Hierarchy:** [where does the eye go first — hero, headline, imagery, nav]
- **Recurring patterns:** [card grids, full-bleed sections, sticky nav, etc.]

## Tone of Voice

- **Register:** [formal / conversational / playful / technical / authoritative]
- **Sentence length:** [short and punchy / long and editorial / mixed]
- **Vocabulary:** [jargon-heavy / plain / poetic]
- **Sample quotes:**
  - "[quote 1]"
  - "[quote 2]"

## Motifs & Signature Moves

[Any recurring visual or editorial patterns that define the brand. Shapes, phrases, UI elements, illustration styles.]

## Consistency Across Sites
[Only if multiple URLs. Explicit: what holds, what drifts.]

## Downstream Use

[Optional 1-2 sentences suggesting what to do with this. Examples: "Feed the Color Palette + Imagery Style sections into an image generation tool as reference to produce matching visuals." Or: "Hand to a designer as a rebrief for a rebuild." Only include if there's an obvious next step — don't pad.]
```

## Step 5: Report back

After writing both files, tell the user:

- The two file paths
- A 2-3 sentence headline summary of what you found (the brand essence in plain language)
- If there were fetch failures or weak signals, say so explicitly — don't let them discover it in the document

### Follow-up routing (where the style guide goes next)

A style guide ends at insight unless it is routed to a consumer. Close with a short routing
block offering the obvious next step(s) for THIS audit — never auto-run them, just name them:

- **Generate matching visuals** — feed the Color Palette + Imagery Style sections into
  `/banana-maker` as reference to produce on-brand images.
- **Rebuild / rebrief** — hand the style guide to a designer, or to `/website-to-hyperframes`
  / a rebuild brief, as the source of truth.
- **Brand-drift action** — if cross-site synthesis found drift, route the decision to the user
  (which direction is canonical?) rather than silently averaging it away; capture the cleanup
  via `goal-maker` with owner/sink/kill if it becomes real work.
- **No action** — if this was a one-off reference pull with no downstream, say so; don't
  manufacture a next step.

Only list routes that genuinely fit this audit. An honest "no obvious next step" beats padding.

## Principles

- **Honesty beats precision.** "Warm terracotta" beats an invented `#C45A3F`. Inference marked as inference beats fake authority.
- **Describe, don't market.** The client summary should describe what's there, not sell it back to them. No "elevates," "curated," "thoughtful" unless those words are earned by evidence.
- **Cross-site claims need cross-site evidence.** If only one URL shows a pattern, don't generalize it to the brand.
- **Thin signal is a finding.** If WebFetch returned mostly empty content, the style guide should say "signal was thin" rather than fabricate around the gap. A 60% style guide with honest gaps is more useful than a 100% style guide with 40% fiction.
- **No CSS jargon in the client doc, no vagueness in the style guide.** The two documents have different audiences — respect that.

## Common failure modes to avoid

- Inventing hex codes to sound authoritative (the biggest risk — resist it)
- Describing every site the same way because your prior is "modern minimal tech brand"
- Burying fetch failures at the bottom of the doc instead of surfacing them up front
- Writing the client summary in marketing-speak ("bold," "innovative," "cutting-edge") — this makes it useless as a mirror of the brand
- Skipping the cross-site consistency analysis when multiple URLs are given — that's often the most valuable part of the audit
