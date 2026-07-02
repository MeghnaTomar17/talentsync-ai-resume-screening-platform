"""
Extraction Quality Evaluator

Evaluates the quality of extracted text to determine the best parser result.
Uses multiple heuristics to score extraction quality.
"""

import re
from typing import Dict, Any


def evaluate_extraction_quality(text: str, parser: str) -> Dict[str, Any]:
    """
    Evaluate the quality of extracted text.
    
    Args:
        text: Extracted text from PDF
        parser: Name of the parser used
        
    Returns:
        Dictionary containing:
        - score: Quality score (0-100)
        - metrics: Individual quality metrics
    """
    if not text or len(text.strip()) < 50:
        return {
            "score": 0,
            "metrics": {
                "text_length": len(text),
                "word_count": 0,
                "alpha_ratio": 0,
                "section_keywords": 0,
                "special_chars": 0
            }
        }
    
    metrics = {}
    score = 100
    
    # Metric 1: Text length
    text_length = len(text)
    metrics["text_length"] = text_length
    
    # Penalize very short extractions
    if text_length < 500:
        score -= 40
    elif text_length < 1000:
        score -= 20
    elif text_length < 2000:
        score -= 10
    
    # Metric 2: Word count
    words = text.split()
    word_count = len(words)
    metrics["word_count"] = word_count
    
    # Penalize very few words
    if word_count < 50:
        score -= 30
    elif word_count < 100:
        score -= 15
    
    # Metric 3: Alphanumeric ratio (indicates garbage characters)
    alpha_chars = len(re.findall(r'[a-zA-Z0-9]', text))
    total_chars = len(text)
    alpha_ratio = alpha_chars / total_chars if total_chars > 0 else 0
    metrics["alpha_ratio"] = round(alpha_ratio, 3)
    
    # Penalize low alphanumeric ratio (lots of special chars)
    if alpha_ratio < 0.5:
        score -= 30
    elif alpha_ratio < 0.7:
        score -= 15
    
    # Metric 4: Resume section keywords
    section_keywords = [
        "experience", "education", "skills", "projects",
        "certifications", "summary", "objective", "work",
        "employment", "technical", "programming"
    ]
    
    text_lower = text.lower()
    found_sections = sum(1 for keyword in section_keywords if keyword in text_lower)
    metrics["section_keywords"] = found_sections
    
    # Reward having resume sections
    if found_sections >= 3:
        score += 10
    elif found_sections >= 2:
        score += 5
    elif found_sections == 0:
        score -= 20
    
    # Metric 5: Special character density (indicates formatting noise)
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s.,;:\-]', text))
    metrics["special_chars"] = special_chars
    
    # Penalize excessive special characters
    if special_chars > text_length * 0.1:
        score -= 20
    elif special_chars > text_length * 0.05:
        score -= 10
    
    # Metric 6: Parser-specific adjustments
    # OCR parsers tend to have more noise
    if parser == "easyocr":
        score -= 5  # Slight penalty for OCR due to potential errors
    
    # Metric 7: Line structure (good resumes have multiple lines)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    metrics["line_count"] = len(lines)
    
    if len(lines) < 5:
        score -= 15
    elif len(lines) < 10:
        score -= 5
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "metrics": metrics
    }


def select_best_extraction(extractions: list) -> Dict[str, Any]:
    """
    Select the best extraction from multiple parser results.
    
    Args:
        extractions: List of extraction result dictionaries
        
    Returns:
        Best extraction result with confidence score
    """
    scored_extractions = []
    
    for extraction in extractions:
        if extraction.get("success", False) and extraction.get("text"):
            quality = evaluate_extraction_quality(extraction["text"], extraction["parser"])
            scored_extractions.append({
                **extraction,
                "confidence": quality["score"],
                "quality_metrics": quality["metrics"]
            })
    
    if not scored_extractions:
        # Return empty result if all parsers failed
        return {
            "text": "",
            "parser_used": "none",
            "confidence": 0,
            "ocr_used": False,
            "fallback_count": len(extractions),
            "success": False
        }
    
    # Sort by confidence score and return the best
    best = max(scored_extractions, key=lambda x: x["confidence"])
    
    # Determine fallback count (how many parsers were tried before success)
    fallback_count = 0
    for extraction in extractions:
        if extraction["parser"] == best["parser"]:
            break
        fallback_count += 1
    
    return {
        "text": best["text"],
        "parser_used": best["parser"],
        "confidence": best["confidence"],
        "ocr_used": best.get("ocr_used", False),
        "fallback_count": fallback_count,
        "success": True,
        "quality_metrics": best["quality_metrics"]
    }
