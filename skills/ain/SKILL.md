---
name: ain
description: Draft proposal responses for the AI Expert Network. Analyzes a client listing, matches portfolio projects, assesses competency gaps, and generates answers to the 3 standard application questions (experience, approach, availability). Use when Matthew says "/ain" or mentions writing a proposal response for the expert network.
user_invocable: true
model: sonnet
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# AIN -- AI Expert Network Proposal Responder

## When to Use

Activate when Matthew:
- Types `/ain`
- Asks to draft a proposal response for the expert network
- Mentions a new referral partner opportunity

## Workflow

### 1. Intake the Proposal

Ask Matthew to paste the raw proposal text. Say:

> Paste the proposal listing and I'll draft responses to the 3 standard questions.

Wait for the pasted text before proceeding.

### 2. Analyze the Proposal

Parse the proposal to identify:
- **Client industry** and domain context
- **Core deliverables** (what they actually need built/evaluated) -- list EVERY distinct initiative
- **Required skills** and tech stack mentioned
- **Any constraints** (timeline, compliance, existing tools)

### 3. Read Portfolio and Defaults

Read these files to inform the response:
- `/home/apexaipc/projects/ai-expert-network/portfolio.md` -- curated project list
- `/home/apexaipc/projects/ai-expert-network/defaults.md` -- availability and reusable defaults

Also check Claude Code memory for any relevant project context that adds depth beyond the portfolio file.

If a prior `/ai-audit` discovery report exists for this client or domain (check `/home/apexaipc/projects/ai-expert-network/` and any saved ai-audit Markdown reports), read it. The `/ai-audit` skill produces ROI-ranked implementation recommendations and a 30/60/90 rollout from a structured discovery intake, richer client-specific context than the raw listing. Use it to ground Q2 (Approach) in the client's actual stated workflow and data blockers rather than generic discovery questions. `/ai-audit` is the upstream discovery step; AIN is the proposal step that consumes its output.

### 3b. Competency Assessment

For EACH distinct initiative identified in step 2, rate portfolio coverage:
- **Strong match**: 2+ projects with direct, relevant experience
- **Adjacent match**: projects that share underlying tech but aren't direct experience
- **Gap**: fewer than 2 strong matches exist

For any initiative rated "adjacent" or "gap":
- Flag it explicitly in the draft (end of Q1)
- Explain the ramp-up approach: what transferable skills apply, what the learning curve looks like, and realistic timeline to proficiency
- If a gap is severe enough that day-one production quality isn't realistic, say so honestly. Example: "While I have ML fundamentals and could work through fine-tuning workflows, my competency isn't at day-one production level for that specific deliverable."

Never hide gaps. Never overstate adjacent experience as direct experience.

### 4. Draft the 3 Responses

**Format (applies to all three answers): one-sentence summary, then tight bullets.** These questions are graded by both an AI and a human. Bullets survive a human skim and let the AI extract discrete claims cleanly; the one-line summary preserves the judgment signal a pure list strips out. Every bullet must carry a concrete claim (a tool, a number, an outcome). No prose paragraphs, no filler.

Generate draft answers for:

**Q1: Relevant Experience**
- Select 4-5 portfolio projects from portfolio.md that best match the proposal's requirements
- **Categorize projects by type, do not name them directly.** Describe each as its category (e.g. "client e-commerce platform on Postgres", "autonomous multi-stage data pipeline", "multi-agent orchestration platform"), not by internal/client name. Keep tools and numbers specific; genericize only the project label.
- EVERY distinct initiative in the proposal must have at least one supporting project. If one doesn't, that's a competency gap (see step 3b)
- Lead with the strongest match
- Include specific technical details that demonstrate capability (not vague claims)
- End with a consolidated tools/stack line
- If competency gaps were identified in step 3b, close Q1 with a brief honest disclosure: what's adjacent vs. new, and the ramp-up plan
- If the referral partner context is known (e.g., ClaudeClaw author), tailor project emphasis accordingly

**Q2: Approach**
- Structure as: Discovery (Week 1) -> specific questions for the client -> technical approach, with the work ordered by leverage (highest-impact fix first)
- Show domain awareness. Ask questions that prove you understand their industry
- Address each distinct initiative in the proposal separately
- Include compliance/regulatory considerations where relevant (HIPAA, GDPR, etc.)
- Be specific about evaluation methodology (structured comparisons, not opinions)
- Light sequencing is allowed here (order is part of the content), but still bullets over paragraphs

**Q3: Availability**
- Pull the default from `defaults.md`
- Adjust if Matthew specifies different availability for this engagement

### 5. Present for Review

Display all 3 draft answers clearly formatted. Ask Matthew:

> Review the drafts. I'll save to the project once you approve (or tell me what to change).

### 6. Save on Approval

Once Matthew approves (or after edits), determine the next proposal number by checking existing `proposal-*` directories in `/home/apexaipc/projects/ai-expert-network/`. Save as:

```
/home/apexaipc/projects/ai-expert-network/proposal-N/proposal.md
```

Format: include the original listing text, the 3 responses, date, and any referral partner context.

## Style Guidelines

- **Format**: summary sentence + bullets, never prose paragraphs. Graded by AI and human both (see step 4).
- **Tone**: Conversational and technically grounded. Write like you're talking to a sharp colleague, not drafting a cover letter. These go to a referral partner, not the end client.
- **No em-dashes**. Use commas, periods, or "and" instead. If you catch yourself reaching for one, restructure the sentence. This is a hard rule, verify the final draft has none.
- **Categorize projects, don't name them**: describe by type ("client e-commerce platform", "autonomous data pipeline"), not by internal/client name. Keep tools and numbers specific. Never say "extensive experience" when you can say "built 11 MCP tools for clinical charting."
- **Confident but honest**: don't claim direct experience when it's adjacent. Frame what transfers and what's new. See step 3b.
- **Cut fluff**: respect the reader's time. No filler paragraphs, no throat-clearing, no restating the question back.
