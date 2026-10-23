---
name: book-to-lens
description: "Create a reusable evaluation LENS from a book's core model or thesis. Reads a book (or a chapter, or works from well-known book knowledge), extracts the mental models the author argues by, then generates an \"evaluate-through-frame\" skill: it takes a target artifact (a project, idea, pipeline, or algorithm) and returns findings plus a score seen through that book's frame. The evaluation sibling of book-to-skill. A lens does NOT execute a procedure and has NO voice; it changes what you NOTICE and what you VALUE. Use when the user says \"book to lens\", \"make a lens from this book\", \"turn this thesis into an evaluation frame\", \"review X through the lens of Y\", or wants a book's model captured as a reusable analytical filter."
---

# Book-to-Lens — Book Model to Reusable Evaluation Frame

Turn a book's core model into a lens: a reusable evaluation frame you apply TO a target
(a project, idea, pipeline, or algorithm) to surface what that frame makes you notice and
value. Sibling of `book-to-skill` (DO) and `book-to-persona` (BE). A lens is SEE: stateless,
no voice, no execution. Same extract -> review -> generate -> validate pipeline, "one schema".

## Skill vs lens vs persona

- **Skill** (book-to-skill): a PROCEDURE. "How do I DO this?" Output: SOP-phased skill.
- **Lens** (this): an EVALUATION FRAME. "What does this model make me SEE and VALUE?"
  Output: an evaluate-through-frame skill that scores a target.
- **Persona** (book-to-persona): a VOICE. "What would this mind say back?" Output: a subagent.

## Scope

EXTRACT-THE-MODEL only: a book whose value is a way of SEEING (a thesis, a set of mental
models, a framework) becomes an analytical filter. Pure how-to with no transferable model
is book-to-skill's job, not this. If the book has neither a model nor a method (pure
narrative), halt with `[NO_MODEL]`.

## Source modes (pick one in Phase 1)

- **Mode A: provided text.** A chapter/draft/notes file the user supplies. Extract the
  model from the page, exactly like book-to-skill.
- **Mode B: well-known book.** A widely-known book the model already understands
  conceptually (e.g. an Audible listen with no text file). Extract the model from
  established understanding of its FRAMEWORK. NEVER reproduce copyrighted passages: a lens
  is the book's concepts-as-criteria, synthesized in your own words, not quotes. If
  understanding is thin or uncertain, drop to Mode A and ask for notes rather than
  fabricate.

## Phase 1: Source & mode

1. Identify the book and choose Mode A or Mode B.
2. Confirm the book offers a transferable MODEL (not just a procedure or a story).
3. If no model is extractable, output `[NO_MODEL]` and halt.

## Phase 2: Model extraction (the lens frames)

Produce the set of FRAMES that make up the lens. For each frame:

- **Name** the model (short, memorable).
- **The question it forces** when looking at a target ("are you over-searching before
  committing?").
- **What it makes you VALUE** (the criterion the author would optimize).
- **Failure signal** it detects (what a target looks like when it violates the model).

Aim for 6-12 frames. Add a one-line **scoring rubric** (how to roll the frames into a
0-100 or red/yellow/green verdict). Flag tacit/edge cases separately. Save the draft lens
to a working dir (e.g. `/tmp/book-to-lens/lens-{slug}.md`).

## Phase 3: Lens review (Human-in-the-Loop)

Present the extracted frames to the user. Ask:

- Do these frames capture how the book actually makes you see?
- Any frame missing, wrong, or over/under-weighted?
- Is the scoring rubric right?

Incorporate feedback before generating. Do not skip this gate.

## Phase 4: Lens generation

Invoke `skill-creator` to generate an evaluate-through-frame skill named `lens-{book-slug}`.

**Key instructions for skill-creator:**

- The generated skill's INPUT is a target artifact (project / idea / pipeline / algorithm),
  named or pasted by the user.
- Its OUTPUT is: per-frame findings (what the frame flagged in this target) + the rubric
  score + a short "what to change" list. No procedure, no voice.
- Each Phase-2 frame becomes a section the skill checks the target against.
- Source attribution in frontmatter (book title, author, that it is a lens).
- The skill must state it is a LENS and refuse to execute the book's method (that is the
  skill sibling's job).

## Phase 5: Validation

1. Read the generated `lens-{slug}` SKILL.md.
2. Verify every Phase-2 frame is represented as a check.
3. Verify it takes a target and returns findings + score (not a how-to).
4. Smoke-test: run the lens against one real target and sanity-check the findings.

## When NOT to use this

- The book teaches a repeatable procedure with no transferable model -> `book-to-skill`.
- You want an author's VOICE to argue back, not a checklist -> `book-to-persona`.
- The book is pure narrative with no model -> output `[NO_MODEL]`.

## Source Attribution

Evaluation sibling of `book-to-skill` (itself the prose sibling of `video-to-skill`,
technique from Mark Kashef, 2026-03-23). book-to-lens adapts the same
extract -> review -> generate -> validate pipeline to produce an analytical frame instead
of a procedure.
