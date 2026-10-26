---
name: aar
description: Run an After-Action Review on any multi-step operation — a build, a dispatch run, a debug session, a deploy, a failed experiment. Gathers forensics from logs, git history, test output, and running processes; classifies failure modes; captures benchmarks; produces a structured AAR saved to the vault with durable lessons written to auto-memory. Use when the user says "aar", "after action review", "let's review what happened", "review this run", or after any operation that produced mixed results worth learning from. Works across any project; includes a CMD appendix for ClaudeClaw dispatch runs.
context: fork
---

# After-Action Review (AAR)

Structured review for any operation that produced data worth learning from — a build, a deploy, a debug session, a dispatch run, a failed experiment. Project-agnostic by default. A CMD appendix at the bottom covers ClaudeClaw dispatch forensics when applicable.

## When to invoke

- After any multi-step operation the user wants to understand (build, deploy, test run, agent dispatch, debug session)
- When the user says: "aar", "after-action review", "let's review", "what went wrong", "review this run"
- Proactively after: a run that failed partway, a git reset used to recover, >30% of a batch failing, an incident that required manual intervention

## Input

Ask once which scope applies, default to "this session" if unclear:

- A specific run id or task id (e.g. mission task id, build id, PR number, commit range)
- A time window (e.g. "last 2 hours", "today")
- "This session" — everything touched since session start
- A specific file, feature, or subsystem

## Phase 1: Gather forensics

Never skip a source — missing data is the most common cause of a shallow AAR. Adapt the list below to the project. If a source doesn't apply, note it and move on. Run in parallel where possible.

### 1. User-reported symptom

Start here. Record exactly what the user said broke, in their words. If they reported a specific error message or timestamp, capture it verbatim before anything else.

### 2. Logs

Whatever logging the project uses:

- Application logs (stdout/stderr, `logs/`, `/var/log/`, `journalctl -u <service>`)
- Process manager logs (`pm2 logs <name>`, `systemctl status`, `docker logs <container>`)
- Build/CI logs (GitHub Actions, local build output, test runner output)
- Framework-specific logs (Next.js `.next/`, Vite, Unity Editor.log)

Grep for the failure timestamp, task id, or error string. Capture first/last 50 lines around the failure window.

### 3. Git history

```bash
git -C <repo> log --oneline -20
git -C <repo> status --short -b
git -C <repo> log --since="<window>" --all --oneline
```

Flag: `WIP: auto-snapshot` commits in the window (the 30-min cron — often indicates interrupted work), uncommitted changes, commits ahead of remote, interleaved authorship on same files (possible race condition).

### 4. Test / build output

If a test run or build was part of the operation:

- Failing test names, assertion messages, stack traces (first and last 10 failures)
- Exit codes, runtime, memory usage if captured
- Type-check / lint output if the failure was caught there

### 5. State files & config

Whatever persistent state the project uses:

- Database records relevant to the run (read-only queries, capture status/error/runtime fields)
- Queue / job files (`open_items.json`, `.queue`, Redis keys, etc.)
- Config files that changed in the window
- Lock files (`/tmp/*.lock`, `*.pid`) that may be stale

### 6. Running processes (if "still running" or runtime seems stuck)

```bash
pgrep -af "<pattern>"
ps auxf | grep -v grep | grep <name>
```

Subprocess gone but status still "running" in state file = stuck executor, diagnose the state machine.

### 7. External forensics (when relevant)

- API response logs, rate-limit headers, provider status pages
- Cloud resource state (Railway, Netlify, Render, GitHub Actions artifacts)
- Portainer / Docker state for containerized workloads

## Phase 2: Classify failures

Every failed step should map to at least one mode. Multiple can apply. Order of specificity: check specific modes first, fall back to generic ones.

### Generic failure modes

| Mode | Signature |
|---|---|
| `timeout` | Runtime exceeded wall-clock budget (usually >0.9× configured limit). |
| `resource_exhaustion` | OOM, disk full, file descriptor exhaustion, rate limit hit. |
| `subprocess_crash` | Non-zero exit, signal (SIGTERM/SIGKILL/SIGSEGV), core dump. |
| `dependency_failure` | Missing binary, broken `node_modules`, pip resolve failure, missing env var. |
| `config_mismatch` | Wrong model name, wrong endpoint, wrong credential, wrong path. |
| `race_condition` | Multiple writers to same file/resource within seconds; interleaved git authorship. |
| `scope_mismatch` | Task scope exceeded the executor's budget (turns, time, context, tokens). |
| `skipped_step` | Result text claims steps that weren't actually executed (verify via side effects). |
| `silent_fallback` | Error was caught and suppressed; operation "succeeded" but produced degraded output. |
| `environmental` | External service down, network flap, DNS issue, auth token expired. |
| `user_input_invalid` | Wrong args, malformed data, missing required flag — the human-side mistake. |
| `unknown` | Insufficient forensics; note what would be needed to classify next time. |

### CMD-specific failure modes (if applicable — see CMD appendix)

| Mode | Signature |
|---|---|
| `max_turns` | Error contains "Reached max turns" — turn cap too low for task scope. |
| `wip_snapshot_collision` | WIP auto-snapshot landed mid-task, mixing multiple agents' edits. |
| `dispatch_ok_exec_failed` | Dispatcher succeeded, downstream executor failed — separates dispatch machinery from execution machinery. |
| `mission_task_no_worktree` | A2A path skipped worktree isolation, parallel tasks collided. |

## Phase 3: Capture benchmarks

Benchmarks are optional but valuable — record when the run produced new numbers worth remembering. Skip if the run was a one-off with no generalizable metric.

Examples of benchmarks worth capturing:

- Build/test runtime at a given codebase size
- Per-operation cost (tokens, API calls, $) for routine operations
- Success rate of an operation across N attempts
- "Sweet spot size" — the task shape that consistently completes under budget
- Cold-start vs warm-start latency
- Cache hit rate

Durable benchmarks go to feedback memory (Phase 5). Ephemeral numbers stay in the AAR file only.

## Phase 4: Write the AAR

Structure (stick to this — don't invent new sections):

1. **What happened** — one paragraph, facts only, no interpretation.
2. **What worked** — 3-5 concrete items, each with evidence.
3. **What didn't work** — 3-5 concrete items, each classified by a Phase 2 failure mode.
4. **Root cause** — the one or two architectural/process gaps that explain the failures. If the gap was user-side, say so plainly.
5. **Benchmark data** — table of metrics captured (omit this section if no benchmarks were worth capturing).
6. **What the user could have done differently** — honest. Includes "nothing, the gap was in the system" when true.
7. **Tools / skills / fixes needed** — ranked by payoff, S/M/L complexity, estimated time.
8. **Action items** — concrete next steps. The top 1-3 that deserve to become queue work
   flow through Phase 6 (judge-gated card proposals); everything else stays in this
   document as reference.

## Phase 5: Persist

1. **Save AAR** to `~/vault/projects/<project-or-topic>-aar-YYYY-MM-DD.md`, or `~/vault/daily/YYYY-MM-DD-aar-<topic>.md` if no clear project.
2. **Feedback memory** — write up to 2-3 `feedback_*.md` entries for durable lessons, per the memory rules (each with **Why:** and **How to apply:** lines). Update existing files rather than duplicating.
3. **Update** `MEMORY.md` index with any new entries.
4. **Action items** — run Phase 6 for the strongest candidates. The AAR may create only
   inert Teletraan proposals. It must never admit, lease, assign, dispatch, or execute
   its own follow-up work.

## Phase 6: Teletraan proposals (judge-gated)

The AAR may convert its strongest recommendations into inert Teletraan proposals only
through this gate. Because the author shares the original work's blind spots, every
proposal remains non-executable until Matthew independently admits it.

### Protocol

1. **Cap: at most 3 candidates per AAR.** An AAR proposing ten items is summarizing, not
   prioritizing. Draft each candidate as a full card (File-Queue schema: id, title, owner,
   sink, kill, shape, `## Goal`, `## Done when`, `## Action`).
2. **Adversarial judge (mandatory, before any proposal is captured).** Use one refute-first
   Claude subagent (Agent tool; sonnet is fine) whose explicit job is to kill each
   candidate, not grade it. The judge must answer, per candidate, with quoted evidence:
   - **Premise**: is it traceable to a CONFIRMED Phase 1/2 finding (quote it), or is it
     speculation? Unverified state claims fail the recon gate.
   - **Class vs instance**: does it fix the failure class or just today's instance?
   - **Duplicate**: search Teletraan tasks and proposals, `~/.claude/skills/`,
     `~/.claude/rules/`, and MEMORY.md — does something already own this?
   - **Guards**: are owner/sink/kill real values (not placeholders)?
   - **Blast radius**: is the stated scope honest about what it touches?
   Verdicts: `PROMOTE` / `PARK` (premise plausible, evidence thin) / `REJECT`.
   One judge only: author + one adversary is the orthogonality ceiling (see
   feedback_prompt_stacking_ceiling).
3. **REJECT** candidates are NOT filed. Record them with the judge's reason in
   a "Declined proposals" subsection of the AAR document so the reasoning survives.
4. **PROMOTE / PARK** candidates go through goal-maker and then `teletraan propose`.
   Include `judge_verdict: PROMOTE|PARK` and the judge reason in the proposal body.
   Require `liveTask: false`; do not call the admission or lease boundary.
5. **Aging check.** Surface AAR proposals older than seven days that have no admitted
   task or explicit expired disposition. A proposal inbox without a human decision is
   not an execution queue.

### Graduation ladder (roadmap, decided 2026-07-11)

Current rung and the two above it. Do not skip rungs; walk /trust-ladder before any flip.

- **Rung A (NOW): same-vendor subagent judge + auto:false on everything.** Chosen on
  economics (no extra API spend); acknowledged weaker against shared blind spots.
- **Rung B: orthogonal judge. PREREQUISITE for Rung C, not a parallel option.** Second
  vendor (gemini-rescue / codex pattern) or the local model on AlienPC (Ollama, see
  autoresearch setup) when economics or setup allow. Vendor diversity escapes same-model
  anchoring (see feedback_review_goal_not_diff). A same-vendor judge can NEVER graduate
  to Rung C regardless of its agreement score: self-preference bias makes the score
  untrustworthy (local evidence: the Matrix AUQ judge lane scored below baseline, 73.5%).
- **Rung C: judge-PROMOTE = dispatchable (drop auto:false for promoted cards).** Exit
  criteria, ALL required:
  1. The sitting judge is orthogonal (Rung B) at the time of measurement; the agreement
     window RESETS whenever the judge model/vendor changes.
  2. **Blind disposal protocol** for every measured proposal: Matthew records his own
     verdict plus a one-line why on the card's Notes BEFORE reading the judge's verdict.
     The index row must never surface judge_verdict (see Protocol step 4); the card
     carries it below the fold. An unblinded disposal does not count toward the window:
     if he reads the verdict first, high agreement can mean anchoring, not alignment,
     and the two are indistinguishable in the data.
  3. Across at least 10 blind disposals, judge verdict matches Matthew's at ≥90%.
     Measured by grepping `proposed_by: aar` cards, comparing `judge_verdict` against
     his pre-read Notes verdict; no separate ledger needed.
  Disagreement rows are the valuable ones: keep them (they are eval/training signal for
  the Matrix/MATS preference lane), never prune them as noise.

## Anti-patterns (don't do these)

- **Don't write an AAR from memory alone.** Always gather forensics first. Shallow AARs are worse than no AAR.
- **Don't classify every failure as "the agent/tool was dumb."** The failure mode is usually in the system (budget caps, missing isolation, missing gates), not the executor's reasoning.
- **Don't pile action items without priority.** If everything is "high", nothing is.
- **Don't duplicate existing feedback memories.** Update the one that already exists when the new lesson is an extension.
- **Don't auto-dispatch AAR action items.** AARs often reveal that the dispatch system itself is the problem — dispatching more work through it amplifies the bug. Cards enter the queue only via Phase 6 (judge gate + auto:false); they never dispatch from an AAR run.
- **Don't skip the judge because a proposal "obviously" passes.** The obvious-looking ones carry the author's blind spots; that is exactly the blind-leading-the-blind case the gate exists for.
- **Don't force benchmarks when there's nothing generalizable.** Not every AAR has reusable metrics.

## Example invocation

User: "Let's AAR this run."
→ Ask: "Which scope — a run/task id, a time window, or this session?"
→ Gather forensics from every applicable source in Phase 1
→ Classify every failure by mode from Phase 2
→ Capture benchmarks if the run produced durable numbers
→ Write the AAR using the 8-section structure
→ Save to vault, write feedback memories, update MEMORY.md index
→ Run Phase 6: draft ≤3 card candidates, judge refutes, write survivors as auto:false cards + index rows
→ Report: file path of the saved AAR, count of new feedback memories, and per-candidate judge verdicts (PROMOTE/PARK/REJECT) with card ids for survivors

---

## Appendix: CMD / ClaudeClaw dispatch runs

When the run being reviewed is a ClaudeClaw mission-task dispatch, add these forensic sources to Phase 1 alongside the generic ones:

### Mission task state (primary source)

```bash
node -e "
const Database = require('/home/apexaipc/projects/agents/command-center/node_modules/better-sqlite3');
const db = new Database('/home/apexaipc/projects/agents/command-center/store/command-center.db', {readonly: true});
// Query by parent mission_task id or WHERE created_at > <unix_ts>
// Capture: status, error, result (first 500 chars), runtime (completed_at - claimed_at), agent_id, title
"
```

### Historical A2A task logs

```bash
curl -s "http://localhost:<agent_port>/task/<task_id>" | python3 -m json.tool
```

Agent ports: research=3143, coding=3144, content=3145, data=3146, kup=3147. Verified
2026-08-30: none of these ports respond (connection refused) and no `command-center` or
`agent-*` pm2 processes are running. This source only applies to a CMD dispatch run from
before the crossover; for current Kup/Ravage/etc. work reviewed via `/aar`, use the
Teletraan event, execution-link, result, and review receipts. Logs often expire after task completion
even for historical runs — if empty, move on.

### pm2 logs

```bash
pm2 logs command-center --lines 80 --nostream
pm2 logs agent-<id> --lines 40 --nostream
```

Grep for the task id or failure-window timestamps. Watch for `[mission-dispatcher]` events.

### Queue cross-reference

```bash
python3 -c "import json; d=json.load(open('/home/apexaipc/projects/claudeclaw/store/open_items.json')); ..."
```

Confirm mission_tasks map back to open_items and statuses are consistent (pending/dispatched/in_progress).

### CMD-specific benchmarks

Update or create per-agent `feedback_<agent>_task_sizing.md` memory files with:

- Typical runtime for a single-file task
- Turn-to-wallclock ratio
- Max turns used vs cap
- Queue-to-claimed latency
- Sweet-spot task size for the agent

One file per agent — don't create duplicates.
