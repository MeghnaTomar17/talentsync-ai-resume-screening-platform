"""
PyMuPDF (fitz) Parser

Primary PDF parser using PyMuPDF for fast and reliable text extraction.
Performs well on most PDF types including modern resumes.
"""

import fitz  # PyMuPDF
from typing import Dict, Any


def extract_text_with_pymupdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using PyMuPDF (fitz).
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - page_count: Number of pages
        - parser: Parser identifier
    """
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page in doc:
            # Extract text with layout preservation
            text = page.get_text("text")  # Plain text extraction
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        full_text = " ".join(text_parts)
        
        return {
            "text": full_text,
            "page_count": len(text_parts),
            "parser": "pymupdf",
            "success": len(full_text.strip()) > 0
        }
        
    except Exception as e:
        return {
            "text": "",
            "page_count": 0,
            "parser": "pymupdf",
            "success": False,
            "error": str(e)
        }
