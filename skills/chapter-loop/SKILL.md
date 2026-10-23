---
name: chapter-loop
description: >-
  A gated, human-in-the-loop revision loop for a single book or long-form chapter.
  Runs three measurable gates against a draft (clarity via first-reader, story-arc
  via a 3-judge blind panel, and analogy-cohesion via the book's analogy ledger),
  proposes targeted voice-preserving edits tied to specific failures, and loops
  until all gates pass or the author stops. It never auto-rewrites: each round it
  proposes, the author writes the change in their own voice, then it re-scores. Use
  when the author says "chapter loop", "run the chapter loop", "loop this chapter",
  "tighten this chapter", "is this chapter ready", "score this chapter", or shares a
  book/long-form chapter and wants it driven toward a clear, cohesive, definitive
  story rather than just a clarity check. For a clarity-only diagnostic use
  first-reader; for argument pressure-testing use counterargument-stress-test. This
  skill orchestrates both plus the story gate. Built for the book "How to think like
  an AI"; the ledger path and reader persona are overridable per invocation.
---

# Chapter Loop

## Why this skill exists

A chapter can be clear and still not tell one story. `first-reader` catches where a
non-expert falls off (jargon, undefined pillars). It does not catch a chapter that
is perfectly readable but braids two competing theses so the reader cannot say what
the chapter was about. Driving a chapter to "clear AND definitive" needs more than a
clarity pass: it needs a clarity gate, a story-arc gate, and a cohesion gate that
keeps analogies consistent across the whole book. This skill runs all three as a
gated loop and protects the author's voice while doing it.

Proven before shipping: the story rubric below was validated on Chapter 1 of "How to
think like an AI" with a 3-judge blind panel (run wf_16ba97dc-53d, 2026-06-14). The
judges scored it with zero spread on every dimension (5/5/5/4) and independently
flagged the same structural flaw, which is the evidence the rubric is stable rather
than one model's taste.

## What it composes

- **`first-reader`** (owned skill): the clarity gate. Produces assumptions-per-page
  and the fall-off map.
- **The story-arc panel** (defined here): the story gate. Three independent blind
  judges score the chapter on a fixed 0 to 5 rubric.
- **The analogy ledger** at `~/vault/book-how-to-think-like-an-ai/analogy-ledger.md`:
  the cohesion gate. Every analogy in the chapter must already be in the ledger or be
  promoted into it. No orphan, one-off analogies.
- **`counterargument-stress-test`** (owned skill): offered, not automatic, for
  chapters that make an argument a skeptic could push back on.

## The three gates and their thresholds

A chapter is "ready" only when all three pass.

### 1. Clarity gate (first-reader)
- HARD pass: zero undefined pillar concepts. A pillar is a term the chapter's payoff
  depends on (e.g. "schema" in Chapter 1). If the reader cannot follow the climax
  because a load-bearing word was never defined in plain language, the gate FAILS
  regardless of the per-page number.
- TARGET: assumptions-per-page under 1.0. Track the number every round; it should
  fall chapter over chapter.

### 2. Story gate (3-judge blind panel) — STRICTEST
- Hook / Tension: **4+**
- Turn: **4+**
- Resolution: **4+**
- Single Takeaway: **5 required.** This is the uncompromising gate. The book's whole
  promise is a clear, definitive story, so a chapter must be unified around ONE
  restatable message, not two competing ones. A 4 here fails the loop.
- Reliability check: if the three judges' one-sentence takeaways diverge, the chapter
  is not unified yet, even if the numbers look acceptable. Treat divergence as a fail
  on Single Takeaway.

### 3. Analogy-cohesion gate (ledger)
- Every analogy used in the chapter is either already in the ledger or gets promoted
  into it this round (author approves the promotion).
- Any analogy on the ledger's "banned in body text" list, or any term the ledger says
  to express in plain words, is flagged.
- A genuinely new good analogy is not a failure: it is a prompt to add it to the
  ledger so later chapters reuse it. An orphan analogy that duplicates a concept the
  ledger already covers with a different picture IS a failure (it breaks cohesion).

## The loop

1. **Read** the chapter and the analogy ledger. Confirm the reader persona (default:
   50-year-old business owner, never used an AI tool; overridable).
2. **Clarity gate**: run `first-reader` on the chapter. Capture the fall-off map and
   the assumptions-per-page number. Append the number to the running log.
3. **Story gate**: run the 3-judge panel (see below). Capture per-dimension scores,
   the three one-sentence takeaways, the agreed weakest dimension, and the agreed fix.
4. **Cohesion gate**: check every analogy in the chapter against the ledger. Flag
   orphans and banned terms. Note new analogies that should be promoted.
5. **Synthesize and PROPOSE**: present which gates passed and failed, and a short list
   of TARGETED edits, each tied to a specific gate failure and a specific passage.
   Do not rewrite the chapter. For each proposed edit, show the failing passage and a
   reference example of the fix, labeled clearly as a reference, not a replacement.
6. **Author writes the change** in their own voice and hands the revised chapter back.
   Promote any approved new analogies into the ledger. Lock any newly-defined pillar
   terms into the ledger's definitions table.
7. **Re-score** (back to step 2). Repeat until all three gates pass, or the kill
   condition trips, or the author stops.
8. On full pass: log the final scores, note the chapter as ready, and offer the
   `counterargument-stress-test` handoff if the chapter makes an argument.

## Voice rule (non-negotiable)

This loop NEVER auto-rewrites the chapter. It diagnoses and proposes; the author
writes. Each round is human-in-the-loop and is not auto-approved. A reference rewrite
may be shown to illustrate what "fixed" looks like, but it is always labeled as a
reference example and never pasted into the manuscript by the skill. A memoir that the
loop rewrites stops being the author's book by round three. When in doubt, propose and
suggest, do not overwrite.

## The story-arc panel

Run three independent blind judges. Each gets ONLY the rubric and the chapter, with no
author context, no book premise, no prior conversation. Convergence across judges is
the reliability signal; divergence on the one-sentence takeaway is itself a fail.

The proven panel script lives at:
`~/.claude/projects/-home-apexaipc-projects-claudeclaw-os/<session>/workflows/scripts/prove-story-rubric-wf_16ba97dc-53d.js`
Re-invoke it with `{scriptPath: ...}` pointed at the new chapter file (change the
CHAPTER constant), or re-create an equivalent 3-judge `parallel()` panel. If a heavy
workflow is not warranted, a single blind judge via the Agent tool is an acceptable
lighter fallback, but it loses the reliability check, so prefer the panel for any
chapter the author intends to publish.

Rubric (score each 0 to 5, quote one verbatim line of evidence per dimension):
1. HOOK / TENSION: does the opening (first ~15%) plant a specific question or stake
   that compels reading on?
2. TURN: is there a clear, locatable pivot where understanding changes, and is it
   earned by what came before?
3. RESOLUTION: does the tension raised at the open get paid off by the close?
4. SINGLE TAKEAWAY: is the chapter unified around ONE message a reader could restate
   in a sentence, rather than several competing ones?
Plus: each judge writes, in one sentence, what the chapter is trying to teach; names
the weakest dimension; and gives one concrete change that would raise it to a 5.

## Logging

- Clarity: append to `~/vault/first-reader-scores.md` (date, chapter, assumptions/page,
  first-fall, disengagement).
- Story: append to `~/vault/book-how-to-think-like-an-ai/story-scores.md` (date,
  chapter, hook/turn/resolution/takeaway, the agreed weakest dimension).
The point of the logs is to watch the numbers improve chapter over chapter. That trend
is the author training out of the curse, not just patching one draft.

## Owner / sink / kill

- owner: the author (Matthew), who approves every proposed edit.
- sink: the revised chapter file, the analogy ledger, and the two score logs.
- kill: stop after 4 rounds on the same chapter without all gates passing, and
  escalate to the author with the single most blocking gate named. Never loop forever
  on a chapter that will not converge.

## Notes

- No em-dashes anywhere in this skill's output. Use a comma, colon, or period.
- This skill is EXPERIMENTAL under the 14-day adoption gate (created 2026-06-14). It
  earns its keep if it runs on at least chapters 2 and 3 within 14 days. Its owner is
  the author and its callsite is the book project. If it is not used, cold-archive it.
- Single-chapter focus beats a shallow pass on a whole manuscript. If handed many
  chapters, do one well, or ask which.
