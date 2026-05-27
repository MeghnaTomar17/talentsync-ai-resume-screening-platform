def calculate_skill_overlap(
    resume_skills,
    job_skills
):

    if len(job_skills) == 0:
        return 0

    matched_skills = set(
        resume_skills
    ).intersection(
        set(job_skills)
    )

    overlap_score = (
        len(matched_skills)
        /
        len(job_skills)
    ) * 100

    return round(
        overlap_score,
        2
    )


def calculate_resume_quality(
    resume_text
):

    score = 0

    word_count = len(
        resume_text.split()
    )

    if 300 <= word_count <= 1200:
        score += 40

    technical_keywords = [
        "project",
        "experience",
        "skill",
        "education",
        "developer"
    ]

    for keyword in technical_keywords:

        if keyword in resume_text:
            score += 10

    return min(score, 100)


def calculate_final_ats_score(
    semantic_score,
    skill_overlap_score,
    quality_score
):

    final_score = (
        semantic_score * 0.4
        +
        skill_overlap_score * 0.3
        +
        quality_score * 0.3
    )

    return round(final_score, 2)