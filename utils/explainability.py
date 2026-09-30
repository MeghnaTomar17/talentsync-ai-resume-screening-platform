from matching.ats_scorer import (
    SEMANTIC_WEIGHT,
    SKILL_OVERLAP_WEIGHT,
    QUALITY_WEIGHT
)


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

# ---------------------------------------------------
# SCORE BREAKDOWN
# ---------------------------------------------------


def build_score_breakdown(

    semantic_score,

    skill_overlap_score,

    quality_score,

    ats_score

):
    """
    Decompose the ATS score into its weighted components.

    Every component is on a 0-100 scale; "contribution" is the number of
    points it adds to the final ATS score (weight x score).
    """

    components = {

        "semantic_similarity": (semantic_score, SEMANTIC_WEIGHT),

        "skill_overlap": (skill_overlap_score, SKILL_OVERLAP_WEIGHT),

        "resume_quality": (quality_score, QUALITY_WEIGHT)
    }

    breakdown = {}

    for name, (score, weight) in components.items():

        breakdown[name] = {

            "score": round(score, 2),

            "weight": weight,

            "contribution": round(score * weight, 2),

            "max_contribution": round(100 * weight, 2)
        }

    return {

        "ats_score": ats_score,

        "components": breakdown,

        "formula": (
            f"{SEMANTIC_WEIGHT} x semantic_similarity + "
            f"{SKILL_OVERLAP_WEIGHT} x skill_overlap + "
            f"{QUALITY_WEIGHT} x resume_quality"
        )
    }


def generate_score_reasons(

    score_breakdown,

    matched_skills,

    missing_skills,

    partial_matches,

    quality_report

):
    """
    Plain-language reasons for the score, built only from the computed
    numbers (deterministic, no LLM).
    """

    reasons = []

    components = score_breakdown["components"]

    semantic = components["semantic_similarity"]

    reasons.append(
        f"Semantic similarity with the job is {semantic['score']:.0f}/100 "
        f"({semantic['contribution']:.1f} of {semantic['max_contribution']:.0f} points)."
    )

    total_job_skills = len(matched_skills) + len(missing_skills)

    skill = components["skill_overlap"]

    if total_job_skills == 0:

        reasons.append(
            "No recognised skills were found in the job description, "
            "so skill overlap is 0."
        )

    else:

        reasons.append(
            f"Resume covers {len(matched_skills)} of {total_job_skills} job skills "
            f"({skill['contribution']:.1f} of {skill['max_contribution']:.0f} points)."
        )

    if matched_skills:

        reasons.append(
            "Matched skills: " + ", ".join(matched_skills) + "."
        )

    if missing_skills:

        reasons.append(
            "Points lost for missing skills: " + ", ".join(missing_skills) + "."
        )

    for partial in partial_matches:

        reasons.append(
            f"{partial['skill']} is missing, but the related skill(s) "
            f"{', '.join(partial['related_skills'])} were found."
        )

    quality = components["resume_quality"]

    reasons.append(
        f"Resume quality/ATS-readability is {quality['score']:.0f}/100 "
        f"({quality['contribution']:.1f} of {quality['max_contribution']:.0f} points)."
    )

    for warning in (quality_report or {}).get("warnings", []):

        reasons.append("Quality warning: " + warning)

    return reasons
