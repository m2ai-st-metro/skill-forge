---
name: workflow-fit-scorer
description: Score any workflow description against 5 automation-fit properties and return a build / switch-tools / resolve-ambiguity verdict. Use when deciding whether a workflow is worth automating, scoping an advisory engagement, or triaging a candidate list.
---

# Workflow Fit Scorer

Takes a workflow description and scores it against five properties that predict whether an automation will succeed in production. Returns a structured verdict with per-property scores and a recommended action.

## Trigger

Use when the user says "/workflow-fit-scorer", "score this workflow", "should I automate this", "automation audit", "is this worth building", or provides a workflow description and asks whether to automate it.

## Phase 1: Intake

Ask (or infer from context):
1. **Workflow description** — what the workflow does, who does it, how often.
2. **Sample run** (optional) — a concrete example of one execution from trigger to output.

If the user provides both, skip to Phase 2. If description is missing, ask for it before proceeding.

## Phase 2: Score Against the 5 Properties

Evaluate the workflow against each property. Score each 0 / 0.5 / 1.

| # | Property | Score 1 | Score 0.5 | Score 0 |
|---|----------|---------|-----------|---------|
| 1 | **Repeats on a schedule or predictable trigger** | Clear trigger (time, event, inbound data) | Trigger exists but frequency varies | Ad-hoc or judgment-triggered |
| 2 | **Recognizable good-vs-bad output** | You can describe pass/fail criteria without seeing the output | You know it when you see it, but can't pre-specify | Novel judgment required every time |
| 3 | **Fits in a single paragraph** | Describable in ≤150 words without losing meaning | Needs 2–3 paragraphs; some steps are ambiguous | Requires a document to specify |
| 4 | **Crosses 2 or more tools** | Clearly touches 2+ distinct tools or data sources | Uses 1 tool but feeds another downstream | Single tool, single data source |
| 5 | **Follows a known, repeatable path** | Same steps every time; exceptions are rare and handleable | Most runs follow the path; exceptions need human escalation | Every run is materially different |

## Phase 3: Verdict

**Total score** = sum of 5 property scores (0–5).

| Score | Verdict | Recommended action |
|-------|---------|-------------------|
| 4.0–5.0 | **BUILD** | High-fit candidate — proceed to build spec |
| 2.5–3.5 | **RESOLVE AMBIGUITY** | One or more properties are unclear — clarify before building |
| 0–2.0 | **SWITCH TOOLS** | Low-fit — route to a more appropriate tool or approach |

### Failure-mode routing for SWITCH TOOLS

When the verdict is SWITCH TOOLS, identify which property fails and recommend:

- **Property 1 fails (no repeatable trigger)** → this is judgment work. Use an interactive chat interface, not an autonomous agent.
- **Property 2 fails (no recognizable quality)** → build the rubric first (see the recognizable-quality-test-generator skill if available), then re-score.
- **Property 3 fails (not paragraph-describable)** → decompose the workflow into sub-workflows and score each independently.
- **Property 4 fails (single tool)** → check whether automation is worth the overhead vs. a built-in tool feature or a simple macro.
- **Property 5 fails (no known path)** → research and documentation phase needed before automation. Use a research-and-synthesis workflow instead.

## Phase 4: Report

```
=================================================================
WORKFLOW FIT SCORE
=================================================================
Workflow:  {one-line summary}
Scored:    {date}

Property Scores
  1. Repeatable trigger:         {score}  {evidence}
  2. Recognizable quality:       {score}  {evidence}
  3. Paragraph-describable:      {score}  {evidence}
  4. Crosses 2+ tools:           {score}  {evidence}
  5. Known path:                 {score}  {evidence}

  Total: {total}/5

Verdict: {BUILD | RESOLVE AMBIGUITY | SWITCH TOOLS}

{If BUILD}: Proceed to build-spec-generator to scaffold the implementation.
{If RESOLVE AMBIGUITY}: Address the following before building:
  - {specific clarifying question per 0.5-scored property}
{If SWITCH TOOLS}: {failure-mode routing recommendation}
=================================================================
```

## What This Does NOT Do

- Does not estimate implementation effort or cost.
- Does not generate the build spec — use build-spec-generator for that.
- Does not evaluate technical feasibility (API access, data availability).
- Does not score the team's capacity to maintain the automation after it ships.

## Source

Extracted from Nate Kadlac newsletter (2026-04-27): "Your team spends 5 hours a week on work a sales consultant automated in an afternoon + the 2 prompts that find your version." The 5-property framework is the scoring rubric behind Nate's Prompt 1 (Workflow Fit Scorer).
