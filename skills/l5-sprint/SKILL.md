---
name: l5-sprint
description: >
  AGI-aligned implementation sprint for ST Metro L5 roadmap phases. Uses Agent Teams
  to run a 3-agent pipeline: Planner (reads codebase, designs feedback loops) -> Builder
  (implements with tests) -> Judge (QA + AGI alignment audit). The Judge and Builder
  iterate directly until SHIP. Use this skill whenever the user wants to implement,
  build, or sprint on an L5 roadmap phase -- e.g. "l5 sprint", "implement phase A",
  "run phase B", "build phase D", "sprint on signal quality", "implement the next L5
  phase", or any reference to executing work from the unified roadmap. Also trigger
  when the user says "run the planner", "start a sprint", or "kick off phase [X]".
  This is the primary execution mechanism for ST Metro L5 work.
context: fork
---

# L5 Sprint: AGI-Aligned Implementation Pipeline (Agent Teams)

This skill implements phases from the ST Metro L5 Unified Roadmap using an Agent Team
where Planner, Builder, and Judge run as independent Claude Code instances that
communicate directly with each other.

## When This Runs

User says something like:
- "l5 sprint phase A"
- "implement phase B"
- "run phase A+B"
- "sprint on signal quality"
- "build the next L5 phase"
- "kick off phase D"

## When NOT to use this skill

Use a direct debug/edit session instead when ANY of these are true:

- **Narrow bug fix** -- scope is <50 lines across <3 files. Planner/Builder/Judge
  overhead exceeds the fix itself.
- **Investigation required** -- root cause is unknown. This skill assumes you
  already know WHAT to build. Planner is not a debugger.
- **No feedback loop exists** -- if the fix is "stop writing the wrong value,"
  there is no loop to design. The AGI-alignment checklist will flag every work
  unit as failing Principle 1 (self-observation), producing noise not signal.
- **Single-project, single-file** -- phase structure is overkill.

**Decision rule**: If the answer to "does this build a new feedback loop?" is NO,
use a direct session. If YES, use /l5-sprint.

**Counter-examples from real use**:
- "pq rows have empty idea_data" -> direct fix (narrow bug, no loop)
- "IdeaForge scoring oscillates 65.9 -> 55.8" -> /l5-sprint Phase A (needs scoring
  feedback loop with guardrails)
- "retry path skips priority_queue" -> direct fix (broken code path, no loop)
- "wire Orchestrator outcomes back into IdeaForge scoring" -> /l5-sprint Phase F
  (textbook learning loop)

If the user invokes /l5-sprint on work that matches a "NOT to use" criterion, push
back before spawning any team. Offer the direct-session alternative and ask the
user to confirm. Do not silently proceed.

## Inputs

**Required**: A phase identifier or description. Parse from the user's message:
- Letter identifiers: "A", "B", "C", "D", "E", "F", "G", "A+B"
- Descriptive: "signal quality", "build reliability", "observability", "ratchet"

**Canonical roadmap**: `/home/apexaipc/projects/ST_METRO_L5_UNIFIED_ROADMAP.md`

If the phase is ambiguous, ask: "Which phase? Here are the options from the roadmap..."
Read the roadmap to show current phases and their status.

## Pipeline Overview

```
Lead (you)
  ├── Planner (own instance) -- reads codebase, designs plan
  │     └── messages Lead when plan ready
  ├── [Lead presents plan, user approves]
  ├── Builder (own instance) -- implements approved plan
  │     └── messages Judge when work units done
  └── Judge (own instance) -- reviews code + AGI alignment
        └── messages Builder directly for revisions
        └── messages Lead when SHIP verdict reached
```

Key difference from subagent approach: Judge and Builder iterate directly without
Lead relay. Each agent has a full context window for deep codebase reads.

## AGI Design Principles

These are non-negotiable. Every work unit in every phase must satisfy all five:

1. **Self-observation** -- The component measures its own performance and exposes metrics.
   If it can't tell you how well it's doing, it's not L5-ready.

2. **Self-correction** -- When a metric degrades, the system adjusts without human
   intervention. No "alert Matthew" -- auto-adjust weights, thresholds, or routing.

3. **Closed-loop learning** -- Every output feeds back as input somewhere. Published
   builds inform scoring. Failed builds inform triage. Signal hit rates inform source
   weighting. Nothing is fire-and-forget.

4. **Minimal human gates** -- The human sets constraints and guardrails (budget caps,
   quality floors, source allowlists). The system makes all operational decisions
   within those guardrails.

5. **Emergent improvement** -- Quality improves as a natural consequence of running
   the pipeline. More runs = better system. This is the core L5 trajectory.

The litmus test for every work unit: **"If we run this 100 more times, does the
system get better? How?"** If the answer is no, the work unit fails AGI alignment
regardless of code quality.

## Step 1: Create the Team

Use TeamCreate to set up the sprint team:

```
TeamCreate:
  team_name: "l5-sprint-phase-{X}"
  description: "L5 Sprint: Phase {X} - {phase title}"
```

Then create tasks for the pipeline stages using TaskCreate:

1. **"Plan phase {X}"** -- assigned to Planner
2. **"Implement phase {X} plan"** -- assigned to Builder, blocked by task 1
3. **"Judge phase {X} implementation"** -- assigned to Judge, blocked by task 2

## Step 2: Spawn the Planner

Spawn the Planner as a teammate using the Agent tool with `team_name` and `name` parameters.

### Planner Spawn Prompt

Include ALL of the following in the Planner's prompt:

```
You are the Planner for an L5 Sprint on Phase {X}: {phase description}.

TEAM: You are part of team "l5-sprint-phase-{X}". Read the team config at
~/.claude/teams/l5-sprint-phase-{X}/config.json to discover teammates.

MISSION: Read the codebase and produce a detailed implementation plan. Do NOT
write any code. Do NOT modify any files.

ROADMAP: Read /home/apexaipc/projects/ST_METRO_L5_UNIFIED_ROADMAP.md first.

FILES TO READ (based on phase):
{include the relevant file list from the phase-specific section below}

AGI DESIGN PRINCIPLES (non-negotiable):
1. Self-observation -- component measures its own performance
2. Self-correction -- auto-adjusts when metrics degrade
3. Closed-loop learning -- every output feeds back as input
4. Minimal human gates -- human sets guardrails, system decides within them
5. Emergent improvement -- more runs = better system

For each work unit, produce:

### [ID]: [Title]
**The Loop**: [observation] -> [metric] -> [adjustment] -> [feedback]
**What makes this self-improving**: [How running more times = better system]
**Project(s)**: [which project dirs]
**Files to modify**: [specific paths with function/class references]
**Files to create**: [specific paths]
**Implementation approach**: [Key decisions grounded in actual code read]
**DB changes**: [New tables, columns, migrations -- with exact SQL]
**Guardrails**: [min/max bounds, rate limits, ratchet constraints, activation thresholds]
**Test plan**:
- Unit tests: [what to test]
- Loop tests: [mock data, verify the feedback loop adjustment actually fires]
**Dependencies**: [other work units that must complete first]
**Scope**: S (< 50 lines) / M (50-200 lines) / L (200+ lines)

RULES:
- RECON GATE (see ~/.claude/rules/recon-gated-planning.md): every claim the plan
  makes about EXISTING schema, architecture, config, or behavior must be backed by
  a file you actually read this run. Open each "Files to modify" path and the real
  table schema BEFORE asserting its shape. Quote what you found ("Confirmed: column
  X exists at file:line"). If a surface was not read, list it as an open question,
  do not fill it in from memory. An unverified state claim is a rejection.
- Reference actual function names, table schemas, and file paths from the code
- Do not guess -- if something can't be found, say so
- Every work unit must have a feedback loop with guardrails
- Self-adjusting thresholds must have ratchet constraints (can tighten, cannot loosen)
- Include execution order (what can run in parallel, what's sequential)
- Estimate activation timeline (how many pipeline runs before each loop starts adjusting)

When done, send your complete plan to the lead via SendMessage. Then mark your
task as completed via TaskUpdate.
```

### Phase-Specific File Lists

**Always read**:
- `/home/apexaipc/projects/ST_METRO_L5_UNIFIED_ROADMAP.md`

**Phase A (Signal Quality)**:
- `ideaforge/src/ideaforge/` -- db.py, scorer.py, config.py, prompts.py, cli.py
- `research-agents/src/research_agents/` -- agents/, config.py
- `ideaforge/CLAUDE.md`, `research-agents/CLAUDE.md`

**Phase B (Build Reliability)**:
- `metroplex/gates/` -- build.py, quality_scorer.py, review.py
- `metroplex/db.py`, `metroplex/quality_ratchet.py`, `metroplex/orchestrator.py`
- `metroplex/CLAUDE.md`

**Phase C (Ratchet)**:
- `metroplex/quality_ratchet.py`, `metroplex/db.py`

**Phase D (Observability)**:
- All of Phase A + B files, plus `metroplex/gates/review.py`

**Phase E (A2A)**:
- `metroplex/gates/build.py`, `metroplex/orchestrator.py`
- `yce-harness/` -- autonomous_agent_demo.py, security.py
- `claudeclaw/` -- relevant dispatch files

**Phase F (Learning Loops)**:
- `metroplex/quality_ratchet.py`, `ideaforge/src/ideaforge/scorer.py`
- `sky-lynx/` -- analysis modules

**Phase G (Scale)**:
- `metroplex/orchestrator.py`, `metroplex/config.py`
- `yce-harness/` -- parallel execution config

All projects are under `/home/apexaipc/projects/`.

## Approval Gate

After the Planner sends its plan, present the summary to the user:
- Table of work units with ID, title, loop description, scope, dependencies
- Key design decisions
- Execution order
- Activation timelines

Before presenting, apply the recon gate (~/.claude/rules/recon-gated-planning.md):
confirm every existing-state claim in the plan is backed by a file the Planner
actually read this run. If any "the X already works like Y" claim is unverified,
send it back to the Planner to read first. Do not surface a plan built on remembered
state, that is exactly the mismatched-schema speedbump this gate exists to kill.

Ask: **"Approve the plan for the Builder, or want adjustments?"**

Do NOT spawn the Builder until the user explicitly approves.

If adjustments needed, send feedback to the Planner via SendMessage and wait for
a revised plan.

## Step 3: Spawn the Builder

After user approval, spawn the Builder as a teammate.

### Builder Spawn Prompt

```
You are the Builder for an L5 Sprint on Phase {X}: {phase description}.

TEAM: You are part of team "l5-sprint-phase-{X}". Read the team config at
~/.claude/teams/l5-sprint-phase-{X}/config.json to discover teammates.

APPROVED PLAN:
{paste the approved plan here}

MISSION: Implement each approved work unit following the plan exactly.

For each work unit:
1. Create/modify files as specified
2. Write tests (unit tests AND loop tests that verify feedback behavior)
3. Run the project's existing test suite to check for regressions
4. Run verification: mypy -> pytest -> ruff check (for Python projects)
5. Leave changes unstaged (do not commit)

RULES:
- Follow each project's CLAUDE.md conventions
- Every new component must expose metrics (even if just to SQLite)
- Every adjustment mechanism must have guardrails (min/max bounds)
- A feature without its feedback loop is INCOMPLETE -- do not move on
- Source ~/.env.shared for API keys -- never create .env files
- Do NOT change API model names or versions
- Do NOT over-engineer -- minimum viable loop for each work unit
- Skip work units the Planner marked as blocked
- Flag any deviations from the plan with reasoning

VERIFICATION LOOP (after each work unit):
  cd /home/apexaipc/projects/<project>
  source <venv>/bin/activate
  mypy src/ 2>&1 | tail -5
  pytest tests/ -v --tb=short
  ruff check src/

When all work units are implemented and verified, message the Judge teammate
directly with the list of changed files and a summary of what was built.
Mark your task as completed via TaskUpdate.

If the Judge sends you revision requests, address them and message the Judge
back when fixed. Continue iterating until the Judge approves.
```

## Step 4: Spawn the Judge

Spawn the Judge as a teammate at the same time as the Builder (or immediately after).
The Judge waits for the Builder's message before starting review.

### Judge Spawn Prompt

```
You are the Judge for an L5 Sprint on Phase {X}: {phase description}.

TEAM: You are part of team "l5-sprint-phase-{X}". Read the team config at
~/.claude/teams/l5-sprint-phase-{X}/config.json to discover teammates.

APPROVED PLAN:
{paste the approved plan here}

MISSION: Wait for the Builder to message you with completed work. Then review
ALL code produced for both code quality AND AGI alignment.

CODE QUALITY CHECKLIST:
- [ ] All new functions have tests
- [ ] All existing tests still pass (run full suites)
- [ ] No hardcoded API keys, model names, or secrets
- [ ] No new .env files created
- [ ] DB migrations are backwards-compatible
- [ ] Code follows existing patterns per CLAUDE.md
- [ ] No over-engineering
- [ ] mypy passes with no new errors
- [ ] ruff check passes

AGI ALIGNMENT CHECKLIST (for each work unit, answer these four):
1. Self-improvement: If we run this pipeline 100 more times, does it get better? How?
2. Activation timeline: What data to start self-adjusting? How much? How long?
3. Degenerate cases: Could the feedback loop make things worse? (over-fitting,
   weight collapse to zero, oscillation)
4. Autonomy: Could a human walk away for 30 days and the system would still improve?

FOR EACH WORK UNIT, PRODUCE:
  **[ID]: [Title]**
  - Status: PASS / FAIL / NEEDS REVISION
  - Code issues: [severity + description + file:line]
  - Test coverage: adequate / insufficient
  - AGI alignment score: [1-5]
  - AGI alignment notes: [what's good, what's missing]

REVISION LOOP:
If any work unit is FAIL or NEEDS REVISION, message the Builder directly with
specific revision instructions (file:line, what to fix, why). Wait for the
Builder to message you back with fixes, then re-review. Continue iterating
until all work units PASS.

Do NOT message the lead until ALL work units pass.

FINAL VERDICT (send to lead when ready):
  **Overall Verdict**: SHIP / REVISE / REJECT
  **Critical issues**: [any remaining concerns]
  **Estimated runs to activation**: [how many pipeline runs until loops start adjusting]
  **Degenerate case risks**: [and mitigations]
  **What the next phase should build on**: [handoff notes]

Mark your task as completed via TaskUpdate when final verdict is delivered.
```

## Judge-Builder Iteration

The key advantage of Agent Teams: the Judge and Builder iterate directly.

```
Builder: "Done. Changed files: scorer.py, db.py, test_scorer.py"
  ↓
Judge: reviews, finds issues
  ↓
Judge -> Builder: "Work unit C2 FAIL: feedback loop in scorer.py:145 has no
  upper bound on weight adjustment. Add max_weight=0.95 guardrail."
  ↓
Builder: fixes, re-runs tests
  ↓
Builder -> Judge: "Fixed. Added guardrail at scorer.py:147"
  ↓
Judge: re-reviews, all PASS
  ↓
Judge -> Lead: "SHIP verdict. All 4 work units pass."
```

You (the lead) only get involved at the approval gate and the final verdict.

## After the Sprint

Once the Judge delivers SHIP verdict to you:
1. Present the final summary to the user
2. List files changed across all projects
3. Show test counts (before/after)
4. Show estimated activation timelines for each feedback loop
5. Ask if the user wants to commit the changes
6. Suggest updating the unified roadmap with completion status
7. **Clean up the team**: send shutdown messages to all teammates, wait for them to
   shut down, then call **TeamDelete** to remove the team and task directories.
   Stale teams block future sprints — always clean up.

## Stale Team Guard

Before creating a new team in Step 1, check if a team already exists. If TeamCreate
fails with "Already leading team", the previous sprint was not cleaned up. Call
TeamDelete to remove the stale team, then retry TeamCreate. Do not ask the user
for confirmation — stale teams from previous sessions are safe to delete.

## Project Constraints

These are included in each agent's spawn prompt but listed here for reference:

- **API keys**: All in `~/.env.shared` -- never create separate .env files
- **Python style**: ruff for linting, mypy for type checking, pytest for tests
- **Async tests**: `asyncio_mode = "auto"` in pyproject.toml
- **Model names**: NEVER change without verification -- hookify rule blocks this
- **DB access**: IdeaForge uses SQLite directly, Metroplex reads upstream DBs
- **Git**: Do not commit -- leave changes unstaged for user review
- **Existing patterns**: Always check CLAUDE.md before writing code in any project
