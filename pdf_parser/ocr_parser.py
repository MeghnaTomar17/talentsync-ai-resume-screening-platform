"""
EasyOCR Parser

OCR-based fallback parser for image-based or scanned PDFs.
Uses EasyOCR to extract text from images when traditional parsers fail.
"""

import easyocr
import numpy as np
from typing import Dict, Any
import fitz  # PyMuPDF for page-to-image conversion


# Initialize EasyOCR reader (lazy loading)
_ocr_reader = None


def get_ocr_reader():
    """
    Lazy load EasyOCR reader to avoid startup overhead.
    """
    global _ocr_reader
    if _ocr_reader is None:
        # Initialize with English language
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader


def extract_text_with_ocr(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using OCR (EasyOCR).
    Converts each page to an image and performs OCR.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - page_count: Number of pages
        - parser: Parser identifier
        - ocr_used: Boolean indicating OCR was used
    """
    try:
        reader = get_ocr_reader()
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            # Convert page to image
            pix = page.get_pixmap()
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                (pix.height, pix.width, pix.n)
            )
            
            # Perform OCR
            result = reader.readtext(img)
            
            # Extract text from OCR results
            page_text = " ".join([detection[1] for detection in result])
            if page_text.strip():
                text_parts.append(page_text)
        
        doc.close()
        
        full_text = " ".join(text_parts)
        
        return {
            "text": full_text,
            "page_count": len(text_parts),
            "parser": "easyocr",
            "success": len(full_text.strip()) > 0,
            "ocr_used": True
        }
        
    except Exception as e:
        return {
            "text": "",
            "page_count": 0,
            "parser": "easyocr",
            "success": False,
            "ocr_used": True,
            "error": str(e)
        }
