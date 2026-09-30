"""Regression tests for preprocessing/skill_normalizer.py."""

import pytest

from preprocessing.skill_normalizer import normalize_skill, normalize_skills, is_known_skill


@pytest.mark.parametrize("raw, canonical", [
    ("React", "React"),
    ("ReactJS", "React"),
    ("React.js", "React"),
    ("Postgres", "PostgreSQL"),
    ("PostgreSQL", "PostgreSQL"),
    ("sklearn", "scikit-learn"),
    ("scikit learn", "scikit-learn"),
    ("Scikit-learn", "scikit-learn"),
    ("NLP", "Natural Language Processing"),
])
def test_aliases_map_to_one_canonical_skill(raw, canonical):
    assert normalize_skill(raw)[0] == canonical


@pytest.mark.parametrize("raw, canonical", [
    # Previously returned the lowercase alias key unchanged
    ("javascript", "JavaScript"),
    ("angularjs", "AngularJS"),
    ("sql", "SQL"),
])
def test_exact_match_returns_canonical_casing(raw, canonical):
    skill, confidence = normalize_skill(raw)
    assert skill == canonical
    assert confidence == 1.0


def test_canonical_names_are_not_remapped_by_substring():
    # Previously "REST API" contained the alias "r" and was mapped to "R"
    assert normalize_skill("REST API")[0] == "REST API"
    assert normalize_skill("Machine Learning")[0] == "Machine Learning"


def test_unknown_words_are_returned_unchanged_with_low_confidence():
    # Previously substring matching turned these into real skills
    assert normalize_skill("Pune") == ("Pune", 0.5)
    assert normalize_skill("Developed") == ("Developed", 0.5)


def test_is_known_skill():
    assert is_known_skill("ReactJS")
    assert is_known_skill("REST API")
    assert not is_known_skill("Houston")


def test_normalize_skills_deduplicates_across_casing():
    skills = [skill for skill, _ in normalize_skills(["JavaScript", "javascript", "js"])]
    assert skills == ["JavaScript"]
