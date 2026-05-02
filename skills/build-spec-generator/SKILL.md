---
name: build-spec-generator
description: Convert a qualified workflow into a complete, platform-agnostic build spec — trigger, inputs/outputs, tool connectors, success criteria, escalation conditions, and quality-check rubric. Use after a workflow has been confirmed worth automating, to produce a spec specific enough for an agent or developer to scaffold a working implementation.
---

# Build Spec Generator

Takes a workflow description (ideally one that has already been scored as a BUILD candidate) and produces a structured build specification. The spec is complete enough to hand to a developer, an agent harness, or an automation platform without further clarification.

## Trigger

Use when the user says "/build-spec-generator", "write a build spec", "spec this automation", "turn this into a runnable spec", "what would I need to build this", or after a workflow-fit-scorer result returns BUILD.

## Phase 1: Intake

Collect (or confirm from prior context):
1. **Workflow name** — short identifier used throughout the spec.
2. **Workflow description** — what the workflow does, who initiates it, what it produces.
3. **Trigger** — what starts a run (schedule, inbound event, user action, webhook, etc.).
4. **Target platform** (optional) — e.g., Claude Code, n8n, Make, ChatGPT Workspace Agents. Default: platform-agnostic.
5. **Existing tools/accounts** — which tool connections already exist vs. need to be created.

If the user passes a workflow-fit-scorer output, extract these from it automatically.

## Phase 2: Spec Elicitation

Ask focused clarifying questions for any missing fields. Limit to one round of questions. If the user asks you to proceed anyway, make reasonable assumptions and flag them clearly in the spec.

Key clarifications to seek:
- **Inputs**: what data/files/text arrive at the trigger, and in what format?
- **Outputs**: what does a successful run produce, where does it go, and who receives it?
- **Tool connectors**: which APIs/services does the workflow read from and write to?
- **Exception handling**: what should the automation do when it hits an error or unexpected input?

## Phase 3: Generate the Build Spec

Produce the spec in the following structure:

```
=================================================================
BUILD SPEC: {workflow_name}
=================================================================
Version:   1.0 (draft)
Date:      {date}
Platform:  {target_platform | platform-agnostic}

SUMMARY
{2–3 sentences: what this workflow does, who benefits, and what it replaces}

TRIGGER
  Type:        {schedule | event | webhook | manual | inbound-data}
  Definition:  {cron expression, event name, endpoint URL, or user action}
  Frequency:   {e.g., daily at 08:00, on every new form submission}

INPUTS
  {for each input:}
  - Name:     {field_name}
    Source:   {tool or data source}
    Format:   {type: string, JSON, file, etc.}
    Required: {yes | no | conditional}

OUTPUTS
  {for each output:}
  - Name:     {output_name}
    Destination: {tool, channel, file path, or person}
    Format:   {type: string, JSON, file, email, Slack message, etc.}
    Timing:   {on completion | per-item | batched}

TOOL CONNECTORS
  {for each tool:}
  - Tool:        {tool name}
    Operations:  {read | write | both}
    Auth:        {OAuth | API key | service account | none}
    Status:      {existing | needs setup}

WORKFLOW STEPS
  {numbered list of steps}
  1. {step description — include: what triggers it, what it reads, what it produces}
  2. ...
  (If a step involves a conditional branch, show both branches)

ERROR HANDLING & ESCALATION
  On data error:     {fallback action — e.g., log and skip, alert human, halt run}
  On tool failure:   {retry policy — e.g., 3 retries with 30s backoff, then alert}
  On quality failure: {what happens when output fails the quality check}
  Escalation path:  {who/what receives alerts — channel, email, ticket queue}

SUCCESS CRITERIA
  A run is successful when:
  {numbered list of observable conditions — measurable, not subjective}

QUALITY CHECK RUBRIC (summary)
  {3–5 bullet criteria — expand with recognizable-quality-test-generator if needed}

IMPLEMENTATION NOTES
  {any platform-specific config, known gotchas, or dependencies to resolve first}

OPEN QUESTIONS
  {numbered list of assumptions made or questions that need owner confirmation}
=================================================================
```

## Phase 4: Platform Variant (optional)

If the user specifies a target platform, append a platform-specific configuration block:

### Claude Code variant
- Which tools need to be added to `--allowedTools`
- Whether this should be a scheduled task or an on-demand skill
- MCP servers required

### n8n / Make variant
- Node types to use per step
- Recommended trigger node
- Data mapping notes

### ChatGPT Workspace Agents variant
- Which built-in connectors cover the tool list
- Connector gaps that need custom MCP servers

## Phase 5: Handoff

After delivering the spec, offer:
1. **"Generate quality rubric"** — expand the Quality Check Rubric section using the recognizable-quality-test-generator skill.
2. **"Estimate effort"** — rough complexity assessment (hours/days) for each step.
3. **"Save spec to file"** — write the spec to `./specs/{workflow_name}-build-spec.md`.

## What This Does NOT Do

- Does not implement the workflow — the spec is an input to implementation, not the implementation.
- Does not validate that the listed tool connectors exist or have the needed permissions.
- Does not account for data privacy, compliance, or retention requirements — flag these in Open Questions if relevant.
- Does not guarantee the spec is complete — OPEN QUESTIONS section surfaces what's missing.

## Source

Extracted from Nate Kadlac newsletter (2026-04-27): "Your team spends 5 hours a week on work a sales consultant automated in an afternoon." The build spec is the artifact behind Nate's Prompt 2 — what a workflow needs to scaffold something that runs, not just demos.
