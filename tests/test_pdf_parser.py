"""PDF extraction boundary tests (text parsers only, OCR disabled)."""

from pathlib import Path

from pdf_parser.pdf_reader import extract_text_from_pdf

ROOT = Path(__file__).resolve().parent.parent


def test_sample_pdf_extracts_text():
    result = extract_text_from_pdf(str(ROOT / "sample_resume" / "sample.pdf"), enable_ocr=False)
    assert result["success"] is True
    assert result["parser_used"] in {"pymupdf", "pdfplumber", "pypdf"}
    assert "Active Directory" in result["text"]


def test_missing_pdf_fails_gracefully(tmp_path):
    result = extract_text_from_pdf(str(tmp_path / "missing.pdf"), enable_ocr=False)
    assert result["success"] is False
    assert result["text"] == ""


def test_non_pdf_content_fails_gracefully(tmp_path):
    fake = tmp_path / "fake.pdf"
    fake.write_bytes(b"this is not a pdf")
    result = extract_text_from_pdf(str(fake), enable_ocr=False)
    assert result["success"] is False
