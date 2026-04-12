#!/usr/bin/env python3
"""Ego Quality Judge -- LLM-evaluated skill quality scoring.

Evaluates skill definitions against a four-dimension rubric (correctness,
completeness, clarity, efficiency) using an LLM judge. Supports batch
evaluation of all skills or targeted evaluation of specific skills.

Usage:
    python src/ego_evaluator.py                          # Evaluate all skills
    python src/ego_evaluator.py classify-agent            # Evaluate one skill
    python src/ego_evaluator.py --update                  # Write scores to registry
    python src/ego_evaluator.py --threshold 50            # Flag skills below 50
    python src/ego_evaluator.py --dry-run                 # Print prompt, skip LLM call

Requires GOOGLE_API_KEY in ~/.env.shared (uses Gemini as the judge model).
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

from quality_rubric import (
    EVALUATION_PROMPT,
    DimensionScore,
    QualityResult,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
RESULTS_DIR = REPO_ROOT / "data" / "ego_results"

# Default judge model -- Gemini via google-generativeai SDK
DEFAULT_MODEL = "gemini-3-flash-preview"


def load_env():
    """Load API keys from ~/.env.shared."""
    env_path = Path.home() / ".env.shared"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ.setdefault(key, value)


def read_skill(skill_name: str) -> str | None:
    """Read SKILL.md content for a given skill."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.is_file():
        return None
    return skill_path.read_text()


def call_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call an LLM and return the response text.

    Uses google-generativeai SDK with Gemini models.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        print("ERROR: google-generativeai not installed. Run: pip install google-generativeai")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set. Source ~/.env.shared first.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(prompt)
    return response.text


def parse_llm_response(response_text: str, skill_name: str) -> QualityResult:
    """Parse the JSON response from the LLM into a QualityResult."""
    # Strip markdown fences if present
    text = response_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {text[:500]}")

    def extract_dim(key: str) -> DimensionScore:
        dim = data.get(key, {})
        score = float(dim.get("score", 0))
        # Clamp to 0-25
        score = max(0.0, min(25.0, score))
        return DimensionScore(
            name=key,
            score=score,
            feedback=str(dim.get("feedback", "")),
        )

    return QualityResult(
        skill_name=skill_name,
        correctness=extract_dim("correctness"),
        completeness=extract_dim("completeness"),
        clarity=extract_dim("clarity"),
        efficiency=extract_dim("efficiency"),
        suggestions=data.get("suggestions", []),
        evaluator_model=DEFAULT_MODEL,
        evaluated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )


def evaluate_skill(skill_name: str, dry_run: bool = False) -> QualityResult | None:
    """Evaluate a single skill and return the QualityResult."""
    content = read_skill(skill_name)
    if not content:
        print(f"  SKIP {skill_name}: no SKILL.md found")
        return None

    prompt = EVALUATION_PROMPT.format(
        skill_name=skill_name,
        skill_content=content,
    )

    if dry_run:
        print(f"  DRY RUN {skill_name}: prompt length = {len(prompt)} chars")
        return None

    print(f"  Evaluating {skill_name}...")
    response = call_llm(prompt)
    return parse_llm_response(response, skill_name)


def save_result(result: QualityResult) -> Path:
    """Persist evaluation result as JSON for audit trail."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"{result.skill_name}_{timestamp}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2) + "\n")
    return path


def update_registry_ego_score(skill_name: str, ego_score: float) -> bool:
    """Write ego_quality_score to a skill's skill-registry.yaml."""
    registry_path = SKILLS_DIR / skill_name / "skill-registry.yaml"
    if not registry_path.is_file():
        return False

    content = registry_path.read_text()
    lines = content.splitlines()
    new_lines = []
    updated = False
    in_metrics = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "metrics:":
            in_metrics = True
            new_lines.append(line)
            continue

        if in_metrics and stripped.startswith("health_score:"):
            new_lines.append(line)
            # Insert ego_quality_score after health_score if not already present
            # Check if next line already has ego_quality_score
            has_ego = any(
                l.strip().startswith("ego_quality_score:")
                for l in lines[i + 1 : i + 3]
            )
            if not has_ego:
                indent = line[: len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}ego_quality_score: {ego_score}")
                updated = True
            continue

        if in_metrics and stripped.startswith("ego_quality_score:"):
            indent = line[: len(line) - len(line.lstrip())]
            new_line = f"{indent}ego_quality_score: {ego_score}"
            if line != new_line:
                new_lines.append(new_line)
                updated = True
            else:
                new_lines.append(line)
            continue

        # Detect leaving metrics block
        if in_metrics and ":" in stripped and not stripped.startswith(
            ("invocations_30d:", "last_invoked:", "manual_rating:", "health_score:", "ego_quality_score:")
        ):
            in_metrics = False

        new_lines.append(line)

    if updated:
        registry_path.write_text("\n".join(new_lines) + "\n")
    return updated


def main():
    args = sys.argv[1:]
    do_update = "--update" in args
    dry_run = "--dry-run" in args
    threshold = 50  # default
    for i, arg in enumerate(args):
        if arg == "--threshold" and i + 1 < len(args):
            threshold = int(args[i + 1])

    skill_filter = [a for a in args if not a.startswith("--") and a not in (str(threshold),)]

    load_env()

    # Determine which skills to evaluate
    if skill_filter:
        skill_dirs = [SKILLS_DIR / name for name in skill_filter if (SKILLS_DIR / name).is_dir()]
    else:
        skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())

    results: list[QualityResult] = []
    for skill_dir in skill_dirs:
        result = evaluate_skill(skill_dir.name, dry_run=dry_run)
        if result:
            results.append(result)
            save_result(result)

    if not results:
        print("\nNo skills evaluated.")
        return 0

    # Print report
    print(f"\n{'Skill':<35} {'Total':>6} {'Corr':>6} {'Comp':>6} {'Clar':>6} {'Effi':>6} {'Flag'}")
    print("-" * 85)
    for r in results:
        flag = "***" if r.total_score < threshold else ""
        print(
            f"{r.skill_name:<35} {r.total_score:>6.1f} "
            f"{r.correctness.score:>6.1f} {r.completeness.score:>6.1f} "
            f"{r.clarity.score:>6.1f} {r.efficiency.score:>6.1f} {flag}"
        )

    flagged = [r for r in results if r.total_score < threshold]
    if flagged:
        print(f"\n{len(flagged)} skill(s) below quality threshold {threshold}:")
        for r in flagged:
            print(f"  - {r.skill_name} ({r.total_score:.1f})")
            for s in r.suggestions[:3]:
                print(f"    * {s}")

    if do_update:
        updated = 0
        for r in results:
            if update_registry_ego_score(r.skill_name, r.total_score):
                updated += 1
        print(f"\nUpdated ego_quality_score in {updated} registry files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
