---
name: braindump
description: Rapid-fire capture of many ideas at once. Unmarked ideas become vault notes; lines explicitly prefixed goal: or task: become inert Teletraan proposals. Use for braindump, /braindump, dump these, or several half-formed ideas.
---

# Braindump — Rapid Idea Capture

Rapid-fire idea capture mode. Speed over polish.

## When triggered

Ask: "What's on your mind? Dump everything — one idea per line, or just stream of consciousness. I'll sort it."

## How to process

1. Take whatever the user gives you — bullet points, sentence fragments, half-formed thoughts
2. Create one markdown file per distinct idea in `ideas/`
3. Filename: `YYYY-MM-DD-[slug].md` (e.g., `2026-03-15-mcp-server-for-linear.md`)
4. Each file gets:

```markdown
---
captured: YYYY-MM-DD
status: raw
tags: [inferred tags]
---

# [Idea title — inferred from their words]

[Their original words, cleaned up just enough to be readable]

## Quick Take
[1-2 sentences: what this could become, who it helps, why it's interesting]
```

5. After processing all ideas, show a summary:
   - How many ideas captured
   - List of filenames created
   - Ask: "Any of these worth promoting to projects/?"

## Goal routing — explicit marker only

A dumped line that STARTS with `goal:` or `task:` (case-insensitive, prefix only —
never inferred) is runnable WORK, not an idea note. For each such line: strip the
marker and run **goal-maker** headless without questions. Submit its output as inert
proposal data with `node ~/projects/teletraan-core/src/cli/teletraan.mjs propose INPUT.json`.
Require `liveTask: false`. Do not admit, lease, dispatch, or execute during a braindump.
No `ideas/` file is written for a successfully proposed line. If proposal capture fails,
fall back to a normal `ideas/` file and say why. List proposal IDs separately from idea
files in the summary. All unmarked lines behave exactly as below.

## Rules
- Never discard anything — even bad ideas get captured
- Don't over-edit their words. Preserve voice and intent.
- If an idea clearly relates to an existing project in projects/, note that connection
- Speed matters more than formatting
