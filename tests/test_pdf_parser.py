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


def test_ocr_is_skipped_when_text_extraction_is_good(monkeypatch):
    from pdf_parser import extraction_pipeline

    calls = []

    def fake_ocr(path):
        calls.append(path)
        return {"text": "", "parser": "easyocr", "success": False, "ocr_used": True}

    pipeline = extraction_pipeline.ExtractionPipeline(enable_ocr=True)
    pipeline.ocr_parser = ("EasyOCR", fake_ocr)
    result = pipeline.extract(str(ROOT / "sample_resume" / "sample.pdf"))

    assert result["success"] is True
    assert result["ocr_used"] is False
    assert calls == []


def test_ocr_runs_as_fallback_when_text_parsers_fail(monkeypatch, tmp_path):
    from pdf_parser import extraction_pipeline

    ocr_text = "Experience Education Skills Python SQL projects\n" * 60

    def fake_ocr(path):
        return {"text": ocr_text, "parser": "easyocr", "success": True, "ocr_used": True}

    fake = tmp_path / "scanned.pdf"
    fake.write_bytes(b"not a real pdf")
    pipeline = extraction_pipeline.ExtractionPipeline(enable_ocr=True)
    pipeline.ocr_parser = ("EasyOCR", fake_ocr)
    result = pipeline.extract(str(fake))

    assert result["success"] is True
    assert result["ocr_used"] is True
    assert result["parser_used"] == "easyocr"
