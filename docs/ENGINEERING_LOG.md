# Engineering Log

Format (handoff §49): Problem · Cause · Investigation · Solution · Why this solution · Files changed · Tests · Result.

---

## 2026-09-30 — Skill extraction returned wrong and missing skills

**Problem**  
Uploaded resumes showed wrong skills (`R`, `C`, `TypeScript`, candidate names, city names) and missed obvious ones (C#, .NET, Node.js, FastAPI, PostgreSQL). Matched/missing skills and the skill-overlap part of the ATS score were therefore unreliable.

**Investigation**  
Traced every stage (raw PDF → extracted text → cleaned text → candidates → normalized → final) on two PDFs and four labelled synthetic resumes (`docs/SKILL_EXTRACTION_EVALUATION.md`). PDF extraction was *not* the cause — the raw text contained the skills. Baseline on the text the app actually used: **recall 5.4 %, precision 6.0 %**.

**Causes (several, stacked)**

1. The React upload page sent `cleaned_text` to `/analyze_resume`, and the backend extracted job skills from `cleaned_description`. `advanced_clean_text` lowercases and deletes every non-letter, so `C#` → `c`, `.NET` → `net`, `Node.js` → `node js`.
2. `normalize_skill` compared the input with the *alias keys* and returned the key, so `javascript` was returned instead of `JavaScript` (duplicates, un-canonical names).
3. `normalize_skill` then fell back to substring matching; with aliases like `c`, `r`, `ts`, `and`-containing words, `REST API` became `R` and random words became `C`, `TypeScript`, `Pandas`, `Weights & Biases`.
4. Pattern methods (bullets, capitalised words, version numbers) returned names, places, verbs and headings, and nothing filtered them.
5. `\b` word boundaries never match aliases ending in symbols (`c++`, `c#`, `.net`); `js` matched inside `node.js`.
6. Short/English-word aliases (`go`, `r`, `swift`, `spring`, `rest`) matched in ordinary prose and names.
7. Vocabulary gaps: HTML, CSS, .NET, Linux, Excel, Power BI… absent; Jest, Selenium, Flutter, Airflow… present in the categorizer but not in the alias map.

**Solution (smallest changes in the existing modules)**

| Change | File |
|---|---|
| Extract skills from the original text; keep FAISS retrieval and the quality report on cleaned text (as before) | `backend/main.py`, `frontend/src/pages/app/ResumeUploadPage.tsx` |
| Extract job skills from `job_description` instead of `cleaned_description` | `backend/main.py` |
| `normalize_skill`: canonical lookup returns the canonical name; substring fallback removed; `is_known_skill()` added | `preprocessing/skill_normalizer.py` |
| Controlled ambiguous-alias rules: `LIST_ONLY_ALIASES` (C, R, Go, Spring, Swift…) only inside lists; `CASE_SENSITIVE_ALIASES` (REST, Excel, Node…) only in exact case | `preprocessing/skill_normalizer.py`, `preprocessing/regex_skill_extractor.py` |
| Symbol-safe token boundaries; multi-word aliases also match hyphens/line breaks; canonical names are matched too | `preprocessing/regex_skill_extractor.py` |
| Pipeline keeps only vocabulary skills (LLM skills still kept when LLM is enabled); raw candidates still returned in `raw_skills` | `preprocessing/skill_extraction_pipeline.py` |
| Small vocabulary additions (~70 aliases) + categories for them, incl. a `Data Analysis & BI` category | `preprocessing/skill_normalizer.py`, `preprocessing/skill_categorizer.py` |
| `advanced_skill_extractor` now honours `enable_llm` | `preprocessing/skill_extractor.py` |
| Lazy imports: Gemini SDK only when LLM is enabled; EasyOCR only when OCR actually runs | `preprocessing/skill_extraction_pipeline.py`, `pdf_parser/ocr_parser.py` |

**Why this solution**  
Each cause was fixed in the component responsible for it; no new modules, frameworks, models or services. The deterministic, explainable design is kept — no LLM replacement. Precision was protected by the vocabulary filter and ambiguity rules instead of "extract more words".

**What is preserved**  
API routes and response schemas; ATS weights and formula; embedding model, FAISS index and retrieval input (still cleaned text); quality report input (still cleaned text); Streamlit app untouched.

**What it could affect**  
- ATS scores change: skill overlap now uses correct resume and job skills, and the quality report's skill-count penalty sees the real skill count.
- Unknown technologies not in the vocabulary are no longer shown (previously shown mixed with noise). They remain visible in `raw_skills`.
- Streamlit's local fallback still extracts from cleaned text (benefits from the extractor fixes but still loses C#/C++/.NET).

**Tests**  
New pytest suite `tests/` (42 tests): normalizer, extraction (symbols, prose sentences, false-positive traps, duplicates, empty input, no Gemini import), PDF parser failure cases, and a quality gate (recall and precision ≥ 95 % on the labelled set).

**Result**  
On the labelled set: **recall 5.4 % → 100 %, precision 6.0 % → 98.7 %**. One known false positive remains (company name *Oracle …* → Oracle Database).

---

## 2026-09-30 — Phase 1b: foundation hardening

| Problem | Cause | Solution | Files |
|---|---|---|---|
| `pip install -r requirements.txt` fails | Conflicting duplicate pins; `fastapi==0.115.0` needs `starlette<0.39` but `starlette==1.1.0` is pinned; `faiss-cpu` missing | Kept freeze versions, `fastapi==0.142.2` (`starlette>=0.46`), added `faiss-cpu==1.15.1`, `pytest==9.1.1`, `pywinpty` Windows-only marker. Verified with `uv pip compile` for Python 3.12 (Windows + Linux) | `requirements.txt` |
| Every upload ran EasyOCR | Pipeline always tried all parsers, OCR included | OCR only when best text-parser confidence < 50 (`OCR_FALLBACK_THRESHOLD`) | `pdf_parser/extraction_pipeline.py` |
| Resumes kept on disk | Deletion was commented out | Delete in `finally` after parsing; a failed delete is logged, not fatal | `backend/services/resume_service.py` |
| OCR flag ignored from React | Sent as form field, endpoint reads a query param | Send `?enable_ocr=true` | `frontend/src/services/resumeService.ts` |

Tests: `test_ocr_is_skipped_when_text_extraction_is_good`, `test_ocr_runs_as_fallback_when_text_parsers_fail`, `test_upload_parses_pdf_and_deletes_file`.

## 2026-09-30 — Phases 2–4, 7: JD matching, explainable score, partial skills

- **Problem:** the handoff's core flow (paste a JD → score) did not exist; the score had no breakdown; no partial/related skills.
- **Solution:**
  - `/analyze_resume` accepts optional `job_description` / `job_title`. Semantic score uses the same Sentence Transformer (`RetrievalService.score_job_description`, TF-IDF fallback like retrieval). Without a JD the old behaviour (best FAISS job) is unchanged. `job_source` tells which was used.
  - ATS weights moved to named constants (**same values 0.4/0.3/0.3**, see AUDIT D1). `utils/explainability.py` builds `score_breakdown` (score, weight, contribution per component) and plain-language `explanation` reasons — deterministic, no LLM.
  - `matching/skill_gap.py`: controlled related-skill groups → `partial_matches`. `missing_skills` keeps its old meaning (all unmatched job skills) so roadmap/coach consumers are unaffected; the score is unchanged.
  - Scoring logic shared by `/analyze_resume` and `/rank_candidates` through one helper (`_score_resume_against_job`) so both always agree.
- **Response schema:** additive only (`partial_matches`, `score_breakdown`, `explanation`, `job_source`); existing fields unchanged.
- **Tests:** `tests/test_ats_scoring.py`, `tests/test_api.py`.

## 2026-09-30 — Phases 5, 8, 9, 10: API hardening, coach inputs, candidate ranking

- `POST /rank_candidates`: 1–50 resumes vs one JD, sorted by ATS score, each with matched/missing/partial skills and reasons, plus a summary (average/highest/lowest, top candidate, most common gaps/matched skills).
- Empty resume/JD text → HTTP 400 (`InvalidInputError`). Gemini failures → HTTP 502 (`ExternalServiceError`) instead of "success" with an error text; the error marker is a constant shared by `utils/llm_feedback.py` / `utils/career_roadmap.py` and the services, so Streamlit still shows the same text.
- Coach receives `missing_skills` and the original resume text.
- `/health` checks FAISS files, jobs dataset and Gemini key (`degraded` when something is missing).
- FAISS index + metadata cached after the first load (was ~11 MB read per request).

## 2026-09-30 — Phase 6: frontend

- Upload page: optional job title + description.
- Analysis page: job source line, "Why this score?" card (component bars + reasons), partially covered skills.
- Coach page: sends original text + missing skills; shows backend error message.
- New Candidate Ranking page (`/app/ranking`, sidebar link): JD + multiple PDFs → ranked list with expandable reasons and gap summary.
- Axios interceptor shows backend `message` instead of "Request failed with status code …".
- Verified: `npm ci && npm run build` (tsc + vite) and `oxlint` pass (built in a scratch copy so `node_modules` never landed in the OneDrive folder).

## Verification (end-to-end, real FAISS + all-MiniLM-L6-v2)

- `python -m pytest tests -q` → **65 passed**.
- Upload `temp_resume.pdf` → analyze against a pasted .NET JD: 9 matched, 8 missing, 3 partial (Angular ← AngularJS, SQL Server ← SQL), ATS 67.45 with reasons.
- Rank IT-manager vs .NET resumes for that JD → .NET developer first (67.45 vs 45.45).
- No Gemini key → `/resume_feedback` returns 502 with a clear message; `/health` reports `degraded`.

## Suggested commits (once the project is in git)

No AI attribution lines — see `CLAUDE.md`.

```text
docs: add CLAUDE.md, repository audit and engineering log
fix: extract skills from original text and repair skill normalization
test: add skill extraction evaluation set and regression tests
fix: make requirements installable and add faiss-cpu and pytest
perf: run OCR only as fallback and cache the FAISS index
fix: delete uploaded resumes after parsing
feat: score resumes against a provided job description
feat: add explainable ATS score breakdown and partial skill matches
feat: add candidate ranking endpoint with summary analytics
fix: pass missing skills to coach and report Gemini failures as errors
feat: add JD input, score explanation and candidate ranking pages
docs: update README and backend API docs
```
