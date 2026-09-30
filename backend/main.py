"""
TalentSync FastAPI Backend

Production-ready REST API for resume analysis, job matching, and career intelligence.
"""

import os
from time import perf_counter

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.exceptions import FileUploadError, InvalidInputError, register_exception_handlers
from backend.core.logger import logger
from backend.core.responses import APIResponse, build_response, start_timer
from preprocessing.text_cleaner import advanced_clean_text
from backend.models import (
    ResumeUploadResponse,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    ResumeFeedbackRequest,
    ResumeFeedbackResponse,
    CareerRoadmapRequest,
    CareerRoadmapResponse,
    HealthCheckResponse,
    JobMatch,
    RankCandidatesRequest,
    RankCandidatesResponse,
    CandidateRanking
)

from backend.services import (
    ResumeService,
    SkillService,
    RetrievalService,
    ATSService,
    FeedbackService,
    RoadmapService
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request.state.start_time = perf_counter()
    logger.info("request_started method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    processing_time = round(perf_counter() - request.state.start_time, 4)
    logger.info(
        "request_finished method=%s path=%s status=%s processing_time=%s",
        request.method,
        request.url.path,
        response.status_code,
        processing_time,
    )
    return response

# Initialize services
resume_service = ResumeService(upload_dir=settings.upload_dir)
skill_service = SkillService()
retrieval_service = RetrievalService(index_dir=settings.faiss_index_dir)
ats_service = ATSService()
feedback_service = FeedbackService()
roadmap_service = RoadmapService()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", response_model=APIResponse[HealthCheckResponse])
async def health_check():
    """
    Health check endpoint.
    
    Checks that the files the pipeline depends on exist and whether Gemini
    is configured. It does not load the embedding model (kept fast).
    """
    start_time = start_timer()
    index_ready = (
        (settings.faiss_index_path / "job_index.faiss").exists()
        and (settings.faiss_index_path / "job_metadata.pkl").exists()
    )
    jobs_ready = settings.jobs_path.exists()
    gemini_ready = bool(settings.gemini_api_key or os.getenv("GEMINI_API_KEY"))

    services = {
        "resume_parsing": "ready",
        "skill_extraction": "ready",
        "faiss_retrieval": "ready" if index_ready else ("tfidf_fallback" if jobs_ready else "unavailable"),
        "ats_scoring": "ready",
        "gemini_feedback": "ready" if gemini_ready else "not_configured",
        "career_roadmap": "ready" if gemini_ready else "not_configured"
    }
    core_ready = index_ready or jobs_ready
    data = HealthCheckResponse(
        status="healthy" if core_ready and gemini_ready else "degraded",
        version=settings.app_version,
        services=services
    )
    return build_response(success=True, message="API is running", data=data, start_time=start_time)


# ============================================================
# RESUME UPLOAD & PARSING
# ============================================================

@app.post("/upload_resume", response_model=APIResponse[ResumeUploadResponse])
async def upload_resume(file: UploadFile = File(...), enable_ocr: bool = True):
    """
    Upload and parse a resume PDF.
    
    Args:
        file: PDF file to upload
        enable_ocr: Whether to enable OCR fallback (default: True)
        
    Returns:
        Parsed resume text and extraction metadata
    """
    start_time = start_timer()
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise FileUploadError("Only PDF resume uploads are supported")

    file_content = await file.read()
    if not file_content:
        raise FileUploadError("Uploaded resume is empty")

    result = resume_service.process_uploaded_resume(
        file_content,
        file.filename,
        enable_ocr=enable_ocr
    )

    data = ResumeUploadResponse(
        resume_id=None,
        resume_text=result["text"],
        cleaned_text=result["cleaned_text"],
        extraction_metadata=result["extraction_metadata"]
    )
    return build_response(success=True, message="Resume parsed successfully", data=data, start_time=start_time)


# ============================================================
# RESUME ANALYSIS
# ============================================================

def _score_resume_against_job(cleaned_resume_text: str,
                              resume_skill_result: dict, job_description: str,
                              semantic_score: float, enable_llm: bool,
                              job_skills: list = None) -> dict:
    """
    Score one resume against one job description.
    
    Shared by /analyze_resume and /rank_candidates so both use exactly the
    same skill comparison, ATS formula and explanation.
    """
    resume_skills = resume_skill_result["extracted_skills"]

    if job_skills is None:
        job_skills = skill_service.extract_skills(
            job_description,
            enable_llm=enable_llm
        )["extracted_skills"]

    skill_comparison = ats_service.get_matched_missing_skills(
        resume_skills,
        job_skills
    )
    quality_report = ats_service.analyze_extraction_quality(
        cleaned_resume_text,
        resume_skills
    )
    skill_overlap_score = ats_service.calculate_skill_overlap_score(
        resume_skills,
        job_skills
    )
    ats_score = ats_service.calculate_ats_score(
        semantic_score,
        skill_overlap_score,
        quality_report["ats_score"]
    )
    explanation = ats_service.explain_score(
        semantic_score,
        skill_overlap_score,
        quality_report["ats_score"],
        ats_score,
        skill_comparison,
        quality_report
    )

    return {
        "job_skills": job_skills,
        "skill_comparison": skill_comparison,
        "quality_report": quality_report,
        "semantic_score": semantic_score,
        "skill_overlap_score": skill_overlap_score,
        "ats_score": ats_score,
        "score_breakdown": explanation["score_breakdown"],
        "explanation": explanation["explanation"],
    }


def _require_text(value: str, field_name: str) -> str:
    """Reject empty or whitespace-only text input."""
    if not value or not value.strip():
        raise InvalidInputError(f"{field_name} must not be empty")
    return value


@app.post("/analyze_resume", response_model=APIResponse[AnalyzeResumeResponse])
async def analyze_resume(request: AnalyzeResumeRequest):
    """
    Analyze a resume: extract skills, find matching jobs, calculate ATS score.
    
    If a job description is provided, the resume is scored against it.
    Otherwise it is scored against the best matching job from the dataset.
    Top dataset jobs are always returned as recommendations.
    
    Args:
        request: Analysis request with resume text and options
        
    Returns:
        Complete analysis including skills, job matches, and ATS scores
    """
    start_time = start_timer()
    _require_text(request.resume_text, "resume_text")

    # Skills are extracted from the original text. The cleaned text is
    # lowercased and stripped of symbols, which destroys skills such as
    # C++, C#, .NET and Node.js. Job retrieval and the quality report keep
    # using the cleaned text exactly as before (cleaning is idempotent, so
    # clients that still send cleaned text get the same retrieval result).
    cleaned_resume_text = advanced_clean_text(request.resume_text)

    skill_result = skill_service.extract_skills(
        request.resume_text,
        enable_llm=request.enable_llm
    )

    resume_skills = skill_result["extracted_skills"]
    categorized_skills = skill_result["categorized_skills"]

    jobs = retrieval_service.retrieve_jobs(
        cleaned_resume_text,
        k=settings.default_job_match_count,
    )

    formatted_jobs = [
        JobMatch(
            job_title=job["job_title"],
            job_description=job["job_description"],
            semantic_score=job["semantic_score"]
        )
        for job in jobs
    ]

    provided_jd = request.job_description if request.job_description and request.job_description.strip() else None

    if provided_jd:
        # Compare with the job description supplied by the user
        job_source = "provided"
        best_job = {
            "job_title": request.job_title or "Provided job description",
            "job_description": provided_jd,
            "semantic_score": retrieval_service.score_job_description(
                cleaned_resume_text,
                advanced_clean_text(provided_jd)
            ),
        }
    elif jobs:
        # No job description: compare with the best dataset match
        job_source = "dataset"
        best_job = jobs[0]
    else:
        data = AnalyzeResumeResponse(
            extracted_skills=resume_skills,
            categorized_skills=categorized_skills,
            skill_confidence=skill_result["confidence_score"],
            skill_count=skill_result["skill_count"],
            extraction_method=skill_result["extraction_method"],
            top_jobs=[],
            best_match=None,
            matched_skills=[],
            missing_skills=[],
            semantic_score=None,
            skill_overlap_score=None,
            ats_score=None,
            quality_report=None
        )
        return build_response(success=True, message="No jobs found for analysis", data=data, start_time=start_time)

    result = _score_resume_against_job(
        cleaned_resume_text,
        skill_result,
        best_job["job_description"],
        best_job["semantic_score"],
        request.enable_llm
    )

    data = AnalyzeResumeResponse(
        extracted_skills=resume_skills,
        categorized_skills=categorized_skills,
        skill_confidence=skill_result["confidence_score"],
        skill_count=skill_result["skill_count"],
        extraction_method=skill_result["extraction_method"],
        top_jobs=formatted_jobs,
        best_match=JobMatch(
            job_title=best_job["job_title"],
            job_description=best_job["job_description"],
            semantic_score=best_job["semantic_score"],
            skill_overlap_score=result["skill_overlap_score"],
            ats_score=result["ats_score"]
        ),
        matched_skills=result["skill_comparison"]["matched_skills"],
        missing_skills=result["skill_comparison"]["missing_skills"],
        partial_matches=result["skill_comparison"]["partial_matches"],
        semantic_score=result["semantic_score"],
        skill_overlap_score=result["skill_overlap_score"],
        ats_score=result["ats_score"],
        quality_report=result["quality_report"],
        score_breakdown=result["score_breakdown"],
        explanation=result["explanation"],
        job_source=job_source
    )
    return build_response(success=True, message="Resume analyzed successfully", data=data, start_time=start_time)


# ============================================================
# CANDIDATE RANKING
# ============================================================

@app.post("/rank_candidates", response_model=APIResponse[RankCandidatesResponse])
async def rank_candidates(request: RankCandidatesRequest):
    """
    Rank several resumes against one job description.
    
    Every candidate is scored with the same pipeline as /analyze_resume.
    Candidates are sorted by ATS score (highest first); each keeps its
    score breakdown and explanation.
    
    Args:
        request: Job description and candidate resume texts
        
    Returns:
        Ranked candidates and summary statistics
    """
    start_time = start_timer()
    _require_text(request.job_description, "job_description")

    job_skills = skill_service.extract_skills(
        request.job_description,
        enable_llm=request.enable_llm
    )["extracted_skills"]
    cleaned_jd = advanced_clean_text(request.job_description)

    scored = []
    for candidate in request.candidates:
        _require_text(candidate.resume_text, f"resume_text for {candidate.candidate_id}")
        cleaned_resume_text = advanced_clean_text(candidate.resume_text)
        skill_result = skill_service.extract_skills(
            candidate.resume_text,
            enable_llm=request.enable_llm
        )
        semantic_score = retrieval_service.score_job_description(cleaned_resume_text, cleaned_jd)
        result = _score_resume_against_job(
            cleaned_resume_text,
            skill_result,
            request.job_description,
            semantic_score,
            request.enable_llm,
            job_skills=job_skills
        )
        scored.append((candidate, skill_result, result))

    scored.sort(key=lambda item: item[2]["ats_score"], reverse=True)

    rankings = [
        CandidateRanking(
            rank=position,
            candidate_id=candidate.candidate_id,
            ats_score=result["ats_score"],
            semantic_score=result["semantic_score"],
            skill_overlap_score=result["skill_overlap_score"],
            quality_score=result["quality_report"]["ats_score"],
            extracted_skills=skill_result["extracted_skills"],
            matched_skills=result["skill_comparison"]["matched_skills"],
            missing_skills=result["skill_comparison"]["missing_skills"],
            partial_matches=result["skill_comparison"]["partial_matches"],
            explanation=result["explanation"]
        )
        for position, (candidate, skill_result, result) in enumerate(scored, start=1)
    ]

    summary = ats_service.summarize_candidates(
        [ranking.model_dump() for ranking in rankings]
    )
    data = RankCandidatesResponse(
        job_title=request.job_title or "Provided job description",
        job_skills=job_skills,
        candidates=rankings,
        summary=summary
    )
    logger.info("candidates_ranked count=%s top=%s", len(rankings), summary.get("top_candidate"))
    return build_response(success=True, message="Candidates ranked successfully", data=data, start_time=start_time)


# ============================================================
# RESUME FEEDBACK
# ============================================================

@app.post("/resume_feedback", response_model=APIResponse[ResumeFeedbackResponse])
async def get_resume_feedback(request: ResumeFeedbackRequest):
    """
    Get AI-powered resume feedback using Gemini.
    
    Args:
        request: Feedback request with resume text and optional job details
        
    Returns:
        Feedback and suggestions for improvement
    """
    start_time = start_timer()
    result = feedback_service.generate_feedback(
        request.resume_text,
        request.resume_skills,
        request.job_title,
        request.job_description,
        missing_skills=request.missing_skills
    )

    data = ResumeFeedbackResponse(
        feedback=result["feedback"],
        suggestions=result["suggestions"]
    )
    return build_response(success=True, message="Feedback generated successfully", data=data, start_time=start_time)


# ============================================================
# CAREER ROADMAP
# ============================================================

@app.post("/career_roadmap", response_model=APIResponse[CareerRoadmapResponse])
async def get_career_roadmap(request: CareerRoadmapRequest):
    """
    Generate a career roadmap using Gemini.
    
    Args:
        request: Roadmap request with skills and target role
        
    Returns:
        Career roadmap with milestones and recommendations
    """
    start_time = start_timer()
    result = roadmap_service.generate_roadmap(
        request.resume_skills,
        request.missing_skills,
        request.target_role
    )

    data = CareerRoadmapResponse(
        target_role=result["target_role"],
        roadmap=result["roadmap"],
        recommendations=result["recommendations"]
    )
    return build_response(success=True, message="Roadmap generated successfully", data=data, start_time=start_time)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    start_time = start_timer()
    data = {
        "name": "TalentSync API",
        "version": settings.app_version,
        "description": settings.app_description,
        "endpoints": {
            "health": "GET /health",
            "upload_resume": "POST /upload_resume",
            "analyze_resume": "POST /analyze_resume",
            "resume_feedback": "POST /resume_feedback",
            "career_roadmap": "POST /career_roadmap",
            "rank_candidates": "POST /rank_candidates"
        }
    }
    return build_response(success=True, message="TalentSync API is running", data=data, start_time=start_time)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
