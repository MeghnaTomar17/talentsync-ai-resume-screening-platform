"""Tests for ATS scoring, skill gaps and the score explanation."""

import pytest

from matching.ats_scorer import (
    calculate_skill_overlap,
    calculate_final_ats_score,
    SEMANTIC_WEIGHT,
    SKILL_OVERLAP_WEIGHT,
    QUALITY_WEIGHT,
)
from matching.skill_gap import analyze_skill_gaps, get_related_skills, RELATED_SKILL_GROUPS
from preprocessing.skill_normalizer import is_known_skill
from utils.explainability import build_score_breakdown, generate_score_reasons


def test_weights_are_the_documented_4_3_3_split():
    # Existing implementation: 40 % semantic, 30 % skill overlap, 30 % quality
    assert (SEMANTIC_WEIGHT, SKILL_OVERLAP_WEIGHT, QUALITY_WEIGHT) == (0.4, 0.3, 0.3)


def test_final_ats_score_formula():
    assert calculate_final_ats_score(80, 50, 70) == pytest.approx(32 + 15 + 21)
    assert calculate_final_ats_score(100, 100, 100) == 100
    assert calculate_final_ats_score(0, 0, 0) == 0


def test_skill_overlap():
    assert calculate_skill_overlap(["Python", "SQL"], ["Python", "SQL", "Docker", "AWS"]) == 50.0
    assert calculate_skill_overlap(["Python"], []) == 0


def test_skill_gaps_matched_missing_partial():
    result = analyze_skill_gaps(
        ["Python", "MySQL", "Docker"],
        ["Python", "PostgreSQL", "Kubernetes", "AWS"],
    )
    assert result["matched_skills"] == ["Python"]
    # missing keeps its old meaning: every job skill not matched
    assert result["missing_skills"] == ["AWS", "Kubernetes", "PostgreSQL"]
    assert result["partial_matches"] == [
        {"skill": "Kubernetes", "related_skills": ["Docker"]},
        {"skill": "PostgreSQL", "related_skills": ["MySQL"]},
    ]


def test_related_skills_do_not_include_the_skill_itself():
    assert "Docker" not in get_related_skills("Docker")
    assert get_related_skills("Unknown Skill") == set()


def test_related_groups_use_vocabulary_names():
    unknown = {skill for group in RELATED_SKILL_GROUPS for skill in group if not is_known_skill(skill)}
    assert unknown == set()


def test_breakdown_contributions_add_up_to_ats_score():
    ats = calculate_final_ats_score(62.5, 40.0, 85.0)
    breakdown = build_score_breakdown(62.5, 40.0, 85.0, ats)
    total = sum(c["contribution"] for c in breakdown["components"].values())
    assert total == pytest.approx(ats, abs=0.02)
    assert breakdown["components"]["semantic_similarity"]["max_contribution"] == 40.0


def test_reasons_explain_matched_missing_and_partial():
    ats = calculate_final_ats_score(60, 50, 80)
    breakdown = build_score_breakdown(60, 50, 80, ats)
    reasons = generate_score_reasons(
        breakdown,
        ["Python"],
        ["PostgreSQL"],
        [{"skill": "PostgreSQL", "related_skills": ["MySQL"]}],
        {"warnings": ["Limited text extracted."]},
    )
    text = " ".join(reasons)
    assert "1 of 2 job skills" in text
    assert "Matched skills: Python" in text
    assert "missing skills: PostgreSQL" in text
    assert "related skill(s) MySQL" in text
    assert "Quality warning: Limited text extracted." in text
