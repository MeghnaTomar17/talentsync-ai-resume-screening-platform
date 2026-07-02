"""
Skill Extraction Pipeline

Production-ready pipeline that combines multiple extraction methods:
1. Regex-based extraction (fast, pattern matching)
2. LLM-based extraction (intelligent, context-aware)
3. Skill normalization (alias mapping, canonical names)
4. Skill categorization (organized by category)

The pipeline automatically selects and merges results from different methods
to provide the most comprehensive skill extraction.
"""

from typing import List, Tuple, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from preprocessing.regex_skill_extractor import extract_skills_with_confidence
from preprocessing.llm_skill_extractor import extract_skills_with_llm, extract_skills_with_llm_detailed
from preprocessing.skill_normalizer import normalize_skills
from preprocessing.skill_categorizer import categorize_skills


class SkillExtractionPipeline:
    """
    Multi-method skill extraction pipeline with normalization and categorization.
    
    Strategy:
    1. Extract skills using regex patterns (fast, reliable) - PRIMARY METHOD
    2. Extract skills using LLM (intelligent, context-aware) - OPTIONAL ENHANCEMENT
    3. Normalize skills to canonical forms
    4. Remove duplicates and merge results
    5. Categorize skills by domain
    
    Note: LLM extraction is disabled by default for faster, local processing.
    Enable it explicitly for enhanced accuracy when needed.
    """
    
    def __init__(self, enable_llm: bool = False, use_llm_categorization: bool = False):
        """
        Initialize the skill extraction pipeline.
        
        Args:
            enable_llm: Whether to use LLM-based extraction (default: False)
                        Set to True for enhanced accuracy at the cost of speed
            use_llm_categorization: Whether to use LLM for categorization (default: False)
        """
        self.enable_llm = enable_llm
        self.use_llm_categorization = use_llm_categorization
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract skills from text using the pipeline.
        
        Args:
            text: Input text (resume or job description)
            
        Returns:
            Dictionary containing:
            - extracted_skills: List of canonical skill names
            - categorized_skills: Skills organized by category
            - confidence_score: Overall confidence in extraction
            - extraction_method: Method(s) used
            - raw_skills: Raw skills before normalization
        """
        # Method 1: Regex-based extraction
        regex_skills = extract_skills_with_confidence(text)
        
        # Method 2: LLM-based extraction (if enabled)
        llm_skills = []
        if self.enable_llm:
            if self.use_llm_categorization:
                # Use detailed LLM extraction with categorization
                llm_result = extract_skills_with_llm_detailed(text)
                if llm_result.get("success"):
                    llm_skills = llm_result.get("skills", [])
                    categorized_from_llm = llm_result.get("categorized", {})
            else:
                # Use simple LLM extraction
                llm_skills = extract_skills_with_llm(text)
        
        # Combine skills from all methods
        all_raw_skills = []
        extraction_methods = []
        
        if regex_skills:
            all_raw_skills.extend(regex_skills)
            extraction_methods.append("regex")
        
        if llm_skills:
            all_raw_skills.extend(llm_skills)
            extraction_methods.append("llm")
        
        # Normalize skills (remove duplicates, canonicalize names)
        normalized_skills = normalize_skills([s[0] for s in all_raw_skills])
        
        # Extract canonical skill names
        extracted_skills = [skill for skill, conf in normalized_skills]
        
        # Calculate overall confidence (average of all normalized skills)
        if normalized_skills:
            confidence_score = sum(conf for skill, conf in normalized_skills) / len(normalized_skills)
        else:
            confidence_score = 0.0
        
        # Categorize skills
        if self.use_llm_categorization and 'categorized_from_llm' in locals():
            # Use LLM categorization
            categorized_skills = categorized_from_llm
        else:
            # Use rule-based categorization
            categorized_skills = categorize_skills(extracted_skills)
        
        return {
            "extracted_skills": extracted_skills,
            "categorized_skills": categorized_skills,
            "confidence_score": round(confidence_score * 100, 2),
            "extraction_method": "+".join(extraction_methods) if extraction_methods else "none",
            "raw_skills": [s[0] for s in all_raw_skills],
            "skill_count": len(extracted_skills)
        }
    
    def extract_simple(self, text: str) -> List[str]:
        """
        Simple extraction that returns just the list of skills.
        
        This is for backward compatibility with existing code that expects
        a simple list of skill strings.
        
        Args:
            text: Input text
            
        Returns:
            List of canonical skill names
        """
        result = self.extract(text)
        return result["extracted_skills"]


# ---------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------

def extract_skills(text: str, enable_llm: bool = True) -> Dict[str, Any]:
    """
    Convenience function for skill extraction with the pipeline.
    
    This is the main entry point for skill extraction.
    
    Args:
        text: Input text (resume or job description)
        enable_llm: Whether to enable LLM-based extraction (default: True)
        
    Returns:
        Dictionary containing extracted skills and metadata
    """
    pipeline = SkillExtractionPipeline(enable_llm=enable_llm)
    return pipeline.extract(text)


def extract_skills_simple(text: str) -> List[str]:
    """
    Simple skill extraction returning just a list of skills.
    
    This maintains backward compatibility with the original skill_extractor.py.
    
    Args:
        text: Input text
        
    Returns:
        List of canonical skill names
    """
    pipeline = SkillExtractionPipeline(enable_llm=True)
    return pipeline.extract_simple(text)
