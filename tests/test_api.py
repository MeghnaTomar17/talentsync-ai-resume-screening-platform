"""
FastAPI endpoint tests.

Retrieval and semantic scoring are replaced with fixed values so the tests
are fast and deterministic. One integration test at the end uses the real
FAISS index and embedding model when they are available.
"""

from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("faiss")
pytest.importorskip("sentence_transformers")

from fastapi.testclient import TestClient

import backend.main as main
from backend.services import feedback_service as feedback_module
from backend.services import roadmap_service as roadmap_module
from matching.ats_scorer import calculate_final_ats_score

ROOT = Path(__file__).resolve().parent.parent
client = TestClient(main.app)

RESUME = """Skills: Python, FastAPI, MySQL, Docker, Git
Experience: built REST APIs with FastAPI and MySQL, deployed with Docker.
Projects, Education, Experience sections included."""

JOB = """We need a backend engineer with Python, FastAPI, PostgreSQL,
Kubernetes and AWS. Git is required."""

FAKE_JOB = {
    "job_title": "Backend Developer",
    "job_description": JOB,
    "cleaned_description": JOB.lower(),
    "semantic_score": 70.0,
    "index": 0,
}


@pytest.fixture
def fake_retrieval(monkeypatch):
    monkeypatch.setattr(main.retrieval_service, "retrieve_jobs", lambda text, k=5: [FAKE_JOB])
    monkeypatch.setattr(main.retrieval_service, "score_job_description", lambda resume, jd: 65.0)


def test_health_reports_services():
    response = client.get("/health")
    assert response.status_code == 200
    services = response.json()["data"]["services"]
    assert services["faiss_retrieval"] in {"ready", "tfidf_fallback", "unavailable"}
    assert services["gemini_feedback"] in {"ready", "not_configured"}


def test_analyze_rejects_empty_resume():
    response = client.post("/analyze_resume", json={"resume_text": "   "})
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_analyze_with_provided_job_description(fake_retrieval):
    response = client.post("/analyze_resume", json={
        "resume_text": RESUME,
        "job_description": JOB,
        "job_title": "Backend Engineer",
    })
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["job_source"] == "provided"
    assert data["best_match"]["job_title"] == "Backend Engineer"
    assert data["semantic_score"] == 65.0
    assert data["matched_skills"] == ["FastAPI", "Git", "Python"]
    assert data["missing_skills"] == ["AWS", "Kubernetes", "PostgreSQL"]
    partial = {p["skill"]: p["related_skills"] for p in data["partial_matches"]}
    assert partial == {"Kubernetes": ["Docker"], "PostgreSQL": ["MySQL"]}

    expected = calculate_final_ats_score(65.0, data["skill_overlap_score"], data["quality_report"]["ats_score"])
    assert data["ats_score"] == expected
    total = sum(c["contribution"] for c in data["score_breakdown"]["components"].values())
    assert total == pytest.approx(data["ats_score"], abs=0.02)
    assert data["explanation"]
    # FAISS recommendations are still returned
    assert data["top_jobs"][0]["job_title"] == "Backend Developer"


def test_analyze_without_job_description_uses_best_dataset_job(fake_retrieval):
    response = client.post("/analyze_resume", json={"resume_text": RESUME})
    data = response.json()["data"]
    assert data["job_source"] == "dataset"
    assert data["best_match"]["job_title"] == "Backend Developer"
    assert data["semantic_score"] == 70.0


def test_analyze_without_jobs_returns_empty_analysis(monkeypatch):
    monkeypatch.setattr(main.retrieval_service, "retrieve_jobs", lambda text, k=5: [])
    response = client.post("/analyze_resume", json={"resume_text": RESUME})
    body = response.json()
    assert body["message"] == "No jobs found for analysis"
    assert body["data"]["ats_score"] is None
    assert "Python" in body["data"]["extracted_skills"]


def test_rank_candidates_sorted_with_summary(fake_retrieval):
    weak = "Skills: Excel, Communication\nExperience in sales."
    response = client.post("/rank_candidates", json={
        "job_description": JOB,
        "job_title": "Backend Engineer",
        "candidates": [
            {"candidate_id": "weak.pdf", "resume_text": weak},
            {"candidate_id": "strong.pdf", "resume_text": RESUME},
        ],
    })
    assert response.status_code == 200
    data = response.json()["data"]
    ids = [c["candidate_id"] for c in data["candidates"]]
    assert ids == ["strong.pdf", "weak.pdf"]
    assert [c["rank"] for c in data["candidates"]] == [1, 2]
    assert data["summary"]["total_candidates"] == 2
    assert data["summary"]["top_candidate"] == "strong.pdf"
    assert data["candidates"][0]["ats_score"] >= data["candidates"][1]["ats_score"]


def test_rank_candidates_requires_candidates():
    response = client.post("/rank_candidates", json={"job_description": JOB, "candidates": []})
    assert response.status_code == 422


def test_feedback_passes_missing_skills(monkeypatch):
    captured = {}

    def fake_feedback(resume_text, resume_skills, missing_skills, target_job):
        captured["missing"] = missing_skills
        return "# ATS Improvement Suggestions\n- Add Docker"

    monkeypatch.setattr(feedback_module, "generate_resume_feedback", fake_feedback)
    response = client.post("/resume_feedback", json={
        "resume_text": RESUME,
        "resume_skills": ["Python"],
        "missing_skills": ["AWS"],
        "job_title": "Backend Engineer",
    })
    assert response.status_code == 200
    assert captured["missing"] == ["AWS"]
    assert response.json()["data"]["suggestions"] == ["Add Docker"]


def test_feedback_failure_is_reported_as_error(monkeypatch):
    monkeypatch.setattr(
        feedback_module, "generate_resume_feedback",
        lambda *args: feedback_module.FEEDBACK_ERROR_PREFIX + "\n\nError:\ninvalid key",
    )
    response = client.post("/resume_feedback", json={"resume_text": RESUME, "resume_skills": []})
    assert response.status_code == 502
    assert response.json()["success"] is False


def test_roadmap_failure_is_reported_as_error(monkeypatch):
    monkeypatch.setattr(
        roadmap_module, "generate_career_roadmap",
        lambda *args: roadmap_module.ROADMAP_ERROR_PREFIX + ": quota exceeded",
    )
    response = client.post("/career_roadmap", json={"resume_skills": [], "missing_skills": []})
    assert response.status_code == 502


def test_upload_rejects_non_pdf():
    response = client.post("/upload_resume", files={"file": ("resume.txt", b"hello", "text/plain")})
    assert response.status_code == 400


def test_upload_parses_pdf_and_deletes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(main.resume_service, "upload_dir", tmp_path)
    with open(ROOT / "sample_resume" / "sample.pdf", "rb") as pdf:
        response = client.post(
            "/upload_resume?enable_ocr=false",
            files={"file": ("sample.pdf", pdf, "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "Active Directory" in data["resume_text"]
    assert data["extraction_metadata"]["ocr_used"] is False
    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(
    not (ROOT / "faiss_index" / "job_index.faiss").exists(),
    reason="FAISS index not built",
)
def test_integration_real_faiss_retrieval():
    response = client.post("/analyze_resume", json={"resume_text": RESUME})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["top_jobs"]) == 5
    assert 0 <= data["ats_score"] <= 100
