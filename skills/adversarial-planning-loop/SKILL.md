---
name: adversarial-planning-loop
description: Runs a plan through an adversarial second model that attacks it until it has nothing left to say, then gates execution on survival. Use before implementing any non-trivial feature, architecture decision, or task sequence where a wrong plan is expensive. Trigger phrases: "stress test my plan", "adversarial planning", "Codex audit", "have a second model review this plan", "plan until it holds".
---

# Adversarial Planning Loop

Before writing a single line of code, subject the plan to a model acting as ruthless auditor.
Iterate until the adversary is silent. Only then execute.

## When to Invoke

- User says "stress test this plan", "adversarial planning loop", "have a second model review this"
- Plan involves non-trivial state (auth, data migrations, multi-service integration)
- Feature has known edge cases or the user has already been surprised by this codebase
- Prior attempts at direct implementation failed or drifted

## Phase 1: Plan Generation

Ask the user (or infer from context) the scope:

1. **What are we building?** One-paragraph description of the feature or change.
2. **Success criteria** — what does done look like, measurably?
3. **Known constraints** — existing interfaces, backwards compatibility, performance budget.

Generate or accept a structured plan:

```
## Plan: {feature}

### Goal
{one paragraph}

### Approach
{numbered steps}

### Assumptions
{list things the plan takes for granted}

### Edge cases considered
{explicitly list; "none" is not acceptable}

### Out of scope
{explicit exclusions prevent scope creep}
```

## Phase 2: Adversarial Review Pass

Shift to an adversarial stance. Attack the plan as a senior engineer who has seen this exact pattern fail before. For each attack:

1. **State the failure mode** — what breaks, under what conditions, for which users
2. **Assign severity**: BLOCKER / SIGNIFICANT / MINOR
3. **Assign likelihood**: PROBABLE / POSSIBLE / EDGE CASE
4. **Cite the assumption violated** — which plan assumption does this break?

Attack categories to cover systematically:

- **Concurrency / race conditions** — what if two requests interleave?
- **Missing error path** — what happens when the third-party call fails?
- **Data integrity** — what's the rollback story? What if the job is interrupted mid-write?
- **Implicit dependency** — does this plan assume something about state that isn't guaranteed?
- **Scope creep vector** — which "simple" step is actually 3 steps?
- **Testing gap** — which step is hardest to test and why?
- **Performance cliff** — at what scale does this plan break?

If no BLOCKER or SIGNIFICANT issues remain, exit to Phase 3. Otherwise, loop.

## Phase 3: Plan Revision

Revise the plan to address every BLOCKER and every SIGNIFICANT issue with likelihood PROBABLE or higher.

For each revision:
- State which attack it addresses
- State what changed in the plan
- Confirm the attack no longer applies to the revised plan (or explicitly acknowledge residual risk)

## Phase 4: Survival Gate

Before execution, confirm:

```
### Plan Survival Summary
Rounds of adversarial review: N
Blockers found: X (all resolved)
Significant issues found: Y (Z resolved, W accepted as residual risk)
Minor issues found: P (not blocking)

Explicit residual risks accepted:
- {risk}: {why we accept it}

Plan approved for execution: YES / NO
```

Only proceed to implementation if "Plan approved: YES". If NO, loop back to Phase 2.

## Phase 5: Execution Handoff

Produce a clean, revised plan document. This becomes the implementation spec:
- Numbered steps, each with a testable exit criterion
- Residual risks called out as inline warnings (not buried in history)
- "Do not implement" list: anything explicitly out of scope

## Verification

- [ ] At least one adversarial round was completed (zero attacks is a failed review, not a passing one)
- [ ] Every BLOCKER was resolved or explicitly accepted with a named owner
- [ ] Residual risks are documented, not silently dropped
- [ ] Final plan has numbered steps with exit criteria

## Source

Mark Kashef — "You Can Run Claude AND Codex Together. Here's How." (2026-04-26)
https://www.youtube.com/watch?v=Fu5KIG2Jm1g

The pattern extracted: use a second model as a ruthless adversarial auditor (Kashef calls it "the master surgeon") that grinds a plan down until it has nothing left to say, then gates execution on survival. Originally demonstrated using the OpenAI Codex Claude Code plugin, but the adversarial loop itself is model-agnostic.
