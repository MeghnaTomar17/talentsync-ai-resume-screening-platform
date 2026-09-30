"""Regression tests for the deterministic skill extraction pipeline."""

import subprocess
import sys
from pathlib import Path

import pytest

from preprocessing.skill_extraction_pipeline import extract_skills
from preprocessing.text_cleaner import advanced_clean_text
from tests.evaluate_skill_extraction import evaluate, summarize

ROOT = Path(__file__).resolve().parent.parent


def skills_of(text):
    return set(extract_skills(text, enable_llm=False)["extracted_skills"])


# ------------------------------------------------------------------
# Symbols inside skill names
# ------------------------------------------------------------------

def test_symbol_skills_are_preserved():
    skills = skills_of("Skills: C++, C#, .NET 6, Node.js, ASP.NET, CI/CD")
    assert {"C++", "C#", ".NET", "Node.js", "ASP.NET", "CI/CD"} <= skills


def test_js_alias_does_not_match_inside_node_js():
    assert "JavaScript" not in skills_of("Built services with Node.js and Express.js")


def test_c_is_not_extracted_from_c_plus_plus_or_c_sharp():
    assert "C" not in skills_of("Worked with C++ and C# daily.")


# ------------------------------------------------------------------
# Skills outside the Skills section
# ------------------------------------------------------------------

def test_skills_in_experience_sentences_are_found():
    text = "- Built a REST API using FastAPI and PostgreSQL deployed on AWS."
    assert {"REST API", "FastAPI", "PostgreSQL", "AWS"} <= skills_of(text)


def test_hyphenated_and_line_broken_multi_word_skills():
    text = "Strong problem-solving and time-\nmanagement skills"
    assert {"Problem Solving", "Time Management"} <= skills_of(text)


# ------------------------------------------------------------------
# False positives
# ------------------------------------------------------------------

def test_names_places_verbs_and_headings_are_not_skills():
    text = "Rahul Mehta\nPune, Maharashtra\nSKILLS\nDeveloped and Implemented Python tools"
    assert skills_of(text) == {"Python"}


@pytest.mark.parametrize("text, not_expected", [
    ("Priya R\nChennai", "R"),
    ("Ready to go the extra mile", "Go"),
    ("Developer, Go Digital Solutions", "Go"),
    ("Analyst, Spring Valley Foods", "Spring Boot"),
    ("Account Manager, Swift Logistics", "Swift"),
    ("Enjoys rest days", "REST API"),
    ("Excellent communication", "Microsoft Excel"),
])
def test_ambiguous_words_are_not_extracted_in_prose(text, not_expected):
    assert not_expected not in skills_of(text)


@pytest.mark.parametrize("text, expected", [
    ("Languages: C, C++, R", {"C", "C++", "R"}),
    ("C/C++ programming", {"C", "C++"}),
    ("Languages: Python, Go, Swift", {"Python", "Go", "Swift"}),
    ("Designed REST APIs", {"REST API"}),
    ("Reports in MS Excel and Excel", {"Microsoft Excel"}),
])
def test_ambiguous_words_are_extracted_in_technology_form(text, expected):
    assert expected <= skills_of(text)


def test_no_duplicate_skills_with_different_casing():
    skills = extract_skills("JavaScript, javascript, JS", enable_llm=False)["extracted_skills"]
    assert skills == ["JavaScript"]


# ------------------------------------------------------------------
# Pipeline behaviour
# ------------------------------------------------------------------

def test_empty_text_returns_no_skills():
    result = extract_skills("", enable_llm=False)
    assert result["extracted_skills"] == []
    assert result["skill_count"] == 0
    assert result["extraction_method"] == "none"


def test_pipeline_does_not_import_gemini_when_llm_disabled():
    code = (
        "import sys; sys.path.insert(0, '.');"
        "from preprocessing.skill_extraction_pipeline import extract_skills;"
        "extract_skills('Python', enable_llm=False);"
        "print('preprocessing.llm_skill_extractor' in sys.modules)"
    )
    output = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert output == "False"


def test_cleaning_is_idempotent():
    # backend/main.py cleans request.resume_text for retrieval; clients that
    # still send already-cleaned text must get the same result.
    text = (ROOT / "tests" / "skill_extraction_cases.py").read_text(encoding="utf-8")
    once = advanced_clean_text(text)
    assert advanced_clean_text(once) == once


# ------------------------------------------------------------------
# Quality gate on the labelled evaluation set
# ------------------------------------------------------------------

def test_labelled_set_recall_and_precision():
    summary = summarize(evaluate(), "raw")
    assert summary["recall"] >= 95.0
    assert summary["precision"] >= 95.0
