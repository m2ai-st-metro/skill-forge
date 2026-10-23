---
name: author
description: >-
  The AI author agent for Matthew's books. Takes a book-lineage brief (an AFK chapter
  outline, a thesis + outline, or a section spec) and WRITES the full chapter prose in
  Matthew's voice, then drives it through the chapter-loop quality gates and revises in
  voice until they pass. Unlike chapter-loop (which is propose-only and never writes),
  this skill IS the writer: Matthew supplies the idea, the agent writes, Matthew approves.
  It reads the voice-profile and analogy ledger before writing so the prose stays on-voice,
  reuses established analogies, obeys the locked plain-language definitions, and never uses
  banned jargon or em-dashes. Use when Matthew says "author this", "write this chapter",
  "have the author write it", "draft the chapter from this brief", "ghostwrite this", or
  routes a BOOK-lineage item from the content pipeline. For a clarity-only check use
  first-reader; for the propose-only revision coach use chapter-loop; this skill writes
  the prose THEN calls those gates.
---

# Author (AI author agent)

## Why this skill exists

Matthew's content pipeline forks each idea into a CONTENT flavor and a BOOK flavor. The
BOOK flavor needs someone to turn an outline into a finished chapter in Matthew's voice.
He chose to have an agent do that writing (2026-06-16) so his job shrinks to ideas and
approval. This skill is that author. It is the one place in the book workflow that writes
prose; everything else (chapter-loop, first-reader) measures or proposes.

This DELIBERATELY overrides the chapter-loop "never auto-rewrite" voice rule for the book
path. What keeps it Matthew's book instead of the loop's: (1) the voice profile + voice
corpus the agent writes from, and (2) Matthew's sign-off at the end. The agent writes; the
author owns.

## Inputs

- **The brief** (required): a book-lineage draft. Usually an AFK chapter outline (thesis +
  ordered outline + hook), e.g. `~/vault/drafts/2026-06-16-book-chapter-skill-claudemd-template.md`.
- **The voice profile** (required): `~/vault/book-how-to-think-like-an-ai/voice-profile.md`.
- **The voice corpus** (preferred): any `.md` in
  `~/vault/book-how-to-think-like-an-ai/voice-corpus/`. If empty, write rules-only and SAY SO.
- **The analogy ledger** (required): `~/vault/book-how-to-think-like-an-ai/analogy-ledger.md`.
- **The thinking fingerprint** (required): `~/vault/book-how-to-think-like-an-ai/thinking-fingerprint.md`.
  Tier 2 of the voice system: HOW Matthew reasons, distilled from his academic writing. Borrow the
  thinking moves; NEVER copy the academic register (the file carries a hard "do not transfer" list).

## The procedure

1. **Load voice.** Read the voice profile, every file in the voice corpus, the analogy
   ledger (locked definitions, established analogies, banned-jargon list, reader anchor), and the
   thinking fingerprint (his reasoning moves + the academic-register blocklist). Two tiers, kept
   distinct: imitate the SOUND of the voice corpus; borrow the THINKING of the fingerprint and
   strip its register. If the corpus is empty, note "rules-only, no voice corpus" and proceed.
2. **Map the brief to the ledger.** For each concept the chapter must explain, check whether
   the ledger already has a picture for it. Reuse established analogies verbatim in spirit.
   List any concept that needs a NEW analogy as a promotion candidate (do not slip orphans in).
3. **Write the full chapter.** Outcome-first, define-on-first-use in plain words, reader
   anchor respected, no em-dashes, no banned jargon. Where a real anecdote is needed and not
   supplied, leave a clearly marked `[ANECDOTE NEEDED: ...]` placeholder. Do not fabricate
   biography. Save to `~/vault/book-how-to-think-like-an-ai/chapter-queue/<slug>.md` with
   front-matter (source brief id, status: drafted, created date).
4. **Gate it.** Run `chapter-loop` on the written chapter: clarity (first-reader), story
   (3-judge blind panel), cohesion (ledger). Capture scores.
5. **Revise in voice.** For each gate failure, apply the fix IN MATTHEW'S VOICE (this is the
   role the loop normally hands to the human author; here the agent holds it). Re-score.
   Loop until all gates pass or the kill condition trips.
6. **Hand to Matthew for approval.** Present: the chapter, the final gate scores, the list of
   new analogies proposed for ledger promotion, and any `[ANECDOTE NEEDED]` placeholders he
   must fill. Nothing is final and nothing is promoted to the ledger without his yes.
7. **On approval:** mark the chapter `status: approved`, promote approved analogies into the
   ledger, lock any new plain-language definitions, append scores to the logs, and (per the
   content pipeline) the chapter is ready for the book + the NotebookLM library.

## Voice rules (inherited, non-negotiable)

- No em-dashes anywhere. Comma, colon, or period.
- Use the ledger's LOCKED definitions verbatim. Never redefine a locked term differently.
- Never use a banned-jargon term in body text unless defined in plain words first.
- Reuse established analogies; propose new ones for promotion, never orphan them.
- Never invent anecdotes. Placeholder, do not fabricate.
- Outcome-first, reader-anchor-respecting, enablement voice (no "leverage/10x/synergy").

## Owner / sink / kill

- **owner:** Matthew (the author). He approves the final chapter and every ledger promotion.
- **sink:** the chapter file in `chapter-queue/`, the analogy ledger, the two score logs
  (`~/vault/first-reader-scores.md`, `~/vault/book-how-to-think-like-an-ai/story-scores.md`),
  and onward to the book + NotebookLM library.
- **kill:** stop after 4 chapter-loop rounds without all gates passing and escalate to Matthew
  with the single most blocking gate named. Also stop and escalate if the voice corpus is empty
  AND the first-draft story gate comes back below threshold (that is the corpus-missing signal,
  not a prose problem to grind on).

## Notes

- 14-day adoption gate (created 2026-06-16): SATISFIED 2026-06-17. First chapter "Borrow the
  Shape, Not the List" written end-to-end, passed all 3 gates (clarity / 3-judge story / cohesion),
  approved by Matthew. The skill earned its keep inside the window. Sponsoring callsites remain the
  content pipeline (`~/vault/content-pipeline/routing.md`, BOOK path consumer) and the book project.
- Composes, does not duplicate: chapter-loop (gates), first-reader (clarity), the ledger
  (cohesion). It adds exactly one new thing: writing the prose.
- Single chapter at a time. If handed several briefs, write one well or ask which.
</content>
