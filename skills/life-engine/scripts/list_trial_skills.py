#!/usr/bin/env python3
"""
List skills currently inside the 14-day adoption gate trial window.

CAVEAT (read before trusting this output): ~/.claude is NOT a git repo, so there
is no real "creation date" for a skill. This script uses the SKILL.md file's
mtime as a proxy for age, the same imperfect signal ~/.claude/audit/sunday-tool-audit.py
already relies on for staleness detection. mtime alone produces false positives:
a skill that is actually weeks/months old and proven by real use, but got a light
content edit recently, would falsely appear "new" here. CONFIRMED 2026-07-15: an
unfiltered mtime-only pass flagged 33 skills, 13 of which (40%) already had real
Skill-tool invocations in the prior 30 days -- including life-engine itself (22
invocations), which only showed "0 days old" because its own SKILL.md had just
been edited to add THIS feature. Fixed by cross-referencing real usage below;
mtime is now only the recency filter, not the sole "still unproven" signal.

USAGE CROSS-CHECK: a skill with >=1 confirmed Skill-tool invocation in the last
30 days (scanned from ~/.claude/projects/**/*.jsonl session transcripts, main +
subagent) has already satisfied "Human adoption" per the CLAUDE.md 14-day gate
regardless of mtime, so it is excluded from this list even if recently edited.
This scan takes several seconds over ~3000+ transcript files -- acceptable for a
once-per-morning run (this script is only invoked on the morning_briefing time
window, never on life-engine's other 30-min ticks), not for a tight loop.

SYMLINK DECISION: some skill directories under ~/.claude/skills are symlinks into
~/.claude/.agents/skills/. This script SKIPS symlinked skill directories entirely
(glob finds them, but Path.is_symlink() filters them out before stat'ing). Two
reasons: (1) such symlink targets may be dangling (target directory does not exist
on disk), so stat'ing through them raises FileNotFoundError anyway -- same "skip a
bad symlink, don't crash the unattended run" posture as sunday-tool-audit.py's
_safe_mtime(); (2) even when a
symlink target DOES resolve, the skill isn't really "created" in ~/.claude/skills
at that mtime -- it is a pointer to content that lives (and is versioned) elsewhere,
so an mtime-based trial clock doesn't mean the same thing for it as for a real skill.

Usage: python3 list_trial_skills.py
Output: a JSON array on stdout, one object per skill still inside the 14-day
window AND without confirmed prior use, sorted by days_remaining ascending
(most urgent first). Empty array (not an error) if nothing qualifies.

owner: Matthew (surfaced via the life-engine morning review page)
sink: stdout, consumed by life-engine's morning_briefing HTML render step
kill: no loop here -- single deterministic pass, re-run each morning by life-engine
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
SKILLS_DIR = HOME / ".claude" / "skills"
SESSIONS_DIR = HOME / ".claude" / "projects"
ADOPTION_GATE_DAYS = 14
USAGE_LOOKBACK_DAYS = 30


def find_used_skill_names(lookback_days: int = USAGE_LOOKBACK_DAYS) -> set[str]:
    """Scan session transcripts for real Skill-tool invocations in the lookback
    window. Returns the set of skill names actually invoked. Never raises on a
    malformed line or file -- a transcript read failure just means that file
    contributes nothing, not a crashed morning briefing."""
    if not SESSIONS_DIR.exists():
        return set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    used: set[str] = set()
    for f in SESSIONS_DIR.rglob("*.jsonl"):
        try:
            with f.open("r", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    msg = d.get("message")
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content")
                    if not isinstance(content, list):
                        continue
                    ts_raw = d.get("timestamp")
                    if not ts_raw:
                        continue
                    try:
                        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if ts < cutoff:
                        continue
                    for item in content:
                        if not isinstance(item, dict):
                            continue
                        if item.get("type") == "tool_use" and item.get("name") == "Skill":
                            inp = item.get("input") or {}
                            skill = inp.get("skill") or inp.get("name")
                            if skill:
                                used.add(skill)
        except Exception:
            continue
    return used


def extract_description(text: str) -> str:
    """Pull the one-line `description:` value out of SKILL.md YAML frontmatter.

    Handles both the plain single-line form (`description: foo`) and the
    folded block-scalar form (`description: >` followed by indented lines,
    as used in life-engine/SKILL.md itself) without a full YAML parser.
    Never raises -- returns "" if frontmatter or the field is missing/malformed.
    """
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return ""
    frontmatter = m.group(1)
    lines = frontmatter.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("description:"):
            continue
        value = stripped[len("description:"):].strip()
        if value in (">", "|", ">-", "|-", "", ">+", "|+"):
            # Block scalar: following indented lines are the folded value.
            block_lines = []
            for cont in lines[i + 1:]:
                if cont.strip() == "":
                    continue
                if not cont.startswith((" ", "\t")):
                    break
                block_lines.append(cont.strip())
            return " ".join(block_lines).strip()
        # Plain single-line value; strip surrounding quotes if present.
        return value.strip('"').strip("'")
    return ""


def find_trial_skills() -> list[dict]:
    if not SKILLS_DIR.exists():
        return []
    used = find_used_skill_names()
    now = datetime.now()
    out = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.is_symlink():
            # See SYMLINK DECISION in the module docstring.
            continue
        if skill_dir.name in used:
            # Confirmed real use already satisfies "Human adoption" per the
            # 14-day gate regardless of mtime -- see USAGE CROSS-CHECK above.
            continue
        skill_md = skill_dir / "SKILL.md"
        try:
            mtime = skill_md.stat().st_mtime
            size_bytes = skill_md.stat().st_size
        except (FileNotFoundError, OSError):
            continue
        mtime_dt = datetime.fromtimestamp(mtime)
        days_old = (now - mtime_dt).days
        if days_old >= ADOPTION_GATE_DAYS:
            continue
        days_remaining = ADOPTION_GATE_DAYS - days_old
        try:
            text = skill_md.read_text(errors="ignore")
        except OSError:
            text = ""
        description = extract_description(text)
        out.append({
            "name": skill_dir.name,
            "days_old": days_old,
            "days_remaining": days_remaining,
            "description": description,
            "skill_md_path": str(skill_md),
            "skill_md_size_bytes": size_bytes,
        })
    return sorted(out, key=lambda s: s["days_remaining"])


def main() -> int:
    trial_skills = find_trial_skills()
    print(json.dumps(trial_skills, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
