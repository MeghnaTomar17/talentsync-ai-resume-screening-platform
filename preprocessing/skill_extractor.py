"""
Skill Extractor - Production-Ready Pipeline

This module provides the main interface for skill extraction
using the multi-layer extraction pipeline with normalization and categorization.
"""

from preprocessing.skill_extraction_pipeline import extract_skills, extract_skills_simple


def advanced_skill_extractor(text: str, enable_llm: bool = False):
    """
    Extract skills from text using the production-ready pipeline.
    
    This function uses regex-based extraction with normalization and categorization.
    LLM-based extraction is available as an optional enhancement for improved accuracy.
    
    Args:
        text: Input text (resume or job description)
        enable_llm: Whether to enable LLM-based extraction (default: False)
                    Set to True for enhanced accuracy at the cost of speed
        
    Returns:
        For backward compatibility, returns a list of canonical skill names.
        To access full metadata including categorization, use extract_skills() directly.
        
    Note:
        This maintains backward compatibility with existing code that expects
        a simple list of skill strings. For full structured output, use:
        
        from preprocessing.skill_extraction_pipeline import extract_skills
        result = extract_skills(text, enable_llm=True)
        # result includes: extracted_skills, categorized_skills, confidence_score, etc.
    """
    return extract_skills_simple(text)