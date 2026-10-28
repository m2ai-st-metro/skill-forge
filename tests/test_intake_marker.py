"""Intake marker invariants (MAI-28).

Four intake files were consumed and never marked, so every scan re-surfaced
them; 10 of their ideas had no artifact and no recorded decision. A fifth and
sixth spelling of "done" would have made it worse. These tests pin the two
rules scripts/mark_intake_processed.py exists to enforce: one marker spelling,
and no marking a file whose ideas have no recorded exit.

Fixtures are synthetic on purpose. data/ is gitignored, so the real intake dir
is runtime state that is absent in a fresh clone and in CI.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import mark_intake_processed as marker  # noqa: E402


HEADER = "# Intake: example\n\n## TLDR\n\nSomething happened.\n\n## Buildable Ideas\n\n"


def write(directory: Path, name: str, ideas: str = "") -> Path:
    path = directory / name
    path.write_text(HEADER + ideas, encoding="utf-8")
    return path


def idea(title: str, routing: str | None = None,
         classification: str | None = "technique") -> str:
    body = f"### {title}\n\nA description of the idea.\n\n- **[a] Effort:** S\n"
    if classification is not None:
        body += f"\n**Classification:** {classification}\n"
    if routing is not None:
        body += f"\n**Routing:** {routing}\n"
    return body + "\n---\n\n"


class TestParseIdeas:
    def test_counts_every_idea_under_the_heading(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One") + idea("Two") + idea("Three"))
        assert [i.title for i in marker.parse_ideas(path.read_text())] == ["One", "Two", "Three"]

    def test_a_file_with_no_ideas_section_yields_nothing(self, tmp_path):
        path = tmp_path / "empty.md"
        path.write_text("# Intake\n\n[NO_NEW_CONTENT]\n", encoding="utf-8")
        assert marker.parse_ideas(path.read_text()) == []

    def test_stops_at_the_next_top_level_section(self, tmp_path):
        """A trailing `## Source update` must not swallow into the last idea."""
        path = write(tmp_path, "a.md", idea("One") + "## Source update\n\n### Not an idea\n")
        assert [i.title for i in marker.parse_ideas(path.read_text())] == ["One"]

    def test_legacy_status_built_line_counts_as_a_built_verdict(self, tmp_path):
        body = "### One\n\nText.\n\n**Classification:** technique\n\n**Status:** Built — `skills/one/`\n"
        path = write(tmp_path, "a.md", body)
        parsed = marker.parse_ideas(path.read_text())
        assert parsed[0].verdict == "BUILT"
        assert parsed[0].problem is None


class TestVerdictValidation:
    @pytest.mark.parametrize("routing", [
        "BUILT — `skills/poly-skill/`",
        "CARD — MAI-31",
        "CARD — Q-20260815-0001",
        "CARD — #104",
        "NO-GO — nothing consumes the output yet",
    ])
    def test_well_formed_verdicts_pass(self, tmp_path, routing):
        path = write(tmp_path, "a.md", idea("One", routing))
        assert marker.unrouted(path) == []

    def test_missing_routing_line_is_a_blocker(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One"))
        assert [t for t, _ in marker.unrouted(path)] == ["One"]

    def test_card_without_an_id_is_a_blocker(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "CARD — will file one later"))
        assert "CARD without a card id" in marker.unrouted(path)[0][1]

    def test_nogo_without_a_reason_is_a_blocker(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "NO-GO"))
        assert "NO-GO without a reason" in marker.unrouted(path)[0][1]

    def test_only_the_unrouted_ideas_are_reported(self, tmp_path):
        path = write(tmp_path, "a.md",
                     idea("Done", "BUILT — `skills/done/`") + idea("Open") + idea("Also open"))
        assert [t for t, _ in marker.unrouted(path)] == ["Open", "Also open"]


class TestClassification:
    """Tool-vs-technique gate (MAI-206). PR #112 (subscription-sdk-bridge) was a TOOL
    force-fit into a SKILL.md because nothing asked the question. Every idea now
    carries a grep-able `**Classification:**` line and only a technique may be BUILT."""

    def test_missing_classification_is_a_blocker(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "BUILT — `skills/one/`", classification=None))
        assert "no **Classification:** line" in marker.unrouted(path)[0][1]

    def test_unknown_classification_is_a_blocker(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "NO-GO — not for us, reason", classification="gadget"))
        assert "not one of technique, tool, other" in marker.unrouted(path)[0][1]

    def test_classification_is_parsed_case_insensitively(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "BUILT — `skills/one/`", classification="Technique"))
        assert marker.parse_ideas(path.read_text())[0].classification == "technique"
        assert marker.unrouted(path) == []

    @pytest.mark.parametrize("classification", ["tool", "other"])
    def test_a_non_technique_routed_built_is_a_blocker(self, tmp_path, classification):
        path = write(tmp_path, "a.md", idea("One", "BUILT — `skills/one/`", classification=classification))
        problems = marker.unrouted(path)
        assert len(problems) == 1
        assert f"{classification}-classified idea routed BUILT" in problems[0][1]

    @pytest.mark.parametrize("routing", [
        "CARD — MAI-207",
        "NO-GO — already have an equivalent in the stack",
    ])
    def test_a_tool_exits_as_card_or_nogo(self, tmp_path, routing):
        path = write(tmp_path, "a.md", idea("One", routing, classification="tool"))
        assert marker.unrouted(path) == []

    def test_a_tool_card_still_needs_an_issue_id(self, tmp_path):
        path = write(tmp_path, "a.md", idea("One", "CARD — will file later", classification="tool"))
        assert "CARD without a card id" in marker.unrouted(path)[0][1]

    def test_marking_refuses_a_tool_built_as_a_skill(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.md", idea("One", "BUILT — `skills/one/`", classification="tool"))
        with pytest.raises(ValueError, match="routed BUILT"):
            marker.mark(path)
        assert path.exists()

    def test_classification_is_grepable(self, tmp_path):
        """The whole point of recording it in the file: a later audit can grep it."""
        path = write(tmp_path, "a.md", idea("One", "CARD — MAI-207", classification="tool"))
        assert "**Classification:** tool" in path.read_text()




class TestMark:
    def test_marking_renames_to_the_processed_suffix(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.md", idea("One", "NO-GO — out of scope for now"))
        assert marker.mark(path).name == "src-2026-01-01.processed.md"
        assert not path.exists()

    def test_marking_refuses_while_an_idea_has_no_exit(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.md", idea("One"))
        with pytest.raises(ValueError, match="no recorded exit"):
            marker.mark(path)
        assert path.exists(), "the file must survive a refused mark"

    def test_force_overrides_the_refusal(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.md", idea("One"))
        assert marker.mark(path, force=True).name == "src-2026-01-01.processed.md"

    def test_marking_an_already_marked_file_is_a_no_op(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.processed.md")
        assert marker.mark(path) == path

    def test_marking_will_not_clobber_an_existing_target(self, tmp_path):
        write(tmp_path, "src-2026-01-01.processed.md")
        path = write(tmp_path, "src-2026-01-01.md")
        with pytest.raises(FileExistsError):
            marker.mark(path)
        assert path.exists()


class TestLegacySuffix:
    def test_done_suffix_maps_onto_the_processed_name(self, tmp_path):
        path = write(tmp_path, "src-2026-01-01.done.md")
        assert marker.marked_name(path).name == "src-2026-01-01.processed.md"

    def test_migrate_renames_only_the_legacy_files(self, tmp_path):
        write(tmp_path, "a-2026-01-01.done.md")
        write(tmp_path, "b-2026-01-02.processed.md")
        bare = write(tmp_path, "c-2026-01-03.md", idea("One"))

        marker.migrate_done(tmp_path)

        names = sorted(p.name for p in tmp_path.glob("*.md"))
        assert names == ["a-2026-01-01.processed.md", "b-2026-01-02.processed.md",
                         "c-2026-01-03.md"]
        assert bare.exists(), "migrate must not touch unmarked files"


class TestSupportingFilesAreNotIntakeItems:
    """The live dir holds `.nate_compiled_header.md`, a template the intake
    writer prepends. Treating it as an item made --check call it READY and
    would have let --mark rename the template out from under the writer."""

    @pytest.mark.parametrize("name", [".nate_compiled_header.md", "_template.md"])
    def test_dot_and_underscore_files_are_skipped(self, tmp_path, name):
        write(tmp_path, name)
        assert marker.intake_files(tmp_path) == []

    def test_a_directory_of_only_supporting_files_is_clean(self, tmp_path):
        write(tmp_path, ".nate_compiled_header.md")
        assert marker.check(tmp_path) == 0

    def test_real_items_are_still_seen_alongside_them(self, tmp_path):
        write(tmp_path, ".nate_compiled_header.md")
        write(tmp_path, "src-2026-01-01.md", idea("One"))
        assert [p.name for p in marker.intake_files(tmp_path)] == ["src-2026-01-01.md"]


class TestCheck:
    def test_clean_directory_exits_zero(self, tmp_path):
        write(tmp_path, "a-2026-01-01.processed.md")
        assert marker.check(tmp_path) == 0

    def test_an_empty_directory_exits_zero(self, tmp_path):
        assert marker.check(tmp_path) == 0

    @pytest.mark.parametrize("name", ["a-2026-01-01.md", "a-2026-01-01.done.md"])
    def test_any_unmarked_or_legacy_file_exits_nonzero(self, tmp_path, name):
        write(tmp_path, name, idea("One", "BUILT — `skills/one/`"))
        assert marker.check(tmp_path) == 1

    def test_check_distinguishes_ready_from_blocked(self, tmp_path, capsys):
        write(tmp_path, "ready-2026-01-01.md", idea("One", "NO-GO — superseded by the main skill"))
        write(tmp_path, "blocked-2026-01-02.md", idea("Two"))

        marker.check(tmp_path)

        out = capsys.readouterr().out
        assert "READY   ready-2026-01-01.md" in out
        assert "BLOCKED blocked-2026-01-02.md" in out
