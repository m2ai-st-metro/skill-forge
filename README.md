<p align="center">
  <img src="assets/skill-forge-banner.jpg" alt="Skill Forge Banner" width="100%">
</p>

<h1 align="center">Skill Forge</h1>
<p align="center"><strong>Content-to-Capability Pipeline + Cold Skill Archive</strong></p>
<p align="center">Ingests AI walkthroughs, extracts techniques, generates Claude Code skills, and serves as the cold archive for skills that have aged out of active use.</p>

---

## What Is This?

Skill Forge watches for new AI content (YouTube videos, newsletters, blog posts) and transforms the techniques found inside into installable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills). Instead of watching a 40-minute walkthrough and manually writing a skill file, Skill Forge does the extraction, structuring, and packaging for you.

**Hot/Cold Lifecycle:** Skills that meet active adoption criteria stay "hot" in Claude Code, ClaudeClaw, or agent manifests. Skills that age out move here as the "cold" archive -- a browsable library for reference, templates, idea scraping, and client onboarding.

**The pipeline:**

```
Content Source --> Technique Extraction --> SKILL.md Generation --> Review & Install
 (video, article)   (Gemini / LLM)          (structured phases)     (human-in-the-loop)
```

---

## Skill Catalog (50 skills)

### Agent Architecture (8 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **classify-agent** | One-question diagnostic: coding harness, dark factory, auto research, or orchestration? | Starting a new agent project and need to pick the right architecture |
| **agent-cost-model** | Models token costs per task, monthly burn, and model-routing optimization | Budgeting an agent workflow or comparing Opus vs Sonnet vs Haiku |
| **agent-memory-architecture-matrix** | Interactive decision matrix for provider-hosted vs self-owned memory backends | Choosing between Anthropic's memory, RAG, or custom persistence |
| **decomposition-scorer** | Scores whether parallel agent tasks have proper isolation boundaries | Before launching parallel agents on decomposed subtasks |
| **mismatch-check** | Detects expensive architecture mismatches (built solution to wrong question) | After building an agent that feels wrong or underperforms |
| **model-router** | Classifies a task and recommends Opus/Sonnet/Haiku tier with cost delta | Routing tasks in a multi-model pipeline |
| **eval-agent** | Scores any agent tool against 3 structural questions: memory, inspectability, compounding | Evaluating a new agent framework or tool before committing |
| **sensemaking-concentrator** | Audit a multi-agent system for distributed sensemaking anti-patterns and recommend where to concentrate interpretation into a single agent | Debugging a multi-agent system where agents produce conflicting actions from the same input |

### Agent Quality & Operations (6 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **delegation-spec** | Generates pre-flight delegation specs that patch structural weaknesses of target tools | Before handing complex work to an autonomous agent |
| **dispatch-handoff-brief** | Structured 7-section delegation brief for Anthropic Dispatch or any agent handoff | Quick-formatting a handoff to a background agent |
| **failure-asymmetry** | Compares skill behavior under human vs agent invocation, finding autonomy-only divergences | Testing whether a skill works the same way unattended |
| **knowledge-work-tests** | Generates evaluation rubrics for non-code deliverables (the missing "test suite" for knowledge work) | Grading agent output that isn't code (reports, analysis, plans) |
| **middleware-trap-detector** | Diagnoses whether a deployment wraps legacy systems without redesign, scaling dysfunction | Auditing automation that feels like it made things worse |
| **simulated-work-detector** | Reviews agent fleet output and flags work that generated artifacts but closed no loops | Auditing whether agents are actually producing value |

### Agent Security & Observability (3 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **agent-authority-map** | Parses settings, hooks, MCP configs to surface "authority vacuums" | Auditing what an agent is actually allowed to do |
| **agent-blast-radius** | Inventories everything an autonomous agent touched over a time window | Post-run forensics: what files, commits, APIs did it hit? |
| **nemoclaw-policy-gen** | Generates NemoClaw YAML security policies for agent sandboxing | Locking down an agent before giving it production access |

### Agent Infrastructure (3 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **agent-architecture-audit** | Evaluates agent code against 12 production infrastructure primitives | Deep audit of an agent codebase for production readiness |
| **agent-doctor** | Comprehensive health check on connected services, API creds, MCP servers, tools | Something isn't working and you need a systems check |
| **agent-readiness-audit** | Scores a codebase across 8 pillars for fitness to support autonomous AI agents | Evaluating whether a repo is ready for agent-driven development |

### Strategic Analysis (8 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **arbitrage-audit** | Maps a business model to 5 exploitable-inefficiency categories with AI compression timelines | Analyzing a company's AI exposure for advisory or investment |
| **career-gap-map** | Calculates individual AI exposure score and produces a migration plan | Personal or team skill-planning against AI compression |
| **gap-trace** | Lightweight 3-question industry diagnostic: inefficiency, AI closure speed, next gap | Quick sales qualification or discovery call prep |
| **executive-briefing** | Transforms complex events into structured briefings: thesis, channels, exposure, actions | Packaging analysis for leadership or client consumption |
| **geopolitical-signal-enricher** | Enriches market/tech signals with geopolitical context and second-order effects | Adding geopolitical depth to any market signal or trend |
| **counterargument-stress-test** | Generates and addresses the N strongest counterarguments against any thesis | Before publishing, presenting, or deciding on a strategic position |
| **strategic-timing-matrix** | Maps decisions against macro events and market windows: accelerate/delay/hedge | Timing a launch, investment, or strategic move |
| **management-function-audit** | Takes an org change description and classifies which management functions (routing, sensemaking, accountability) were removed, retained, or weakened — predicts failure modes with historical precedents | Auditing a reorg, layer removal, or any restructuring to understand what will break and in what order |

### Developer Tooling (5 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **claude-architect-audit** | Audits Claude Code setup against Anthropic's 5 Certified Architect domains | Checking if your Claude Code config follows best practices |
| **claudemd-router** | Restructures a bloated CLAUDE.md into a lean router with .claude/rules/ files | Your CLAUDE.md is over 200 lines and getting unwieldy |
| **agents-md-generator** | Generates or lints AGENTS.md files from repo analysis | Onboarding AI agents to a new repo |
| **mcp-compatibility-scanner** | Scans MCP server implementations for protocol compliance (draft) | Verifying an MCP server before publishing or deploying |
| **visual-qa-loop** | Recursive build-inspect-fix loop using Claude-in-Chrome for visual verification (draft) | UI work where you need visual regression checking |

### Context & Token Management (5 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **context-fork-guide** | Reference for adding `context: fork` to isolate heavy skill execution | A skill is bloating your main context window |
| **context-hygiene** | Three shields: /by-the-way, /fork, context:fork | Context window feels cluttered or session feels slow |
| **boot-tax-monitor** | Monitors Claude Code session startup overhead against a token threshold | Sessions feel slow to start or you suspect config bloat |
| **token-burn-auditor** | Audits live environment for token waste with actionable reduction targets | Monthly token cost review or after adding new plugins/skills |
| **pre-turn-budget-guardian** | Enforces a token budget ceiling by checking projected usage before each turn | Running cost-sensitive automated loops |

### Platform Analysis (3 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **mcp-portability-auditor** | Scores an agent stack for vendor lock-in via MCP portability | Evaluating how trapped you are in one platform |
| **platform-dependency-mapper** | Audits AI stack lock-in across 4 axes: data, integrations, behavioral context, billing | Comprehensive vendor dependency assessment |
| **platform-shift-detector** | Monitors tech company signals to detect platform-level shifts vs incremental features (draft) | Watching for breaking changes from AI providers |

### Workflow & Delegation (3 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **open-loop-audit** | Scans open loops and classifies each as real delegation vs simulated work | Weekly review: how much of your work actually moved forward? |
| **failure-postmortem** | Structured AI system failure post-mortem using 6 named failure patterns | Something broke and you need to learn from it systematically |
| **spec-gap-detector** | Stress-tests agent prompts/specs for ambiguity, missing constraints, edge cases | Before deploying a prompt or agent spec to production |

### Meta & Skill Tooling (3 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **compound-skill-orchestrator** | Builds orchestrator skills that chain multiple skills in sequence via context:fork | You need a pipeline of skills to run in order |
| **optimize-description** | Rewrites a skill's description for maximum agent discoverability | A skill exists but never gets triggered when it should |
| **skill-audit** | Audits skills directory for gaps, redundancies, and formalization opportunities | Periodic skill library maintenance |

### Content Creation (2 skills)

| Skill | Summary | Use When |
|-------|---------|----------|
| **video-to-skill** | Turns screen recordings into Claude Code skills via Gemini video understanding | You watched a tutorial and want to capture the technique |
| **viral-shorts-pipeline** | End-to-end TikTok/YouTube Shorts: theme to posted video (Kling AI + Gemini + Blotato) | Batch-producing short-form social video content |

### Deployment (1 skill)

| Skill | Summary | Use When |
|-------|---------|----------|
| **remote-channels** | Sets up Claude Code remote access via Telegram and Discord | You want to interact with Claude Code from mobile |

---

## Skills That Work Together

### Full Agent Deployment Pipeline
`classify-agent` -> `decomposition-scorer` -> `delegation-spec` -> `dispatch-handoff-brief` -> `failure-postmortem`

Classify what to build, validate task decomposition, write the delegation spec, generate the handoff brief, run post-mortems when things break. The full lifecycle from "what should I build?" to "what went wrong?"

### Agent Governance Stack
`agent-architecture-audit` + `agent-authority-map` + `agent-blast-radius` + `nemoclaw-policy-gen`

Audit infrastructure gaps, map permissions, track what was actually touched, generate sandboxing policies. Four pillars of agent governance.

### Token Economics Trilogy
`boot-tax-monitor` + `token-burn-auditor` + `pre-turn-budget-guardian` (+ `model-router`)

Measure startup cost, find ongoing waste, enforce per-turn ceiling, route to cheaper models. Full token lifecycle coverage.

### Strategic Advisory Engagement
`gap-trace` -> `arbitrage-audit` -> `career-gap-map` -> `executive-briefing` -> `counterargument-stress-test` -> `strategic-timing-matrix`

Quick diagnostic, deep business analysis, personalize to individual, package for leadership, stress-test the thesis, time the moves. A complete consulting engagement in skill form.

### Skill Quality Pipeline
`skill-audit` -> `spec-gap-detector` -> `failure-asymmetry` -> `optimize-description`

Find library gaps, stress-test specs, test human vs agent divergence, sharpen descriptions. The skill maintenance loop.

### Platform Lock-in Assessment
`platform-dependency-mapper` -> `mcp-portability-auditor` -> `platform-shift-detector`

Map vendor dependencies, score MCP portability, detect platform-level moves that change the calculus.

### Claude Code Setup Optimization
`claude-architect-audit` -> `claudemd-router` -> `context-hygiene` -> `context-fork-guide` -> `agents-md-generator`

Audit config, restructure CLAUDE.md, apply context management, add fork isolation, generate AGENTS.md. The "make Claude Code work better" stack.

### Agent Delegation Quality Gate
`eval-agent` -> `delegation-spec` -> `knowledge-work-tests` -> `simulated-work-detector`

Score the target tool, write a spec that patches weaknesses, define success criteria for non-code output, audit whether the work was real.

---

## Non-Obvious Adaptations

These skills have uses beyond their stated purpose:

- **agent-blast-radius** -- Run on your own Claude Code session to see your personal footprint across repos. Not just for agents.
- **spec-gap-detector** -- Use on client contracts and SOWs, not just agent prompts. Any ambiguous spec benefits from gap detection.
- **career-gap-map** -- Run on each team member's allocation to identify which roles are most exposed to AI compression.
- **knowledge-work-tests** -- Write acceptance criteria for your own deliverables before starting, not just to grade agent output.
- **counterargument-stress-test** -- Run on blog posts or proposals before publishing. Forces you to address counterarguments proactively.
- **decomposition-scorer** -- Evaluate a human team's sprint backlog for isolation boundaries. Works for human parallelism too.
- **gap-trace** -- Use as a sales qualification tool during discovery calls to demonstrate AI advisory value instantly.
- **claudemd-router** -- Apply the router pattern to any config-heavy system (nginx, CI/CD, Terraform). Universal principle.
- **failure-asymmetry** -- Test any runbook or documentation. If a human can follow it but automation can't, the doc has hidden assumptions.
- **open-loop-audit** -- Use for personal weekly reviews. Classify your own open loops to spot "simulated productivity."
- **video-to-skill** -- Extract SOPs from competitor product demos. Competitive intelligence through process extraction.
- **middleware-trap-detector** -- Audit non-AI automation (Zapier, n8n, IFTTT). Any workflow wrapping a broken process exhibits the same trap.

---

## Overlap Notes

Skills that cover similar ground (kept for different use cases):

| Pair | Distinction |
|------|-------------|
| **delegation-spec** vs **dispatch-handoff-brief** | delegation-spec patches tool weaknesses; dispatch-handoff-brief is a standard 7-section template |
| **arbitrage-audit** vs **gap-trace** | gap-trace is the 5-minute version; arbitrage-audit is the full engagement |
| **agent-architecture-audit** vs **agent-readiness-audit** | architecture-audit checks the agent's code (12 primitives); readiness-audit checks the repo the agent will work on (8 pillars) |
| **boot-tax-monitor** vs **token-burn-auditor** | boot-tax-monitor focuses on startup; token-burn-auditor covers the full session. Intentional trilogy with pre-turn-budget-guardian |
| **simulated-work-detector** vs **open-loop-audit** | simulated-work-detector audits agent fleet; open-loop-audit covers all loops including human |
| **platform-dependency-mapper** vs **mcp-portability-auditor** | dependency-mapper is broad (4 axes); portability-auditor is MCP-specific subset |
| **context-fork-guide** vs **context-hygiene** | fork-guide is specifically about `context: fork`; hygiene covers 3 broader techniques |

---

## How to Use These Skills

### Install a Single Skill

```bash
git clone https://github.com/m2ai-ultra-magnus-IF/skill-forge.git
cp -r skill-forge/skills/classify-agent ~/.claude/skills/
```

Restart Claude Code. The skill will be available as a slash command (`/classify-agent`) or auto-triggered by its description.

### Install All Skills

```bash
git clone https://github.com/m2ai-ultra-magnus-IF/skill-forge.git
cp -r skill-forge/skills/* ~/.claude/skills/
```

### Skill File Structure

```
skills/
  skill-name/
    SKILL.md              # The skill definition (frontmatter + phases)
    skill-registry.yaml   # Metadata sidecar (optional, for lifecycle tracking)
```

---

## How the Pipeline Works

1. **Source Monitoring** -- Checks configured content sources for new material since the last check
2. **Content Ingestion** -- Downloads content. For videos, uses Gemini's video understanding API
3. **Technique Extraction** -- Identifies discrete, reusable techniques that could become skills
4. **Skill Generation** -- Structures each technique into SKILL.md with frontmatter, phases, verification steps, source attribution
5. **Quality Evaluation** -- Ego evaluator (Gemini 2.0 Flash) scores skills on Correctness, Completeness, Clarity, Efficiency
6. **Human Review** -- Generated skills land as PRs for review before merging

## Project Structure

```
skill-forge/
  skills/               # 50 skills (cold archive + active)
  data/
    intake/             # Newsletter/content input staging
    skill_invocations.db # Invocation tracking (SQLite)
    last_check.txt      # Timestamp of last content source check
  src/                  # Pipeline source code
    build_registry.py   # Aggregates skill registries
    sync_hash.py        # Drift detection between repo and deployed
    scorecard.py        # Health score computation
    ego_evaluator.py    # LLM quality evaluation (Gemini)
    quality_rubric.py   # Quality scoring dimensions
    refinement_pipeline.py # Generates refinement proposals
  schema/               # JSON Schema for skill-registry.yaml
  templates/            # Skill generation templates
  tests/                # Pytest test suite
  registry.yaml         # Aggregated skill registry index
  BLUEPRINT.md          # Strategic design (5-phase roadmap)
```

## Contributing

Found a great AI walkthrough with a technique worth capturing? Open a PR with:

1. **Source link** -- URL to the video, article, or newsletter
2. **Technique summary** -- What the technique does in 1-2 sentences
3. **Proposed skill name** -- Short, descriptive kebab-case name

Or generate the skill yourself using the `video-to-skill` skill from this repo.

## License

MIT
