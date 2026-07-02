# TalentSync Backend API

Production-ready FastAPI backend for the TalentSync AI resume screening platform.

## Overview

This backend provides RESTful API endpoints for resume analysis, job matching, ATS scoring, and career intelligence. It extracts all business logic from the Streamlit frontend into reusable service modules.

## Architecture

### Directory Structure

```
backend/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application and endpoints
├── models.py                # Pydantic request/response models
└── services/                # Business logic modules
    ├── __init__.py
    ├── resume_service.py    # Resume parsing and text extraction
    ├── skill_service.py     # Skill extraction and categorization
    ├── retrieval_service.py # FAISS-based job retrieval
    ├── ats_service.py       # ATS scoring and quality analysis
    ├── feedback_service.py  # Gemini-powered resume feedback
    └── roadmap_service.py   # Career roadmap generation
```

### Service Modules

Each service encapsulates specific business logic:

- **ResumeService**: Multi-layer PDF extraction pipeline
- **SkillService**: Regex-based and LLM-enhanced skill extraction
- **RetrievalService**: FAISS semantic job matching
- **ATSService**: ATS scoring and quality metrics
- **FeedbackService**: Gemini resume coaching
- **RoadmapService**: Career roadmap generation

## API Endpoints

### Health Check

```
GET /health
```

Returns API health status and service availability.

### Upload Resume

```
POST /upload_resume
Content-Type: multipart/form-data

Parameters:
- file: PDF file (required)
- enable_ocr: boolean (optional, default: true)

Response:
{
    "success": true,
    "message": "Resume parsed successfully",
    "extraction_metadata": {
        "parser_used": "pymupdf",
        "confidence": 95,
        "ocr_used": false,
        "fallback_count": 0
    }
}
```

### Analyze Resume

```
POST /analyze_resume
Content-Type: application/json

Request:
{
    "resume_text": "Extracted resume text...",
    "enable_llm": false
}

Response:
{
    "success": true,
    "extracted_skills": ["Python", "JavaScript", "React"],
    "categorized_skills": {
        "Programming Languages": ["Python", "JavaScript"],
        "Frontend Frameworks": ["React"]
    },
    "skill_confidence": 87.5,
    "skill_count": 3,
    "extraction_method": "regex",
    "top_jobs": [...],
    "best_match": {...},
    "matched_skills": [...],
    "missing_skills": [...],
    "semantic_score": 85.0,
    "skill_overlap_score": 70.0,
    "ats_score": 77.5,
    "quality_report": {...}
}
```

### Resume Feedback

```
POST /resume_feedback
Content-Type: application/json

Request:
{
    "resume_text": "Resume text...",
    "resume_skills": ["Python", "JavaScript"],
    "job_title": "Software Engineer",
    "job_description": "Job description..."
}

Response:
{
    "success": true,
    "feedback": "Detailed feedback...",
    "suggestions": ["Suggestion 1", "Suggestion 2"]
}
```

### Career Roadmap

```
POST /career_roadmap
Content-Type: application/json

Request:
{
    "resume_skills": ["Python", "JavaScript"],
    "missing_skills": ["AWS", "Docker"],
    "target_role": "Senior Software Engineer"
}

Response:
{
    "success": true,
    "target_role": "Senior Software Engineer",
    "roadmap": [...],
    "recommendations": [...]
}
```

## Installation

1. Install dependencies:
```bash
pip install fastapi uvicorn[standard] python-multipart
```

2. Ensure FAISS index is built:
```bash
python build_index.py
```

3. Set environment variables:
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key
```

## Running the Backend

### Development Mode

```bash
cd backend
python main.py
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### Service Configuration

Services can be configured with custom paths:

```python
resume_service = ResumeService(upload_dir="uploads")
retrieval_service = RetrievalService(index_dir="retrieval/index")
```

### CORS Configuration

CORS is currently configured to allow all origins. For production, update the middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

All endpoints return standardized error responses:

```json
{
    "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 422: Validation error (invalid request)
- 500: Internal server error

## Integration with Frontend

### Streamlit Integration

The existing Streamlit app can be updated to use the API:

```python
import requests

API_BASE_URL = "http://localhost:8000"

# Upload resume
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{API_BASE_URL}/upload_resume",
        files={"file": f},
        data={"enable_ocr": True}
    )

# Analyze resume
response = requests.post(
    f"{API_BASE_URL}/analyze_resume",
    json={
        "resume_text": resume_text,
        "enable_llm": False
    }
)
analysis = response.json()
```

### Future React Frontend

The API is designed to work seamlessly with a React frontend:

```javascript
const API_BASE_URL = 'http://localhost:8000';

// Analyze resume
const analyzeResume = async (resumeText) => {
  const response = await fetch(`${API_BASE_URL}/analyze_resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, enable_llm: false })
  });
  return response.json();
};
```

## Performance Considerations

### FAISS Index
- Ensure the FAISS index is built before running the backend
- Index is loaded once at startup for efficiency
- Index size depends on job dataset

### LLM Calls
- LLM extraction is disabled by default for speed
- Enable with `enable_llm=True` for enhanced accuracy
- LLM calls add ~2-5 seconds per request

### File Uploads
- Uploaded files are stored in the `uploads/` directory
- Consider implementing cleanup for old uploads
- Maximum file size can be configured in FastAPI

## Security Considerations

### Production Checklist
- [ ] Configure CORS for specific origins
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Secure file upload handling
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Add logging and monitoring
- [ ] Implement input sanitization

## Dependencies

- FastAPI 0.115.0
- Uvicorn 0.32.0
- Pydantic 2.x
- All existing project dependencies (FAISS, Gemini, etc.)

## Testing

### Manual Testing

Use the Swagger UI at http://localhost:8000/docs to test endpoints interactively.

### Automated Testing

Test endpoints using curl:

```bash
# Health check
curl http://localhost:8000/health

# Analyze resume
curl -X POST http://localhost:8000/analyze_resume \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Sample text...", "enable_llm": false}'
```

## Troubleshooting

### FAISS Index Not Found
Ensure you've built the index:
```bash
python build_index.py
```

### Gemini API Errors
Check your `.env` file contains a valid `GEMINI_API_KEY`.

### Import Errors
Ensure you're running from the project root directory:
```bash
python backend/main.py
```

## Future Enhancements

- [ ] Add authentication (JWT/OAuth)
- [ ] Implement rate limiting
- [ ] Add request caching
- [ ] Support for multiple resume formats (DOCX, TXT)
- [ ] Resume storage and retrieval
- [ ] Batch job processing
- [ ] WebSocket support for real-time updates
- [ ] Admin dashboard
- [ ] Analytics and usage tracking
