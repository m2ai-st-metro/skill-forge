---
name: tldr
description: Save a summary of this conversation to the vault. Key decisions, things to remember, next actions. Store in the right folder automatically.
---

Summarize this conversation:
1. What was decided or figured out
2. Key things to remember
3. Next actions (if any)

Format as a clean markdown note with today's date in the title.
Save to the most relevant folder based on the topic discussed.
- Client work → clients/[name]/ or projects/[name]/
- Research → research/
- General → daily/ with today's date

## Vault memory.md (gated: most sessions write nothing)

Update `~/vault/memory.md` ONLY if a durable pattern or preference actually
emerged this session. Most sessions produce none. Writing "no new patterns
this session" is the correct and common outcome. Skip the file entirely,
do not write a placeholder entry.

A candidate qualifies only if all three hold:

1. **It would change how a future session behaves.** A fact you looked up,
   a summary of what happened, or a one-off decision is not a pattern.
   It belongs in the daily note, which you already wrote.
2. **There is evidence in THIS session.** Point at the moment it showed up:
   a correction, a repeated failure, a preference stated out loud. A
   plausible-sounding generalization with no moment behind it does not count.
3. **It is not already recorded.** Check `~/vault/memory.md` for an existing
   entry covering it. If one exists and is now wrong or incomplete, UPDATE
   that entry rather than appending a second one.

This is the same bar the global auto-memory uses. Vault `memory.md` does not
load at session start, so a weak entry costs nothing per session, but it
still costs you later, when you go looking and find noise instead of signal.

## Vault log.md entry (Karpathy LLM Wiki pattern)

After the daily note is saved, append one entry to `~/vault/log.md` using
this exact format so `grep "^## \\["` produces a clean timeline:

```
## [YYYY-MM-DD] ingest | <short session title>
One-line summary of what happened or what was decided. Link to the full
note using Obsidian wikilink syntax: [[daily/YYYY-MM-DD-topic-slug]].
```

Operation type is almost always `ingest` for /tldr sessions. Use `query`
only if the session was purely asking the vault questions (no new content
filed). Use `lint` only if the session was a health check over existing
vault content.

If the session touched a topic that has a dedicated `~/vault/wiki/<topic>/`
folder, ALSO append the same entry to that topic's `wiki/<topic>/log.md`
and update `wiki/<topic>/index.md` if new entity/concept pages were created.
If no matching topic wiki exists, the vault-root `log.md` entry is sufficient.

### Rotate log.md at 150 KB (do not let it grow unbounded)

`log.md` is append-only and nothing was trimming it. By 2026-08-22 it had reached
**239 KB / 359 entries** and had to be split by hand (entries before 2026-07-01 moved to
`log-archive-2026H1.md`, leaving 74 KB / 139 entries).

**Before appending, check the size.** If `log.md` exceeds ~150 KB:

1. Split entries older than the current half-year into
   `~/vault/log-archive-<YYYY><H1|H2>.md`.
2. Give the archive the same `## [YYYY-MM-DD]` format so the grep timeline still works
   across both files.
3. Add a pointer line to `log.md`'s preamble naming the archive and its entry count.
4. **Verify by entry count and byte total, not by eyeballing it.** Entries in `log.md` are
   NOT strictly chronological (32 out-of-order transitions as of the 2026-08-22 split), so
   a naive "everything above line N" cut silently drops or duplicates entries. Filter by
   each entry's own parsed date, then assert `len(archived) + len(kept) == len(original)`
   and that byte totals match.

`memory-archive-2026.md` (the 2026-06-26 `memory.md` split) is the precedent for the
naming and the pointer-line convention.

### memory.md is a CURATION problem, not a rotation problem

Do not rotate `memory.md` to fix its size. As of 2026-08-22 it is 460 KB and holds ~199
dated session entries against exactly one curated section (`## My Preferences`). That is a
direct violation of this skill's own gate above: memory.md is for durable patterns and
preferences, and a session summary is not one. Rotating it would just archive the symptom.

If it is over ~200 KB, the correct response is to say so and ask whether to prune, not to
split it automatically.

## Perceptor sync (retired 2026-08-29)

/tldr no longer auto-syncs the note to Perceptor (OS self-review decision; the PostToolUse
reminder hook was removed the same day). The Perceptor MCP and its contexts remain available
for on-demand `perceptor_save` when Matthew asks.
