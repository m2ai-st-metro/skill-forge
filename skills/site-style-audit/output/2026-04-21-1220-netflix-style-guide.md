# Style Guide — Netflix (Logged-Out Homepage)

**Source URLs:** https://www.netflix.com/
**Extracted:** 2026-04-21
**Confidence notes:** Copy, layout structure, and CTAs observed directly. No CSS color values, CSS variables, or `font-family` declarations came through the fetch — styling is delegated to external stylesheets that WebFetch did not surface. Color and typography sections below are qualitative only; no hex codes are recorded because none were observed. This is the pre-login marketing homepage only, not the logged-in product UI, which is a different design system.

## Color Palette

No CSS color values were visible in the fetched markup. The following are qualitative descriptions only; treat them as inferred from brand convention, not observed in this fetch.

- **Primary:** signature red — used for the main CTA button and brand wordmark *(inferred)*
- **Accent:** white — used for headline and body text over the hero image *(inferred)*
- **Neutral / background:** deep black — used as the page background and in gradients behind the hero imagery *(inferred)*
- **Text:** white on dark backgrounds, dark on light *(inferred)*

If exact tokens are needed, consult Netflix's public brand resources rather than relying on this guide.

## Typography

- **Headings:** unknown from fetch — `font-family` not declared in the visible markup. Character: likely a custom brand sans-serif (Netflix has a documented proprietary typeface), but this is inference not observation.
- **Body:** unknown from fetch
- **Accent / display:** unknown
- **Notes:** Headline copy is short and declarative ("Unlimited movies, TV shows, and more"). Sentence case is used, not all-caps. The headline-to-subhead ratio is substantial — the subheading ("Starts at $8.99. Cancel anytime.") sits visibly below the primary headline as secondary emphasis.

## Imagery Style

- **Medium:** photography / branded composite. The hero uses a single full-bleed image. File path hint: `assets.nflxext.com/ffe/siteui/vlv3/...TRIFECTA-perspective...large.jpg` — the filename suggests a rendered composite rather than a single photograph.
- **Mood:** cinematic, high production value (inferred from brand category; content of the specific image not visible to the fetch)
- **Subject patterns:** content-forward — the imagery on this page is about titles (shows, films) rather than people using the product or lifestyle photography
- **Treatment:** full-bleed hero, likely edge-to-edge with copy overlaid. No icon-heavy illustrations observed.

## Layout

- **Structure:** vertical long-form marketing page composed of distinct modules, stacked
- **Density:** balanced — generous space around the hero, tighter packing in the Top 10 grid and feature blocks
- **Hierarchy:** eye goes first to the hero headline and price, then to the inline email capture, then down to the Top 10 ranking. The page is designed to convert above the fold and use the rest of the page to overcome objections.
- **Recurring patterns:**
  - Full-bleed hero with centered value proposition
  - Numbered social proof grid (Top 10 titles, 1-10)
  - 4-cell feature grid (device compatibility, offline downloads, content breadth, parental controls)
  - 6-item FAQ accordion (collapsible)
  - Multi-column footer with language selector
  - Inline email capture repeated twice (above the fold and near the bottom)

## Tone of Voice

- **Register:** conversational, price-forward, confident but not aspirational
- **Sentence length:** short. Most observed lines are under 10 words.
- **Vocabulary:** plain. No jargon, no marketing-ese like "elevate," "curated," "immersive." Uses concrete nouns (titles, price, devices) rather than abstract benefits.
- **Sample quotes:**
  - "Unlimited movies, TV shows, and more"
  - "Starts at $8.99. Cancel anytime."
  - "The Netflix you love for just $8.99."
  - "Ready to watch?"

## Motifs & Signature Moves

- **Price on repeat.** "$8.99" appears in multiple places on the page, including directly beneath the main headline. Price is treated as a brand anchor, not a detail.
- **Risk removal as a headline promise.** "Cancel anytime" is given the same visual weight as the price itself.
- **Top 10 as social proof.** A numbered ranked list of current titles, 1-10. This is a distinctive Netflix pattern that carries over from the product UI.
- **Question-as-CTA.** "Ready to watch?" frames the email capture as an invitation rather than a sales close.
- **Bilingual language toggle surfaced in the nav.** EN/ES switch is elevated to primary navigation, not buried in the footer.
- **Inline email field as the conversion unit.** No "sign up" page jump — the email field is the form, repeated above the fold and again further down.

## Downstream Use

For a rebuild brief or competitive landing page: the structural pattern (hero with price + inline email → numbered social proof → feature grid → FAQ → footer) is the most portable finding in this document and is worth more than the color/type specs, which need direct CSS or a headless render to capture properly. If you need exact color/type tokens, rerun with a screenshot-to-vision or a headless browser render; WebFetch alone will not give you them.
