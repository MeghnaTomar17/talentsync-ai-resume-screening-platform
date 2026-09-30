# TalentSync AI — Repository Audit

**Date:** 30 Sep 2026  
**Scope:** audit required by `claude_handoff.txt` §40 / §52, done before feature work.  
**Source of truth:** the code in this folder. Where the handoff and the code disagree, both are listed under *Discrepancies*.

---

## 1. Repository structure

```
talentsync-ai-resume-screening-platform-main/
├── app/streamlit_app.py          legacy Streamlit dashboard (calls API, falls back to local modules)
├── backend/                      FastAPI app
│   ├── main.py                   routes
│   ├── models.py                 Pydantic request/response models
│   ├── core/                     config, logger, exceptions, response envelope
│   └── services/                 resume, skill, retrieval, ats, feedback, roadmap
├── frontend/                     React 19 + Vite + TypeScript + TanStack Query
├── pdf_parser/                   PyMuPDF → pdfplumber → pypdf → EasyOCR + quality scoring
├── preprocessing/                text cleaner, regex/alias skill extractor, normalizer, categorizer, optional Gemini extractor
├── matching/                     Sentence-Transformer similarity, ATS scorer
├── retrieval/                    FAISS IndexFlatIP job retriever
├── utils/                        extraction quality, explainability, Gemini feedback, Gemini roadmap
├── faiss_index/                  prebuilt index (2,277 jobs) + metadata pickle
├── datasets/                     jobs.csv, resumes.csv (56 MB), Resume/ (2,484 PDFs in 24 categories)
├── notebooks/                    data understanding, PDF parser, preprocessing experiments
├── sample_resume/sample.pdf      dataset IT-manager resume
├── temp_resume.pdf               real candidate resume (git-ignored, contains PII)
├── tests/                        NEW – pytest suite + skill-extraction evaluation
└── docs/                         NEW – this audit, evaluation, engineering log
```

## 2. Existing architecture

```
React ──► FastAPI /upload_resume ──► pdf_parser (best of 4 parsers) ──► raw text + cleaned text
      └─► FastAPI /analyze_resume
              ├─ skills   : preprocessing (regex + alias vocabulary → normalizer → categorizer)
              ├─ retrieval: FAISS top-k jobs from datasets/jobs.csv (TF-IDF fallback if FAISS/model fails)
              ├─ job skills: same extractor on the best-matching dataset job
              ├─ quality  : utils/extraction_quality.py
              └─ ATS score: matching/ats_scorer.py
      └─► /resume_feedback (Gemini)   └─► /career_roadmap (Gemini)
```

## 3. Backend status

| Item | Status |
|---|---|
| Entry point | `backend/main.py` (`uvicorn backend.main:app`) |
| Routes | `GET /`, `GET /health`, `POST /upload_resume`, `POST /analyze_resume`, `POST /resume_feedback`, `POST /career_roadmap` (+ `POST /rank_candidates` added after the audit) |
| Response envelope | `APIResponse{success, message, data, timestamp, processing_time}` |
| Errors | central handlers for `TalentSyncError`, HTTP, validation, unhandled |
| Logging | rotating file `logs/talentsync-api.log` + console |
| Config | `backend/core/config.py` (pydantic-settings, `.env`) |
| CORS | `allow_origins=["*"]` with `allow_credentials=True` (see bugs) |

## 4. Frontend status

React 19 + Vite + TS, React Router, TanStack Query, Axios client (`VITE_API_BASE_URL`), Recharts.
Pages: Landing, Login/Register/Forgot (UI only, no auth logic), Dashboard, Upload, Analysis, Coach, Roadmap.
State is kept in `sessionStorage` (`store/resumeStore.ts`). React is the canonical UI; Streamlit is legacy/demo.

## 5. ML status

| Component | Implementation |
|---|---|
| PDF extraction | runs PyMuPDF, pdfplumber, pypdf **and** EasyOCR (when enabled), picks highest heuristic score |
| Cleaning | lowercase, strip HTML/URLs, **remove every non-letter**, NLTK stopwords + WordNet lemmatizer (with fallbacks) |
| Skill extraction | regex + controlled alias vocabulary (`SKILL_ALIASES`), optional Gemini (off in API) |
| Embeddings | `all-MiniLM-L6-v2` (Sentence Transformers) |
| Vector search | FAISS `IndexFlatIP` on L2-normalised vectors (= cosine), 2,277 jobs, built by `build_index.py` from **cleaned** job descriptions |
| Fallback | TF-IDF cosine over `jobs.csv` if FAISS/model loading fails |

## 6. ATS scoring status

`matching/ats_scorer.calculate_final_ats_score`:

```
ATS = 0.4 × semantic_score + 0.3 × skill_overlap_score + 0.3 × quality_score
```

- `semantic_score` = FAISS cosine × 100 for the best dataset job
- `skill_overlap_score` = |resume ∩ job skills| / |job skills| × 100
- `quality_score` = `quality_report["ats_score"]` from `utils/extraction_quality.py` (in the API); `calculate_resume_quality` is only used by a Streamlit fallback path.

**Not changed.** See discrepancy D1.

## 7. Skill-gap status

Matched = set intersection, Missing = job − resume (exact canonical strings). At audit time partial/related skills were not implemented (now added, see D3) and the extracted skills were unreliable (see `SKILL_EXTRACTION_EVALUATION.md`), so matched/missing lists were largely noise.

## 8. LLM status

- `utils/llm_feedback.py` (coach), `utils/career_roadmap.py` (roadmap), `preprocessing/llm_skill_extractor.py` (optional extraction). Model from settings: `gemini-2.5-flash`.
- Uses the `google-generativeai` SDK, whose support has ended (Google recommends `google-genai`). Not changed.
- At audit time Gemini failures were returned as normal text with `success: true`, and `FeedbackService` always passed `missing_skills=[]` to the coach prompt (both fixed, B15).

## 9. Testing status

Before: **no tests**. Now: `tests/` with 65 pytest tests — skill normalizer, skill extraction, labelled-set quality gate, PDF parser + OCR fallback, ATS formula, skill gaps, explanation, and every API endpoint (plus one integration test with the real FAISS index). All pass (`python -m pytest tests -q`). Frontend: `npm run build` (tsc + vite) and `oxlint` pass; no automated UI tests.

## 10. Git status

**This folder is not a git repository** (it is a GitHub ZIP download, `-main` suffix). Branch, remote, uncommitted changes and commit history could not be inspected, so the historical commits listed in the handoff (Gemini feedback, coach, roadmap, extraction quality, Streamlit, FAISS, FastAPI, React) were verified only against the current code — all eight features exist in code.
**Action for the developer:** clone the real repository and copy these changes into it (or `git init` + add remote) before committing.

## 11. Environment / setup status

- Root `.env.example` was missing → **added** (placeholders only). `frontend/.env.example` exists.
- `.gitignore` correctly ignores `.env`, `.venv/`, `node_modules/`, `uploads/`, `logs/`, `temp_resume.pdf`.
- `requirements.txt` was not installable (duplicate conflicting pins for `requests`, `python-multipart`, `uvicorn`; `fastapi==0.115.0` incompatible with the pinned `starlette==1.1.0`; `faiss-cpu` and `pytest` missing). **Fixed**: kept the `pip freeze` versions, `fastapi==0.142.2`, added `faiss-cpu`, `pytest`, Windows-only marker on `pywinpty`. Resolution verified with `uv pip compile` (Python 3.12, Windows and Linux). The pins require **Python ≥ 3.11**.

## 12. Bugs / problems found

| # | Area | Problem | Status |
|---|---|---|---|
| B1 | Skills | Frontend sent `cleaned_text` to `/analyze_resume`; cleaning removes all symbols and case, so C++, C#, .NET, Node.js, ASP.NET, CI/CD were destroyed before extraction | **Fixed** |
| B2 | Skills | Job skills were extracted from `cleaned_description` (same loss) | **Fixed** |
| B3 | Skills | `normalize_skill` returned the lowercase alias key instead of the canonical name → `javascript` and `JavaScript` both reported, `angularjs` never canonicalised | **Fixed** |
| B4 | Skills | Substring fallback in `normalize_skill` mapped anything containing a short alias to that skill (`REST API`→`R`, many words → `C`, `TypeScript`, `Pandas`, `Weights & Biases`) | **Fixed** (removed) |
| B5 | Skills | Regex/capitalised-word patterns returned names, places, verbs and headings as skills (`Pune`, `Developed`, `SKILLS`) | **Fixed** (vocabulary filter; raw candidates still in `raw_skills`) |
| B6 | Skills | `\b` boundaries never match aliases ending in symbols (`c++`, `c#`, `.net`) and `js` matched inside `node.js` | **Fixed** |
| B7 | Skills | Ambiguous aliases matched in prose: `go the extra mile`→Go, `Priya R`→R, `Swift Logistics`→Swift, `Spring Valley`→Spring Boot, `rest days`→REST | **Fixed** (list-only / case-sensitive rules) |
| B8 | Skills | Categorizer knew Jest, Selenium, Flutter, Airflow, OAuth… but the alias map did not, so they were never extracted; HTML/CSS/Linux/Excel etc. missing entirely | **Fixed** (small controlled additions) |
| B9 | Skills | `advanced_skill_extractor(enable_llm=False)` ignored its argument and called Gemini | **Fixed** |
| B10 | Deps | Deterministic pipeline imported the Gemini SDK at import time; `pdf_parser` imported EasyOCR/torch at import time even with OCR disabled | **Fixed** (lazy imports) |
| B11 | PDF | With `enable_ocr=True` (default) EasyOCR runs on **every** upload even when text parsers succeed (slow) | **Fixed** — OCR only below confidence 50 |
| B12 | API | `enable_ocr` is a query parameter; the frontend sent it as a form field (ignored) | **Fixed** in React (Streamlit legacy still sends a form field; default is the same) |
| B13 | Privacy | Uploaded PDFs were saved to `uploads/` and never deleted (handoff §29) | **Fixed** — deleted right after parsing |
| B14 | API | CORS wildcard with credentials | Not a bug in practice: Starlette echoes the request origin when credentials are allowed. Restrict `CORS_ORIGINS` for deployment |
| B15 | LLM | Coach never received missing skills; Gemini errors reported as success | **Fixed** — `missing_skills` passed; failures return HTTP 502 |
| B16 | Frontend | Coach page sent cleaned text to Gemini (poor context) | **Fixed** — original text sent |
| B17 | Health | `/health` returned "ready" for all services without checking | **Fixed** — checks FAISS files, dataset and Gemini key |
| B18 | PDF | Two-column resumes are read in interleaved order (e.g. EDUCATION / PROFESSIONAL EXPERIENCE headings adjacent). Does not affect bag-of-skills extraction; matters if section detection is added | Open |
| B19 | Skills | Company names that equal a technology (`Oracle Towers Realty` → Oracle Database) still produce false positives | Known limitation |
| B20 | Deps | `requirements.txt` could not be installed (conflicting pins, missing `faiss-cpu`) | **Fixed** — verified with `uv pip compile` for Python 3.12 on Windows and Linux |
| B21 | Perf | FAISS index + 8 MB metadata pickle re-read from disk on every `/analyze_resume` | **Fixed** — cached after first load |
| B22 | API | Empty resume text was analysed; axios showed generic error messages | **Fixed** — HTTP 400 + backend message shown in UI |

## 13. Discrepancies (handoff vs code) and how they were resolved

| # | Handoff says | Code does | Resolution |
|---|---|---|---|
| D1 | ATS 4:3:3 = 40 % skill, 30 % semantic, 30 % quality | 40 % **semantic**, 30 % **skill**, 30 % quality | **Kept the code's weights** (handoff rule: implementation is the source of truth; never change weights without explicit instruction). Weights are now named constants and shown in the score breakdown. Change `SEMANTIC_WEIGHT` / `SKILL_OVERLAP_WEIGHT` in `matching/ats_scorer.py` if the team decides otherwise. |
| D2 | User pastes a job description | No JD input | **Added** optional `job_description` to `/analyze_resume` and a JD box on the upload page; dataset matching remains the default |
| D3 | Partial / related skill category | Not implemented | **Added** `matching/skill_gap.py` (`partial_matches`, explanation only, score unchanged) |
| D4 | `utils/explainability.py` explains scores | Unused by API | **Extended** with `build_score_breakdown` / `generate_score_reasons`, used by the API |
| D5 | README describes Streamlit as UI, FAISS as planned | React is the UI; FAISS implemented | **README updated** |
| D6 | Section-aware extraction | No section detection | Open — skills are searched in the whole text, which already covers Experience/Projects sentences |

## 14. What is complete

PDF multi-parser extraction + quality score · text cleaning · deterministic skill extraction (now validated) · normalization · categorisation · Sentence-Transformer embeddings · FAISS retrieval with TF-IDF fallback · ATS score · matched/missing skills · extraction quality report · Gemini coach · Gemini roadmap · FastAPI with envelopes/logging/errors · React dashboard, upload, analysis, coach, roadmap pages · test suite for extraction.

## 15. Roadmap status (handoff §41)

| Phase | Status |
|---|---|
| 1 Foundation (PDF → text → skills → normalization) | Done, validated (`SKILL_EXTRACTION_EVALUATION.md`) |
| 2 Matching (resume ↔ JD) | Done — provided JD or best dataset job |
| 3 ATS scoring | Done — formula tested, weights as named constants (D1 kept) |
| 4 Skill gaps (matched / partial / missing) | Done |
| 5 API | Done — `/rank_candidates` added, validation, error codes, health checks, tests |
| 6 Frontend | Done — JD input, score breakdown, partial skills, ranking page |
| 7 Explainability | Done — breakdown + deterministic reasons |
| 8 AI Coach | Existing; now receives missing skills and original text; failures surfaced |
| 9 Candidate ranking | Done (backend + page) |
| 10 Recruiter analytics | Basic summary in ranking (average, top, common gaps); full dashboard not built |

**Remaining**

1. Put the project under git (clone the real repo, copy these changes) and commit in the order listed in `ENGINEERING_LOG.md`.
2. Confirm D1 (weights) with the team.
3. Migrate `google-generativeai` → `google-genai` (old SDK no longer supported) — needs a Gemini key to test.
4. Section detection (D6), multi-column PDF ordering (B18), authentication (UI only today), full recruiter dashboard.
