---
name: tie-breaker
description: Use when Claude Code and Hermes (or any two models/agents) disagree on how to clear a blocker and a human needs a plain-language tie-breaker page. Trigger on "tie-breaker", "/tie-breaker", "break the tie", "Claude and Hermes disagree", "two models recommend different things", or any time two agents or vendors have given conflicting recommendations about a blocker, decision, or fix, even if the user does not say "tie-breaker".
allowed-tools: Bash, Read, Write, Agent, AskUserQuestion
model: sonnet
---

# tie-breaker

Two agents or vendors disagree on how to clear a blocker. This skill does not pick a winner. It restates the disagreement in plain language, synthesizes two middle-ground options, and publishes a page on the CCOS Bunker so Matthew makes the call.

Experimental under the 14-day adoption gate: created 2026-08-29, review 2026-09-12. STANDS ALONE: gemini-rescue/codex:rescue give one second opinion; this skill adjudicates between two existing opinions for a human.

## Inputs

- The blocker or issue statement.
- Model A: name, recommendation, reasoning (paste text or a file path).
- Model B: name, recommendation, reasoning.
- If a side's position is missing, get it:
  - **Hermes**: `hermes chat -Q -q "<prompt>" --reasoning medium` (Bash, one-shot; prints a session_id then the answer).
  - **Claude**: reason inline, or dispatch an Agent for a fresh independent take.
  - Gemini/Codex are optional third opinions via `/gemini-rescue` or `/codex:rescue`, never required.

## Procedure

1. **Restate the blocker in layman's terms.** No jargon. Assume a smart non-engineer reader.
2. **Present each side's recommendation in plain language**: what it does, why that model thinks so, what it costs or risks, what could go wrong.
3. **Synthesize exactly two middle-ground options** built from the two recommendations (e.g. sequence A then B with a checkpoint, or take A's mechanism with B's safeguard). Each option needs: a one-line summary, ordered steps, tradeoffs, who does what, and how to reverse it.
4. **Build a comparison table**: effort, risk, reversibility, speed, and which model would object and why.
5. **Add a "what I would pick and why" line from Claude**, clearly labeled as opinion, not a decision.
6. **Render and publish:**
   - Fill a JSON file matching `assets/example.json`'s shape.
   - Run `node scripts/render-tiebreaker.mjs <input.json> <output.html>`, writing the HTML to `/home/apexaipc/outputs/tie-breaker/<YYYY-MM-DD>-<slug>.html`.
   - Publish: `node ~/projects/agents/claudeclaw-os/scripts/bunker-add.mjs --title "Tie-breaker: <slug>" --task "<issue id if any>" --tags tie-breaker,<slug> <file>`.
   - Report the Bunker URL the command prints. Never a localhost URL; the dashboard lives at 10.0.0.46.
7. **Print a short terminal summary** (about 5 lines): the two middle-ground options and the Bunker link. Then stop and wait for Matthew's pick. This skill never executes the chosen option itself.

## Writing rules

- No em-dashes anywhere, in the JSON content or the rendered HTML.
- Plain language throughout: this page is for a decision, not a technical audit.
- The JSON is the source of truth for layout; do not hand-write HTML for a real run, always go through `render-tiebreaker.mjs` so every tie-breaker page looks the same.

## JSON contract

See `assets/example.json` for a complete worked example. Top-level keys:

```json
{
  "issue": "plain-language restatement of the blocker",
  "models": [
    { "name": "...", "recommendation": "...", "reasoning": "...", "risks": "..." }
  ],
  "middle_ground": [
    { "title": "...", "summary": "...", "steps": ["..."], "tradeoffs": "...", "who": "...", "reversal": "..." }
  ],
  "comparison": [
    { "option": "...", "effort": "...", "risk": "...", "reversibility": "...", "speed": "...", "objection": "..." }
  ],
  "claude_pick": "one paragraph, clearly labeled as opinion"
}
```

`models` normally has exactly two entries (A and B); a third opinion from Gemini or Codex can be appended as a third entry if one was gathered. `middle_ground` must have exactly two entries per Matthew's spec.

## What this skill does not do

- It does not execute the chosen option. It stops after publishing and reporting the link.
- It does not run evals or the skill-creator eval loop.
- It is not a general second-opinion tool; that's `/gemini-rescue` or `/codex:rescue`, which produce one opinion, not an adjudication between two existing ones.
