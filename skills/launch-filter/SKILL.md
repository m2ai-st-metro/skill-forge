---
name: launch-filter
description: Evaluate any agent or AI product announcement against a 5-question structured filter (tool integration, openness, data access, ecosystem formation, stackability) and return a scored go/wait/skip verdict. Prevents reactive adoption of every new launch before understanding fit.
---

# Launch Filter

Takes any agent or AI product announcement — a URL, press release, release notes, or pasted text — and runs it through a 5-question sequential filter. Returns a structured verdict: go (adopt/integrate now), wait (monitor but don't act yet), or skip (doesn't fit current stack).

## Trigger

Use when the user says "/launch-filter", "should I adopt this agent", "evaluate this launch", "is this worth integrating", "run this through the filter", or pastes/links an AI product announcement and asks whether it fits their stack.

## Phase 1: Intake

Accept the announcement as:
- A URL (fetch content)
- Pasted press release, blog post, or release notes text
- A product name + brief description the user provides

If only a product name is provided with no content, ask the user to paste a description or provide a URL — do not hallucinate product details.

## Phase 2: Five-Question Filter

Evaluate the announcement against each question in order. A NO on any question is a disqualifier — note it and proceed to produce the verdict anyway, but flag which question failed.

### Question 1 — Tool Integration: Does it plug into existing tools, or does it expect migration?

**Signal for YES:** Ships adapters, plugins, APIs, or native connectors for common workflows (email, calendar, code editors, Slack, CRM). Users can try it alongside existing tools.

**Signal for NO:** Requires moving data into a new system, re-training in a proprietary interface, or abandoning current workflows as a precondition of value.

Score: **YES / PARTIAL / NO**

---

### Question 2 — Openness: Can other agents or developers build on top of it?

**Signal for YES:** Exposes an SDK, API, MCP-compatible tools, webhook surface, or is open-source. Third parties can extend or integrate without a partnership agreement.

**Signal for NO:** Closed ecosystem — functionality available only through the vendor's own interface or to approved partners.

Score: **YES / PARTIAL / NO**

---

### Question 3 — Data Access: Does it access data your team actually cares about?

**Signal for YES:** Native access to the team's actual data graph (Microsoft 365 / Graph, Google Workspace, Salesforce 360, custom RAG, internal databases). Not a generic demo dataset.

**Signal for NO:** Only accesses public data or requires manual upload. No connection to the team's working data without significant integration effort.

Score: **YES / PARTIAL / NO**

---

### Question 4 — Ecosystem Formation: Is an ecosystem forming?

Look for: marketplace or app store listings, active SDK/partner program, named integrations shipping (not promised), and regular release cadence (weekly/monthly updates, not a single launch).

**Signal for YES:** Two or more of the above signals are present and verifiable today.

**Signal for NO:** Single launch with no marketplace, no named partners yet, no visible SDK adoption.

Score: **YES / PARTIAL / NO**

---

### Question 5 — Stackability: Can Agent A build on top of Agent B, or will it displace them?

**Signal for YES:** Deterministic logic hooks, scripted interfaces (like an Agent Script API), or explicit orchestration support (the product is designed to be called by other agents or automation pipelines).

**Signal for NO:** The product is positioned as a replacement for other agents — it does everything itself and has no programmatic invocation surface for external callers.

Score: **YES / PARTIAL / NO**

---

## Phase 3: Verdict

### Scoring Logic

Count questions answered YES or PARTIAL (PARTIAL = 0.5):

| Score     | Verdict     | Meaning                                                                    |
|-----------|-------------|----------------------------------------------------------------------------|
| 4.0–5.0   | **GO**      | Strong fit. Integrate or adopt now. First-mover window may exist.          |
| 2.5–3.5   | **WAIT**    | Promising but gaps. Monitor; re-evaluate in 60–90 days or when gaps close. |
| 0–2.0     | **SKIP**    | Does not fit current stack or strategy. Move on.                           |

If Question 1 or Question 3 scores NO, the verdict is capped at WAIT regardless of total score — poor tool integration and no data access are deal-breakers for enterprise adoption.

## Phase 4: Output

```
AGENT LAUNCH FILTER
===================
Product: {name}
Announced: {date or "undated"}

Q1 — Tool integration:    {YES|PARTIAL|NO} — {one sentence}
Q2 — Openness:            {YES|PARTIAL|NO} — {one sentence}
Q3 — Data access:         {YES|PARTIAL|NO} — {one sentence}
Q4 — Ecosystem forming:   {YES|PARTIAL|NO} — {one sentence}
Q5 — Stackability:        {YES|PARTIAL|NO} — {one sentence}

Score:   {X.X / 5}
Verdict: {GO | WAIT | SKIP}

Rationale:
{2–3 sentences on the deciding factors}

If WAIT — re-evaluate when:
{specific condition or milestone that would upgrade to GO}

If GO — first action:
{concrete integration or adoption step}
===================
```

## What This Does NOT Do

- Does not evaluate vendor financial stability, pricing, or contract terms.
- Does not benchmark the product's model quality or accuracy.
- Does not replace a technical proof-of-concept — the filter is a strategic pre-screen, not a build decision.
- Does not evaluate whether the product fits a specific enterprise compliance posture. Use a dedicated security/compliance review for that.

## Source

Framework derived from Nate Kadlac newsletter (2026-04-29): "The 5-question filter I run every agent launch through (so you can stop reading release notes)." The 5 questions are Nate's framework; the scoring thresholds, PARTIAL scoring, and deal-breaker rules are added extensions.
