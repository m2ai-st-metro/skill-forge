---
name: preflight-check
description: >
  Pre-flight validation that runs before any implementation work. Scans all active
  repos for dirty state, broken tests, stale locks, missing env vars, and target
  file existence. Outputs a PREFLIGHT_REPORT.md with green/yellow/red per repo and
  a safe-to-proceed or fix-first recommendation. Use when the user says "/preflight",
  "preflight check", "pre-flight", "run preflight", or as the first step in any
  sprint skill (self-healing-claudex, etc.).
context: fork
---

# Preflight Check: Pre-Implementation Validation

Run this before any implementation work begins. It catches the problems that waste
entire sessions: wrong files, dirty repos, broken tests, stale locks.

## Phase 1: Conventions Already in Context

`/home/apexaipc/CLAUDE.md` and `/home/apexaipc/.claude/CLAUDE.md` auto-load into every
session's system prompt; project-scoped files under `/home/apexaipc/.claude/rules/`
auto-load when the session is under `projects/**`. Do not re-read all of them here —
that was a ~1,350-line re-read of content already loaded. Only Read a specific
`~/.claude/rules/*.md` file if the target task touches a topic it covers and it has not
already surfaced in context (e.g. the task touches a specific remote machine, or a topic
with an on-demand reference file not covered by auto-load).

Hold in mind from what's already loaded:
- Hard rules (things that must never happen)
- Learned mistakes (past incidents to avoid)
- Environment constraints (env vars, paths, SSH aliases)

## Phase 2: Repository Health Scan

Scan all git repos under `/home/apexaipc/projects/`. For each repo that is a git directory:

```bash
# Run these for EVERY git repo found
git -C /home/apexaipc/projects/<repo> status --porcelain 2>/dev/null
git -C /home/apexaipc/projects/<repo> log --oneline -5 2>/dev/null
```

Classify each repo:
- **GREEN**: Clean working tree, no uncommitted changes
- **YELLOW**: Uncommitted changes present (unstaged or staged) -- not blocking but notable
- **RED**: Merge conflicts, detached HEAD, or broken state

Only report repos that are YELLOW or RED in the final output. GREEN repos get a single
summary line ("N repos clean").

## Phase 3: Failure Pattern Detection

Check for these known failure patterns:

### 3a. Stale Lock Files
```bash
ls -la /tmp/*.lock 2>/dev/null
ls -la /home/apexaipc/projects/st-metro/metroplex/.lock 2>/dev/null
ls -la /home/apexaipc/projects/st-metro/ideaforge/data/*.lock 2>/dev/null
```
If any lock files exist, check their age. Locks older than 1 hour are likely stale.

**Classify each stale lock — do not emit one blanket warning (Q-20260711-0020, 2026-07-19).**
A stale lock is a symptom with three distinct causes that need three different responses.
For each lock older than 1 hour, check whether the process that made it is alive
(`kill -0 <pid>` if the lock stores a pid, else `ps`/`pgrep` for the owning pipeline) and
whether the owning job's log shows a clean finish, then classify:

| Class | Evidence | Response |
|---|---|---|
| **completed-but-unreleased** | Owner's log shows a successful finish AFTER the lock mtime | Safe to remove; note the release bug |
| **crashed** | No owning process alive, log ends mid-run or with an error | Remove lock, flag the crash as its own finding (the crash, not the lock, is the story) |
| **legitimately-held** | Owning process is ALIVE (long build, active mission) | Do NOT remove; report as held and wait |

A stale lock is NOT itself evidence of a crash (learned 7-09: a stale lock after a
successful run is a release bug, not a failure). Never delete a lock without the
liveness check.

### 3b. WAL Files (SQLite)
```bash
find /home/apexaipc/projects -name "*.db-wal" -size +0c 2>/dev/null
```
Non-empty WAL files indicate uncommitted SQLite transactions or crashed processes.

### 3c. Environment Variables
Source `~/.env.shared` and verify these critical keys are set (non-empty):
- `ANTHROPIC_API_KEY` (note: may be intentionally disabled -- check memory)
- `GOOGLE_API_KEY`
- `GITHUB_TOKEN`
- `PORTAINER_USER` and `PORTAINER_PASS`

Report missing keys as YELLOW (not RED) since some may be intentionally unset.

### 3d. Broken Test Suites
If the user's task targets a specific project, run that project's test suite:
```bash
# Python projects (subshell, not bare cd -- Bash tool blocks a leaking cd):
(cd /home/apexaipc/projects/<target> && source venv/bin/activate 2>/dev/null && pytest tests/ --tb=line -q 2>&1 | tail -10)
# TypeScript projects:
npm test --prefix /home/apexaipc/projects/<target> 2>&1 | tail -10
```
Only run tests for the TARGET project(s), not all repos. Testing all repos would take
too long. If no specific target, skip this step and note "test check skipped -- no target specified".

### 3e. Running Processes
```bash
# Check for zombie Claude Code sessions or stuck builds
ps aux | grep -E "(claude|yce|metroplex|ideaforge)" | grep -v grep | head -10
```
Report any unexpected long-running processes that might conflict.

### 3f. Unity .meta / GUID Drift (Unity repos only — Q-20260714-0002, 2026-07-19)

Run ONLY when the target repo is a Unity project (has `Assets/` AND `ProjectSettings/`):

```bash
# 1. Uncommitted .meta churn (GUID drift in flight — the Bootstrap missing-script class)
git -C <repo> status --short | grep '\.meta' | head -20
# 2. Assets missing their .meta sibling (Unity will mint a NEW GUID -> scene links break)
(cd <repo>/Assets && find . -type f ! -name '*.meta' | while read f; do [ -f "$f.meta" ] || echo "MISSING META: $f"; done | head -20)
# 3. Orphan .meta files (asset deleted, meta left -> noise + churn on next editor open)
(cd <repo>/Assets && find . -name '*.meta' | while read m; do [ -e "${m%.meta}" ] || echo "ORPHAN META: $m"; done | head -20)
```

Any MISSING META is **RED** for scene-referencing work: an untracked GUID will be
regenerated and silently sever scene links (root cause of the 7-13 Bootstrap
missing-script bug; headless tests attach components programmatically and are BLIND
to this class — preflight is the detector, not the test suite). Uncommitted `.meta`
churn is YELLOW: commit them before any build/PR (freeze GUIDs). Orphan metas are
YELLOW cleanup.

## Phase 4: Target Verification

If the user's task mentions specific files, directories, or repos:

1. Verify each path exists using `ls` or `test -e`
2. For files: confirm they are readable and non-empty
3. For repos: confirm they have the expected structure (CLAUDE.md, src/, tests/, etc.)
4. For branches: confirm the expected branch exists with `git branch -a`

This prevents the #1 session-waster: planning changes to files that don't exist or
have been moved.

If no specific targets mentioned, skip this phase.

## Phase 5: Generate Report

Write the report to `/tmp/PREFLIGHT_REPORT.md` with this structure:

```markdown
# Preflight Report
**Date**: {YYYY-MM-DD HH:MM}
**Target**: {what the user plans to work on, or "general check"}

## Summary
**Verdict**: SAFE TO PROCEED / FIX FIRST / PROCEED WITH CAUTION

## Repository Status
- {N} repos clean
- {list YELLOW repos with details}
- {list RED repos with details}

## Failure Patterns
| Check | Status | Details |
|-------|--------|---------|
| Stale locks | G/Y/R | {details} |
| WAL files | G/Y/R | {details} |
| Env vars | G/Y/R | {missing keys} |
| Tests | G/Y/R/SKIP | {pass/fail count} |
| Processes | G/Y/R | {conflicts} |

## Target Verification
| Path | Exists | Notes |
|------|--------|-------|
| {path} | Y/N | {details} |

## Recommendations
{If any RED: list specific fix commands}
{If any YELLOW: list what to watch for}
{If all GREEN: "No blockers detected. Safe to proceed."}
```

## Phase 6: Act on Results

After generating the report:

- **All GREEN**: Print a one-line summary and proceed. Do not make the user read a full report for a clean check.
- **YELLOW only**: Print the summary table. Note the cautions. Proceed unless the user says otherwise.
- **Any RED**: Print the full report. Propose specific fix commands for each RED item. Do NOT proceed with the main task until the user acknowledges or the fixes are applied.

## Integration with Sprint Skills

When called as the first step of another skill (e.g., self-healing-claudex), pass the
verdict forward. If RED, halt the sprint and report. If GREEN/YELLOW, continue to the
next skill step.

To invoke from another skill's prompt:
```
Before starting implementation, run the preflight check skill (/preflight) targeting
the project directories involved in this sprint.
```

## What This Does NOT Do

- Does not modify any files (read-only scan)
- Does not commit, push, or change git state
- Does not run destructive commands
- Does not check remote services (NAS, AlienPC) unless the task involves them
- Does not run full test suites across all repos (only targeted)
