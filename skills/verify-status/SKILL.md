---
name: verify-status
description: Establish live ground truth before any planning or resume work
---

Do NOT read memory.md, handoff notes, or prior session summaries as fact.

1. Run live checks for the current project (git log/status, gh issue list, running services, cron).
2. Build a table: Claim | Source | Verified? | Evidence command | Actual value.
3. Explicitly list anything you could NOT verify.
4. Only after the table is complete, propose next steps.

Every number you state must come from a command run in THIS session.
