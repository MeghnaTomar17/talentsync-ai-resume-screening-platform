"""
pypdf Parser

Fallback PDF parser using pypdf (formerly PyPDF2).
Good for simple PDFs and as a secondary fallback option.
"""

from pypdf import PdfReader
from typing import Dict, Any


def extract_text_with_pypdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using pypdf.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - page_count: Number of pages
        - parser: Parser identifier
    """
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = " ".join(text_parts)
        
        return {
            "text": full_text,
            "page_count": len(text_parts),
            "parser": "pypdf",
            "success": len(full_text.strip()) > 0
        }
        
    except Exception as e:
        return {
            "text": "",
            "page_count": 0,
            "parser": "pypdf",
            "success": False,
            "error": str(e)
        }
