"""
ATS Service

Handles ATS scoring and quality analysis.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from matching.ats_scorer import (
    calculate_skill_overlap,
    calculate_resume_quality,
    calculate_final_ats_score
)
from utils.extraction_quality import analyze_extraction_quality
from backend.core.logger import logger


class ATSService:
    """Service for ATS scoring and quality analysis."""
    
    def calculate_skill_overlap_score(self, resume_skills: List[str], 
                                      job_skills: List[str]) -> float:
        """
        Calculate skill overlap between resume and job.
        
        Args:
            resume_skills: List of resume skills
            job_skills: List of job skills
            
        Returns:
            Skill overlap score (0-100)
        """
        score = calculate_skill_overlap(resume_skills, job_skills)
        logger.info("ats_skill_overlap score=%s resume_skills=%s job_skills=%s", score, len(resume_skills), len(job_skills))
        return score
    
    def calculate_resume_quality_score(self, cleaned_text: str) -> float:
        """
        Calculate resume quality score.
        
        Args:
            cleaned_text: Cleaned resume text
            Resume quality score (0-100)
        """
        score = calculate_resume_quality(cleaned_text)
        logger.info("ats_resume_quality score=%s text_length=%s", score, len(cleaned_text))
        return score
    
    def calculate_ats_score(self, semantic_score: float, 
                           skill_overlap_score: float,
                           quality_score: float) -> float:
        """
        Calculate final ATS score.
        
        Args:
            semantic_score: Semantic similarity score (0-100)
            skill_overlap_score: Skill overlap score (0-100)
            quality_score: Resume quality score (0-100)
            
        Returns:
            Final ATS score (0-100)
        """
        score = calculate_final_ats_score(semantic_score, skill_overlap_score, quality_score)
        logger.info(
            "ats_final_score semantic=%s skill_overlap=%s quality=%s final=%s",
            semantic_score,
            skill_overlap_score,
            quality_score,
            score,
        )
        return score
    
    def analyze_extraction_quality(self, cleaned_text: str, 
                                    resume_skills: List[str]) -> Dict[str, Any]:
        """
        Analyze extraction quality.
        
        Args:
            cleaned_text: Cleaned resume text
            resume_skills: Extracted skills
            
        Returns:
            Dictionary with quality analysis
        """
        report = analyze_extraction_quality(cleaned_text, resume_skills)
        logger.info(
            "extraction_quality_analyzed quality=%s ats=%s type=%s",
            report.get("quality_score"),
            report.get("ats_score"),
            report.get("resume_type"),
        )
        return report
    
    def get_matched_missing_skills(self, resume_skills: List[str], 
                                    job_skills: List[str]) -> Dict[str, List[str]]:
        """
        Get matched and missing skills.
        
        Args:
            resume_skills: List of resume skills
            job_skills: List of job skills
            
        Returns:
            Dictionary with matched and missing skills
        """
        matched = list(set(resume_skills).intersection(set(job_skills)))
        missing = list(set(job_skills) - set(resume_skills))
        
        return {
            "matched_skills": matched,
            "missing_skills": missing
        }
