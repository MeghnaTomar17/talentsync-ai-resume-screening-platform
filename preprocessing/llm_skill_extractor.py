"""
LLM-based Skill Extractor

Uses Google Gemini to extract skills from text using natural language understanding.
Provides intelligent extraction that can understand context and identify skills
that might be missed by pattern matching.
"""

import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import os
import json
from typing import List, Tuple

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def extract_skills_with_llm(text: str, max_skills: int = 50) -> List[Tuple[str, float]]:
    """
    Extract skills from text using Gemini LLM.
    
    This method uses natural language understanding to identify skills
    in context, which can catch skills that pattern matching might miss.
    
    Args:
        text: Input text (resume or job description)
        max_skills: Maximum number of skills to extract
        
    Returns:
        List of (skill, confidence) tuples
    """
    try:
        prompt = f"""
You are an expert technical recruiter and skills analyst. Your task is to extract
technical and professional skills from the given text.

TEXT:
{text[:8000]}

INSTRUCTIONS:
1. Extract all technical skills, tools, technologies, frameworks, and methodologies mentioned.
2. Include programming languages, databases, cloud platforms, DevOps tools, libraries, etc.
3. Also include relevant soft skills if mentioned in a professional context.
4. Normalize skill names to their standard forms (e.g., "JS" → "JavaScript", "ReactJS" → "React").
5. Return ONLY a JSON array of skill names.
6. Do not include explanations or additional text.
7. Limit to the most important and relevant skills (max {max_skills}).

Output format:
["Skill1", "Skill2", "Skill3", ...]
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        
        # Try to extract JSON from the response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            skills = json.loads(response_text)
            
            # Assign high confidence to LLM-extracted skills
            return [(skill, 0.95) for skill in skills if isinstance(skill, str)]
            
        except json.JSONDecodeError:
            # Fallback: try to parse as comma-separated list
            skills = [s.strip().strip('"\'') for s in response_text.split(',')]
            return [(skill, 0.9) for skill in skills if skill]
            
    except Exception as e:
        # Return empty list on error
        print(f"LLM skill extraction error: {e}")
        return []


def extract_skills_with_llm_detailed(text: str) -> dict:
    """
    Extract skills with detailed categorization using Gemini LLM.
    
    This method provides more detailed output including skill categories
    and confidence levels.
    
    Args:
        text: Input text (resume or job description)
        
    Returns:
        Dictionary with structured skill information
    """
    try:
        prompt = f"""
You are an expert technical recruiter and skills analyst. Your task is to extract
and categorize skills from the given text.

TEXT:
{text[:8000]}

INSTRUCTIONS:
1. Extract all technical skills, tools, technologies, frameworks, and methodologies.
2. Categorize each skill into one of these categories:
   - Programming Languages
   - Frontend Frameworks
   - Backend Frameworks
   - Databases
   - Cloud Platforms
   - AI/ML
   - DevOps
   - Tools & Libraries
   - Soft Skills
   - Data Engineering
   - Mobile Development
   - Testing
   - Security
3. Normalize skill names to standard forms.
4. Return ONLY a JSON object with categories as keys and skill arrays as values.
5. Do not include explanations or additional text.

Output format:
{{
    "Programming Languages": ["Python", "JavaScript"],
    "Frontend Frameworks": ["React", "Vue.js"],
    ...
}}
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            categorized_skills = json.loads(response_text)
            
            # Flatten to (skill, confidence) tuples
            all_skills = []
            for category, skills in categorized_skills.items():
                if isinstance(skills, list):
                    for skill in skills:
                        if isinstance(skill, str):
                            all_skills.append((skill, 0.95))
            
            return {
                "skills": all_skills,
                "categorized": categorized_skills,
                "success": True
            }
            
        except json.JSONDecodeError:
            return {
                "skills": [],
                "categorized": {},
                "success": False,
                "error": "Failed to parse LLM response"
            }
            
    except Exception as e:
        return {
            "skills": [],
            "categorized": {},
            "success": False,
            "error": str(e)
        }
