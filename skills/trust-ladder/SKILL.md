---
name: trust-ladder
description: "Build trust in a freshly-defined agent or automated job BEFORE you let it run unattended. Walks the three-move \"prove it before you trust it\" protocol in order: make it look before it acts (read-only recon), guard the dangerous rule in two places (intention plus an independent run-time backstop), then hand off slowly up a four-rung ladder from watched to trusted. Use this whenever someone is about to automate, schedule, cron, or \"set and forget\" an agent, loop, or job, or says \"is this safe to automate\", \"should I trust this agent yet\", \"prove it before I trust it\", \"trust ladder\", \"how do I roll this out safely\", \"graduate this to unattended\", or has just finished writing a job's spec and wants to walk away from it. Trigger even when automation is implied rather than named (e.g. \"let's just let it run overnight\"), because skipping this protocol is the most expensive habit in agent ops."
source:
  type: book
  title: How to Train Your Agent
  chapter: "Part 3: Prove It Before You Trust It"
  author: Matthew Snow
  date: 2026-06-15
  pipeline: book-to-skill
---

# Trust Ladder: Prove It Before You Trust It

Turn a freshly-specified agent or job into a trusted one by proving it works, not by
hoping it does. A job on paper is not the same as a job that works: the instruction can be
perfect and the thing can still wander off, act confidently on a wrong assumption, or quietly
break in a way nobody notices for a week. Handing over a clean job and immediately trusting it
is the single most expensive habit in agent ops.

The mental model: an agent is a brilliant new hire. You do not give a new hire the company
bank account on day two. Not because they are dishonest, but because you have not *seen* them
work yet. You let them shadow you, you check what they turn in, you spot-check for a while, and
one day you realize you stopped checking because they earned it. Trust is built, not given. The
mistake people make is skipping the earning and leaping straight from "I wrote the instructions"
to "it runs my business while I sleep." This skill is the in-between, and the in-between is the
training.

There are three moves and they run **in strict order**: look before it acts, then guard the
rule in two places, then hand off slowly. Do not reorder them and do not skip one.

## When to use this

Reach for this skill the moment a job is about to go from "defined" to "running on its own":
before wiring a cron or `/schedule`, before starting an unattended `/loop`, before granting an
agent write/spend/send permissions, or any time someone says "let's just let it run." If the
job is purely interactive and supervised (a human watches every run), you are already on rung 1
of the ladder and can use this skill to plan the climb.

## Move one: make it look before it acts (recon first)

The first time you run a new job, do not let the agent *do* anything. Let it only *look* and
report what it sees and what it would act on.

1. Run the job in a read-only / dry-run mode (or explicitly instruct the agent to act on
   nothing this pass).
2. Make it surface the concrete things it is about to act on, ideally the specific items, before
   it touches any of them. "Show me the three things you would change" beats "trust me." If the
   job is not built yet (you have only a spec), recon is not skippable, it is deferred: name
   exactly what the look-pass must show, and treat the move as incomplete until a real look-pass
   has actually run. A described recon is not a done recon.
3. Read the report and check it against **your own assumptions** about the system, not just the
   agent's behavior. You are validating your mental model as much as the agent's. Your
   assumptions are usually the wrong ones.

This sounds too cautious and it is the most useful habit in the whole protocol. A real example:
a builder was about to stack a week of work on top of an agent, assuming that agent published
things out into the world on its own. Before building, almost as an afterthought, he had it just
*look* and report what it actually did. It had never published anything in its life, it only ever
read and reported. The assumption underneath a week of planned work was simply wrong, and one
look caught it before anything collapsed.

It protects you in the other direction too, where the agent does too *much*: a test helper that
was only supposed to check one small thing ran the same change five times before anyone caught
it; an agent told to "read my email" with no narrowing tried to swallow a thousand messages at
once and burned a small fortune in the first minute. Neither was a dumb agent. Both were a human
who let the thing act before they watched it look.

### Decision point: premise contradiction

After the look-report comes back, judge it against the plan. If the report contradicts a premise
the plan depends on (the agent does not do what you assumed, or it would act on far more or far
less than expected), **STOP**. Fix the premise before building anything on top of it. Use the
checkpoint below rather than quietly proceeding.

```
AskUserQuestion:
  "The look-report contradicts a premise this plan depends on: <state the contradiction>.
   Proceeding would build on a foundation that is not there. How do you want to handle it?"
  options: [Fix the premise and re-recon, Proceed anyway (I accept the risk), Stop here]
```

## Move two: guard the important rule in two places (two-layer gate)

Every job that could do real damage has one rule that matters most: the stopping or limiting
rule (for example "try three times, then quit and text me", a spend cap, a message cap). Writing
it on the spec is step one. It is not enough on its own.

Think about a stove. The recipe says "do not leave the burner unattended." That is a rule on
paper, and paper rules are exactly the ones you forget at two in the morning when you are tired.
So good stoves also have an automatic shutoff that kills the burner whether you remembered the
rule or not. Two guards on the same danger: one is the intention, the other is the backstop that
fires at the actual moment things would go wrong.

1. **Guard 1 (intention):** the rule you write into the job's spec at setup, when you are calm
   and thinking clearly.
2. **Guard 2 (backstop):** a *separate* mechanism that fires automatically at the moment the job
   runs, when you are not watching. It assumes you forgot Guard 1. Think of a credit card's hard
   cap: you also tell yourself you will not overspend, but the card stops the charge whether you
   remembered or not. For an agent that is "never send more than five messages" or "stop after
   three tries" enforced by the system itself, not by the prompt's good intentions.

Require **both** on anything that touches money, sends messages to other people, or deletes
things. Why two and not one? A single guard is one mistake away from nothing. If the only thing
between you and a runaway job is a rule you wrote once and hoped to honor, you have a hope, not a
guard. The backstop costs almost nothing and is the thing that saves you on the night the first
guard fails. Belt and suspenders.

### Decision point: does this job spend, message, or delete?

```
AskUserQuestion:
  "Does this job spend money, send messages to other people, or delete/overwrite things?"
  options: [Yes (two guards required), No (single guard acceptable)]
```

If yes, do not proceed to Move three until a real Guard 2 exists as a separate run-time
mechanism. Naming an intention twice is not two guards.

## Move three: hand off slowly (the trust ladder)

Now you let go, but by inches, not all at once. There is a ladder, and you climb one rung at a
time. Each rung is earned by the one below it working:

1. **Watch it run, in the room.** The first few times, you sit there while it works, watching
   over its shoulder.
2. **Let it run, then check every result.** It runs on its own, but you read everything it
   produces before you act on it, like reviewing every report a new hire hands in.
3. **Spot-check.** You have seen enough good results that you only glance at one now and then.
4. **Trust the output.** You stopped checking, because it earned it. This is the day you
   actually get your time back.

Never jump rungs. The reason people get burned by agents is almost always that they leapt from
rung 1 straight to rung 4: they watched it succeed once and decided it was trustworthy forever.
That is the same error as trusting a new hire's first good week to mean they never need checking
again. And yes, this part is slow, a little boring, and feels beneath you. That feeling is the
trap. The slow watching *is* the training. The agents that "go rogue" almost always belong to the
people who found this part too tedious to do.

A job that has never run a supervised pass is at **rung 0: not yet on the ladder.** It enters at
rung 1 only after the Move-one look-pass has actually run and (where required) Guard 2 exists. So
the honest starting state for a brand-new job is rung 0, and the request to "just cron it" is a
leap all the way to rung 4. Place the job on the rung it has actually earned, name the evidence
that would graduate it to the next rung, and only move up when that evidence exists.

## Hard rules (these are the point, not suggestions)

These are the tacit lessons the chapter teaches, stated plainly. They hold even when they feel
excessive, because the failure they prevent is expensive and quiet.

- **The first run is a look, not a leap.** Always recon before action on a new job.
- **Validate your own assumptions, not just the agent's behavior.** Treat every remembered fact
  about the system as unverified until the look-report confirms it.
- **Two guards minimum on anything that spends, messages people, or deletes.** One guard is a
  hope, not a guard.
- **Guard 2 must be a separate mechanism that fires at run time,** independent of Guard 1's
  intention. Guard the same invariant at the point of intent and at the point of action.
- **Climbing the ladder slowly is the training.** The boredom is the trap, not a reason to skip.
- **The order is fixed:** look, then double-guard, then graduate. Do not reorder or skip.

## Output

Produce a short readiness summary for the job in question:

- **Recon result:** what the look-pass showed, and whether it confirmed or contradicted the plan's
  premises.
- **Guards:** Guard 1 (the written rule) and, where required, Guard 2 (the independent run-time
  backstop) named explicitly. Flag any required-but-missing Guard 2.
- **Current rung:** which of the four rungs the job has earned, and the specific evidence needed to
  graduate to the next.

Skip none of the three sections. If the job is not ready to leave rung 1, say so plainly: what you
have without the protocol is not trust, it is a hope wearing trust's clothes, and hope is the thing
that runs all night on a broken task while you sleep.

## Source attribution

Extracted by the `book-to-skill` pipeline from "How to Train Your Agent", Part 3, "Prove It
Before You Trust It" (Matthew Snow, 2026-06-15). The new-hire, stove-shutoff, and credit-card-cap
analogies are the chapter's own.
