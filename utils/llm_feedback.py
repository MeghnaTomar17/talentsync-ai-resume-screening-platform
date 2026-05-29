import google.generativeai as genai

from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

print("ENV PATH:", env_path)
key = os.getenv("GEMINI_API_KEY")

print("ENV PATH:", env_path)
print("KEY FOUND:", key is not None)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)




def generate_resume_feedback(

    resume_text,

    resume_skills,

    missing_skills,

    target_job

):

    prompt = f"""
You are an expert recruiter and ATS consultant.

Candidate Resume:

{resume_text[:4000]}

Detected Skills:

{resume_skills}

Missing Skills:

{missing_skills}

Target Job:

{target_job}

Provide:

1. Resume strengths
2. Resume weaknesses
3. Missing skills analysis
4. ATS improvement suggestions
5. Learning recommendations

Keep response structured and concise.
"""

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    print("Generating Gemini feedback...")

    response = model.generate_content(
        prompt
    )
    print("Gemini feedback generated.")

    return response.text