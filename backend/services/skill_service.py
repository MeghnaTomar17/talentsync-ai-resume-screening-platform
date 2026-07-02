"""
Skill Service

Handles skill extraction using the production-ready skill extraction pipeline.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.skill_extraction_pipeline import extract_skills
from backend.core.logger import logger


class SkillService:
    """Service for skill extraction and categorization."""
    
    def extract_skills(self, text: str, enable_llm: bool = False) -> Dict[str, Any]:
        """
        Extract skills from text.
        
        Args:
            text: Input text (resume or job description)
            enable_llm: Whether to enable LLM-based extraction (default: False)
            
        Returns:
            Dictionary containing extracted skills and metadata
        """
        result = extract_skills(text, enable_llm=enable_llm)
        logger.info(
            "skills_extracted method=%s count=%s confidence=%s llm=%s",
            result["extraction_method"],
            result["skill_count"],
            result["confidence_score"],
            enable_llm,
        )
        
        return {
            "extracted_skills": result["extracted_skills"],
            "categorized_skills": result["categorized_skills"],
            "confidence_score": result["confidence_score"],
            "extraction_method": result["extraction_method"],
            "skill_count": result["skill_count"]
        }
    
    def extract_skills_simple(self, text: str, enable_llm: bool = False) -> List[str]:
        """
        Extract skills returning just the list (for backward compatibility).
        
        Args:
            text: Input text
            enable_llm: Whether to enable LLM-based extraction
            
        Returns:
            List of canonical skill names
        """
        result = self.extract_skills(text, enable_llm=enable_llm)
        return result["extracted_skills"]
