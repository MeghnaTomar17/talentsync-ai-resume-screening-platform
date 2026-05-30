import re


def analyze_extraction_quality(

    resume_text,

    extracted_skills

):

    extraction_score = 100

    ats_score = 100

    warnings = []

    recommendations = []

    # ==========================================
    # TEXT LENGTH CHECK
    # ==========================================

    text_length = len(resume_text)

    if text_length < 1000:

        extraction_score -= 30

        ats_score -= 20

        warnings.append(
            "Very little text extracted."
        )

        recommendations.append(
            "Use an ATS-friendly resume with selectable text instead of image-based content."
        )

    elif text_length < 2000:

        extraction_score -= 15

        ats_score -= 10

        warnings.append(
            "Limited text extracted."
        )

        recommendations.append(
            "Add more detailed project, experience, and skills information."
        )

    # ==========================================
    # SKILL COUNT CHECK
    # ==========================================

    skill_count = len(extracted_skills)

    if skill_count < 5:

        extraction_score -= 25

        ats_score -= 15

        warnings.append(
            "Very few skills detected."
        )

        recommendations.append(
            "Create a dedicated Skills section listing technical skills clearly."
        )

    elif skill_count < 10:

        extraction_score -= 10

        ats_score -= 5

        warnings.append(
            "Limited skill extraction."
        )

        recommendations.append(
            "Highlight more relevant technical skills throughout the resume."
        )

    # ==========================================
    # WEIRD CHARACTER CHECK
    # ==========================================

    weird_chars = len(

        re.findall(

            r"[^a-zA-Z0-9\s.,]",

            resume_text
        )
    )

    if weird_chars > 100:

        extraction_score -= 20

        ats_score -= 15

        warnings.append(
            "Unusual formatting detected."
        )

        recommendations.append(
            "Reduce excessive icons, symbols, graphics, and decorative elements."
        )

    # ==========================================
    # SECTION DETECTION
    # ==========================================

    resume_lower = resume_text.lower()

    section_keywords = [

        "education",

        "experience",

        "skills",

        "projects",

        "certifications",

        "internship"
    ]

    found_sections = 0

    for section in section_keywords:

        if section in resume_lower:

            found_sections += 1

    if found_sections < 3:

        ats_score -= 20

        warnings.append(
            "Important resume sections are missing or difficult to detect."
        )

        recommendations.append(
            "Use clear section headings such as Skills, Experience, Projects, and Education."
        )

    # ==========================================
    # RESUME TYPE DETECTION
    # ==========================================

    if ats_score >= 85:

        resume_type = "ATS-Friendly"

    elif ats_score >= 70:

        resume_type = "Modern Resume"

    elif ats_score >= 50:

        resume_type = "Possibly Canva / Multi-Column"

    else:

        resume_type = "Graphic Heavy Resume"

    # ==========================================
    # QUALITY LEVEL
    # ==========================================

    if extraction_score >= 85:

        quality = "Excellent"

    elif extraction_score >= 70:

        quality = "Good"

    elif extraction_score >= 50:

        quality = "Moderate"

    else:

        quality = "Poor"

    # ==========================================
    # SAFETY LIMITS
    # ==========================================

    extraction_score = max(
        0,
        min(
            extraction_score,
            100
        )
    )

    ats_score = max(
        0,
        min(
            ats_score,
            100
        )
    )

    # ==========================================
    # RETURN REPORT
    # ==========================================

    return {

        "quality_score": extraction_score,

        "quality_level": quality,

        "ats_score": ats_score,

        "resume_type": resume_type,

        "warnings": warnings,

        "recommendations": recommendations,

        "text_length": text_length,

        "skill_count": skill_count,

        "sections_detected": found_sections
    }