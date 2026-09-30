"""
Pydantic Models for TalentSync API

Request and response models for all API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ============================================================
# RESUME UPLOAD & PARSING MODELS
# ============================================================

class ResumeUploadData(BaseModel):
    """Parsed resume payload."""
    resume_id: Optional[str] = None
    resume_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    extraction_metadata: Optional[Dict[str, Any]] = None


ResumeUploadResponse = ResumeUploadData


# ============================================================
# RESUME ANALYSIS MODELS
# ============================================================

class AnalyzeResumeRequest(BaseModel):
    """Request to analyze a resume."""
    resume_text: str = Field(..., description="Extracted text from resume")
    enable_llm: bool = Field(default=False, description="Enable LLM for enhanced skill extraction")
    job_description: Optional[str] = Field(
        default=None,
        description="Target job description. When omitted, the best matching job from the dataset is used"
    )
    job_title: Optional[str] = Field(default=None, description="Title of the provided job description")


class PartialMatch(BaseModel):
    """A job skill that is missing but has related skills in the resume."""
    skill: str
    related_skills: List[str]


class SkillInfo(BaseModel):
    """Information about an extracted skill."""
    skill: str
    category: Optional[str] = None


class CategorizedSkills(BaseModel):
    """Skills organized by category."""
    category: str
    skills: List[str]


class JobMatch(BaseModel):
    """Information about a matched job."""
    job_title: str
    job_description: str
    semantic_score: float
    skill_overlap_score: Optional[float] = None
    ats_score: Optional[float] = None


class AnalyzeResumeData(BaseModel):
    """Resume analysis payload."""
    extracted_skills: List[str]
    categorized_skills: Dict[str, List[str]]
    skill_confidence: float
    skill_count: int
    extraction_method: str
    top_jobs: List[JobMatch]
    best_match: Optional[JobMatch] = None
    matched_skills: List[str]
    missing_skills: List[str]
    semantic_score: Optional[float] = None
    skill_overlap_score: Optional[float] = None
    ats_score: Optional[float] = None
    quality_report: Optional[Dict[str, Any]] = None
    partial_matches: List[PartialMatch] = []
    score_breakdown: Optional[Dict[str, Any]] = None
    explanation: List[str] = []
    job_source: str = Field(default="dataset", description="'provided' (user job description) or 'dataset' (best FAISS match)")


AnalyzeResumeResponse = AnalyzeResumeData


# ============================================================
# CANDIDATE RANKING MODELS
# ============================================================

class CandidateInput(BaseModel):
    """One candidate resume to rank."""
    candidate_id: str = Field(..., description="File name or any identifier chosen by the client")
    resume_text: str


class RankCandidatesRequest(BaseModel):
    """Request to rank several resumes against one job description."""
    job_description: str
    job_title: Optional[str] = None
    candidates: List[CandidateInput] = Field(..., min_length=1, max_length=50)
    enable_llm: bool = False


class CandidateRanking(BaseModel):
    """Ranking result for one candidate."""
    rank: int
    candidate_id: str
    ats_score: float
    semantic_score: float
    skill_overlap_score: float
    quality_score: float
    extracted_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[PartialMatch] = []
    explanation: List[str] = []


class RankCandidatesData(BaseModel):
    """Ranked candidates plus summary statistics."""
    job_title: str
    job_skills: List[str]
    candidates: List[CandidateRanking]
    summary: Dict[str, Any]


RankCandidatesResponse = RankCandidatesData


# ============================================================
# RESUME FEEDBACK MODELS
# ============================================================

class ResumeFeedbackRequest(BaseModel):
    """Request for resume feedback."""
    resume_text: str
    resume_skills: List[str]
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    missing_skills: List[str] = []


class ResumeFeedbackData(BaseModel):
    """Resume feedback payload."""
    feedback: str
    suggestions: List[str]


ResumeFeedbackResponse = ResumeFeedbackData


# ============================================================
# CAREER ROADMAP MODELS
# ============================================================

class CareerRoadmapRequest(BaseModel):
    """Request for career roadmap generation."""
    resume_skills: List[str]
    missing_skills: List[str]
    target_role: Optional[str] = None


class RoadmapMilestone(BaseModel):
    """A milestone in the career roadmap."""
    phase: str
    skills_to_learn: List[str]
    timeline: str
    resources: List[str]


class CareerRoadmapData(BaseModel):
    """Career roadmap payload."""
    target_role: str
    roadmap: str
    recommendations: List[str]


CareerRoadmapResponse = CareerRoadmapData


# ============================================================
# HEALTH CHECK MODELS
# ============================================================

class HealthCheckData(BaseModel):
    """Health check payload."""
    status: str
    version: str
    services: Dict[str, str]


HealthCheckResponse = HealthCheckData
