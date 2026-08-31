---
name: ai-audit
description: Run a structured AI implementation audit conversationally — collect contact, business, workflow, data, and AI-plan inputs across 6 sections, then generate a Markdown recommendation report (top-3 implementations ranked by ROI for the stated budget, named tools/vendors, 30/60/90-day rollout, two highest-impact data-quality blockers). Use when Matthew says "/ai-audit", "run an AI audit", "audit a client for AI", or during a discovery call where structured intake helps. Output is a Markdown report; routes optionally through AIN (proposal context), RepMan (client follow-up), or LeadGen (qualification scoring).
---

# AI Audit Skill

## Origin & status

Repurposed 2026-04-30 from a Cowork Live Artifact port plan (originally `m2ai-archive/ai-audit`, a Bolt-scaffolded React form wizard that collected the same 6 sections of input but only `console.log`'d the result with no LLM call). Rationale for skill-not-artifact: a chat-pasted form wizard is worse UX than conversational intake, and a skill can route the recommendation through Matthew's existing client-facing agents instead of dead-ending in a Cowork sandbox that the actual client (the audit subject) can't see.

**14-day adoption gate**: experimental until **2026-05-14**. Survives only if Matthew runs it 3+ times (real client or mock), or if an active agent (e.g. AIN, RepMan) lists it in their manifest. If neither happens, delete this skill.

## When to trigger

- `/ai-audit` (explicit invocation)
- "run an AI audit on [client]"
- "audit [company] for AI implementation"
- "let's do a discovery call intake for [client]"
- During an in-progress client conversation when Matthew asks for structured intake

Do NOT trigger on: generic questions about AI ("what AI tool should I use?"), code reviews, or model selection — those are different surfaces.

## Required inputs (collected conversationally, one section at a time)

The skill walks 6 sections in order, asking for each field. Skip fields the user has already answered earlier in the conversation. After each section, summarize back what was captured before moving to the next — gives Matthew a chance to correct in flight.

```ts
type AuditData = {
  email: string;
  timestamp: string;  // ISO 8601, set automatically
  business_overview: {
    company_name: string;
    industry: 'Software Development' | 'Healthcare' | 'Finance' | 'E-commerce'
            | 'Manufacturing' | 'Education' | 'Real Estate' | 'Consulting'
            | 'Marketing' | 'Other';
    employees: '1-10' | '11-25' | '26-50' | '51-100' | '101-500' | '500+';
    goals: string[];  // multi-select from BUSINESS_GOALS below
  };
  workflow_analysis: {
    tasks: { description: string; frequency: string; time_per_instance: string }[];
  };
  data_infrastructure: {
    data_sources: string[];  // multi-select from DATA_SOURCES below
    source_details: Record<string, string>;  // free-text per source
    data_quality: 'Excellent' | 'Good' | 'Mixed' | 'Poor';
    willing_to_improve: boolean;
  };
  ai_implementation: {
    interested_tools: string[];  // multi-select from AI_TOOLS below
    budget: number;  // USD, range 5000–100000+
    implementation_preference: 'Gradual rollout with pilot programs'
                             | 'Full implementation across all departments'
                             | 'Start with one department and expand'
                             | 'Proof of concept first';
    compliance_needs: string;  // free-text, e.g. "GDPR, SOC 2"
  };
};

const BUSINESS_GOALS = [
  'Increase operational efficiency', 'Reduce manual data entry',
  'Improve customer response times', 'Scale business operations',
  'Reduce costs', 'Improve data accuracy',
  'Enhance customer experience', 'Automate repetitive tasks',
];
const DATA_SOURCES = [
  'CRM System (HubSpot, Salesforce)', 'Google Sheets/Excel',
  'Payment Systems (Stripe, PayPal)', 'Support Platforms (Zendesk, Intercom)',
  'Website Contact Forms', 'Email Marketing Tools',
  'Social Media Platforms', 'Database Systems',
];
const AI_TOOLS = [
  'Chatbots for customer support', 'Automated lead scoring',
  'Document processing', 'Email automation',
  'Data analysis and reporting', 'Predictive analytics',
  'Content generation', 'Process automation',
];
```

## Conversational flow

1. **Contact** — ask for the audit subject's email. One question.
2. **Business overview** — ask company name, industry (offer the list), employee size band (offer the bands), and main business goals (multi-select from `BUSINESS_GOALS`, also accept free-text additions).
3. **Workflow analysis** — ask for 1–5 repetitive tasks. For each: description, frequency (daily/weekly/monthly), rough time per instance. Stop when the user says "no more" or after 5.
4. **Data infrastructure** — ask which data sources they currently use (multi-select from `DATA_SOURCES`). For each selected, ask one follow-up: "anything specific about how you use [source] today?" Then ask data quality (Excellent/Good/Mixed/Poor) and willingness to improve.
5. **AI implementation preferences** — ask which AI tool categories interest them (multi-select from `AI_TOOLS`), budget range (5K–100K+), implementation preference (offer the four options), and compliance constraints (free-text).
6. **Review** — print back the full `AuditData` payload as a labelled summary. Ask: "Ready to generate the recommendation, or revise a section?"

After confirmation, call the recommendation prompt below.

## Recommendation prompt template

Pass `AuditData` to Claude with this exact prompt:

> You are an AI implementation consultant. Based on the audit payload below, produce a Markdown report containing exactly four sections:
>
> 1. **Top 3 AI implementations** ranked by ROI given the stated budget. For each, justify the ranking with a one-sentence ROI rationale tied to the company's stated goals.
> 2. **Specific named tools/vendors** for each implementation — no generic categories. If multiple vendors fit, name 2–3 with a short comparison.
> 3. **A 30/60/90-day rollout plan** that respects the stated implementation preference. Include exit criteria for each phase.
> 4. **Two highest-impact data-quality blockers** to address first, given the stated data sources and quality level.
>
> Be concrete. Use the company name throughout. No fluff, no boilerplate caveats. If the budget is unrealistic for the goals, say so directly in section 1.
>
> ```json
> { ...AuditData... }
> ```

## Output format

A single Markdown report with the four sections above. Save it to `~/vault/clients/<company-slug>/ai-audit-<YYYY-MM-DD>.md` and offer to also:
- Hand off to **AIN** if there's a matching open proposal listing.
- Hand off to **RepMan** if the audit subject is an existing client (check `~/vault/clients/`).
- Hand off to **LeadGen** to score the qualification.
- Push to Perceptor via `/vault-push` if it should be accessible from Claude Desktop.

## Follow-up routing (turn the report into work)

The handoffs above are the routing block — make them explicit rather than letting the report
dead-end. After saving, close with one line per applicable route:

- **AIN** -> if there is a matching open proposal listing (proposal context).
- **RepMan** -> if the audit subject is an existing client (check `~/vault/clients/`).
- **LeadGen** -> to score qualification.
- **Perceptor** (`/vault-push`) -> if it should be reachable from Claude Desktop.
- **Client follow-up actions** -> the report's 30/60/90 plan and the two data-quality blockers
  are the client's bounded work; if Matthew commits to driving any of it, capture it via
  `goal-maker` with owner/sink/kill (a reminder to "check on the rollout" with no owner/sink/kill
  is an orphan loop). HIL gate stands: Matthew reviews before any external send.
- **No action** -> if none of the routes apply (mock run, internal practice), say so explicitly
  so silence is not mistaken for a missed handoff.

## What this skill does NOT do

- Multi-tenant intake (one audit per session).
- Persistent in-progress state across sessions — if Matthew quits midway, the partial audit is lost. If this becomes a real problem, layer in `~/vault/clients/<slug>/ai-audit-draft.md` checkpointing.
- Sending the recommendation to the client — Matthew always reviews before any external send.

## Provenance

- Original React app: `m2ai-archive/ai-audit` (53KB, Vite+TS+Tailwind, last pushed 2025-07-22).
- Original port plan: `/home/apexaipc/projects/fork-playbook-cowork-spike/ai-audit-port-plan.md` (now superseded by this skill).
- Cowork Live Artifact port deliberately **not pursued** — see the original plan's "Reality check on the source" section for context.
