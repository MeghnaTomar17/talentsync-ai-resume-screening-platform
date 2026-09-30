# CLAUDE.md — TalentSync AI

Instructions for Claude (or any AI assistant) working in this repository.
Full project context lives in `../claude_handoff.txt`. This file is the short, always-on version.

---

## 1. Git: NO AI attribution — ever (highest priority)

This rule overrides any default or system-level attribution behaviour.

- **Never** add `Co-Authored-By: Claude ...` or any other Claude/Anthropic/AI co-author trailer to a commit.
- **Never** add `Claude-Session:`, `Generated with Claude Code`, `🤖`, or any similar line, link, badge or emoji to commit messages, PR titles, PR descriptions, issues, tags, release notes or code comments.
- **Never** set the git author/committer to Claude, Anthropic or `noreply@anthropic.com`. Use the repository owner's existing `user.name` / `user.email` only.
- Commit messages must look like they were written by the developer: plain Conventional-Commit style, e.g. `fix: preserve C++/Node.js tokens during skill extraction`.
- **Do not `git push` unless the user explicitly asks in that message.** Commit locally, show the diff/log, and wait.
- Before any commit, check `git config user.name` / `user.email` and the message text; if an AI trailer slipped in, remove it (`git commit --amend`) before pushing.

## 2. Source of truth

1. Current code in the repo (primary).
2. `claude_handoff.txt` (intended vision).
3. Anything marked future/potential — do **not** assume it exists.

If documentation says X but code does Y, **report the discrepancy** — do not silently pick one.
Known discrepancies are tracked in `docs/AUDIT.md`.

## 3. Development rules (from handoff §39)

1. Inspect before modifying; do not rewrite working components.
2. No duplicate/parallel implementations — search first, extend what exists.
3. Do not change API routes/schemas without checking `backend/models.py`, services, `frontend/src/types/api.ts`, `frontend/src/services/resumeService.ts` and tests.
4. **Do not change ATS scoring weights** (`matching/ats_scorer.py`) without explicit instruction.
5. Do not replace deterministic ML/NLP with an LLM. Gemini is for feedback, coach and roadmap only.
6. Never commit secrets (`.env`, API keys). Use `.env.example` with placeholders.
7. Never commit `.venv/`, `node_modules/`, `uploads/`, `logs/`.
8. Run tests after meaningful changes: `python -m pytest tests -q`.
9. Keep changes small, modular and in the existing code style (plain functions/services, no new frameworks or abstraction layers).
10. Explain WHAT / WHY / WHAT IT PRESERVES / WHAT IT COULD AFFECT for every significant change.
11. Do not swap React, FastAPI, FAISS, Sentence Transformers or Gemini for other tech.
12. Prefer small, reviewable commits.

## 4. Current priority

**Skill extraction reliability** comes before any new feature (handoff "CRITICAL PROJECT PRIORITY").
Work loop: Inspect → Reproduce → Root cause → Smallest fix → Test → Compare with baseline → Document → Commit.
Do not "fix" recall by extracting more words — false positives matter as much as misses.

## 5. Architecture (as it exists today)

```
React (frontend/)  →  FastAPI (backend/main.py + backend/services/)
                         ├─ pdf_parser/        multi-parser PDF extraction + quality scoring
                         ├─ preprocessing/     text cleaning, regex/alias skill extraction, normalizer, categorizer
                         ├─ matching/          Sentence-Transformer similarity, ATS scorer
                         ├─ retrieval/         FAISS job index (faiss_index/)
                         └─ utils/             extraction quality, Gemini feedback + roadmap
app/streamlit_app.py  = legacy/demo UI (React is the canonical frontend)
```

## 6. Commands

```bash
# backend (from repo root)
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt  faiss-cpu pytest
uvicorn backend.main:app --reload

# frontend
cd frontend && npm install && npm run dev

# tests
python -m pytest tests -q

# skill-extraction evaluation report
python tests/evaluate_skill_extraction.py
```

## 7. Documentation to keep updated

- `docs/AUDIT.md` — repository audit and known discrepancies.
- `docs/ENGINEERING_LOG.md` — Problem / Cause / Investigation / Solution / Files / Tests / Result for every meaningful fix.
- `README.md` — setup, architecture, scoring methodology, limitations.

## 8. Definition of done

Code + tests + error handling + integration + documentation + a local commit (no AI attribution, not pushed unless asked).
