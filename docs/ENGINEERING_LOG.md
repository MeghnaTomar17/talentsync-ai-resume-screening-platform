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
