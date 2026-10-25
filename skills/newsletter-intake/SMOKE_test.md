# SMOKE_test — newsletter-intake

End-to-end invocation that proves all 5 stages produce the contract output, plus the `[NO_ACTION]` short-circuit path.

## Invocation A — happy path (newsletter present)

```
Run newsletter-intake for sender=natesnewsletter@substack.com on date=2026-05-17.
Output path: /home/apexaipc/projects/st-metro/skill-forge/data/intake/nate-2026-05-17.md
```

## Expected output A

Console summary:
```
SEARCH: thread=18f2c4abe9d0a1b2 subject="The agent stack you'll actually run"
EXTRACT-BODY: 3,847 chars, 4 outbound URLs
FETCH-LINKS: 4/4 fetched OK (Substack: 3, article: 1)
ANALYZE: TLDR + 7 buildable ideas extracted
WRITE: /home/apexaipc/projects/st-metro/skill-forge/data/intake/nate-2026-05-17.md (created)
```

File contents (`nate-2026-05-17.md`):
```markdown
# TLDR

Nate argues the 2026 agent stack collapses into three layers (orchestrator, skill, model-router) and that durability now matters more than raw capability. His main claim is that anyone still building monolithic agents will be out-iterated by people who shipped a router last quarter.

# Buildable ideas

1. **Model-router benchmark harness** — periodically score router decisions against actual cost/quality outcomes.
   - effort: M
   - deps: Anthropic API, OpenRouter API
   - value: 4/5
   - why now: router accuracy is unmeasured today; without it cost optimization is guess-work.

2. **Skill durability score** — flag skills that haven't been invoked in 14 days for cold-archive.
   - effort: S
   - deps: Claude Code session log reader
   - value: 4/5
   - why now: skill-audit already lists stale, but doesn't surface a number.

[…5 more ideas…]
```

## Invocation B — empty inbox

```
Run newsletter-intake for sender=natesnewsletter@substack.com on date=2026-05-19.
```

## Expected output B

```
[NO_ACTION]
```

(Pipeline halts; no file written.)

## Pass criteria

- **Stage 1**: Always emits either a `SEARCH: thread=...` line or `[NO_ACTION]` — never both, never neither.
- **Stage 4**: TLDR is exactly 2 sentences. Buildable ideas list is numbered, with all 4 assessments per idea (effort / deps / value / why-now). Ideas are extracted from content, not invented.
- **Stage 5**: Output file has exactly two top-level headings (`# TLDR` and `# Buildable ideas`) and nothing else — no preamble, no signature, no footer.
- **Idempotency**: Running the same date twice writes a `-v2.md` sibling file; original is untouched.
- **Halt safety**: `[NO_ACTION]` path writes nothing to disk and emits only that token.

## Counter-example (fail)

Output containing a 3-sentence TLDR, or buildable ideas with missing "why now" lines, or a file that includes both an extraction *and* a "see also" appendix — all break the Skill Forge downstream parser.
