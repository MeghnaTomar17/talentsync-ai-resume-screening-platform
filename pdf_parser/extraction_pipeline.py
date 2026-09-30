"""
Multi-Layer PDF Extraction Pipeline

Production-ready pipeline that automatically selects the best parser
for PDF text extraction. Uses a fallback strategy with quality evaluation.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pdf_parser.pymupdf_parser import extract_text_with_pymupdf
from pdf_parser.pdfplumber_parser import extract_text_with_pdfplumber
from pdf_parser.pypdf_parser import extract_text_with_pypdf
from pdf_parser.ocr_parser import extract_text_with_ocr
from pdf_parser.quality_evaluator import select_best_extraction


# OCR is slow (EasyOCR + torch), so it only runs when the text-based parsers
# did not produce a usable extraction (same 0-100 scale as "confidence").
OCR_FALLBACK_THRESHOLD = 50


class ExtractionPipeline:
    """
    Multi-layer PDF extraction pipeline with automatic parser selection.
    
    Strategy:
    1. Try PyMuPDF (fast, reliable for most PDFs)
    2. Try pdfplumber (good for complex layouts)
    3. Try pypdf (simple PDFs)
    4. Select best result based on quality evaluation
    5. Only if that result is missing or below OCR_FALLBACK_THRESHOLD,
       run EasyOCR (image-based/scanned PDFs) and select again
    """
    
    def __init__(self, enable_ocr: bool = True):
        """
        Initialize the extraction pipeline.
        
        Args:
            enable_ocr: Whether to use OCR as last fallback (default: True)
        """
        self.enable_ocr = enable_ocr
        self.parsers = [
            ("PyMuPDF", extract_text_with_pymupdf),
            ("pdfplumber", extract_text_with_pdfplumber),
            ("pypdf", extract_text_with_pypdf),
        ]
        self.ocr_parser = ("EasyOCR", extract_text_with_ocr)
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF using the best available parser.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing:
            - text: Extracted text
            - parser_used: Name of the parser that produced best result
            - confidence: Quality confidence score (0-100)
            - ocr_used: Boolean indicating if OCR was used
            - fallback_count: Number of parsers tried before success
            - success: Boolean indicating successful extraction
            - all_results: All extraction attempts (for debugging)
        """
        extractions = []
        
        # Try each text parser in order
        for parser_name, parser_func in self.parsers:
            extractions.append(self._run_parser(parser_name, parser_func, pdf_path))
        
        # Select the best extraction
        best_result = select_best_extraction(extractions)
        
        # OCR fallback only when the text parsers were not good enough
        if self.enable_ocr and best_result["confidence"] < OCR_FALLBACK_THRESHOLD:
            parser_name, parser_func = self.ocr_parser
            extractions.append(self._run_parser(parser_name, parser_func, pdf_path))
            best_result = select_best_extraction(extractions)
        
        # Add metadata about the pipeline run
        best_result["all_results"] = [
            {
                "parser": e["parser"],
                "success": e.get("success", False),
                "text_length": len(e.get("text", ""))
            }
            for e in extractions
        ]
        
        return best_result
    
    def _run_parser(self, parser_name, parser_func, pdf_path: str) -> Dict[str, Any]:
        """Run one parser and turn unexpected exceptions into a failed result."""
        try:
            return parser_func(pdf_path)
        except Exception as e:
            # Log error but continue to next parser
            return {
                "text": "",
                "parser": parser_name,
                "success": False,
                "error": str(e)
            }
    
    def extract_with_min_quality(self, pdf_path: str, min_confidence: int = 50) -> Dict[str, Any]:
        """
        Extract text with a minimum confidence threshold.
        If no parser meets the threshold, returns the best available.
        
        Args:
            pdf_path: Path to PDF file
            min_confidence: Minimum acceptable confidence score (0-100)
            
        Returns:
            Same as extract(), with additional 'meets_threshold' field
        """
        result = self.extract(pdf_path)
        result["meets_threshold"] = result["confidence"] >= min_confidence
        return result


# ---------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------

def extract_text_from_pdf(pdf_path: str, enable_ocr: bool = True) -> Dict[str, Any]:
    """
    Convenience function for PDF extraction with automatic parser selection.
    
    This is the main entry point for the extraction pipeline.
    
    Args:
        pdf_path: Path to PDF file
        enable_ocr: Whether to enable OCR fallback (default: True)
        
    Returns:
        Dictionary containing:
        - text: Extracted text
        - parser_used: Name of the parser used
        - confidence: Quality confidence score (0-100)
        - ocr_used: Boolean indicating if OCR was used
        - fallback_count: Number of fallbacks used
        - success: Boolean indicating success
    """
    pipeline = ExtractionPipeline(enable_ocr=enable_ocr)
    return pipeline.extract(pdf_path)
