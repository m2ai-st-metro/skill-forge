---
name: subscription-sdk-backend
description: "Power an internal, self-built tool (a vibe-coded app, dashboard, or automation) using a headless session of an AI coding subscription (via that provider's Agent SDK) instead of a separately metered API key. Eliminates double-paying for AI usage: once for the coding subscription that built the tool, again for a metered API key that runs it. Use when someone has built or is about to build an internal-only tool that needs LLM calls and already pays for an AI coding subscription (Claude Code, Codex, or similar) whose vendor SDK supports headless/programmatic use."
---

# Subscription SDK Backend

## Trigger pattern

Use this skill when someone:
- Has built (or is building) an internal tool — a meeting summarizer, analytics dashboard, thumbnail generator, file sorter, triage tool — that needs LLM calls
- Already pays for an AI coding subscription (e.g. Claude Code, Codex) and does not want a second, separately metered API key just to run that tool
- Wants the tool to run for personal or internal team use only (not to be resold or exposed as a public SaaS)

## Prerequisites

- An active AI coding subscription whose provider ships an Agent SDK supporting headless/programmatic sessions authenticated against that existing subscription (not a separate API key)
- Read the provider's terms of service for that SDK before building: headless-subscription use is typically authorized for internal/personal tooling only, not for reselling access or building a commercial product on top of someone else's subscription seat
- An AI coding agent to help scaffold the bridge code

## Complexity

Intermediate — the core swap is small, but getting agent-to-agent authorization and headless invocation right requires care.

## Procedure

1. **Identify the layer being replaced.** In a normal vibe-coded internal tool, "click a button" -> "call a metered API with its own key and billing" is the flow. This skill replaces only that one layer: the API-key-and-meter call becomes a call through the coding subscription's own SDK.

2. **Confirm the SDK supports headless/subscription auth.** Look for the provider's Agent SDK documentation describing how to construct a session with no explicit API key — it should authenticate using the existing local subscription login/session rather than a token you pass in code.

3. **Instruct your coding agent explicitly to use the SDK as the backend**, not an API key. State the constraint directly in the build prompt, e.g.: "All AI calls in this app go through the [provider] SDK using my existing subscription login. Do not ask for or hardcode an API key; the SDK should find its own authorization automatically."

4. **Scaffold the bridge.** Have the agent write a thin server-side module that:
   - Constructs the SDK client with no explicit credentials (letting it pick up the local subscription session)
   - Accepts a request from your app's frontend/CLI
   - Spins up a headless SDK session in the background to service that one request
   - Returns the result to the caller

5. **Reuse for every capability the subscription offers.** If the underlying subscription's models can do more than text (e.g. also generate images), the same SDK bridge can serve those requests too — swap the call type, not the auth layer.

6. **Set effort/model tier per call.** Route cheap, high-volume calls (e.g. classification, sorting) to a lower-cost model/effort tier and reserve higher tiers for calls that need it, since you're now paying via subscription usage/limits rather than per-token billing.

7. **(Optional) Share the tool internally over a private network** (e.g. a mesh VPN like Tailscale) rather than deploying it publicly, keeping it inside the "internal/personal use" scope the SDK's terms of service require.

## Verification

- Confirm the running app makes zero calls to a metered, separately-billed API key — check outbound network calls or provider dashboards to verify no external API key usage is being charged
- Confirm the app still functions end-to-end (request in, generated result out) using only the subscription-backed SDK session
- Re-read the SDK's terms of service and confirm the deployment is internal/personal use only, not a public-facing service built on someone else's subscription

## Common pitfalls

- Building this for a public-facing or resold product — most providers' subscription SDKs explicitly prohibit this in their terms of service
- Forgetting to tell the coding agent explicitly not to fall back to an API key; without an explicit instruction it may default to the more familiar API-key pattern
- Assuming every subscription tier or plan includes headless SDK access — confirm the specific plan supports it before building around it

## Source attribution

- Derived from a YouTube video by Mark Kashef (channel ID `UCHkzp52CldSPZqU5T49mOnA`), published 2026-08-19, demonstrating internal tools (a meeting analyzer, a social analytics dashboard) powered by a headless coding-subscription SDK session instead of a metered API key.
