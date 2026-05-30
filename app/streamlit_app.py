import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys



sys.path.append(".")
sys.path.append("..")

from utils.llm_feedback import (
    generate_resume_feedback
)

from utils.career_roadmap import (
    generate_career_roadmap
)

from utils.extraction_quality import (
    analyze_extraction_quality
)

from preprocessing.text_cleaner import advanced_clean_text

from preprocessing.skill_extractor import (
    advanced_skill_extractor
)

from pdf_parser.pdf_reader import (
    extract_text_from_pdf
)

from matching.semantic_matcher import (
    calculate_semantic_similarity
)

from matching.ats_scorer import (

    calculate_skill_overlap,

    calculate_resume_quality,

    calculate_final_ats_score
)

from utils.explainability import (
    generate_match_explanation
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(

    page_title="TalentSync AI",

    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("TalentSync AI")

st.subheader(
    "AI-Powered Resume Screening & Job Recommendation System"
)

# ---------------------------------------------------
# LOAD JOB DATASET
# ---------------------------------------------------

job_df = pd.read_csv(
    "datasets/jobs.csv"
)

job_df["cleaned_job_description"] = (

    job_df["Job Description"]

    .astype(str)

    .apply(advanced_clean_text)
)

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader(

    "Upload Resume PDF",

    type=["pdf"]
)

# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------

if uploaded_file is not None:

    status = st.empty()

    status.info("Reading Resume PDF...")

    with st.spinner("Processing Resume"):

        try:

            status.info("Resume uploaded")

            with open("temp_resume.pdf", "wb") as f:
                f.write(uploaded_file.read())

            status.info("Resume saved")

            resume_text = extract_text_from_pdf(
                "temp_resume.pdf"
            )

            status.info("Extracting text from PDF")

            cleaned_resume = advanced_clean_text(
                resume_text
            )

            status.info("Cleaning resume text")

            resume_skills = advanced_skill_extractor(
                cleaned_resume
            )

            quality_report = analyze_extraction_quality(

                cleaned_resume,

                resume_skills
            )

            status.info("Extracting skills")

            all_scores = []

            progress = st.progress(0)

            total_jobs = len(job_df)

            st.info(f"Scanning {len(job_df)} job descriptions...")

            progress_text = st.empty()

            for index, row in job_df.iterrows():

                score = calculate_semantic_similarity(
                    cleaned_resume,
                    row["cleaned_job_description"]
                )

                all_scores.append(score)

                progress.progress(
                    (index + 1) / total_jobs
                )

                progress_text.write(f"Analyzing Job {index + 1}/{total_jobs}")

            status.info("Semantic matching completed")

            status.success("Resume Analysis Complete!")

            st.toast("Analysis completed successfully!", icon="🎉")

            st.balloons()

        except Exception as e:

            st.error(f"ERROR: {e}")

    # STORE SCORES

    job_df["semantic_score"] = all_scores

    # GET BEST MATCHED JOB

    best_job = job_df.sort_values(

        by="semantic_score",

        ascending=False

    ).iloc[0]

    # ---------------------------------------------------
    # BEST MATCHED JOB INFO
    # ---------------------------------------------------

    best_job_title = best_job["Job Title"]

    best_job_description = best_job[
        "cleaned_job_description"
    ]

    semantic_score = best_job[
        "semantic_score"
    ]

    # ---------------------------------------------------
    # JOB SKILLS
    # ---------------------------------------------------

    job_skills = advanced_skill_extractor(
        best_job_description
    )

    matched_skills = list(

        set(resume_skills).intersection(
            set(job_skills)
        )
    )

    missing_skills = list(

        set(job_skills).difference(
            set(resume_skills)
        )
    )

    

    # ---------------------------------------------------
    # ATS SCORING
    # ---------------------------------------------------

    skill_overlap_score = calculate_skill_overlap(

        resume_skills,

        job_skills
    )

    quality_score = calculate_resume_quality(
        cleaned_resume
    )

    final_ats_score = calculate_final_ats_score(

        semantic_score,

        skill_overlap_score,

        quality_score
    )

    # ---------------------------------------------------
    # EXPLAINABILITY
    # ---------------------------------------------------

    explanation = generate_match_explanation(

        resume_skills,

        job_skills,

        semantic_score,

        final_ats_score
    )

    with st.spinner(
    "Generating AI Resume Feedback..."
):

        feedback = generate_resume_feedback(

            cleaned_resume,

            resume_skills,

            explanation["missing_skills"],

            best_job_title
        )

    with st.spinner(
    "Generating Career Roadmap..."
):

        roadmap = generate_career_roadmap(

            best_job_title,

            resume_skills,

            explanation["missing_skills"]
        )

    # ---------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------

    st.subheader("Best Matched Job")

    st.success(best_job_title)

    st.subheader("Debug Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Resume Skills")
        st.write(resume_skills)

    with col2:
        st.write("Job Skills")
        st.write(job_skills)

    with st.expander(
    "View Matched Job Description"):

        st.write(best_job["Job Description"])
    
    # ==================================================
# RESUME QUALITY ANALYSIS
# ==================================================

    st.subheader("Resume Quality Analysis")

    quality_score = quality_report["quality_score"]

    ats_score = quality_report["ats_score"]

    resume_type = quality_report["resume_type"]

# --------------------------------------------------
# QUALITY BADGE
# --------------------------------------------------

    if ats_score >= 85:

        st.success(
            "✅ ATS-Friendly Resume Detected"
        )

    elif ats_score >= 70:

        st.info(
            "ℹ️ Mostly ATS-Friendly Resume"
        )

    else:

        st.warning(
            "⚠️ ATS Compatibility Issues Detected"
        )

# --------------------------------------------------
# MAIN METRICS
# --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Extraction Quality",
            f"{quality_score}%"
        )

    with col2:

        st.metric(
            "ATS Compatibility",
            f"{ats_score}%"
        )

    with col3:

        st.metric(
            "Resume Type",
            resume_type
        )

# --------------------------------------------------
# ATS WARNING
# --------------------------------------------------

    if ats_score < 70:

        st.warning(
            """
     This resume appears to use a complex layout.

Possible causes:
- Canva template
- Multi-column design
- Icons and graphics
- Text boxes
- Decorative formatting

Some ATS systems may struggle to parse
all information correctly.

For best ATS performance:
✅ Use a single-column layout
✅ Use clear section headings
✅ Avoid excessive graphics
✅ Keep skills in a dedicated section
"""
        )

# --------------------------------------------------
# DETAILS
# --------------------------------------------------

    with st.expander(
        "View Extraction Details"
    ):

        st.write(
            f"**Characters Extracted:** {quality_report['text_length']}"
        )

        st.write(
            f"**Skills Detected:** {quality_report['skill_count']}"
        )

        st.write(
            f"**Extraction Quality Level:** {quality_report['quality_level']}"
        )

        if quality_report["warnings"]:

            st.markdown("### ⚠️ Detected Issues")

            for warning in quality_report["warnings"]:

                st.write(
                    f"- {warning}"
                )

# --------------------------------------------------
# RECOMMENDATIONS
# --------------------------------------------------

    if quality_report["recommendations"]:

        st.subheader(
            "🛠 Resume Improvement Suggestions"
        )

        for recommendation in quality_report["recommendations"]:

            st.info(
                recommendation
            )
    # ---------------------------------------------------
    # SCORE CARDS
    # ---------------------------------------------------

    st.subheader("ATS Analysis Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(

            "Semantic Score",

            f"{semantic_score}%"
        )

    with col2:

        st.metric(

            "Skill Overlap",

            f"{skill_overlap_score}%"
        )

    with col3:

        st.metric(

            "Final ATS Score",

            f"{final_ats_score}%"
        )

    # ---------------------------------------------------
    # SKILLS
    # ---------------------------------------------------

    st.subheader("Extracted Resume Skills")

    st.write(resume_skills)

    st.subheader("Extracted Job Skills")

    st.write(job_skills)

    # ---------------------------------------------------
    # MATCHED / MISSING SKILLS
    # ---------------------------------------------------

    st.subheader("Matched Skills")

    if matched_skills:

        for skill in matched_skills:

            st.success(skill)

    else:

        st.warning("No matched skills found.")

    if explanation["matched_skills"]:

        st.success(
            explanation["matched_skills"]
        )

    else:

        st.warning(
            "No matched skills found."
        )

    st.subheader("Missing Skills")

    if missing_skills:

        for skill in missing_skills:

            st.error(skill)

    else:

        st.success("No major missing skills detected.")

    if explanation["missing_skills"]:

        st.error(
            explanation["missing_skills"]
        )

    else:

        st.success(
            "No major missing skills detected."
        )

    # ---------------------------------------------------
    # SCORE VISUALIZATION
    # ---------------------------------------------------

    score_data = {

        "Semantic Score": semantic_score,

        "Skill Overlap": skill_overlap_score,

        "ATS Score": final_ats_score
    }

    fig, ax = plt.subplots()

    ax.bar(

        score_data.keys(),

        score_data.values()
    )

    ax.set_ylabel("Scores")

    ax.set_title("Resume Analysis Scores")

    st.pyplot(fig)

    # ---------------------------------------------------
    # TOP JOB RECOMMENDATIONS
    # ---------------------------------------------------

    
    st.subheader("Top Recommended Jobs")

    top_jobs = job_df.sort_values(
        by="semantic_score",
        ascending=False
        ).head(5)

    for rank, (_, row) in enumerate(
        top_jobs.iterrows(),
        start=1
    ):

        st.write(
            f"{rank}. {row['Job Title']} "
            f"({row['semantic_score']:.2f}%)"
        )

    st.subheader(
        "AI Resume Coach"
    )

    with st.expander(
        "View Personalized Resume Feedback"
    ):

        st.markdown(
            feedback
        )

    st.subheader(
    "Career Growth Roadmap"
)

    st.markdown(
        roadmap
    )