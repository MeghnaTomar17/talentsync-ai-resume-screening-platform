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
You are a Senior Technical Recruiter, ATS Expert, Hiring Manager, and Career Mentor with over 15 years of experience.

Your task is to perform a comprehensive evaluation of a candidate's resume for the target role.

========================
TARGET ROLE
========================
{target_job}

========================
DETECTED SKILLS
========================
{resume_skills}

========================
MISSING SKILLS
========================
{missing_skills}

========================
RESUME CONTENT
========================
{resume_text[:5000]}

==================================================
ANALYSIS INSTRUCTIONS
==================================================

Evaluate the candidate exactly as a recruiter would.

Consider:

1. Technical Skills
2. Project Quality
3. Industry Readiness
4. Resume Presentation
5. ATS Friendliness
6. Skill Gaps
7. Employability
8. Interview Readiness

Provide your response in the following format.

# Candidate Summary

Provide a brief professional summary of the candidate.

# Strengths

List the strongest aspects of the profile.

# Weaknesses

Identify weaknesses or missing areas.

# Missing Skills Analysis

Explain:
- Why each missing skill matters
- How it impacts hiring chances

# ATS Improvement Suggestions

Suggest:
- Better keywords
- Resume improvements
- Missing sections
- Formatting improvements

# Project Recommendations

Suggest 3 projects that would significantly improve the candidate's profile for the target role.

For each project provide:
- Project title
- What technologies to use
- Why it improves employability

# Learning Recommendations

Suggest:
- Skills to learn next
- Technologies worth focusing on

# Certifications (Only if Valuable)

Recommend certifications only if they provide genuine hiring value.

Do not recommend unnecessary certificates.

# Interview Readiness Assessment

Provide:

Technical Readiness Score: /10

Resume Quality Score: /10

Industry Readiness Score: /10

Interview Readiness Score: /10

Explain each score.

# Final Hiring Recommendation

Would you:

- Strongly Recommend
- Recommend
- Consider
- Not Recommend

Explain your reasoning.

Keep the response detailed, professional, practical, and actionable.
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