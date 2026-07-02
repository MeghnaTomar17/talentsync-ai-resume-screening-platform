"""
pdfplumber Parser

Fallback PDF parser using pdfplumber for robust text extraction.
Good for complex layouts and tables.
"""

import pdfplumber
from typing import Dict, Any


def extract_text_with_pdfplumber(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using pdfplumber.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - page_count: Number of pages
        - parser: Parser identifier
    """
    try:
        full_text = ""
        page_count = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + " "
                    page_count += 1
        
        return {
            "text": full_text.strip(),
            "page_count": page_count,
            "parser": "pdfplumber",
            "success": len(full_text.strip()) > 0
        }
        
    except Exception as e:
        return {
            "text": "",
            "page_count": 0,
            "parser": "pdfplumber",
            "success": False,
            "error": str(e)
        }
