---
name: api-breaking-change-scanner
description: Scan a codebase for deprecated API call parameters that cause 400 errors when migrating between model versions (e.g., 4.6 → 4.7). Greps for known removed params (top_k, top_p, temperature, budget_tokens schema) with call-site context and fix recommendations.
---

# API Breaking Change Scanner

Greps a codebase for API call parameters that were removed or changed in a target model version, preventing silent 400 errors during migration.

## Trigger

Use when the user says "/api-breaking-change-scanner", "scan for breaking API changes", "check deprecated params", "pre-migration API scan", or when preparing to migrate model versions.

## Phase 1: Intake

Collect (or infer from context):
1. **Scan target** — directory to scan. Default: current working directory.
2. **Migration** — from-model → to-model (e.g., `claude-sonnet-4-6 → claude-opus-4-7`). Default: `any → claude-opus-4-7`.

Tell the user:
```
Scanning: {path}
Migration: {from} → {to}
```

## Phase 2: Built-in Breaking Change Manifest

The manifest lists known deprecated parameters per provider/version. Before applying any findings, the user should verify current deprecations against the current API documentation — this manifest covers the 4.7 migration as of 2026-04-21 and will go stale.

### Anthropic — claude-opus-4-7

| Parameter | Severity | Note |
|-----------|----------|------|
| `top_k` | BREAKING — 400 error | Removed. No replacement. |
| `top_p` | BREAKING — 400 error | Removed. No replacement. |
| `temperature` | BREAKING — 400 error | Removed for Opus 4.7. Still valid for Sonnet/Haiku. |
| `budget_tokens` | WARNING — verify | `thinking.budget_tokens` schema may have changed. Confirm structure against current API docs. |

**Note on temperature**: Only flag as BREAKING when the call target is confirmed as an Opus 4.7 endpoint. Flag as WARNING if the model reference is ambiguous or dynamic.

## Phase 3: Grep Scan

Run all four Grep calls **in parallel** using the Grep tool (not Bash). Use `output_mode: "content"`, `-n: true`, `-C: 3`.

**Grep 1 — top_k:**
```
pattern: "top_k\s*[:=]|[\"']top_k[\"']"
glob: "*.{py,ts,js,jsx,tsx,yaml,yml,json,toml}"
```

**Grep 2 — top_p:**
```
pattern: "top_p\s*[:=]|[\"']top_p[\"']"
glob: "*.{py,ts,js,jsx,tsx,yaml,yml,json,toml}"
```

**Grep 3 — temperature (in LLM call context):**
```
pattern: "temperature\s*[:=]|[\"']temperature[\"']"
glob: "*.{py,ts,js,jsx,tsx,yaml,yml,json,toml}"
```

**Grep 4 — budget_tokens:**
```
pattern: "budget_tokens\s*[:=]|[\"']budget_tokens[\"']"
glob: "*.{py,ts,js,jsx,tsx,yaml,yml,json,toml}"
```

Filter out paths containing: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `.git/`.

## Phase 4: Triage

For each match:

1. **Read context lines** to determine if the match is inside an LLM API call (look for `anthropic`, `messages.create`, `client.messages`, `claude`, `generate_content`).
2. **Classify**:
   - **BREAKING**: param is inside an Anthropic API call targeting Opus 4.7 (or targeting Opus generically)
   - **WARNING**: param is in a config dict or dynamic context — model target unclear
   - **FALSE POSITIVE**: param is unrelated (e.g., `temperature` in weather/physics code, `top_k` in a vector search config with no LLM context)

3. **Deduplicate**: config file + code that reads it → show both, mark config as the fix location.

## Phase 5: Report

```
=================================================================
API BREAKING CHANGE SCAN
=================================================================
Target:    {path}
Migration: {from} → {to}
Date:      {date}

BREAKING — will return 400 after migration:
  # File                    Line  Param        Evidence
  1 src/agent.py             42   top_k        anthropic.messages.create(..., top_k=0.9)
  2 src/config.py            18   temperature  model_params = {"model": "claude-opus-4-7", "temperature": 0.7}

WARNINGS — verify before migration:
  # File                    Line  Param          Note
  3 src/scorer.py            91   temperature    model target is dynamic — may or may not be Opus 4.7
  4 src/llm.py               33   budget_tokens  verify thinking param schema matches current API spec

SUMMARY
  Breaking:       {n}  (fix required before migration)
  Warnings:       {n}  (verify against current API docs)
  False positives:{n}  (noted, skipped)
  Files affected: {n}

RECOMMENDED ACTIONS
{numbered list — one action per BREAKING finding}

NOTE: Verify current deprecation list against API docs before applying changes.
      temperature is still valid for claude-sonnet-* and claude-haiku-*;
      only remove it from calls explicitly targeting Opus 4.7.
=================================================================
```

If zero findings: report clean with a one-liner and exit.

## Phase 6: Act

After displaying the report, offer:
- **"Apply safe fixes automatically?"** — only removes `top_k` and `top_p` from confirmed Anthropic call contexts (unambiguous BREAKING). Never auto-removes `temperature` (requires confirming model target).
- **"Walk me through each warning?"** — step through WARNING items one at a time.
- **"Save report to /tmp/api-breaking-change-scan-{date}.md?"**

Do NOT auto-apply `temperature` removals without model target confirmation — removing it from a Sonnet call would be wrong.

## What This Does NOT Do

- Does not check model ID validity — only checks call parameters.
- Does not check repo state, locks, or env vars.
- Does not scan runtime config fetched from external services.
- Does not auto-update `budget_tokens` schema — that requires reading the current API spec first.

## Source

Extracted from Nate Kadlac newsletter (2026-04-21): "Opus 4.7 is smarter, more literal, and quietly more expensive. Those are three different problems." Breaking params for Opus 4.7 migration: temperature, top_p, top_k removed; budget_tokens schema changed.
