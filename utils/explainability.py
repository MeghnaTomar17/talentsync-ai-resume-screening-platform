def generate_match_explanation(

    resume_skills,

    job_skills,

    semantic_score,

    ats_score

):

    matched_skills = list(
        set(resume_skills).intersection(
            set(job_skills)
        )
    )

    missing_skills = list(
        set(job_skills) - set(resume_skills)
    )

    explanation = {

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "semantic_score": semantic_score,

        "ats_score": ats_score
    }

    return explanation