"""Tests for quality_rubric.py -- rubric data structures and scoring."""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quality_rubric import DimensionScore, QualityResult, EVALUATION_PROMPT


class TestDimensionScore:
    def test_basic_creation(self):
        d = DimensionScore(name="correctness", score=20.0)
        assert d.name == "correctness"
        assert d.score == 20.0
        assert d.max_score == 25.0
        assert d.feedback == ""

    def test_normalized_score(self):
        d = DimensionScore(name="clarity", score=12.5)
        assert d.normalized() == 50.0

    def test_normalized_zero(self):
        d = DimensionScore(name="clarity", score=0.0)
        assert d.normalized() == 0.0

    def test_normalized_full(self):
        d = DimensionScore(name="clarity", score=25.0)
        assert d.normalized() == 100.0

    def test_normalized_zero_max(self):
        d = DimensionScore(name="clarity", score=10.0, max_score=0.0)
        assert d.normalized() == 0.0


class TestQualityResult:
    def _make_result(self, scores=(20, 18, 22, 15)):
        return QualityResult(
            skill_name="test-skill",
            correctness=DimensionScore(name="correctness", score=scores[0], feedback="Good"),
            completeness=DimensionScore(name="completeness", score=scores[1], feedback="OK"),
            clarity=DimensionScore(name="clarity", score=scores[2], feedback="Great"),
            efficiency=DimensionScore(name="efficiency", score=scores[3], feedback="Bloated"),
            suggestions=["Fix thing 1", "Fix thing 2"],
            evaluator_model="gemini-3-flash-preview",
            evaluated_at="2026-04-03T12:00:00Z",
        )

    def test_total_score(self):
        r = self._make_result((20, 18, 22, 15))
        assert r.total_score == 75.0

    def test_total_score_all_max(self):
        r = self._make_result((25, 25, 25, 25))
        assert r.total_score == 100.0

    def test_total_score_all_zero(self):
        r = self._make_result((0, 0, 0, 0))
        assert r.total_score == 0.0

    def test_dimensions_list(self):
        r = self._make_result()
        dims = r.dimensions
        assert len(dims) == 4
        assert dims[0].name == "correctness"
        assert dims[3].name == "efficiency"

    def test_to_dict(self):
        r = self._make_result((20, 18, 22, 15))
        d = r.to_dict()
        assert d["skill_name"] == "test-skill"
        assert d["total_score"] == 75.0
        assert d["correctness"]["score"] == 20
        assert d["correctness"]["feedback"] == "Good"
        assert len(d["suggestions"]) == 2
        assert d["evaluator_model"] == "gemini-3-flash-preview"

    def test_to_dict_has_all_dimensions(self):
        r = self._make_result()
        d = r.to_dict()
        for key in ("correctness", "completeness", "clarity", "efficiency"):
            assert key in d
            assert "score" in d[key]
            assert "feedback" in d[key]


class TestEvaluationPrompt:
    def test_prompt_has_placeholders(self):
        assert "{skill_name}" in EVALUATION_PROMPT
        assert "{skill_content}" in EVALUATION_PROMPT

    def test_prompt_formatting(self):
        rendered = EVALUATION_PROMPT.format(
            skill_name="test-skill",
            skill_content="# Test Skill\nDo the thing.",
        )
        assert "test-skill" in rendered
        assert "# Test Skill" in rendered

    def test_prompt_contains_rubric_dimensions(self):
        for dim in ("Correctness", "Completeness", "Clarity", "Efficiency"):
            assert dim in EVALUATION_PROMPT
