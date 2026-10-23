---
name: prompt-goodies
description: Pull a fresh "carrot or two" out of the content Matthew is currently working on, ready to attach to a Skool or community post. A carrot is a small, standalone-useful freebie derived from THAT content (a tailored copy-paste prompt, a mini-checklist, a one-page framework, a fill-in template, or a worked mini-example) that gives the masses real value and leaves them wanting the full thing. Use whenever Matthew says "prompt goodies", "give me a carrot", "carrot for this post", "pull a freebie out of this", "what can I give away with this post", "extract a prompt from this", or is about to post content and wants a giveaway to bundle with it. Also still upgrades a delegation prompt the user pastes in (the easy-button mode), and can serve the published prompt-pattern ladder on request.
---

# Prompt Goodies

The forward job of this skill is **carrot extraction**: take the content Matthew is working on
right now and produce one or two fresh, paste-ready giveaways he can bundle with a community
post. The old "publish the ladder" job is done (it now lives on the page at
memyselfplusai.com/edge/#prompt-goodies); the ladder remains here only as raw material to draw
from. See [references/ladder.md](references/ladder.md).

## Mode 1 (primary) — Extract a carrot or two

### Step 1: Get the source content
The carrot must come FROM the content, never from memory or a prior post. Resolve the source:
- If Matthew pasted text or named a file/draft, use that.
- If he says "what we're working on" or "this post," use the in-process artifact from the
  current session (the draft, chapter, page, or thread being built).
- If it is genuinely unclear what content he means, ask ONE question: "Which piece should I
  pull the carrot from?" Do not guess across his whole vault.

### Step 2: Find the most giveable nuggets
Read the content and look for the 1-2 things that are (a) immediately useful on their own,
(b) specific to this content, not generic advice, and (c) a true taste of the deeper material.
The best carrot makes someone think "I can use this today" and then "I want the rest."

### Step 3: Shape each nugget into a carrot
Pick the form that fits the nugget, do not default to "a prompt" every time:
- **Copy-paste prompt** — a ready-to-run prompt for a specific job in the content. Build it
  from the levers in references/ladder.md, but tailored to the content's actual task. Never
  paste a canonical rung unchanged.
- **Mini-checklist** — the 4-6 checks the content implies, as a list someone can run.
- **One-page framework** — the content's core method named and laid out (e.g. the five-box
  intake form, the three trust moves).
- **Fill-in template** — a skeleton the reader completes for their own situation.
- **Worked mini-example** — one concrete before/after that shows the idea landing.

### Step 4: Make it post-ready
- Short and scannable. A carrot a reader can absorb in under a minute.
- Plain language, no jargon, no em-dashes. Matthew's voice: warm, no fluff, no flattery.
- Self-contained: it works without buying anything. The pull to the full content is implicit
  in how good the free piece is, not a paywall.
- Each carrot gets a one-line "why this is the carrot" note for Matthew (not for the post).

### Step 5: Deliver
- Default to 2 carrots; 1 is fine if the content only has one strong giveaway, up to 3 if
  Matthew asks. Tell him if you could only find one good one rather than padding.
- Output each carrot as a clean markdown block he can paste straight into Skool.
- Offer to save them (e.g. alongside the post draft) or render an HTML version.

### What NOT to do
- Do not recycle the published ladder rungs or any prior post. Fresh, from this content.
- Do not hand back a generic prompt that is not tied to the content.
- Do not give away so much that the post itself has nothing left to say.
- Do not invent claims, commands, or steps the content does not support.

## Mode 2 (kept) — The easy button: upgrade a pasted prompt

The user pastes a prompt (or describes a task they are about to delegate) and wants it better.
Diagnose it against the checklist below, then return their prompt rewritten with ONLY the
missing items the situation needs. A single-worker task never needs items 6-8. Show the
rewritten prompt first, then a short list of what you applied and why, one line each. Preserve
the user's own wording and structure; the items are additions and fences, not a voice rewrite.

Diagnostic checklist:
1. **Receipt** — demands pasted evidence (exact command + output), not just "it works".
2. **Fence** — says what the worker must NOT touch, with the owner named.
3. **Green loop** — gives the exact verify command, "iterate until green", and cleanup of residue.
4. **House rules** — relays environment constraints WITH the approved workaround.
5. **Named slop** — names the failure mode to avoid, in quotes, not "high quality".
6. **Pinned contract** — shared interface pasted verbatim into every prompt ("implement EXACTLY this").
7. **Greppable privilege** — permission/tool list derivable from the worker's own tasks, both directions.
8. **Never list** — each role has explicit "never" boundaries pointing at the neighbor who owns that action.

Items 1-5 apply to any delegated task. Items 6-8 only when multiple workers coexist.

## Mode 3 (reference) — Serve the published ladder

If the user explicitly wants the patterns themselves to learn or teach, point them to the live
page (memyselfplusai.com/edge/#prompt-goodies) or serve one or two rungs VERBATIM from
references/ladder.md (never the whole ladder at once). This is now secondary; the page is the
canonical home.

## Notes
- This is an UPDATE to an existing skill, not a new one (no 14-day gate reset).
- evals/evals.json still targets the old serve/upgrade behavior and should be refreshed to
  cover Mode 1 carrot extraction.
