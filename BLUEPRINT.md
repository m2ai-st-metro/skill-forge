# BLUEPRINT — Skill Forge Dynamic Lifecycle

> Strategy brief: `vault/projects/skill-forge-lifecycle-strategy-2026-03-30.md`
> Status: PHASE 2a COMPLETE (2026-03-30)
> Reviewed: 2026-03-30 (aligned with st-agent-registry patterns post Phase 1-3 completion)

## Vision

Skills are first-class citizens with the same rigor as agents — registered, versioned, measured, reviewed, and refined through a closed loop: **AutoResearch scouts → Forge builds/refines → Sky-Lynx + scorecard measures**.

## Design Principles

1. **Mirror st-agent-registry patterns** — YAML sidecar files, sync hashes, learning blocks. Skills and agents share the same ecosystem conventions.
2. **Reuse Metroplex patch infrastructure** — `SkillUpgradePatch` follows the same contract pattern as `AgentUpgradePatch`. Sky-Lynx proposes, Metroplex applies.
3. **No premature abstraction** — registry lives in skill-forge until a second producer emerges.

---

## Phase 1: Skill Registry & Lifecycle State (COMPLETE)

**Goal:** Replace flat-file skill storage with a structured, queryable registry.

### Deliverables
- [x] **Skill registry schema** — YAML sidecar per skill (`skill-registry.yaml`) alongside each `SKILL.md`, mirroring st-agent-registry's `registry.yaml` pattern:
  ```yaml
  name: context-hygiene
  version: "1.0.0"
  status: active  # draft | active | under_review | refined | deprecated
  created: "2026-03-21"
  last_reviewed: null
  sync_hash: null  # SHA256 of deployed SKILL.md vs repo — detects drift

  source:
    type: youtube  # youtube | newsletter | community | autoresearch
    url: "https://youtube.com/watch?v=..."
    author: "Mark Kashef"
    date: "2026-03-19"

  taxonomy:
    domain: context-management
    complexity: beginner  # beginner | intermediate | advanced

  metrics:
    invocations_30d: 0
    last_invoked: null
    manual_rating: null
    health_score: null

  learning:
    total_patches_applied: 0
    total_patches_proposed: 0
    last_patch_at: null
    effectiveness_score: null

  lineage:
    parent_version: null
    derived_from: null
    changelog: []

  dependencies: []
  ```
- [x] **Lifecycle states**: `draft` → `active` → `under_review` → `refined` → `deprecated`
- [x] **Registry index** — aggregated `registry.yaml` at repo root for quick catalog queries
- [x] **Backfill existing skills** — 18 skills backfilled (17 active, 1 draft)
- [x] **Sync hash implementation** — `src/sync_hash.py` detects drift between `~/.claude/skills/` and repo
- [x] **Forge pipeline update** — skill creation now produces `skill-registry.yaml` + `SKILL.md` together

### Design Decisions (Resolved)
- **Manifest format**: YAML sidecar (`skill-registry.yaml`), matching st-agent-registry's `registry.yaml` convention. Not JSON, not frontmatter.
- **Registry index consumers**: Forge review pass, Sky-Lynx analysis, AutoResearch (catalog awareness), future marketplace.

---

## Phase 2a: Invocation Tracking & Health Scorecard (COMPLETE)

**Goal:** Capture skill usage data and compute health scores from proxy metrics.

### Deliverables
- [x] **Invocation hook** — PostToolUse hook on `Skill` matcher
  - Script: `~/.claude/scripts/log-skill-invocation.sh`
  - Extracts skill name from `$CLAUDE_TOOL_INPUT` JSON, writes to SQLite
  - 5s timeout, exit 0 always (never blocks session)
- [x] **Invocation database** — `data/skill_invocations.db`
  - Table: `skill_invocations` (id, skill_name, invoked_at, session_id)
  - Indexed on skill_name and invoked_at
  - Init script: `src/init_db.py`
- [x] **Health scorecard** — `src/scorecard.py`
  - Formula: invocations 40% + staleness 20% + deployed 20% + manual_rating 20%
  - When manual_rating is null, weight redistributes (50/20/30/0)
  - `--update` writes health_score + invocations_30d to registry files
  - `--threshold N` flags underperformers (default: 30)
- [x] **Forge audit command** — `audit-skills` section added to Forge CLAUDE.md
  - Runs scorecard, decides action per flagged skill (deploy, refine, deprecate)

### Design Decisions (Resolved)
- **Hook type:** PostToolUse on Skill — fires after skill loads, confirms actual invocation
- **Storage:** Centralized SQLite DB, synced to registry on scorecard run
- **Threshold:** 30/100 to start — tunable as data accumulates
- **Staleness decay:** 60-day window (100 at creation → 0 at 60 days)

---

## Phase 2b: Patch Pipeline & Sky-Lynx Integration

**Goal:** Close the refinement loop — Sky-Lynx proposes patches, Metroplex applies them.

> **Prerequisite:** Phase 2a operational with meaningful invocation data (2+ weeks).

### Deliverables
- [ ] **Completion signal** — heuristic for successful skill invocation
  - Positive: conversation continues normally after skill
  - Negative: user `/clear`, overrides skill output, abandons mid-skill
  - Rough proxy — accuracy improves with Ego in Phase 4
- [ ] **`SkillUpgradePatch` contract** — mirrors `AgentUpgradePatch` from st-agent-registry:
  - Defined in st-records as a shared contract (same pattern as agent patches)
  - Fields: skill_name, patch_type (content | metadata | taxonomy), section, action (add | replace | remove), content, rationale
  - Stored in `skill_patches` table (Metroplex DB, alongside `agent_patches`)
  - Sky-Lynx proposes patches → Metroplex Gate 3 applies them → registry.yaml `learning` block updated
- [ ] **Sky-Lynx integration** — skill health data available in Sky-Lynx analysis, skill patches proposed alongside agent patches

### Design Decisions to Make
- Patch auto-apply — should `SkillUpgradePatch` follow the same `auto_apply_threshold` pattern from department learning policies?
- Completion signal accuracy — how reliable is the proxy before Ego?

---

## Phase 3: AutoResearch Integration

**Goal:** Give AutoResearch a focused mission as Forge's scout.

### Deliverables
- [ ] **AutoResearch brief document** — explicit research targets:
  - Skill gap detection (community signals for unmet needs)
  - Competitive scanning (other skill/prompt repos, Cursor rules, etc.)
  - Source freshness checks (are existing skill sources still valid/current?)
  - Breaking change detection (API/SDK updates affecting skills)
- [ ] **Output format spec** — structured findings that Forge's intake can consume
  - New skill candidates → Forge INGEST pipeline
  - Refinement signals for existing skills → flag in registry
  - Project-scale discoveries → route to IdeaForge (not skill-forge)
- [ ] **AlienPC cron update** — AutoResearch nightly job uses the new focused brief
- [ ] **Intake integration** — Forge processes AutoResearch findings alongside YouTube/newsletter sources

### Design Decisions to Make
- AutoResearch output format — JSON findings file? Direct DB write? Git commit to a shared intake dir?
- How does AutoResearch know the current skill catalog? Read registry.json? API call?
- Rate limiting — how much community scanning is too much per nightly run?

---

## Phase 4: Ego Quality Judge

**Goal:** Replace proxy metrics with LLM-evaluated skill quality.

> **Prerequisite:** Phases 1-3 operational. Ego project unpaused and adapted.

### Deliverables
- [ ] **Quality rubric** — what makes a skill output "good"?
  - Correctness — does it produce working code/config?
  - Completeness — does it cover the technique end-to-end?
  - Clarity — are instructions unambiguous?
  - Efficiency — does it avoid unnecessary steps or token waste?
- [ ] **Ego skill evaluator** — mutation-evaluation loop applied to skills
  - Input: skill definition + sample invocation context
  - Output: quality score + specific improvement suggestions
  - Feeds back to Forge for refinement
- [ ] **Automated refinement pipeline** — Ego identifies weakness → Forge drafts improvement → PR for review
- [ ] **Scorecard upgrade** — Ego quality score added to health scorecard (high weight)

### Design Decisions to Make
- Ego execution model — local Ollama (AlienPC), cloud LLM, or hybrid?
- Judgment cadence — every invocation? Periodic batch? On-demand?
- Auto-merge threshold — can Ego-suggested minor improvements skip human review?

---

## Phase 5: Marketplace Readiness (Phase H Alignment)

**Goal:** Skill registry and quality system ready to power external distribution.

> **Prerequisite:** Phases 1-4 stable with meaningful data.

### Deliverables
- [ ] **Public catalog generation** — registry.json → browsable skill catalog
- [ ] **Packaging** — skills exportable as standalone installable units
- [ ] **Quality badge** — health score visible to consumers (active, high-quality, deprecated)
- [ ] **Taxonomy navigation** — browse by domain, complexity, product category
- [ ] **Distribution channels** — GitHub (free/SEO), paid packs (Gumroad/Lemon Squeezy)

---

## Dependencies & Constraints

| Dependency | Blocks | Status |
|-----------|--------|--------|
| Claude Code hook system | Phase 2 (invocation tracking) | Available, needs design |
| st-agent-registry Phase 3 (patch pipeline) | Phase 2 (`SkillUpgradePatch` reuse) | COMPLETE (2026-03-30) |
| st-records contracts | Phase 2 (`SkillUpgradePatch` contract definition) | Available, needs new contract |
| Metroplex Gate 3 | Phase 2 (patch application) | COMPLETE for agents, needs skill extension |
| AutoResearch cron on AlienPC | Phase 3 | Running, needs refocus |
| Ego project | Phase 4 | PAUSED since 2026-03-14 |
| Phase H marketplace decision | Phase 5 | On L5 roadmap, not started |

## Not In Scope

- Replacing Sky-Lynx — it continues as the analytics/recommendations layer
- Building a second skill producer — Forge is the only producer for now
- Standalone registry repo extraction — revisit only if a second producer emerges
- Rebuilding patch infrastructure — reuse `AgentUpgradePatch` patterns from st-agent-registry
