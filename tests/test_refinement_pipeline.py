"""Tests for refinement_pipeline.py -- proposal generation and management."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import refinement_pipeline


class TestGenerateProposal:
    SAMPLE_RESULT = {
        "skill_name": "weak-skill",
        "total_score": 40.0,
        "correctness": {"score": 8, "feedback": "Major errors"},
        "completeness": {"score": 12, "feedback": "Missing sections"},
        "clarity": {"score": 10, "feedback": "Vague instructions"},
        "efficiency": {"score": 10, "feedback": "Some bloat"},
        "suggestions": ["Fix errors", "Add missing phases", "Clarify triggers"],
        "evaluator_model": "gemini-3-flash-preview",
    }

    def test_generates_proposal(self):
        proposal = refinement_pipeline.generate_proposal(self.SAMPLE_RESULT)
        assert proposal["skill_name"] == "weak-skill"
        assert proposal["total_score"] == 40.0
        assert proposal["status"] == "pending"
        assert len(proposal["priority_areas"]) > 0

    def test_weakest_dimension_is_first_priority(self):
        proposal = refinement_pipeline.generate_proposal(self.SAMPLE_RESULT)
        areas = proposal["priority_areas"]
        # correctness (8) is weakest
        assert areas[0]["dimension"] == "correctness"
        assert areas[0]["severity"] == "high"

    def test_suggestions_carried_through(self):
        proposal = refinement_pipeline.generate_proposal(self.SAMPLE_RESULT)
        assert len(proposal["suggestions"]) == 3


class TestGetLatestResult:
    def test_returns_latest_file(self, tmp_path):
        results_dir = tmp_path / "ego_results"
        results_dir.mkdir()

        old = {"total_score": 40, "skill_name": "test"}
        new = {"total_score": 60, "skill_name": "test"}
        (results_dir / "test_20260401_100000.json").write_text(json.dumps(old))
        (results_dir / "test_20260402_100000.json").write_text(json.dumps(new))

        original = refinement_pipeline.RESULTS_DIR
        refinement_pipeline.RESULTS_DIR = results_dir
        try:
            result = refinement_pipeline.get_latest_result("test")
            assert result["total_score"] == 60
        finally:
            refinement_pipeline.RESULTS_DIR = original

    def test_returns_none_when_no_results(self, tmp_path):
        original = refinement_pipeline.RESULTS_DIR
        refinement_pipeline.RESULTS_DIR = tmp_path / "empty"
        try:
            result = refinement_pipeline.get_latest_result("nonexistent")
            assert result is None
        finally:
            refinement_pipeline.RESULTS_DIR = original


class TestSaveProposal:
    def test_saves_to_disk(self, tmp_path):
        original = refinement_pipeline.PROPOSALS_DIR
        refinement_pipeline.PROPOSALS_DIR = tmp_path / "proposals"
        try:
            proposal = {
                "skill_name": "test",
                "total_score": 45.0,
                "status": "pending",
                "priority_areas": [],
                "suggestions": [],
            }
            path = refinement_pipeline.save_proposal(proposal)
            assert path.is_file()
            saved = json.loads(path.read_text())
            assert saved["skill_name"] == "test"
        finally:
            refinement_pipeline.PROPOSALS_DIR = original


class TestListProposals:
    def test_lists_pending(self, tmp_path):
        proposals_dir = tmp_path / "proposals"
        proposals_dir.mkdir()
        (proposals_dir / "s1_20260401.json").write_text(json.dumps({"skill_name": "s1", "status": "pending"}))
        (proposals_dir / "s2_20260402.json").write_text(json.dumps({"skill_name": "s2", "status": "applied"}))

        original = refinement_pipeline.PROPOSALS_DIR
        refinement_pipeline.PROPOSALS_DIR = proposals_dir
        try:
            proposals = refinement_pipeline.list_proposals()
            assert len(proposals) == 2
            pending = [p for p in proposals if p["status"] == "pending"]
            assert len(pending) == 1
        finally:
            refinement_pipeline.PROPOSALS_DIR = original
