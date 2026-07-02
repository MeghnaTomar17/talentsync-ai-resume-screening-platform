"""
Roadmap Service

Handles Gemini-powered career roadmap generation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.career_roadmap import generate_career_roadmap
from backend.core.logger import logger


class RoadmapService:
    """Service for career roadmap generation using Gemini."""
    
    def generate_roadmap(self, resume_skills: List[str], missing_skills: List[str],
                        target_role: str = None) -> Dict[str, Any]:
        """
        Generate career roadmap using Gemini.
        
        Args:
            resume_skills: Extracted skills from resume
            missing_skills: Missing skills for target role
            target_role: Target role (optional)
            
        Returns:
            Dictionary with roadmap and recommendations
        """
        target = target_role or "Career Growth"
        roadmap_text = generate_career_roadmap(target, resume_skills, missing_skills)
        logger.info("gemini_roadmap_generated target=%s characters=%s", target, len(roadmap_text))
        
        return {
            "target_role": target,
            "roadmap": roadmap_text,
            "recommendations": self._extract_recommendations(roadmap_text)
        }

    def _extract_recommendations(self, roadmap_text: str) -> List[str]:
        """Extract bullet recommendations from generated roadmap text."""
        recommendations = []
        for line in roadmap_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("-", "*")):
                recommendations.append(stripped.lstrip("-* ").strip())
        return recommendations[:8]
