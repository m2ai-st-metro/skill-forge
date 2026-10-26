---
name: gemini-rescue
description: Get a second opinion from Google Gemini on the current diff, plan, or problem. Use when Claude is stuck, when an implementation needs adversarial review by a different vendor, or when a 1M-context audit is needed that Claude can't fit. Sibling to /codex:rescue but with Gemini as the second vendor. Trigger on "second opinion", "rescue with Gemini", "let Gemini review this", "adversarial review", "1M-context audit", "/gemini-rescue".
---

# gemini-rescue

Hand off the current problem to Google Gemini for an independent read. Two modes — pick the one that matches the task.

## When to use

- **Adversarial review**: Claude has a plan or implementation that looks right but is high-blast-radius (auth, migrations, payments, infra). Get an uncorrelated reviewer.
- **Stuck**: Claude has tried 2+ angles and is going in circles. A second vendor often sees a different path.
- **1M-context audit**: The codebase or document is larger than fits in Claude's context. Gemini 2.5 Pro handles 1M tokens natively.
- **NOT for**: simple lookups (use Claude directly), Gemini-specific features (call the SDK directly), or tasks where you already know Gemini-2.5-Flash won't add signal.

## Vendor preflight (mandatory, before round 1)

Before the first `mcp__gemini__gemini_ask`/`mcp__gemini__gemini_run` of any review loop,
fire a 1-token probe: `mcp__gemini__gemini_ask` with prompt `Reply with the single word OK`.
Anything but a healthy reply
means Gemini is DOWN — say so explicitly, record the failure in the session output,
and fall back to Codex (`/codex:rescue`), or to the all-Claude Judge
(`/self-healing-claudex` in `claude-judge` reviewer mode) if Codex is also dead. Probe
Codex on the EXACT flag path
you will invoke it with, not just auth. If you will run it with
`--dangerously-bypass-approvals-and-sandbox` (as `run-codex-review.sh` does), probe
with that flag — NOT `--sandbox workspace-write`: on kernel-6.17 + AppArmor
(`apparmor_restrict_unprivileged_userns=1`) the bwrap sandbox modes fail
(`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, still exit 0) while
the bypass path works. Probing the wrong mode false-reports Codex DOWN (2026-07-04
saw the sandbox dead; 2026-07-22 diagnose confirmed the bypass path is alive).
A two-vendor loop with one dead vendor is silently a one-vendor loop.

## Two modes

### Mode A — One-shot review (`gemini_ask`)

For diff or plan review, classification, scoring, structured output. Fast, cheap, stateless. **Claude stays the orchestrator.**

Call the `mcp__gemini__gemini_ask` MCP tool with:
- `prompt`: the full review prompt (include the diff/plan/problem inline)
- `system_prompt`: role framing (e.g., "You are an adversarial code reviewer. Find what's wrong, not what's right.")
- `model`: optional override (default is set in the MCP server env)
- `temperature`: lower for review, higher for brainstorming

Treat the response as one opinion, not ground truth. Cross-reference with the actual code.

### Mode B — Agentic dispatch (`gemini_run`)

For tasks where you want Gemini to *do the work itself* — read files, navigate the repo, propose patches. Slower, more expensive, but you get a full second agent.

Call the `mcp__gemini__gemini_run` MCP tool with:
- `task`: the full task description (include any file paths Gemini should read)
- `cwd`: working directory Gemini should operate in
- `timeout_seconds`: hard kill (default 300)
- `output_format`: `text` or `json`

Use this for 1M-context audits, parallel agent-on-agent work, or when you'd otherwise spawn a Codex rescue.

## After the rescue

1. Read Gemini's response critically — it can hallucinate, miss context, or just be wrong.
2. Verify any specific claims (function names, file paths, model IDs) against the actual code.
3. If Gemini surfaced something Claude missed, name what it caught and why Claude missed it — that's the value of vendor orthogonality.
4. Do NOT auto-apply Gemini's patches. Treat them as suggestions, the same way you'd treat a teammate's review.

## Related

- `/codex:rescue` — same idea, OpenAI as the second vendor. Use Codex for code-specific problems where GPT excels; use Gemini for long-context, multimodal, or when Codex has already been tried.
- The gemini-mcp server lives at `~/projects/infra/gemini-mcp/` and is registered at user scope via `claude mcp add gemini ...`. Also registered for ccos via `~/projects/agents/claudeclaw-os/.claude/settings.json`.
- This skill is the **primary sponsoring callsite** for gemini-mcp under the 14-day adoption gate. If `/gemini-rescue` doesn't see use within 14 days of creation, both the skill and the MCP server need re-evaluation.
