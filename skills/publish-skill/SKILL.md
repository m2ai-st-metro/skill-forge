---
name: publish-skill
description: >
  Sanitize a personal Claude Code skill into a shareable version for the
  m2ai-skills-pack plugin. Scans the source SKILL.md for personal references
  (names, hardcoded paths, LAN IPs, internal project/agent names, client names),
  proposes replacements, writes a genericized copy into the correct themed
  plugin under ~/projects/products/m2ai-skills-pack/, registers it in the manifest, and
  regenerates the README from that manifest. Use when the user says "publish
  this skill", "share skill X", "make a shareable version", or
  "/publish-skill <name>".
---

# Publish Skill: Personal → Shareable Pipeline

This skill is the bridge between a personal skill (in `~/.claude/skills/`) and
the public `m2ai-skills-pack` plugin. It never publishes without explicit
per-match confirmation on personal references.

## When to use

- User says "publish this skill", "make this shareable", "add to the pack"
- User invokes `/publish-skill <skill-name>`
- After creating a new skill that the user flags as shareable
- During batch migration of existing personal skills

- Right after `/skill-creator` finishes a new skill: ask "Is this potentially shareable for the m2ai-skills-pack?" If yes, this is the next skill to run, within the same 14-day adoption window so shareability and proving compound together.

## Inputs

- `<skill-name>` — the folder name under `~/.claude/skills/`
- (optional) `--dry-run` — scan and report without writing

If the name is ambiguous or missing, list the skills in `~/.claude/skills/`
and ask which one.

## Personal-reference detection

Run these scans against the source SKILL.md and any supporting files in the
skill folder:

### Regex sweeps

| Pattern | Category | Default action |
|---|---|---|
| `Matthew\|matthew` | Personal name | Replace with "the user" or "you" |
| `/home/apexaipc\b` | Hardcoded home path | Replace with `~` or `$HOME` |
| `10\.0\.0\.\d+` | LAN IP | Replace with `<your-host>:<port>` and flag |
| `apexaipc` | Username | Replace with `<user>` |
| `memyselfplusai\.com\|m2ai\b` | Business name | Keep only if skill is M2AI-branded |
| `ST[- ]Metro\|Snow-Town\|Metroplex\|Ultra Magnus\|YCE\|Sky-Lynx\|IdeaForge\|ClaudeClaw\|Galvatron\|Ravage\|Scout\|RepMan\|Soundwave\|Kup\|Tyrest` | Internal project/agent names | Flag — usually remove or genericize |
| `Sprinkle of Sage\|AiVA\|AIN\|Kevin\b` | Client names | Always flag — never publish |
| `MatthewSnow2\|m2ai-portfolio\|m2ai-st-metro` | GitHub orgs | Replace with generic "your org" |
| `Verstappen\|cuttlefish` | Personal framing metaphors | Flag — usually remove |
| `vault/\|\.perceptor\|MEMORY\.md` | Personal tooling assumptions | Genericize or flag as prerequisite |
| `Surface tablet\|AlienPC\|NAS\|ProBook` | Personal hardware aliases | Replace with generic |
| `~/\.env\.shared` | Personal env convention | Replace with `.env` or flag as prerequisite |

### Semantic checks (read the file, not regex)

- Does the skill's framing assume a specific ecosystem? (e.g. "L5 pipeline",
  "14-day gate") — if yes, flag the section and suggest a generic reframe.
- Does it reference roadmap files or memory indexes that only exist in
  Matthew's environment? Flag as "prerequisite not shared".
- Does the description paragraph name the user? Rewrite to be user-agnostic.

## Workflow

### 1. Read source

```
~/.claude/skills/<name>/SKILL.md
~/.claude/skills/<name>/**  (any supporting files)
```

### 2. Run detection

Produce a table: `line | matched pattern | category | proposed replacement`.
Show it to the user. For each row, the user chooses: **keep / replace /
parameterize / cut**.

- **keep** — leave as-is (rare, only if the reference is inert trivia)
- **replace** — accept the proposed replacement
- **parameterize** — convert to a `${VAR}` the user configures
- **cut** — remove the sentence/section entirely

If there are more than ~15 matches, group them by category and let the user
approve a category at a time ("replace all Matthew→user", "cut all agent
names", etc.).

### 3. Resolve the target plugin, then apply edits

**The pack is no longer a flat `skills/` dir.** As of 2026-07-16 it is 7 themed
plugins, each with its own `skills/`, and the old `~/projects/products/m2ai-skills-pack/skills/`
path NO LONGER EXISTS. Writing there creates a directory nothing reads and that
no manifest knows about.

`skills-manifest.json` at the pack root is the SSOT. It maps every skill to a
division, and every division to the plugin that owns it. Resolve the target:

```bash
PACK=~/projects/products/m2ai-skills-pack
node -e '
  const m = require(process.argv[1] + "/skills-manifest.json");
  const name = process.argv[2];
  const d2p = {}; for (const p of m.plugins) for (const d of p.divisions) d2p[d] = p.id;
  const div = m.skills[name];
  if (!div) { console.error("NOT IN MANIFEST: pick a division (see below)"); process.exit(1); }
  console.log(d2p[div] + "/skills/" + name);
' "$PACK" <name>
```

Write the sanitized version to `$PACK/<resolved-plugin>/skills/<name>/SKILL.md`.

**If the skill is NOT already in the manifest** (the normal case for a genuinely
new skill), it has no division yet. Show the user the 13 divisions with their
`focus` line, ask which one fits, and add `"<name>": "<division-id>"` to
`skills.<name>` in `skills-manifest.json`. Do not guess: an unassigned skill is
an orphan, and `scripts/sync-from-manifest.mjs` refuses to write when it finds
one. That refusal is the gate working, not a bug to route around.

If the skill has supporting files (scripts, templates, etc.), copy them too and
run the same sanitization pass. Note `.gitignore` ignores
`m2ai-*/skills/*/{output,reports,dist,build,logs,tmp}/`: those are runtime
artifact dirs and must not be published. `examples/`, `references/`, `evals/`
and `scripts/` are legitimate and stay tracked.

### 3a. Validate the YAML frontmatter (quote-the-description guard)

Before moving on, confirm the written SKILL.md frontmatter actually parses.
An UNQUOTED `description`, `when_to_use`, or `argument-hint` value that contains
a colon (`Output:`, `Trigger phrases:`), a bracket, or a pipe breaks the YAML
parser and GitHub renders "Error in user YAML: mapping values are not allowed in
this context" (this silently hit 14 pack skills on 2026-06-25). Double-quote any
such value. Booleans/ints (`user_invocable: true`) stay unquoted. Verify:

```bash
# $TARGET is the plugin-resolved path from step 3, NOT the dead flat skills/ dir.
python3 -c "import yaml,sys; d=yaml.safe_load(open(sys.argv[1]).read().split('---')[1]); \
  assert d.get('name') and d.get('description'), 'MISSING name or description'; print('frontmatter OK')" \
  "$TARGET/SKILL.md"
```

The assert is not decoration: a skill missing `name` or `description` is a Cursor
Marketplace rejection criterion AND cannot auto-trigger in Claude Code, so it
silently becomes explicit-invoke-only. Two skills shipped that way for months
before `tests/cursor-schema.test.sh` C-37a caught them on 2026-07-16.

The PostToolUse hook `~/.claude/hooks/skill-frontmatter-guard.py` is the run-time
backstop that auto-quotes these on any SKILL.md write; this step is the
point-of-intent check so a broken copy never leaves the pipeline in the first
place.

### 4. Add a `## Configuration` section

If the skill relies on parameterized paths/env vars, append a configuration
block at the end of the shared SKILL.md explaining what the user must set.
Example:

```markdown
## Configuration

This skill expects:

- `$VAULT_DIR` — path to your notes vault (default: `~/vault`)
- `$PROJECTS_DIR` — path to your code projects (default: `~/projects`)

Set these in your shell profile or pass them when invoking the skill.
```

### 5. Regenerate the README. Do NOT hand-edit it.

**The README is GENERATED.** Its counts, division tables, and both
`marketplace.json` files are all derived from `skills-manifest.json` by
`scripts/sync-from-manifest.mjs`. Appending a line by hand is silently reverted
the next time that script runs, and the loss is invisible until someone notices a
count disagreeing (this exact trap bit on 2026-07-16: hand-edited manifests were
reverted mid-session and the commit captured only the unrelated file).

So step 4 is the real edit (register the skill in the manifest) and this step is
just:

```bash
cd ~/projects/products/m2ai-skills-pack
node scripts/sync-from-manifest.mjs          # regenerate every derived file
node scripts/sync-from-manifest.mjs --check  # must report: all generated files in sync
```

Then run the pack's own guards before reporting success:

```bash
bash scripts/leak-scan.sh                # must be clean; it reads BINARY too
bash tests/gate0.test.sh                 # 93
bash tests/cursor-schema.test.sh         # 9, incl. C-37a: every skill needs name+description
bash tests/phase2-gate.sh                # 11
```

`cursor-schema` C-37a is the one that matters most here: a published skill
missing `name` or `description` frontmatter is an explicit Cursor Marketplace
**rejection criterion**, and it cannot auto-trigger in Claude Code either. If
your sanitization pass dropped either field, that test catches it.

### 6. Report diff

Show the user:
- Files written
- Count of personal references removed/replaced/parameterized
- Any reference the user marked "flag for manual review"
- README section updated
- Suggested commit message

Do NOT commit or push — the user handles that (or runs a separate commit step).

## Output

After running, produce a short summary:

```
Published: <skill-name>
Source:     ~/.claude/skills/<name>/SKILL.md (<N> lines)
Target:     ~/projects/products/m2ai-skills-pack/<plugin>/skills/<name>/SKILL.md (<M> lines)
Plugin:     <plugin-id>  (division: <division-id>)
Manifest:   registered / already present
Personal refs: <N> detected, <A> replaced, <B> parameterized, <C> cut
Generated:  README + both marketplace.json regenerated, --check in sync
Guards:     leak-scan clean · gate0 93 · cursor-schema 9 · phase2-gate 11
Prereqs:    <list of external dependencies the user must provide>
```

## Rules

- **Never publish without showing the diff first.** The user must see every
  personal reference and approve the replacement.
- **Client names are always flagged, never auto-replaced.** A leaked client
  name is worse than a broken skill.
- **Do not overwrite an existing shared skill without asking.** If the target
  file exists, show the diff and ask: overwrite / merge / abort.
- **Do not commit or push.** This skill ends at file write. The user handles
  version bumps and git operations.
- **Preserve skill behavior.** Genericization should not change what the skill
  does — only who it references. If behavior must change to be portable, flag
  it and ask.
- **Never hand-edit a generated file.** README, both `marketplace.json` files,
  and all 14 per-plugin `plugin.json` files are emitted by
  `scripts/sync-from-manifest.mjs`. Edit `skills-manifest.json` (the SSOT) or the
  generator, then regenerate. A hand edit to any of them is reverted on the next
  run, silently.
- **Never publish a skill without `name` AND `description` frontmatter.** It is a
  Cursor Marketplace rejection criterion, and a skill with no `description`
  cannot auto-trigger in Claude Code either: it silently degrades to
  explicit-invoke-only. `tests/cursor-schema.test.sh` C-37a enforces this.

- **Run `/skill-maintenance` on the source skill first.** The content-quality gate runs before the sanitization gate — a sanitized copy of a low-quality skill is still low-quality.

## Prerequisites in the pack

The pack itself lives at `~/projects/products/m2ai-skills-pack/`. If it doesn't exist,
abort and tell the user to clone it first. Do not scaffold it from scratch.
