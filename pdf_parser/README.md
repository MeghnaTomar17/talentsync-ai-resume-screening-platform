# Multi-Layer PDF Extraction Pipeline

## Overview

This module provides a production-ready, multi-layer PDF extraction pipeline that automatically selects the best parser for resume text extraction. It replaces the single-parser approach (pdfplumber) with a robust fallback strategy that handles various PDF types including Canva resumes, multi-column layouts, scanned documents, and image-heavy PDFs.

## Architecture

### Components

- **`pymupdf_parser.py`**: Primary parser using PyMuPDF (fitz)
  - Fast and reliable for most PDF types
  - Good layout preservation
  - First-choice parser

- **`pdfplumber_parser.py`**: Fallback parser using pdfplumber
  - Excellent for complex layouts and tables
  - Robust text extraction
  - Second-choice parser

- **`pypdf_parser.py`**: Secondary fallback using pypdf
  - Good for simple PDFs
  - Lightweight alternative
  - Third-choice parser

- **`ocr_parser.py`**: OCR-based fallback using EasyOCR
  - Handles image-based and scanned PDFs
  - Converts pages to images and performs OCR
  - Last-resort parser

- **`quality_evaluator.py`**: Extraction quality assessment
  - Evaluates text quality using multiple heuristics
  - Scores extraction from 0-100
  - Selects best result across parsers

- **`extraction_pipeline.py`**: Main orchestration logic
  - Manages parser fallback chain
  - Coordinates quality evaluation
  - Returns best extraction with metadata

- **`pdf_reader.py`**: Public interface
  - Backward-compatible API
  - Entry point for the application

## Extraction Strategy

### Parser Order

1. **PyMuPDF** → Fast, reliable, handles most PDFs well
2. **pdfplumber** → Excellent for complex layouts and tables
3. **pypdf** → Good for simple PDFs, lightweight
4. **EasyOCR** → OCR fallback for image-based/scanned PDFs

### Quality Evaluation

The pipeline evaluates each extraction using multiple metrics:

- **Text Length**: Penalizes very short extractions
- **Word Count**: Ensures sufficient content
- **Alphanumeric Ratio**: Detects garbage characters
- **Section Keywords**: Rewards resume-specific sections (experience, skills, etc.)
- **Special Character Density**: Penalizes formatting noise
- **Line Structure**: Ensures proper document structure
- **Parser-Specific Adjustments**: OCR parsers get slight penalty for potential errors

### Automatic Selection

The pipeline:
1. Attempts extraction with each parser in order
2. Evaluates quality of each successful extraction
3. Selects the best result based on confidence score
4. Returns metadata about the extraction process

## Usage

### Basic Usage

```python
from pdf_parser.pdf_reader import extract_text_from_pdf

# Extract text with automatic parser selection
result = extract_text_from_pdf("resume.pdf")

# Access extracted text
text = result["text"]

# Access metadata
parser_used = result["parser_used"]
confidence = result["confidence"]
ocr_used = result["ocr_used"]
fallback_count = result["fallback_count"]
```

### Disable OCR

```python
# Disable OCR fallback for faster processing
result = extract_text_from_pdf("resume.pdf", enable_ocr=False)
```

### Using the Pipeline Directly

```python
from pdf_parser.extraction_pipeline import ExtractionPipeline

pipeline = ExtractionPipeline(enable_ocr=True)
result = pipeline.extract("resume.pdf")
```

### Minimum Quality Threshold

```python
pipeline = ExtractionPipeline()
result = pipeline.extract_with_min_quality("resume.pdf", min_confidence=60)

if result["meets_threshold"]:
    print("Good quality extraction")
else:
    print("Low quality extraction, but best available")
```

## Return Value Structure

```python
{
    "text": "Extracted text content",
    "parser_used": "pymupdf",  # Name of best parser
    "confidence": 95,  # Quality score (0-100)
    "ocr_used": False,  # Whether OCR was used
    "fallback_count": 0,  # Number of parsers tried before success
    "success": True,  # Whether extraction succeeded
    "quality_metrics": {
        "text_length": 2500,
        "word_count": 420,
        "alpha_ratio": 0.85,
        "section_keywords": 4,
        "special_chars": 45,
        "line_count": 35
    },
    "all_results": [
        {"parser": "pymupdf", "success": True, "text_length": 2500},
        {"parser": "pdfplumber", "success": True, "text_length": 2450},
        # ...
    ]
}
```

## Integration with Streamlit

The Streamlit app now displays extraction metadata:

- **Parser Used**: Which parser produced the best result
- **Extraction Confidence**: Quality score (0-100)
- **OCR Used**: Whether OCR was required
- **Fallback Count**: How many parsers were tried

Detailed extraction information is available in an expandable section showing:
- Success status
- Text length
- Quality metrics breakdown
- All parser attempts with status

## Benefits

### Before (Single Parser)
- Only pdfplumber
- Poor performance on Canva/multi-column resumes
- Fails on scanned/image-based PDFs
- No quality assessment
- No fallback mechanism

### After (Multi-Layer Pipeline)
- 4 parser options with automatic selection
- Handles diverse PDF types effectively
- OCR capability for image-based documents
- Quality-based parser selection
- Comprehensive metadata
- Production-ready error handling

## Dependencies

Added to `requirements.txt`:
- `pymupdf==1.25.5` - Fast PDF parsing
- `pypdf==5.3.0` - Robust PDF parsing
- `easyocr==1.7.2` - OCR for image-based PDFs

## Performance Considerations

### Speed
- PyMuPDF: Fastest (milliseconds)
- pdfplumber: Fast (tens of milliseconds)
- pypdf: Fast (tens of milliseconds)
- EasyOCR: Slow (seconds per page)

### Memory
- Traditional parsers: Low memory usage
- EasyOCR: Higher memory usage (image processing)

### Recommendations
- Enable OCR for maximum compatibility
- Disable OCR for faster processing if you know PDFs are text-based
- The pipeline automatically skips OCR if earlier parsers succeed

## Error Handling

The pipeline handles errors gracefully:
- Individual parser failures don't stop the pipeline
- All parsers are attempted before selecting best result
- Returns best available extraction even if some parsers fail
- Provides detailed error information in `all_results`

## Extensibility

To add a new parser:

1. Create a new parser module (e.g., `new_parser.py`)
2. Implement extraction function returning the standard format
3. Add to `ExtractionPipeline.__init__()` parsers list
4. The pipeline will automatically include it in the fallback chain

## Future Enhancements

- Add support for more OCR engines (Tesseract, PaddleOCR)
- Implement parallel parser execution for speed
- Add caching for repeated extractions
- Support for password-protected PDFs
- Image preprocessing for better OCR accuracy
- Parser-specific quality thresholds
