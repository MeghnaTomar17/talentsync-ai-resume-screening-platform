import google.generativeai as genai

from dotenv import load_dotenv
from pathlib import Path
import os

# ---------------------------------------------------
# LOAD ENV VARIABLES
# ---------------------------------------------------

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ---------------------------------------------------
# GENERATE RESUME FEEDBACK
# ---------------------------------------------------

def generate_resume_feedback(

    resume_text,

    resume_skills,

    missing_skills,

    target_job

):

    try:

        prompt = f"""
You are an expert recruiter, ATS consultant, and career mentor.

Analyze the following candidate information.

Target Job:
{target_job}

Resume Skills:
{resume_skills}

Missing Skills:
{missing_skills}

Resume Content:
{resume_text[:4000]}

Provide your response in the following format:

## Strengths
- List key strengths

## Weaknesses
- List weaknesses

## Missing Skills Analysis
- Explain which missing skills are important

## ATS Improvement Suggestions
- Suggest improvements for ATS score

## Career Recommendations
- Suggest learning paths, projects, or certifications

Keep the response practical, concise, and personalized.
"""

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return f"""
 Feedback Generation Failed

Error:
{str(e)}

Please verify:
- Internet connection
- Gemini API key
- Gemini API quota
- Model availability
"""