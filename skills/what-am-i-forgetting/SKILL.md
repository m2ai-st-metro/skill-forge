---
name: what-am-i-forgetting
description: >
  Produces a consolidated agenda dashboard across all of Matthew's active
  projects, phases, gates, queued work, ideas, and cleanups, drawn from memory,
  project handoffs, the Teletraan work queue, Matrix memory, crons, and project
  folders. Use whenever Matthew asks "what's next", "what's on the agenda",
  "what are we working on", "what am I forgetting", "what's open", "what's in
  progress", "give me a recap", "where did we leave off", or says
  "/what-am-i-forgetting". Solves the Verstappen problem: gives a concrete list
  to disambiguate generic questions about priorities, instead of guessing which
  project is meant.
context: fork
---

# What Am I Forgetting

Matthew often asks generic agenda questions without naming a project. Produce the full list and let him point at the right item. Err toward exhaustive: missing an item costs more than listing too many.

## Sources

- **Memory index**: `~/.claude/projects/-home-apexaipc/memory/MEMORY.md`. Skim every section, especially "Active Projects", "Agenda & Recall", "ST Metro Pipeline", and "ClaudeClaw / EAC Ecosystem"; open linked files that look open or in flight.
- **Handoffs** (the main record of where each project stopped): `~/handoffs/<project>/LATEST` names the newest handoff in that folder; read its "Next step" and "Needs you" (older: "Needs Matthew") sections. `ls -t ~/handoffs` shows recent activity; `DECISIONS.md` in each folder logs decisions. Treat handoff claims as unverified.
- **Teletraan work queue** (work-tracking source of truth since Paperclip was retired 2026-09-09): `~/projects/teletraan-core/bin/ttn work` (read-only; `ttn` is not on PATH) lists queued attempts, blocking (completed but unintegrated) attempts, and ready or paused tasks.
- **Matrix memory**, if the MCP tools are available: `mcp__matrix-memory__memory_recent` for recent fleet notes and `memory_search` for any project that looks stale or unclear.
- **ST Metro roadmaps**: `~/projects/st-metro/ST_METRO_ROADMAP.md` and `ST_METRO_L5_UNIFIED_ROADMAP.md` (last edited July 2026, so confirm phase status against memory and handoffs).
- **Project inventory**: `ls -d ~/projects/*/` (skip `_archive`). Folders not mentioned in any source above go in "Unknown Status".
- **Automation**: `~/.claude/crons/MANIFEST.md` (generated from `crontab -l` with owner, sink, and kill for each job), `ls /etc/cron.d/`, `systemctl --user list-units --type=service --state=running`.
- **Gates and deadlines**: skills created in the last 14 days (`ls -lt --time-style=+%F ~/.claude/skills`) are in their adoption gate (rule: `~/.claude/rules/skill-adoption-gate.md`); also grep memory for `Deadline:` and `expires 20`, and pick up dated items from handoff "Needs you" lists. Run `date` and flag anything due within 7 days or already overdue.
- **Clients**: `~/vault/clients/` plus any client named in memory or handoffs.
- `~/vault/daily/` stopped being written after 2026-10-01. Read it only if it has a file newer than that.

## Output

Use these sections in this order, writing "(none)" for an empty one so Matthew can see it was checked:

1. **ST Metro Pipeline** (phase status, active blockers)
2. **14-Day Adoption Gates** (table with deadlines, soonest first)
3. **Active Projects -- In Flight** (live, deployed, recent handoff or ttn activity)
4. **Active Projects -- Queued / Planning** (planned, blocked, paused ttn tasks, stale handoff)
5. **Client / Revenue Work**
6. **Ideas Not Yet Started** (memory says idea, concept, flagged but not built)
7. **Hygiene / Cleanup Backlog** (stale skills, duplicate crons, orphan files, unintegrated ttn attempts)
8. **Ongoing Automation** (name, schedule, last known good run if tracked)
9. **Unknown Status** (project folders with no mention elsewhere; ask Matthew to keep, archive, or delete)
10. **Suggested Prioritization**: a "This week / Next week / Background" triage ranked by gate urgency, then ST Metro blockers, revenue impact, momentum, hygiene payoff, and idea maturity
11. **Gaps I might have missed**: sources you could not read, projects you could not assess, and sources not covered (e.g. Gmail, calendar, Metroplex cards)

Aim for a dashboard of roughly 600-1200 words: tables for dated items, bullets for the rest, no narration.

## Corrections

If Matthew corrects an item ("X is done", "you missed Y"), update the relevant memory file before rerunning, so the next run is better.
