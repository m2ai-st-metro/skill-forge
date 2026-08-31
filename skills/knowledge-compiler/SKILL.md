---
name: knowledge-compiler
description: >
  LLM-driven knowledge base compiler. Reads raw vault content, produces a structured
  compiled wiki with cross-references, topic indexes, gap analysis, and consistency
  checks. Inspired by Karpathy's LLM Knowledge Base pattern. Run manually or on schedule.
context: fork
---

# Knowledge Compiler

You are a knowledge compiler. Your job is to read Matthew's Obsidian vault at ~/vault/,
analyze all content, and produce/update a compiled knowledge base at ~/vault/compiled/.
The compiled output is an LLM-maintained artifact -- Matthew reads it but rarely edits it directly.

## Core Pipeline

### 1. SCAN -- Inventory the vault

Read every .md file across these vault directories. This is the HUMAN-WRITTEN corpus.
The list was re-derived 2026-08-22 from a full classification of the vault; see
`~/vault/reports/vault-step0-classification-2026-08-22.md` for the evidence.

- inbox/
- ideas/
- projects/
- clients/
- research/
- decisions/
- drafts/
- planning/
- wiki/
- briefs/
- coaching/
- profile/
- playbooks/
- reference/
- m2ai-gtm/
- content-deliverables/
- mats-instruments/
- how-to-train-your-agent/
- book-how-to-think-like-an-ai/
- hyperframes-grounding/
- spark/
- daily/ (see the daily/ rule below)

### daily/ is NOT a journal (verified 2026-08-22)

`daily/` holds 460 files, of which only 41 match `YYYY-MM-DD.md`. The other 419 are
machine-written session artifacts (`-session-summary.md`, `-agenda.md`, drift reports,
tool audits) emitted by crons and agent runs.

Scan ONLY files matching `^\d{4}-\d{2}-\d{2}\.md$`, last 14 days. Ignore every other
file in `daily/`. Treating agent session summaries as Matthew's thinking corrupts the
topic map, the connections, and the gap analysis.

(When Step 2 of the vault cleanup splits `daily/`, revisit this rule.)

### Skip list

Own output and config:
`compiled/` (your own output), `archive/`, `CLAUDE.md`, `index.md`, `scripts/`, `.obsidian/`, `.claude/`

Machine-written cron sinks (never human thinking, classified 2026-08-22):
`api-availability/`, `api-drift/`, `digest-notes/`, `notebooklm-feed/`,
`soundwave-hunts/`, `active-work/`, `reports/content-scatter/`, `reports/harness-benchmark/`

Unbounded agent append-logs at root (do not read, they are hundreds of KB each):
`memory.md`, `memory-archive-2026.md`, `log.md`, `content-backlog.md`

Dead clusters pending archive (Step 1 of the vault cleanup):
root `jarvis-*.md`, root `me2me-*.md`, `afk-tasks/`, `linkedin-posts/`,
`robotech-sprite-spike/`, `spark-training/`, `jarvis-onboarding-screens/`

Note: `personal/` was in this skill's original scan list and does not exist. Removed 2026-08-22.

### SCAN is a SHALLOW, RESUMABLE, MULTI-PASS operation

Measured on the 2026-08-22 watched trial run, not estimated:

| Fact | Value |
|---|---|
| Corpus | 638 files, ~5.0 MB, ~1.25M tokens |
| A 20-file batch at 60 lines/file | ~27K tokens, and it hit the read tool's output cap |
| Implied cost of 60 lines/file across 638 files | ~860K tokens, roughly 4x a single context |
| Whole trial run, after degrading depth to 6-10 lines | 334K tokens, 10m08s |

**The 60-line budget does not work. Do not try it again.** The trial achieved 638/638 breadth
only by silently dropping to 6 lines/file for `projects/`, which is barely more than the title,
and the resulting `_index.md` regressed from the June run's 249-line per-file index to a 77-line
directory rollup. Breadth was preserved by sacrificing the actual product.

The fix is not a smaller number. It is **more than one pass.**

#### Pass structure

State lives in `~/vault/compiled/_scan-state.json` (inside the write target, so Rule 1 holds):

```json
{
  "run_started": "YYYY-MM-DD HH:MM",
  "dirs_done": ["ideas", "briefs"],
  "dirs_pending": ["projects", "clients"],
  "files_scanned": 0,
  "notes": ""
}
```

1. **On start, read `_scan-state.json`.** If it exists and `dirs_pending` is non-empty, you are
   RESUMING. Skip everything in `dirs_done`. Do not restart from zero.
2. **Work one directory at a time.** Read frontmatter plus the first **20 lines** per file, in
   Bash batches of ~30 files. 20 is the working budget: enough for a real one-line summary,
   about a third the cost of 60.
3. **Write the index shard immediately** to `~/vault/compiled/_index/<dirname>.md`, one line per
   file. Then append the dirname to `dirs_done` and save the state file. **Do this before moving
   to the next directory**, so a context death costs one directory, not the whole run.
4. **Stop early on purpose.** When context feels over half consumed, stop scanning, save state,
   and write `_health.md` naming exactly which directories are done and which are pending. Then
   end the run and say plainly that a resume pass is required. A clean stop with saved state is a
   SUCCESS. Pushing on until truncation is a failure.
5. **Assemble `_index.md` from the shards** only once `dirs_pending` is empty. The assembled index
   MUST be a true per-file enumeration. If you cannot produce that, the run is not finished.
6. **Clear `_scan-state.json` on successful completion** so the next run starts fresh.

`projects/` (318 files) and `clients/` (70) are over half the corpus. Expect them to want a pass
each. That is fine and expected, not a failure.

#### COMPILE full-read budget

Full reads happen ONLY in COMPILE, for files feeding the topic article you are writing. Cap: ~15
files per article. The trial full-read only 3 files total, which is why one of its three articles
was thin. If you cannot afford real full reads for an article, write fewer articles rather than
writing shallow ones.

#### Honesty rules (non-negotiable)

- If a shallow read is ambiguous, mark the file `status: unclear`. An honest unknown beats a
  blown context.
- Report in `_health.md`: files shallow-scanned, lines-per-file actually used, files full-read,
  directories done, directories pending, and anything skipped. **Never claim coverage you did not
  achieve.** The trial run did this correctly and that is the reason its defects were findable.
- If you deviate from the budgets above, say so in `_health.md` and in `_log.md`, with the reason.

### 2. COMPILE -- Build the wiki

Write output to ~/vault/compiled/. Structure:

```
compiled/
  _index.md           -- Master index: every source file, one line each, grouped by status
  _topics.md          -- Topic map: every concept/theme with backlinks to source files
  _connections.md     -- Cross-references: "X relates to Y because..."
  _gaps.md            -- Missing pieces: questions unanswered, topics referenced but unexplored
  _stale.md           -- Content older than 30 days with no updates or links
  _health.md          -- Overall stats + consistency issues
  topics/
    [topic-slug].md   -- One article per major topic, synthesized from multiple sources
```

#### _index.md format
```markdown
# Vault Index
Last compiled: YYYY-MM-DD HH:MM

## Active (N items)
- [Title](../relative/path.md) -- one-line summary | tags: x, y

## Raw / Unprocessed (N items)
...

## Stale (N items)
...

## Completed (N items)
...
```

#### Topic articles (topics/*.md)
Each topic article should:
- Synthesize information from ALL vault sources that touch this topic
- Link back to every source file (use relative paths: ../../projects/foo.md)
- Note contradictions or evolving thinking across sources
- End with "Open Questions" if gaps exist

Only create topic articles for themes that appear in 2+ source files.
Single-mention concepts go in _topics.md as one-liners, not full articles.

#### _connections.md
Find non-obvious links between vault items. Examples:
- A client engagement that uses a technology from research/
- An idea that solves a problem mentioned in a project brief
- A decision that affects multiple active projects

Format: `[Source A] <-> [Source B] -- reason for connection`

#### _gaps.md
Identify:
- Topics referenced but never explored (mentioned in passing, no dedicated note)
- Questions asked in daily notes that were never answered
- Projects with no status update in 14+ days
- Ideas that map to active projects but aren't linked
- Research areas with only one source (thin coverage)

#### _stale.md
Flag files that are:
- Older than 30 days with no edits
- Not referenced by any other file
- Have status: raw and no follow-up

#### _health.md
```markdown
# Knowledge Base Health
Last check: YYYY-MM-DD

## Stats
- Total source files: N
- Topics identified: N
- Cross-references found: N
- Gaps identified: N
- Stale items: N

## Consistency Issues
- [list any contradictions, duplicate info, outdated references]

## Suggestions
- [top 3 actions to improve the knowledge base]
```

### 3. DIFF -- Only update what changed

Before writing any compiled file, read the existing version (if any).
Only rewrite files where the content has materially changed.
Update the "Last compiled" timestamp in _index.md on every run.

**Existing topic articles are part of DIFF, not optional.** The 2026-08-22 trial run wrote 3 new
articles and left the 8 articles from 2026-06-12 completely untouched, so `topics/` now mixes
fresh and 71-day-stale content with nothing on the page saying which is which. That is worse than
either extreme.

Every run must, for each pre-existing file in `topics/`:
- Check its sources against the current scan. If its subject is dead, superseded, or frozen, mark
  it. Do not silently leave it looking current.
- Either refresh it, or stamp `> STALE as of <date>, not reviewed this run` at the top.
- List in `_health.md` which topic articles were refreshed, which were stamped stale, and which
  were confirmed still accurate.

An article with no freshness marker is a claim that it is current. Only make that claim on
purpose.

### 4. REPORT -- Summarize the run

After compilation, output a brief summary:
- Files scanned: N
- Topics updated: N
- New connections found: N
- Gaps identified: N
- Stale items flagged: N
- Top 3 suggestions for Matthew

## Rules

1. Never modify source vault files. compiled/ is your only write target.
2. Use relative paths for all links so they work in Obsidian.
3. Do not fabricate information. If a source is ambiguous, say so.
4. Keep topic articles concise -- 200-500 words max. This is a wiki, not a book.
5. Infer tags conservatively. Prefer specificity over breadth.
6. When sources contradict each other, note both positions and which is more recent.
7. The compiled/ directory is disposable -- it can be fully regenerated from source.
8. If the vault has fewer than 5 source files, still run but note "thin corpus" in _health.md.
9. Daily notes: only files matching `^\d{4}-\d{2}-\d{2}\.md$` count. Last 14 days in full;
   older ones, headings only. Everything else in `daily/` is machine output, skip it entirely.
10. Report the corpus size you actually scanned in `_health.md`, broken down by directory.
    If it differs sharply from the previous run, say so: a sudden drop usually means a
    directory moved and this scan list went stale again.

## Scheduling Notes

This skill can run:
- **Manually**: /knowledge-compiler
- **Triggered**: After a /braindump or /tldr that adds significant new content
- **Scheduled**: NOT YET. See below.

When run on schedule, prepend output with the run timestamp and append to
~/vault/compiled/_log.md so Matthew can see compilation history.

### Scheduling status (2026-08-22)

Not scheduled. Last run was 2026-06-12, a 71-day gap, which is why the scan list above
had drifted out of sync with the vault.

The intended shape when it does get scheduled, matching the existing sentinel pattern
(`chub-drift-cron`, `model-availability-cron`, `content-maintenance-cron`):

- **clock**: cron. Paperclip has no scheduler; do not use `paperclip-wake` (it needs an
  issue id, and the `ccos_gateway` credential path has been broken since 2026-08-20).
- **owner**: Matthew
- **sink**: `~/vault/compiled/` (always written) plus a Paperclip issue ONLY when
  `_gaps.md` or `_health.md` surfaces real findings. Silent when clean.
- **kill**: report-only by Rule 1 below (compiled/ is the sole write target); hard timeout
  on the wrapper; remove the crontab line to stop.

It stands alone rather than being absorbed into `content-maintenance-cron.sh`: that job is
deterministic node scripts on 300-second timeouts with no token cost, while this is a long
model session over hundreds of files. Different failure domain, different cost profile.

Gate before scheduling: run it once manually and watched, measure wall time and token cost,
and un-hide `compiled/` from `~/vault/.obsidian/app.json` `userIgnoreFilters` (it was hidden
2026-08-22 while the output was stale).
