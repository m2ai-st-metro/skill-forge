# SMOKE_test — forge-content-scan

One end-to-end invocation that proves the scan returns the contract shape.

## Invocation

```
Forge content scan: Two content sources to check.
SOURCE 1 — Mark Kashef YouTube RSS: Check https://www.youtube.com/feeds/videos.xml?channel_id=UCHkzp52CldSPZqU5T49mOnA for new videos since last check.
SOURCE 2 — Nate's Newsletter: Search Gmail for emails from natesnewsletter@substack.com received today (2026-05-18).
Today's date is 2026-05-18.
```

## Expected output (one new video on source 1, nothing on source 2)

```
SOURCE 1 — Mark Kashef YouTube RSS:
NEW: Building a Multi-Agent News Watcher with Claude | 2026-05-18 | https://youtu.be/AbCdEf12345

SOURCE 2 — Nate's Newsletter:
[NO_NEW_CONTENT] since 2026-05-17T19:00:00-05:00

Summary: 1 new item across 2 sources.
```

## Expected output (nothing new — common case)

```
SOURCE 1 — Mark Kashef YouTube RSS:
[NO_NEW_CONTENT] since 2026-05-18T09:00:00-05:00

SOURCE 2 — Nate's Newsletter:
[NO_NEW_CONTENT] since 2026-05-17T19:00:00-05:00

Summary: 0 new items across 2 sources.
[NO_ACTION]
```

## Pass criteria

- Every source has its own `SOURCE N — <name>:` header on its own line.
- Each source reports either ≥1 `NEW:` line **or** exactly one `[NO_NEW_CONTENT] since <ts>` line — never both, never neither.
- Trailing `Summary: N new items across M sources.` line is present with correct counts.
- When `N=0`, an additional `[NO_ACTION]` line follows the summary so cron can short-circuit.
- No items hallucinated — every `NEW:` row must map to a real entry in the source feed/inbox.

## Counter-example (fail)

Output mixing `NEW:` and `[NO_NEW_CONTENT]` under the same source, or omitting the `Summary:` line, or emitting `[NO_ACTION]` when N>0 — any of these break the downstream dispatcher's regex parser.

## Stage 2: newsletter extraction (formerly newsletter-intake)

End-to-end invocation that proves all 5 steps produce the contract output, plus the `[NO_ACTION]` short-circuit path.

### Invocation A: happy path (newsletter present)

```
Run forge-content-scan Stage 2 for sender=natesnewsletter@substack.com on date=2026-05-17.
Output path: /home/apexaipc/projects/st-metro/skill-forge/data/intake/nate-2026-05-17.md
```

### Expected output A

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

1. **Model-router benchmark harness**: periodically score router decisions against actual cost/quality outcomes.
   - effort: M
   - deps: Anthropic API, OpenRouter API
   - value: 4/5
   - why now: router accuracy is unmeasured today; without it cost optimization is guess-work.

2. **Skill durability score**: flag skills that haven't been invoked in 14 days for cold-archive.
   - effort: S
   - deps: Claude Code session log reader
   - value: 4/5
   - why now: skill-audit already lists stale, but doesn't surface a number.

[…5 more ideas…]
```

### Invocation B: empty inbox

```
Run forge-content-scan Stage 2 for sender=natesnewsletter@substack.com on date=2026-05-19.
```

### Expected output B

```
[NO_ACTION]
```

(Pipeline halts; no file written.)

### Pass criteria

- **Step 1 (SEARCH)**: Always emits either a `SEARCH: thread=...` line or `[NO_ACTION]`: never both, never neither.
- **Step 4 (ANALYZE)**: TLDR is exactly 2 sentences. Buildable ideas list is numbered, with all 4 assessments per idea (effort / deps / value / why-now). Ideas are extracted from content, not invented.
- **Step 5 (WRITE)**: Output file has exactly two top-level headings (`# TLDR` and `# Buildable ideas`) and nothing else: no preamble, no signature, no footer.
- **Idempotency**: Running the same date twice writes a `-v2.md` sibling file; original is untouched.
- **Halt safety**: `[NO_ACTION]` path writes nothing to disk and emits only that token.

### Counter-example (fail)

Output containing a 3-sentence TLDR, or buildable ideas with missing "why now" lines, or a file that includes both an extraction *and* a "see also" appendix: all break the Skill Forge downstream parser.
