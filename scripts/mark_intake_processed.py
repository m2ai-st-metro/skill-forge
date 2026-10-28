#!/usr/bin/env python3
"""Owner for the data/intake/*.processed.md marker (MAI-28).

Intake files were consumed, their top ideas were built, and the marker rename
never happened, so every later scan re-surfaced them as backlog. Nothing in the
repo performed that rename: the convention was carried by hand, and by-hand
conventions drift. Three spellings were live at once (62 `.processed.md`, 4
`.done.md`, 4 bare) and 10 ideas across the bare files had no artifact and no
recorded decision.

This script is the missing owner. It enforces two rules:

1. One marker spelling. `.done.md` is a legacy alias and migrates to
   `.processed.md`.
2. A file may not be marked processed while any of its buildable ideas has no
   recorded exit. Reading an idea is not an outcome; the idea is BUILT (an
   artifact exists), CARD (a tracked follow-up was spawned), or NO-GO (an
   explicit decision not to act, with a reason). Marking first would hide the
   open ideas, which is exactly how these four drifted.
3. Every idea carries a `**Classification:**` line: technique | tool | other
   (MAI-206). Only a TECHNIQUE may be BUILT into a skill. A TOOL (a thing to
   install or call, PR #112 subscription-sdk-bridge was one force-fit into a
   SKILL.md) or OTHER exits as CARD (a Paperclip evaluation issue, filed via
   `node scripts/open-intake-pr.mjs --tool-issue ...`) or NO-GO. The line is
   grep-able: `grep -rn "Classification:.. tool" data/intake/`.

`data/` is gitignored, so this operates on runtime state; only the script and
its tests are tracked.

Usage:
    python scripts/mark_intake_processed.py --check
    python scripts/mark_intake_processed.py --migrate-done
    python scripts/mark_intake_processed.py --mark data/intake/foo-2026-01-01.md
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INTAKE_DIR = REPO_ROOT / "data" / "intake"

PROCESSED_SUFFIX = ".processed.md"
LEGACY_SUFFIX = ".done.md"

IDEAS_HEADING = re.compile(r"^##\s+Buildable Ideas\s*$", re.MULTILINE)
SECTION_HEADING = re.compile(r"^##\s+(?!#)", re.MULTILINE)
IDEA_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)

# `**Routing:** CARD — MAI-31` is the canonical form. `**Status:** Built — path`
# predates it and is accepted as an equivalent BUILT verdict.
ROUTING = re.compile(r"^\*\*Routing:\*\*\s*(BUILT|CARD|NO-GO)\b[\s—:-]*(.*)$", re.MULTILINE)
LEGACY_BUILT = re.compile(r"^\*\*Status:\*\*\s*Built\b[\s—:-]*(.*)$", re.MULTILINE | re.IGNORECASE)

CARD_ID = re.compile(r"(MAI-\d+|Q-\d{8}-\d{4}|#\d+)")
MIN_REASON_CHARS = 12

# `**Classification:** technique` (tool-vs-technique gate, MAI-206). Same line shape as Routing.
CLASSIFICATION = re.compile(r"^\*\*Classification:\*\*\s*([A-Za-z-]+)\b", re.MULTILINE)
CLASSIFICATIONS = ("technique", "tool", "other")


@dataclass(frozen=True)
class Idea:
    title: str
    verdict: str | None
    detail: str
    classification: str | None = None

    @property
    def problem(self) -> str | None:
        """Why this idea does not yet have a valid exit, or None if it does."""
        if self.classification is None:
            return "no **Classification:** line (expected technique, tool, or other)"
        if self.classification not in CLASSIFICATIONS:
            return (f"classification {self.classification!r} is not one of "
                    f"{', '.join(CLASSIFICATIONS)}")
        if self.verdict is None:
            return "no **Routing:** line (expected BUILT, CARD, or NO-GO)"
        if self.classification != "technique" and self.verdict == "BUILT":
            return (f"{self.classification}-classified idea routed BUILT; only techniques become "
                    "skills, a tool/other exits as CARD (Paperclip evaluation issue) or NO-GO")
        if self.verdict == "CARD" and not CARD_ID.search(self.detail):
            return "CARD without a card id (expected MAI-<n>, Q-<date>-<n>, or #<n>)"
        if self.verdict in ("NO-GO", "BUILT") and len(self.detail.strip()) < MIN_REASON_CHARS:
            noun = "reason" if self.verdict == "NO-GO" else "artifact path"
            return f"{self.verdict} without a {noun}"
        return None


def is_marked(path: Path) -> bool:
    return path.name.endswith(PROCESSED_SUFFIX)


def is_legacy(path: Path) -> bool:
    return path.name.endswith(LEGACY_SUFFIX)


def marked_name(path: Path) -> Path:
    """The `.processed.md` path for an intake file, whatever spelling it has now."""
    name = path.name
    for suffix in (PROCESSED_SUFFIX, LEGACY_SUFFIX, ".md"):
        if name.endswith(suffix):
            return path.with_name(name[: -len(suffix)] + PROCESSED_SUFFIX)
    return path.with_name(name + PROCESSED_SUFFIX)


def parse_ideas(text: str) -> list[Idea]:
    """Every `### ` entry under the `## Buildable Ideas` heading, with its verdict.

    Returns [] when the file has no Buildable Ideas section: intake runs that
    found nothing are legitimately markable with no routing at all.
    """
    start = IDEAS_HEADING.search(text)
    if start is None:
        return []
    body = text[start.end():]
    nxt = SECTION_HEADING.search(body)
    if nxt is not None:
        body = body[: nxt.start()]

    ideas: list[Idea] = []
    matches = list(IDEA_HEADING.finditer(body))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[match.end():end]
        classified = CLASSIFICATION.search(chunk)
        classification = classified.group(1).lower() if classified else None

        routed = ROUTING.search(chunk)
        if routed is not None:
            ideas.append(Idea(match.group(1), routed.group(1), routed.group(2), classification))
            continue
        legacy = LEGACY_BUILT.search(chunk)
        if legacy is not None:
            ideas.append(Idea(match.group(1), "BUILT", legacy.group(1), classification))
            continue
        ideas.append(Idea(match.group(1), None, "", classification))
    return ideas


def unrouted(path: Path) -> list[tuple[str, str]]:
    """(idea title, problem) for every idea in the file lacking a valid exit."""
    ideas = parse_ideas(path.read_text(encoding="utf-8"))
    return [(idea.title, problem) for idea in ideas if (problem := idea.problem)]


def intake_files(directory: Path) -> list[Path]:
    """Intake items only.

    `.nate_compiled_header.md` is a template the intake writer prepends, not an
    item to route; a dot- or underscore-prefixed name marks that class of
    supporting file. Without this filter --check reported the header as READY
    and --mark would have renamed the template out from under the writer.
    """
    return sorted(p for p in directory.glob("*.md")
                  if p.is_file() and not p.name.startswith((".", "_")))


def mark(path: Path, *, force: bool = False) -> Path:
    """Rename an intake file to `.processed.md`. Refuses on unrouted ideas."""
    if not path.is_file():
        raise FileNotFoundError(path)
    blockers = unrouted(path)
    if blockers and not force:
        detail = "\n".join(f"    - {title}: {problem}" for title, problem in blockers)
        raise ValueError(
            f"{path.name} has {len(blockers)} idea(s) with no recorded exit; "
            f"marking it processed would hide them:\n{detail}"
        )
    target = marked_name(path)
    if target == path:
        return path
    if target.exists():
        raise FileExistsError(target)
    path.rename(target)
    return target


def check(directory: Path) -> int:
    """Report drift. Exit code 1 when any intake file is unmarked or mis-spelled."""
    files = intake_files(directory)
    if not files:
        print(f"no intake files under {directory}")
        return 0

    legacy = [p for p in files if is_legacy(p)]
    bare = [p for p in files if not is_marked(p) and not is_legacy(p)]

    print(f"intake files: {len(files)}")
    print(f"  {PROCESSED_SUFFIX}: {sum(1 for p in files if is_marked(p))}")
    print(f"  {LEGACY_SUFFIX} (legacy spelling): {len(legacy)}")
    print(f"  unmarked: {len(bare)}")

    for path in legacy:
        print(f"LEGACY  {path.name} -> {marked_name(path).name} (run --migrate-done)")

    for path in bare:
        blockers = unrouted(path)
        if blockers:
            print(f"BLOCKED {path.name}: {len(blockers)} idea(s) with no recorded exit")
            for title, problem in blockers:
                print(f"          - {title}: {problem}")
        else:
            print(f"READY   {path.name}: every idea routed, run --mark")

    return 1 if (legacy or bare) else 0


def migrate_done(directory: Path) -> int:
    moved = 0
    for path in intake_files(directory):
        if not is_legacy(path):
            continue
        target = marked_name(path)
        if target.exists():
            print(f"skip {path.name}: {target.name} already exists")
            continue
        path.rename(target)
        print(f"renamed {path.name} -> {target.name}")
        moved += 1
    print(f"migrated {moved} file(s) to {PROCESSED_SUFFIX}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--intake-dir", type=Path, default=INTAKE_DIR)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="report marker drift")
    group.add_argument("--migrate-done", action="store_true",
                       help=f"rename {LEGACY_SUFFIX} files to {PROCESSED_SUFFIX}")
    group.add_argument("--mark", type=Path, metavar="FILE",
                       help="mark one intake file processed")
    parser.add_argument("--force", action="store_true",
                        help="mark despite unrouted ideas (records nothing, hides them)")
    args = parser.parse_args(argv)

    if args.check:
        return check(args.intake_dir)
    if args.migrate_done:
        return migrate_done(args.intake_dir)

    try:
        target = mark(args.mark, force=args.force)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"marked {target.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
