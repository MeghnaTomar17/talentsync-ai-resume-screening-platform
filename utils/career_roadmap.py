import google.generativeai as genai

from dotenv import load_dotenv
from pathlib import Path
import os

from backend.core.config import settings

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

genai.configure(
    api_key=settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
)


def generate_career_roadmap(

    target_job,

    resume_skills,

    missing_skills

):

    try:

        prompt = f"""
You are an experienced career mentor.

Target Role:
{target_job}

Current Skills:
{resume_skills}

Missing Skills:
{missing_skills}

Create a realistic and practical learning roadmap.

Requirements:

1. Create a 30-Day Roadmap.

2. Divide into:
   Week 1
   Week 2
   Week 3
   Week 4

3. Include:
   - Skills to learn
   - Concepts to study
   - Mini projects
   - Resources to explore

4. Prioritize skills based on industry demand.

5. Focus on employability.

6. Suggest one portfolio project at the end.

Output should be structured and actionable.
"""

        model = genai.GenerativeModel(
            settings.gemini_model
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return f"Roadmap generation failed: {str(e)}"
