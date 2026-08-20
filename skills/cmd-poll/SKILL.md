---
name: cmd-poll
description: Poll in-flight CMD (Command Center) missions, show their status, and fetch completed results. Use when Matthew says "check CMD", "poll missions", "cmd status", "what happened with that mission", or after dispatching work via mission-cli and wanting to see results. Surfaces running/queued/completed tasks in one view so he doesn't have to remember task IDs.
---

# cmd-poll — CMD Mission Status Dashboard

Consolidated view of recent Command Center missions. CMD is the orchestrator
running on `http://localhost:3142` (port 3142). Mission results are
retrievable via `mission-cli`.

## When to use

Use this skill when Matthew:
- Invokes `/cmd-poll` explicitly
- Asks "check CMD", "poll missions", "cmd status", "any missions done?"
- Follows up on work he just dispatched via `mission-cli create`
- Asks what happened with a specific mission by title/agent/partial ID

## Execution

Run this sequence of Bash commands. Do not interactive-prompt Matthew for
arguments; produce the full dashboard up front.

### 1. List recent missions

```bash
CMDCLI=/home/apexaipc/projects/command-center/dist/server/server/mission-cli.js
node $CMDCLI list --limit 15
```

### 2. Fetch full results for every mission in a terminal state since the last check

For each mission in the list with status `completed` or `failed` from the
last hour (or since Matthew's last `cmd-poll` invocation if obvious from
context), fetch the full result:

```bash
node $CMDCLI result <task-id>
```

Group terminal-state missions by agent; show the Title, Runtime, and a
trimmed Result (first ~40 lines or the inline-markdown summary if the agent
returned one).

### 3. Show queued + running separately

Anything still `queued` or `running` gets its own short section with:
- Task ID (first 8 chars)
- Agent
- Title
- How long it has been queued/running

## Output format

Produce this structure:

```
## CMD Mission Status (polled YYYY-MM-DD HH:MM)

### In Flight (queued + running)
<table or "(none)">

### Completed since last check
#### <agent-name>: <title>
(runtime: Xs)
<trimmed result>

---

### Failed since last check
<same format as completed, but surface the error prominently>
```

Keep it tight. If there are no completed-since-last-check missions, say so
in one line rather than dumping stale results.

## Common gotchas

- `mission-cli` lives at `dist/server/server/mission-cli.js` (nested path
  from tsc output, not `dist/mission-cli.js`).
- Default CMD_URL is `http://localhost:3142`. If the orchestrator is down,
  `curl http://localhost:3142/api/agents` returns empty/error — report
  "CMD orchestrator unreachable" and stop instead of guessing.
- Completed missions include a `result` field; failed missions include
  `error`. Always surface `error` in the Failed section.
- If a mission result is very long (>100 lines), summarise rather than
  dumping the whole thing. Matthew can ask for the full result by ID if he
  wants it.

## Related

- Dispatch missions with: `node $CMDCLI create --agent <id> --title "<t>" "<prompt>"`
- Available agents: research (Soundwave), coding (Ravage), data, kup,
  content (Creator), custom-forge (Forge), claude-code
- Mission-task worktree isolation docs: `projects/command-center/CLAUDE.md`
