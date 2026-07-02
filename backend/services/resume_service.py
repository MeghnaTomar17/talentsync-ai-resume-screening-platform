"""
Resume Service

Handles resume parsing and text extraction using the multi-layer PDF extraction pipeline.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import uuid
from time import perf_counter

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from pdf_parser.pdf_reader import extract_text_from_pdf
from preprocessing.text_cleaner import advanced_clean_text
from backend.core.config import settings
from backend.core.logger import logger


class ResumeService:
    """Service for resume parsing and text extraction."""
    
    def __init__(self, upload_dir: str = settings.upload_dir):
        """
        Initialize the resume service.
        
        Args:
            upload_dir: Directory to store uploaded resumes
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        saved_filename = f"{file_id}{file_extension}"
        saved_path = self.upload_dir / saved_filename
        
        # Save file
        with open(saved_path, "wb") as f:
            f.write(file_content)

        logger.info("resume_uploaded filename=%s saved_path=%s bytes=%s", filename, saved_path, len(file_content))
        
        return str(saved_path)
    
    def parse_resume(self, file_path: str, enable_ocr: bool = True) -> Dict[str, Any]:
        """
        Parse resume from PDF file.
        
        Args:
            file_path: Path to PDF file
            enable_ocr: Whether to enable OCR fallback
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = perf_counter()
        extraction_result = extract_text_from_pdf(file_path, enable_ocr=enable_ocr)
        extraction_time = round(perf_counter() - start_time, 4)
        logger.info(
            "resume_parsed parser=%s confidence=%s ocr_used=%s extraction_time=%s",
            extraction_result.get("parser_used"),
            extraction_result.get("confidence"),
            extraction_result.get("ocr_used"),
            extraction_time,
        )
        
        # Clean the extracted text
        cleaned_text = advanced_clean_text(extraction_result["text"])
        
        return {
            "text": extraction_result["text"],
            "cleaned_text": cleaned_text,
            "extraction_metadata": {
                "parser_used": extraction_result.get("parser_used"),
                "confidence": extraction_result.get("confidence"),
                "ocr_used": extraction_result.get("ocr_used"),
                "fallback_count": extraction_result.get("fallback_count"),
                "success": extraction_result.get("success"),
                "extraction_time": extraction_time
            }
        }
    
    def process_uploaded_resume(self, file_content: bytes, filename: str, 
                                 enable_ocr: bool = True) -> Dict[str, Any]:
        """
        Process an uploaded resume file.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            enable_ocr: Whether to enable OCR fallback
            
        Returns:
            Dictionary containing parsed resume and metadata
        """
        # Save uploaded file
        file_path = self.save_uploaded_file(file_content, filename)
        
        # Parse resume
        parsed_result = self.parse_resume(file_path, enable_ocr=enable_ocr)
        
        # Clean up uploaded file (optional)
        # os.remove(file_path)
        
        return parsed_result
