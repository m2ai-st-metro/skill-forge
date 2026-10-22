---
name: agent-message-bus-designer
description: Design the inter-agent messaging layer for a multi-agent system — per-agent private state, a directed send-to-agent tool, urgency tiers that decide whether a running agent is interrupted or reads the note at its next checkpoint, and a user-turn preemption rule. Use when concurrent agents need to exchange findings mid-task without stopping, when deciding which messages may cancel in-flight work, or when a team of agents keeps blocking on each other because every handoff is a full stop. Trigger on "how should my agents talk to each other", "design an agent mailbox", "agents keep blocking each other", "when should one agent interrupt another", or "inter-agent messaging protocol".
---

# Agent Message Bus Designer

Most multi-agent designs fail in one of two directions: a single shared brain where
every agent sees everything (context bloat, cross-contamination), or a strict
sequential pipeline where agent A must fully stop before agent B can act (wasted
wall-clock, findings arrive too late to matter).

The middle path is a message bus: agents hold private state and exchange directed
notes, and each note carries an urgency tier that determines whether the recipient
stops what it is doing.

## Phase 1 — Establish private state per agent

For each agent in the system, define these four fields. They are private by default;
nothing is shared implicitly.

| Field | What it holds | Why private |
|---|---|---|
| Identity | Stable name and one-sentence job | Prevents role drift under long runs |
| Task history | Its own turns only | Keeps context windows bounded |
| Working notes | Scratch findings not yet published | Half-formed work should not leak |
| Inbox | Notes addressed to it, unread and read | The only channel for outside facts |

Write these out before designing any message. If two agents need identical private
state, they are one agent.

## Phase 2 — Define the directed send

Specify one tool, available to every agent, with an explicit payload contract:

- `to` — a single named recipient. Broadcast is not a default; if you need fan-out,
  enumerate recipients so the cost is visible.
- `urgency` — one of the tiers from Phase 3.
- `claim` — the finding itself, stated as a fact, not a summary of activity.
- `action_requested` — what the recipient should do differently, or `none` for FYI.
- `expires_after` — the point past which the note is stale and should be dropped
  (a phase name or step index, not a wall-clock time).

The `action_requested` field is what keeps the bus from degenerating into status
chatter. A note with no requested action and no durable claim should not be sent.

## Phase 3 — Set urgency tiers and the interrupt rule

Three tiers is almost always enough. Write the interrupt behavior explicitly, because
the default in most harnesses is "deliver whenever," which is not a design.

| Tier | Delivery | Use for |
|---|---|---|
| `fyi` | Read at the recipient's next natural checkpoint | Context that improves later steps but does not invalidate current work |
| `redirect` | Read at next checkpoint, must be acknowledged before the phase closes | New constraints, changed requirements, a better source |
| `abort` | Cancels the recipient's in-flight work immediately | The current work is now known to be wasted or harmful |

The bar for `abort` is that continuing produces something that will be thrown away, or
something destructive. "I found something interesting" is `fyi`. "The spec you are
building against was superseded" is `redirect`. "The target file is being deleted" is
`abort`.

Record the rule as a testable sentence, for example: *an agent checks its inbox at
every phase boundary and after every tool result; only `abort` may interrupt between
those points.*

## Phase 4 — Protect the user turn

One rule overrides everything above: an in-flight exchange with the human is never
preempted by an agent message. Agent traffic queues behind it regardless of tier.

Without this rule, a busy system will interleave agent chatter into the human's
conversation and the operator loses the ability to steer.

## Phase 5 — Decide what is shared vs. sent

Not everything belongs on the bus. Sort each piece of state:

- **Sent** — a finding one specific agent needs to change its behavior now.
- **Shared store** — a durable fact several agents will need later. Write it once to
  a common store and reference it; do not mail copies.
- **Neither** — activity narration. Drop it.

If more than roughly a third of your traffic is `fyi` with `action_requested: none`,
the agents are narrating rather than coordinating; tighten the send contract.

## Verification

The design is complete when you can answer all of these from the written spec, with
no appeal to "the framework handles it":

1. For each agent, what are its four private fields?
2. What is the exact payload of a send, field by field?
3. At what points does an agent read its inbox?
4. Which tier, and only which tier, may cancel in-flight work? What is the stated bar?
5. What happens to an agent note that arrives mid-way through a human turn?
6. Name one piece of state that belongs in the shared store rather than on the bus,
   and say why.
7. Pick one real handoff in your system and trace it: sender, recipient, tier,
   `action_requested`, and what the recipient does differently as a result.

If question 7 produces "the recipient logs it," the message should not exist.

## Notes

This pattern is harness-agnostic — it describes the protocol, not an implementation.
It composes with a shared-memory design (which covers durable cross-agent state) but
solves a different problem: live coordination between agents that are running at the
same time.

## Source

Derived from "Cursor Accidentally Exposed Grok Bot's Blueprint" by Mark Kashef,
published 2026-08-26 — a breakdown of a reconstructed multi-agent system's
inter-agent messaging, urgency handling, and per-agent isolation.
