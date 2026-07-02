"""
PDF Reader - Multi-Layer Extraction Pipeline

This module provides the main interface for PDF text extraction
using the multi-layer extraction pipeline with automatic parser selection.
"""

from pdf_parser.extraction_pipeline import extract_text_from_pdf as extract_with_pipeline


def extract_text_from_pdf(pdf_path: str, enable_ocr: bool = True):
    """
    Extract text from PDF using the multi-layer extraction pipeline.
    
    This function automatically selects the best parser based on extraction quality.
    It tries parsers in this order: PyMuPDF -> pdfplumber -> pypdf -> EasyOCR.
    
    Args:
        pdf_path: Path to PDF file
        enable_ocr: Whether to enable OCR fallback for image-based PDFs (default: True)
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - parser_used: Name of the parser that produced best result
        - confidence: Quality confidence score (0-100)
        - ocr_used: Boolean indicating if OCR was used
        - fallback_count: Number of parsers tried before success
        - success: Boolean indicating successful extraction
        - quality_metrics: Detailed quality metrics
        - all_results: All extraction attempts (for debugging)
        
    Note:
        For backward compatibility, if you only need the text string,
        access result['text'] from the returned dictionary.
    """
    return extract_with_pipeline(pdf_path, enable_ocr=enable_ocr)