---
name: workflow-router
description: Pick the best-fit multi-agent workflow PATTERN for a task and hand back a ready-to-run Workflow() script. Does light read-only recon on the real target, classifies the task into one of six orchestration shapes (Classify-and-Act, Fan-out-and-Synthesize, Adversarial-Verification, Generate-and-Filter, Tournament, Loop-Until-Done), runs a gap/tie-break AskUserQuestion wizard, then scaffolds the actual Workflow() script with a one-line rationale and the runner-up. Use when Matthew says "workflow router", "which workflow", "pick a workflow", "what workflow should I use", "how should I orchestrate this", "fan this out", "classify/triage these", "tournament these", "verify these claims", "brainstorm and filter", "loop until", or describes a task that wants multiple agents and is unsure which shape fits. Do NOT use to pick a GOAL's execution shape (that is goal-maker) or to break an already-clean goal into ordered subtasks (that is decompose-goal) or to rewrite an agent's system prompt (that is prompt-rewriter).
---

# workflow-router — task to best-fit workflow pattern + a runnable script

A task that wants several agents ("do due diligence on this data room", "triage my
inbox", "rank these resumes") has a correct orchestration SHAPE, and picking the wrong
one is expensive: a fan-out where a classifier belonged scatters one answer across N
handlers; a cold-scoring pass where a tournament belonged ranks badly. This skill closes
that gap. It reads what is actually on disk, maps the evidence to one of six named
patterns, fills any missing inputs through a short wizard, and emits the literal
`Workflow()` script ready to launch.

It sits DOWNSTREAM of goal-maker and decompose-goal and owns exactly one seam:
**task -> best-fit workflow pattern -> the orchestration script.** It does not run the
workflow (that is the user's call, and launching a Workflow spends tokens). It hands the
script back with a rationale and the runner-up, and stops.

The six patterns are not invented here. They are the patterns the `Workflow` tool already
documents (pipeline+dedup, parallel+barrier-synthesize, adversarial-verify, judge-panel,
tournament-bracket, loop-until-dry). This skill is the picker and the scaffolder, not a
new engine.

## Two modes (name which one you are in)

This skill is used two legitimate ways. Decide which BEFORE Step 5 so the hand-off matches
intent:

- **Scope-only** — the caller wants the *thinking*: which shape fits and why. The script is a
  by-product (often it gets pasted into a deliverable as an appendix, or the caller does the
  work by hand). Common when the real ask is a document, not a dispatch. The output is the
  rationale + runner-up; the script rides along.
- **Scaffold-for-dispatch** — the caller intends to RUN the work. The script is the product.

Default to scope-only when unsure (it never spends tokens you were not asked to spend). Either
way the rule below holds: never auto-launch.

## The six patterns (the rubric)

| # | Pattern | Concept | Fires when the target/task has... | Canonical example |
|---|---------|---------|-----------------------------------|-------------------|
| 1 | **Classify-and-Act** | Receptionist: read each item, label it, route to the right handler; dedup against what is already tracked | A heterogeneous QUEUE of incoming items of mixed type that each go to a DIFFERENT downstream action | Inbox triage (bug / refund / lead / spam) |
| 2 | **Fan-out-and-Synthesize** | Split a corpus into independent parts, summarize each in a CLEAN context so files never cross-contaminate, then a barrier step merges them into ONE cited output | A corpus of many parts (folders, docs) that all feed ONE merged, source-cited deliverable | Due diligence on a data room -> one memo |
| 3 | **Adversarial-Verification** | Extract each claim, then spin an independent skeptic per claim to refute it against the real source; return what failed and why | A SINGLE artifact full of discrete factual/technical CLAIMS to be checked before shipping | Fact-checking a blog post |
| 4 | **Generate-and-Filter** | One generator over-produces options; a DIFFERENT judge scores them all against criteria and filters | A need to CREATE many options then keep the best (generator and judge must differ) | 40 video titles -> judge picks the winners |
| 5 | **Tournament** | Pairwise comparisons against a rubric, winners advance through a bracket held by a deterministic loop | An EXISTING pool of candidates to RANK, where relative comparison beats cold scoring | Rank every resume for a role |
| 6 | **Loop-Until-Done** | Keep forming theories and adversarially testing each in isolation, repeating UNTIL a specific result is reached, not for a fixed count | An intermittent / hard-to-reproduce target with an unknown number of attempts to a clear done-state | Hunt a 1-in-50 flaky test |

### The three discriminators (resolve close calls)

Most misclassifications are one of three confusable pairs. Decide each by its single
distinguishing axis:

1. **Fan-out (2) vs Classify-and-Act (1) — converge vs diverge.**
   Fan-out CONVERGES N parts into ONE merged output (a memo, a report). Classify-and-Act
   DIVERGES each item to a DIFFERENT handler (bug vs refund vs spam). Ask: does every part
   feed one answer (fan-out), or does each item get routed somewhere else (classify)?

2. **Generate-and-Filter (4) vs Tournament (5) — create vs rank-existing.**
   Generate-and-Filter CREATES the options, then scores them absolutely. Tournament takes a
   pool that ALREADY EXISTS and ranks it by pairwise comparison. Ask: am I making the
   candidates (generate), or ordering ones I already have (tournament)?

3. **Adversarial-Verification (3) vs Loop-Until-Done (6) — one pass vs repeat-until.**
   Verification is ONE pass over a FIXED set of claims, parallelized. Loop-Until-Done
   REPEATS an attempt until a hard-to-reach result is met, with no known attempt count.
   Ask: is the work-set fixed and finite (verify), or do I keep trying until something
   happens (loop)?

## Step 1 — Read the mode (interactive vs headless)

- **Interactive** (a human invoked this live): you may ask the gap/tie-break questions in
  Step 4. Default to this when unsure.
- **Headless** (a cron, pipeline step, or non-interactive dispatch called it): never ask
  questions, nothing is listening. Make a best-effort pick, fill placeholders with your best
  guesses, and list every assumption under `## Assumptions` so a human can correct it.

## Step 2 — Light recon (read-only)

If the task names a target (a folder, an inbox, a data room, a draft, a test directory, a
candidate pool), spawn ONE `Explore` subagent (read-only) against it. Ask the agent to
report, and nothing more:

- **Volume + types:** how many items, what file types.
- **Structure:** one flat directory vs many subfolders; one document vs many.
- **Pattern-signals** (the evidence the rubric needs):
  - Duplicates likely against an existing tracker? -> signal for Classify-and-Act dedup.
  - External sources that findings must cite? -> signal for Fan-out.
  - Discrete factual/technical claims in one artifact? -> signal for Adversarial-Verification.
  - A pool of comparable candidates to order? -> signal for Tournament.
  - An intermittent / "until" condition with no fixed attempt count? -> signal for Loop-Until-Done.

Keep the recon read-only and shallow: shape and signals, not a full read of every file. If
no target is named (pure "generate" tasks often have none), skip recon and rely on the
prompt plus the wizard.

## Step 3 — Classify

Map the recon evidence (or, if no target, the prompt) to a **primary pick** and a
**runner-up**, each with a one-line reason. Run the three discriminators above on any close
call. The pick must cite evidence ("recon found 9 subfolders each with source PDFs ->
Fan-out"), not the prompt's wording alone, which often lies about the real shape (a
"research" prompt over a single file is not a fan-out).

## Step 4 — Wizard (gap / tie-break only)

Use `AskUserQuestion` ONLY to:

- **Fill a missing required input** the chosen template needs: target path, output filename,
  scoring rubric / criteria, the done-condition for a loop, or the handler set for routing.
- **Break a tie** when primary and runner-up are within one discriminator of each other:
  present both with their one-line reasons and let the user pick.

Skip the wizard entirely when the pick is clear and every required input is already known.
Keep it to 1-3 targeted questions. This honors the "smart and to-the-point" preference: no
fixed interrogation, only the questions that change the output.

## Step 5 — Scaffold and hand off

Open `scaffolds.md` (in this skill directory), take the chosen pattern's template, and fill
its `{{PLACEHOLDER}}` slots from the recon'd target, the task, and the wizard answers. Then
emit, in this order:

1. The complete `Workflow({ script })` ready to paste or launch.
2. A one-line **rationale** ("Classify-and-Act: a heterogeneous ticket queue routed to four
   different handlers, with dedup against what is already tracked").
3. The **runner-up** pattern and why it lost (the discriminator that decided it).
4. A **routing block** — the explicit next-step options, so the hand-off is not a dead end:
   - **Launch it** — only on explicit user opt-in (the user passed `--launch`, or answers yes
     to a single closing "scaffold only, or launch now?" question). That opt-in is what makes
     calling the Workflow tool rule-compliant; without it, do not launch.
   - **Save it as a named workflow** — offer to persist the script to
     `~/.claude/workflows/<name>.js` so a good scaffold becomes a reusable asset the Workflow
     tool can run later by name, instead of evaporating into chat. This is the highest-value
     chain; offer it whenever the script is non-trivial.
   - **Hand off sideways** — if the chosen pattern needs per-item subtasks first, point to
     `decompose-goal`.

Do NOT call the Workflow tool yourself unless the user has explicitly opted into launch (see
above). Scaffolding and routing are the contract; execution is the user's call.

## Output contract

```
### Recommended workflow: <Pattern name>

<one-line rationale tied to recon evidence>

Runner-up: <Pattern name> — <the discriminator that ruled it out>

```js
<the filled Workflow() script from scaffolds.md>
```

Next (pick one): **launch** with the Workflow tool (explicit opt-in only — it does not run
until you say so) · **save** to ~/.claude/workflows/<name>.js to reuse it later · **decompose**
first if the pattern needs per-item subtasks.
```

In headless mode, append an `## Assumptions` block listing every guessed placeholder. In a
clean interactive run where nothing was guessed, omit it.

## Worked example (interactive)

Input: "Triage the tickets in ~/vault/support-inbox by routing each to bug, refund, lead, or
spam, and don't re-handle anything already tracked."

- **Step 2 recon:** `Explore` over `~/vault/support-inbox` -> 37 markdown tickets, flat
  directory, several near-duplicate subject lines, an existing `tracked.json` alongside.
- **Step 3 classify:** heterogeneous queue, each ticket routes to a DIFFERENT handler,
  duplicates present -> **Classify-and-Act** (primary). Runner-up Fan-out loses on
  discriminator 1: the items diverge to four handlers, they do not converge into one memo.
- **Step 4 wizard:** the handler set and the dedup source are both named, the path is given
  -> no questions needed, recommend silently.
- **Step 5:** fill the Classify-and-Act template with `{{TARGET}}=~/vault/support-inbox`,
  `{{HANDLERS}}=bug, refund, lead, spam`, `{{TRACKED}}=tracked.json`, emit the script +
  rationale + runner-up.

## What workflow-router does NOT do

- It does not launch the workflow. It hands back the script and stops. Running it spends
  tokens and is the user's explicit call.
- It does not pick a GOAL's execution shape (one-shot / loop / cron / subagents). That is
  goal-maker, which sits upstream.
- It does not break a clean goal into ordered subtasks. That is decompose-goal.
- It does not rewrite an agent's system prompt. That is prompt-rewriter.

Holding this seam is what keeps it composable: goal-maker decides whether to use subagents
at all, workflow-router decides which subagent SHAPE, and the Workflow tool runs it.
