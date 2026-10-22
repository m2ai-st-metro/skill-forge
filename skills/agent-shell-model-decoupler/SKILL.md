---
name: agent-shell-model-decoupler
description: "Design a provider-swap layer for a fixed-UI AI agent product (a commercial or closed-source computer-use / coding-agent app) so the underlying LLM can be changed mid-session without losing the app's tools, permissions, file access, or chat history. Splits the app into an operating layer (execution, tool calls, sandbox, UI, transcript) and a decision layer (which model answers each turn), and routes requests to the decision layer before they touch the app's native model. Use when you want to keep a subscription product's UI, tools, and workspace but pay for or route to a different model provider (OpenRouter, a coding-agent SDK, another vendor's API key) behind it."
---

# agent-shell-model-decoupler

Most agent products (a boxed coding-agent app, a computer-use assistant, a chat product with sandboxed tool access) bundle two things that don't need to be bundled: the **operating layer** (sandbox/VM, file permissions, tool whitelist, screen or terminal control, chat transcript) and the **decision layer** (which LLM turns a message into a response and tool calls). This technique separates them so you can swap the decision layer's model/provider without rebuilding or losing the operating layer.

## Trigger

Use when someone says: "I like this agent app's tools/UI/permissions but not its default model", "how do I use my own API key / subscription inside this closed product", "can I swap the model behind this agent mid-conversation without losing context", "brain-in-a-jar for my agent app", or "make this agent product provider-agnostic."

## Prerequisites

- The target app must expose *some* interception point before a message reaches its native model: a config file, an installable plugin/router step, a terminal/shell the app grants you inside its own sandbox, or an documented extension mechanism. If there is truly no interception point (fully closed, no shell, no config, no plugin API), this technique does not apply — stop and say so.
- Credentials for the model(s) you want to route to (a model-aggregator API key, a coding-agent SDK login, or a direct provider API key).
- The app's minimum paid tier if authentication to the app itself is gated behind one — you're still using the app's operating layer, so you still need to be let in.
- Willingness to accept an unofficial integration: this rides on the app's current internal structure, is not vendor-supported, and can break on the app's next update.

## Complexity

High. This is a reverse-engineering and systems-integration task, not a config toggle. Budget for iteration and for the integration breaking on app updates.

## Phase 1: Confirm the split is possible

1. Identify the app's operating-layer surface: what does it manage that you want to keep? (sandbox/VM, tool permissions, file whitelist, chat history/transcript, UI).
2. Identify the app's decision-layer surface: where does a user message actually get handed to a model? Look for a per-conversation config, a "provider" or "model" setting, an installable extension point, or — as a fallback — a sandboxed shell/terminal the app itself grants you, which you can use to authenticate a separate CLI/SDK session independent of the app's own request path.
3. If no interception point exists at all, stop here and report that this technique doesn't apply to this app.

## Phase 2: Build the router

1. Build (or install) a small router component that: accepts the app's outgoing message, sends it to the chosen external provider/model instead of the app's native model, and returns the response in the format the app's operating layer expects.
2. Make the provider selection explicit and switchable per conversation or per "bot"/workspace (e.g. a `/provider <name>` command or a config field), not a single global default — different conversations may warrant different models (a research thread vs. a fast-response thread).
3. Preserve conversation continuity: the router must inherit the existing transcript/context when it takes over, not start a fresh session, or every model swap resets the conversation.
4. Keep the app's own tool-calling and permission checks in the loop for anything the operating layer controls (file access, screen/shell actions). The external model can request an action; the operating layer still approves or whitelists it. Do not grant the swapped-in model raw, unmediated access to the sandbox — that defeats the permissions the operating layer exists to provide.

## Phase 3: Handle the edges

- **Sub-agents/helpers spawned by the app itself** typically still run on the app's native model, not your router — only the top-level conversation that goes through your router benefits. Note this limitation to the user rather than promising full-stack model swap.
- **Cost tracking**: if routing to a metered provider (pay-per-token aggregator, a paid SDK), verify the swap is actually taking effect (check the provider's usage/balance before and after a request) rather than trusting the UI label.
- **Free/community model tiers** on aggregators are useful for low-stakes requests but are not reliable for latency or uptime — do not route anything time-sensitive to them by default.

## Verification

- A message sent through the router visibly used the external model (ask the model to self-identify, or confirm a balance/usage change on the external provider), not the app's default.
- Switching providers mid-conversation preserves prior context — the response references earlier turns correctly.
- Operating-layer permissions still gate tool actions requested by the swapped-in model; the model cannot bypass the app's file/tool whitelist.
- The integration is documented (what was intercepted, how, and its dependency on the app's current version) so it can be revisited when the app updates.

## Source

YouTube video transcript, Mark Kashef channel, published 2026-08-31: "How to Use ANY AI Model in GrokBot." Technique: decision-layer/operating-layer split enabling a fixed-UI agent product to run on a swapped-in model provider while retaining its native tools, permissions, and transcript.
