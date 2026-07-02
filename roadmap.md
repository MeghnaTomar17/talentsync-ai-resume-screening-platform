Standardize all FastAPI responses.

Requirements:
- Create a common response schema for every endpoint.
- Every response should include:
  - success
  - message
  - data
  - timestamp
  - processing_time
- Update all endpoints to use the common response model.
- Preserve existing functionality.

Create centralized configuration management for the FastAPI backend.

Requirements:
- Create backend/core/config.py using Pydantic BaseSettings.
- Move API keys, model names, FAISS paths, upload paths, and configurable settings into config.py.
- Replace hardcoded values across the backend with configuration values.
- Keep behavior unchanged.

Add production-ready logging to the FastAPI backend.

Requirements:
- Create backend/core/logger.py.
- Log API requests, parser selection, extraction time, FAISS retrieval, ATS scoring, Gemini calls, and errors.
- Use Python logging with rotating log files.
- Keep logs structured and readable.

Implement centralized exception handling for FastAPI.

Requirements:
- Create custom exception handlers.
- Return consistent JSON error responses.
- Handle validation errors, file upload errors, missing resources, and internal server errors.
- Remove scattered try/except blocks where appropriate.

Test and validate every FastAPI endpoint.

Requirements:
- Verify all routes.
- Ensure request and response models are correct.
- Validate file uploads.
- Fix any remaining endpoint issues.
- Ensure Swagger documentation works correctly.