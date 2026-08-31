---
name: daily
description: Start the day with vault context. Read today's daily note or create one. Surface top priorities. Ask what we're working on.
---

Read today's daily note at daily/YYYY-MM-DD.md (use today's actual date).
If it doesn't exist, create it with this template:

# [Today's Date]

## Top of Mind

## Today's Focus

## Notes

Then check the inbox/ folder and list any unprocessed files found.
Read the most relevant active project or client folder for context.
Summarize the top 3 priorities for today based on recent notes.

For a fuller cross-project agenda that goes beyond recent notes (open phases, gates, queued work, stalled projects), run `/what-am-i-forgetting`. The daily note surfaces what is top of mind; `/what-am-i-forgetting` casts the wide net across all roadmaps, memory files, and project folders so nothing active is silently dropped.

## Perceptor Staleness Check

After the standup, check when Perceptor was last synced by looking at
~/projects/perceptor/.perceptor/index.json (the last_updated field).

Also check if any files in ~/vault/projects/ or ~/vault/decisions/ have
been modified more recently than the last Perceptor sync.

If vault content is newer than the last Perceptor sync by 3+ days,
add a brief note at the end:
"Vault projects have changed since last Perceptor sync — run /vault-push if needed."

Keep it to one line. Don't nag if everything is in sync.

Ask: "What are we working on today?"
