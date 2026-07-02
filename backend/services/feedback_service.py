"""
Feedback Service

Handles Gemini-powered resume feedback generation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.llm_feedback import generate_resume_feedback
from backend.core.logger import logger


class FeedbackService:
    """Service for resume feedback using Gemini."""
    
    def generate_feedback(self, resume_text: str, resume_skills: List[str],
                         job_title: str = None, job_description: str = None) -> Dict[str, Any]:
        """
        Generate resume feedback using Gemini.
        
        Args:
            resume_text: Cleaned resume text
            resume_skills: Extracted skills
            job_title: Target job title (optional)
            job_description: Target job description (optional)
            
        Returns:
            Dictionary with feedback and suggestions
        """
        feedback_text = generate_resume_feedback(
            resume_text,
            resume_skills,
            [],
            job_title or job_description or "Target Role"
        )
        logger.info("gemini_feedback_generated target=%s characters=%s", job_title or job_description or "Target Role", len(feedback_text))
        
        return {
            "feedback": feedback_text,
            "suggestions": self._extract_suggestions(feedback_text)
        }

    def _extract_suggestions(self, feedback_text: str) -> List[str]:
        """Extract a compact suggestions list from markdown feedback."""
        suggestions = []
        capture = False

        for line in feedback_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                capture = "suggestion" in stripped.lower() or "recommendation" in stripped.lower()
                continue
            if capture and stripped.startswith(("-", "*")):
                suggestions.append(stripped.lstrip("-* ").strip())

        return suggestions[:8]
