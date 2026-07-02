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


AnalyzeResumeResponse = AnalyzeResumeData


# ============================================================
# RESUME FEEDBACK MODELS
# ============================================================

class ResumeFeedbackRequest(BaseModel):
    """Request for resume feedback."""
    resume_text: str
    resume_skills: List[str]
    job_title: Optional[str] = None
    job_description: Optional[str] = None


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
