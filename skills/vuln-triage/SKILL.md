---
name: vuln-triage
description: Lightweight defensive vulnerability triage for repos owned by this workspace. Runs a deterministic grep pass (scripts/scan_candidates.sh) for five high-signal classes (command injection, path traversal, hardcoded secrets, SSRF, unsafe YAML/pickle loads), then the LLM judges only the flagged spans and writes a severity-ranked markdown report. Use when Matthew says "vuln triage", "/vuln-triage", "scan <repo> for vulnerabilities", "security triage this repo", or "check this repo for injection/secrets/SSRF". Never auto-fixes; refuses repos outside this workspace.
---

# vuln-triage

Defensive, CVP-free vulnerability triage for OUR OWN repos. This is the
engineer-our-own branch of card Q-20260718-0023 (the VulnHunter spike was
blocked on Anthropic CVP enrollment). It is an entry-point-forward,
taint-style candidate scan, not attacker simulation.

Two-pass pattern (proven by content-freshness-audit): a deterministic grep
pass flags candidate spans, then the LLM judges ONLY the flagged spans.
Never read the whole repo into context; never judge lines the scanner did
not emit.

## Hard rules

1. Defensive-only. The helper refuses (exit 3) any target whose resolved
   real path is outside /home/apexaipc. Do not work around a refusal, do
   not copy an outside repo into the workspace to bypass it.
2. Never auto-fix. This skill NEVER edits, formats, or "quick-fixes" files
   in the target repo. Output is a report with suggested fix direction only.
   Fixes are separate, human-approved work.
3. Out of scope: exploit generation, proof-of-concept payloads, full
   attacker simulation, scanning third-party or cloned upstream code for
   offense. If asked for any of these, decline and point at the report.

## Procedure

### Step 1: resolve the target

Take the repo path from the user. Accept absolute, tilde, or relative
forms. If ambiguous, ask. Do not scan more than one repo per run.

### Step 2: run the deterministic scanner

```bash
bash ~/.claude/skills/vuln-triage/scripts/scan_candidates.sh <repo-path>
```

- Exit 0: candidates on stdout as `CLASS<TAB>file:line:text`, ending with
  `SCAN_COMPLETE candidates=<N>`. N counts the spans emitted for you to judge.
  A class that exceeds the per-class cap (200) emits a `CLASS<TAB>TRUNCATED
  (<total> candidates, showing 200)` line; the total lives in that marker, and
  a truncated class means the repo needs a narrower scan scope.
- Exit 2: bad target (missing or not a directory). Report the error, stop.
- Exit 3: REFUSED (outside workspace). Relay the refusal verbatim, stop.

#### Markdown-aware mode (`SCAN_INCLUDE_MD=1`)

Default mode excludes `*.md`/`*.markdown`, treating them as prose. That is
wrong for a repo like skill-forge where `SKILL.md` IS the payload: it carries
the instructions and inline shell/python snippets an agent will run (MAI-136).
For any target where markdown can itself be an executable payload (skill
repos, prompt libraries, agent-instruction repos), run:

```bash
SCAN_INCLUDE_MD=1 bash ~/.claude/skills/vuln-triage/scripts/scan_candidates.sh <repo-path>
```

This folds `*.md`/`*.markdown` into the same five taint classes (fenced code
blocks and inline commands inside the file match the same code-shaped
patterns as any other source file) and adds a sixth, markdown-only class:
`PROMPT_INJECTION` (instruction-override language such as "ignore previous
instructions", "reveal your system prompt", "you are now DAN"). Judge
`PROMPT_INJECTION` spans the same way as the other five: read context, decide
severity, never invent findings outside what the scanner flagged. Ordinary
code repos should keep using the default (unset) mode.

The helper finishes in under 30 seconds on a mid-size repo. If it does not,
something is wrong (huge unpruned dir); stop and investigate rather than
raising the cap.

`candidates=0` is a real result: report the repo as clean for the five
scanned classes, note the classes scanned, and finish. A scan failure is
never reported as "clean".

### Step 3: judge ONLY the flagged spans

For each candidate line, read a small context window (about 10 lines
around the file:line with the Read tool). Then classify:

- CRITICAL: reachable from untrusted input with direct impact (RCE, secret
  in shipped code, arbitrary file read).
- HIGH: dangerous pattern with plausible untrusted reachability.
- MEDIUM: dangerous pattern, reachability unclear or internal-only input.
- LOW: bad hygiene, defense-in-depth concern.
- FALSE_POSITIVE: discard, but record the one-line reason (e.g. "argv is
  developer-controlled build constant").

The grep pass is deliberately over-broad; your job is precision. Judge
each span on its own evidence. Do not invent findings at lines the scanner
did not flag; if you notice something adjacent, note it in a "seen in
passing" footnote, not as a ranked finding.

### Step 4: write the report

Write to `~/vault/reports/vuln-triage/<repo-name>-<YYYY-MM-DD>.md`
(`mkdir -p ~/vault/reports/vuln-triage` first). Structure:

```markdown
# Vuln triage: <repo-name> (<date>)

Target: <resolved path>  |  Candidates: <N>  |  Findings: <M> (<by severity>)
Classes scanned: command injection, path traversal, hardcoded secrets, SSRF, unsafe deserialization

## Findings (severity-ranked)

### 1. [CRITICAL] <one-line title>
- Where: <file>:<line>
- Why: <2-3 sentences: the taint path, what input reaches it>
- Fix direction: <what to change, not a patch>

...

## Discarded candidates (false positives)
- <file>:<line>: <reason>

## Not covered
Entry-point-forward candidate scan only. No attacker simulation, no
dynamic analysis, classes limited to the five above.
```

Severity-rank strictly: CRITICAL, then HIGH, MEDIUM, LOW. Summarize the
result in chat with the report path and the top finding.

### Step 5: stop

No fixes, no follow-up edits to the target repo. If Matthew wants fixes,
that is a new task (route code fixes to Ravage per cmd-agent-routing).

## Tests

`bash ~/.claude/skills/vuln-triage/tests/run_tests.sh` runs the full
contract: planted fixture (3 known findings) must flag, clean fixture must
not, refusal paths, determinism, read-only guarantee, and a timed live
scan of ~/projects/research/greppy.

## 14-day adoption gate

Experimental until 2026-08-02. Intended sponsor: Ravage (CMD coding agent;
security review fits its PR-review role). If by that date it has fewer
than 3 human invocations, no active-agent manifest entry, and no active
callsite, cold-archive to ~/projects/st-metro/skill-forge/skills/vuln-triage/ per
the user-level 14-day rule.
