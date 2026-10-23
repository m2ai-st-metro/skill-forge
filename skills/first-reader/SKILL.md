---
name: first-reader
description: >-
  A cold-reader editing pass that fights the curse of knowledge in the user's
  writing. It spawns a subagent that role-plays a specific non-expert reader,
  reads a draft WITHOUT the author's context, and reports exactly where that
  reader falls off, then supplies everyday analogies, a reference rewrite, and a
  curse-of-knowledge score. Use this whenever the user shares a chapter, post,
  email, or section and wants to know if a non-expert will follow it, or says
  "first reader", "read this cold", "where will my reader fall off", "check this
  for assumptions", "did I assume too much", "is this too jargony", "curse of
  knowledge", or worries that they over-assume reader knowledge. Trigger even
  when the user does not name the skill but pastes a draft and asks whether it
  lands for a lay audience. Default reader is a 50-year-old business owner who
  has never used an AI tool; the persona is overridable per invocation. This is
  a DIAGNOSTIC pass, never an auto-rewrite, so the author keeps their voice.
---

# First Reader

## Why this skill exists

A writer cannot see their own curse of knowledge. Once you understand something,
the inferential steps that got you there collapse into a single obvious move, and
you stop writing them down. You are not being lazy, you literally cannot perceive
the gap, because the missing step is filled in by knowledge the reader does not
have. The only reliable fix is an outside reader who does not share your context
and who tells you, honestly, where they got lost.

This skill manufactures that reader on demand. It does not rewrite the author's
work into bland clarity (that would strip the voice, which for a personal or
narrative piece is the whole point). It diagnoses. It hands the author a precise
map of where a real, named reader falls off, the raw material to fix it
(analogies), one worked example of a fix, and a number to track progress over
time.

## The reader persona

Every run is anchored to ONE concrete reader. A vague "general audience" produces
vague feedback, because the cold-reader has nobody specific to be. Specificity is
what makes the confusion real.

Default persona (use unless the user overrides it):

> A 50-year-old business owner, sharp and successful in their own field, who has
> never used an AI tool. They have a normal adult vocabulary but zero AI or
> software vocabulary. They have no idea what a "model", "prompt", "token",
> "context window", "agent", or "LLM" is. They are not stupid, they are
> uninitiated. They will keep reading as long as it makes sense, and the moment a
> sentence assumes something they do not know, they quietly disengage.

If the user names a different reader (a CFO, a teacher, a teenager, a developer),
swap the persona and keep everything else the same. Always state which persona
you used at the top of the report, so the author knows whose eyes they are
getting.

## How to run it

1. Get the draft. It may be pasted inline or in a file the user points to. If the
   user gives a whole book or many chapters, ask which section to read, or default
   to the first unreviewed one. A focused pass on one section beats a shallow pass
   on everything.

2. Spawn a cold-reader subagent (use the Task / Agent tool). Isolate it: give it
   ONLY the persona and the draft text, and explicitly withhold the surrounding
   conversation, the book's premise, and any author context. The whole value comes
   from the subagent not knowing what the author knows. Use a prompt shaped like
   the one in "Cold-reader subagent prompt" below.

3. Take the subagent's raw confusion report and shape it into the four-part output
   below. You may add the analogy bank and the reference rewrite yourself (the
   subagent supplies the confusion map; you, with full context, are better placed
   to propose accurate analogies and a faithful rewrite).

4. Offer the counterargument handoff. If the piece makes an argument a skeptical
   reader could push back on, offer to run it through the `counterargument-stress-test`
   skill next. Do not run it automatically.

## Cold-reader subagent prompt

Spawn the subagent with something close to this. The constraints matter: if it
starts being charitable or filling gaps with its own knowledge, the report
becomes useless.

```
You are role-playing a specific reader, and ONLY this reader:
<persona>

You are about to read a draft. Read it strictly as this person. Do not use any
knowledge this person would not have. When a sentence relies on a term or concept
this reader does not know, you DISENGAGE at that exact point and record it. Do not
be charitable. Do not infer what the author probably meant. Do not look it up.

For the draft below, report:
1. Every point where you fell off, with the EXACT sentence or phrase quoted, and
   one line on why you fell off (undefined term / assumed prior concept / skipped
   logical step / unexplained jargon / too many new ideas at once).
2. The handful of concepts you would have needed explained, in plain words, to
   keep going.
3. One honest sentence: at what point, if any, did you stop genuinely following
   and start just moving your eyes over words?

Draft:
<draft>
```

## Output format

Always produce these four parts, in this order, with these headings. Lead with the
persona line so the author knows whose reading this is.

> Read as: <persona, one line>

### 1. Fell-off map

The heart of the report. Each entry is a place the reader lost the thread. Quote
the author's text verbatim so they can find it, then name the cause in a few
words. Order by where it appears in the draft.

**Example entry:**
Input passage: "Once you give the model the right context, the agent just runs
the loop on its own."
Output entry:
- "give the model the right context": assumes the reader knows what a "model" is
  and that you can "give" it anything. Three unexplained ideas (model, context,
  giving context) stacked in seven words.
- "the agent just runs the loop": "agent" and "loop" are both undefined; reader
  has no picture of what is actually happening.

### 2. Analogy bank

For each abstract concept that tripped the reader, offer one concrete, everyday
analogy the persona would already understand. These are raw material, not
mandates. The author picks the ones that fit their voice. Favor analogies from the
reader's world (running a business, hiring, kitchens, tools, paperwork) over
technical ones.

**Example:**
- "context window" → like a desk: only so much can be spread out on it at once,
  and when it fills up, older papers get pushed off the edge to make room.
- "model vs memory" → the model is the smart temp worker who is brilliant but
  forgets everything at the end of each shift; the memory store is the filing
  cabinet they check at the start of the next one.

### 3. Reference rewrite (example only, do not paste)

Pick the single worst fell-off passage and rewrite it for the persona. Label it
clearly as a REFERENCE EXAMPLE, not a replacement. The author should read it to
see what "explained" looks like, then write their own version in their own voice.
State this explicitly every time, because the temptation to paste it in is real
and pasting it in is how a memoir loses its author.

> This is a reference example to show what fully-explained looks like for this
> reader. Do not paste it in. Use it as a target, then say it in your own voice.

### 4. Curse-of-knowledge score

A simple, repeatable number so progress is measurable across drafts. Compute:

- **Assumptions per page**: count of distinct unexplained terms or skipped steps
  in the fell-off map, divided by pages (assume ~400 words per page if length is
  unclear). Report the raw count and the per-page rate.
- **First-fall point**: how far in (percent of the way through) the reader got
  before the first time they fell off. Earlier is worse.
- **Disengagement point**: where, if anywhere, the reader stopped truly following.

Present it plainly, for example:
> Assumptions: 11 across ~2.5 pages = 4.4 per page. First fall at 8% (second
> paragraph). Reader disengaged around 60%.

Then one sentence of interpretation: is the problem front-loaded jargon, a single
unexplained pillar concept everything else rests on, or a steady drip.

## Keeping the author's voice

Repeat this principle in how you talk about the work: the goal is not to make the
writing sound like everyone else's clear writing. It is to remove the specific
places a specific reader falls off, while keeping everything that makes it the
author's. When in doubt, diagnose and suggest, do not overwrite. If the author
asks you to just rewrite the whole thing, you can, but flag that a full rewrite
trades voice for clarity and offer the diagnostic version first.

## Tracking progress over time

If the author runs this repeatedly on the same project, keep the scores comparable
and, if useful, append them to a simple running log (for example
`~/vault/first-reader-scores.md`) with the date, the section, and the three
numbers. The point is to watch assumptions-per-page fall chapter over chapter,
which is the author training themselves out of the curse, not just patching one
draft.

## Notes

- No em-dashes anywhere in this skill's output. Use a comma, colon, or period.
  This is a hard house rule.
- This skill is most useful on explanatory or narrative writing for a non-expert
  audience. It is overkill for an email to a peer who shares all your context, and
  it should say so rather than invent problems that are not there.
