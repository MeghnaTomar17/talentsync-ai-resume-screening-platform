"""
TalentSync FastAPI Backend

Production-ready REST API for resume analysis, job matching, and career intelligence.
"""

from time import perf_counter

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.exceptions import FileUploadError, register_exception_handlers
from backend.core.logger import logger
from backend.core.responses import APIResponse, build_response, start_timer
from backend.models import (
    ResumeUploadResponse,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    ResumeFeedbackRequest,
    ResumeFeedbackResponse,
    CareerRoadmapRequest,
    CareerRoadmapResponse,
    HealthCheckResponse,
    JobMatch
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
    """Health check endpoint."""
    start_time = start_timer()
    data = HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "resume_parsing": "ready",
            "skill_extraction": "ready",
            "faiss_retrieval": "ready",
            "ats_scoring": "ready",
            "gemini_feedback": "ready",
            "career_roadmap": "ready"
        }
    )
    return build_response(success=True, message="API is healthy", data=data, start_time=start_time)


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

@app.post("/analyze_resume", response_model=APIResponse[AnalyzeResumeResponse])
async def analyze_resume(request: AnalyzeResumeRequest):
    """
    Analyze a resume: extract skills, find matching jobs, calculate ATS score.
    
    Args:
        request: Analysis request with resume text and options
        
    Returns:
        Complete analysis including skills, job matches, and ATS scores
    """
    start_time = start_timer()
    skill_result = skill_service.extract_skills(
        request.resume_text,
        enable_llm=request.enable_llm
    )

    resume_skills = skill_result["extracted_skills"]
    categorized_skills = skill_result["categorized_skills"]

    jobs = retrieval_service.retrieve_jobs(
        request.resume_text,
        k=settings.default_job_match_count,
    )

    if not jobs:
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

    best_job = jobs[0]
    job_skill_result = skill_service.extract_skills(
        best_job["cleaned_description"],
        enable_llm=request.enable_llm
    )
    job_skills = job_skill_result["extracted_skills"]

    skill_comparison = ats_service.get_matched_missing_skills(
        resume_skills,
        job_skills
    )
    quality_report = ats_service.analyze_extraction_quality(
        request.resume_text,
        resume_skills
    )
    semantic_score = best_job["semantic_score"]
    skill_overlap_score = ats_service.calculate_skill_overlap_score(
        resume_skills,
        job_skills
    )
    ats_score = ats_service.calculate_ats_score(
        semantic_score,
        skill_overlap_score,
        quality_report["ats_score"]
    )

    formatted_jobs = [
        JobMatch(
            job_title=job["job_title"],
            job_description=job["job_description"],
            semantic_score=job["semantic_score"]
        )
        for job in jobs
    ]

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
            semantic_score=best_job["semantic_score"]
        ),
        matched_skills=skill_comparison["matched_skills"],
        missing_skills=skill_comparison["missing_skills"],
        semantic_score=semantic_score,
        skill_overlap_score=skill_overlap_score,
        ats_score=ats_score,
        quality_report=quality_report
    )
    return build_response(success=True, message="Resume analyzed successfully", data=data, start_time=start_time)


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
        request.job_description
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
            "career_roadmap": "POST /career_roadmap"
        }
    }
    return build_response(success=True, message="TalentSync API is running", data=data, start_time=start_time)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
