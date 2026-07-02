import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import requests

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

sys.path.append(".")
sys.path.append("..")

# Keep direct imports for fallback and local processing
from preprocessing.text_cleaner import advanced_clean_text
from preprocessing.skill_extraction_pipeline import extract_skills
from pdf_parser.pdf_reader import extract_text_from_pdf
from utils.explainability import generate_match_explanation
from utils.llm_feedback import generate_resume_feedback
from utils.career_roadmap import generate_career_roadmap


# ============================================================
# API CLIENT FUNCTIONS
# ============================================================

def call_api(endpoint: str, method: str = "GET", data: dict = None, files: dict = None):
    """
    Make an API call to the backend.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST)
        data: JSON data for POST requests
        files: Files for multipart upload
        
    Returns:
        JSON response or None on error
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data, timeout=60)
            else:
                response = requests.post(url, json=data, timeout=60)
        else:
            st.error(f"Unsupported method: {method}")
            return None
        
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and {"success", "message", "data"}.issubset(payload):
            if not payload.get("success"):
                st.error(payload.get("message", "API request failed"))
                return None
            return payload.get("data")
        return payload
        
    except requests.exceptions.ConnectionError:
        st.warning(f"Could not connect to backend at {API_BASE_URL}. Using local processing.")
        return None
    except requests.exceptions.Timeout:
        st.error("API request timed out. Using local processing.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None


def upload_resume_via_api(file_content: bytes, filename: str, enable_ocr: bool = True):
    """Upload resume via API."""
    return call_api(
        "/upload_resume",
        method="POST",
        files={"file": (filename, file_content, "application/pdf")},
        data={"enable_ocr": enable_ocr}
    )


def analyze_resume_via_api(resume_text: str, enable_llm: bool = False):
    """Analyze resume via API."""
    return call_api(
        "/analyze_resume",
        method="POST",
        data={"resume_text": resume_text, "enable_llm": enable_llm}
    )


def get_resume_feedback_via_api(resume_text: str, resume_skills: list, 
                                 job_title: str = None, job_description: str = None):
    """Get resume feedback via API."""
    return call_api(
        "/resume_feedback",
        method="POST",
        data={
            "resume_text": resume_text,
            "resume_skills": resume_skills,
            "job_title": job_title,
            "job_description": job_description
        }
    )


def get_career_roadmap_via_api(resume_skills: list, missing_skills: list, target_role: str = None):
    """Get career roadmap via API."""
    return call_api(
        "/career_roadmap",
        method="POST",
        data={
            "resume_skills": resume_skills,
            "missing_skills": missing_skills,
            "target_role": target_role
        }
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
# Note: Jobs are now loaded via FAISS index for efficient retrieval
# Original dataset is used for index building via build_index.py

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

            # Try to use API for processing, fallback to local
            use_api = st.checkbox("Use Backend API", value=True, help="Use FastAPI backend for processing")
            
            if use_api:
                # Upload and analyze via API
                with open("temp_resume.pdf", "rb") as f:
                    file_content = f.read()
                
                # Upload resume
                upload_result = upload_resume_via_api(file_content, "temp_resume.pdf")
                
                if upload_result:
                    resume_text = upload_result.get("resume_text", "")
                    cleaned_resume = upload_result.get("cleaned_text", "")
                    extraction_result = {
                        **(upload_result.get("extraction_metadata") or {}),
                        "text": resume_text,
                    }
                else:
                    extraction_result = extract_text_from_pdf("temp_resume.pdf")
                    resume_text = extraction_result["text"]
                    cleaned_resume = advanced_clean_text(resume_text)
                
                # Analyze via API
                analysis_result = analyze_resume_via_api(cleaned_resume, enable_llm=False)
                
                if analysis_result:
                    # Use API results
                    resume_skills = analysis_result["extracted_skills"]
                    categorized_skills = analysis_result["categorized_skills"]
                    skill_confidence = analysis_result["skill_confidence"]
                    skill_count = analysis_result["skill_count"]
                    skill_extraction_result = {
                        "extracted_skills": resume_skills,
                        "categorized_skills": categorized_skills,
                        "confidence_score": skill_confidence,
                        "skill_count": skill_count,
                    }
                    
                    # Build job_df from API results
                    job_df_with_scores = []
                    all_scores = []
                    
                    for job in analysis_result["top_jobs"]:
                        all_scores.append(job["semantic_score"] / 100)  # Convert back to 0-1
                        job_df_with_scores.append({
                            'Job Title': job['job_title'],
                            'Job Description': job['job_description'],
                            'cleaned_job_description': job['job_description'],  # API doesn't return cleaned
                            'semantic_score': job['semantic_score'] / 100
                        })
                    
                    job_df = pd.DataFrame(job_df_with_scores)
                    
                    # Get best match
                    if analysis_result["best_match"]:
                        best_job_title = analysis_result["best_match"]["job_title"]
                        best_job_description = analysis_result["best_match"]["job_description"]
                        semantic_score = analysis_result["best_match"]["semantic_score"]
                        matched_skills = analysis_result["matched_skills"]
                        missing_skills = analysis_result["missing_skills"]
                        skill_overlap_score = analysis_result["skill_overlap_score"]
                        ats_score = analysis_result["ats_score"]
                        quality_report = analysis_result["quality_report"]
                        
                        # Extract job skills for display
                        job_skill_result = extract_skills(best_job_description, enable_llm=False)
                        job_skills = job_skill_result["extracted_skills"]
                    else:
                        st.warning("No jobs found via API")
                        st.stop()
                else:
                    # Fallback to local processing
                    st.warning("API unavailable, using local processing")
                    use_api = False
            
            if not use_api:
                # Local processing (original logic)
                extraction_result = extract_text_from_pdf("temp_resume.pdf")
                resume_text = extraction_result["text"]
                cleaned_resume = advanced_clean_text(resume_text)
                
                status.info("Extracting text from PDF")
                status.info("Cleaning resume text")
                
                # Import local modules
                from utils.extraction_quality import analyze_extraction_quality
                from retrieval.faiss_retriever import retrieve_top_jobs
                
                skill_extraction_result = extract_skills(cleaned_resume, enable_llm=False)
                resume_skills = skill_extraction_result["extracted_skills"]
                categorized_skills = skill_extraction_result["categorized_skills"]
                skill_confidence = skill_extraction_result["confidence_score"]
                skill_count = skill_extraction_result["skill_count"]
                
                quality_report = analyze_extraction_quality(cleaned_resume, resume_skills)
                
                status.info("Extracting skills")
                status.info("Performing semantic matching with FAISS...")
                
                with st.spinner("Searching for best job matches"):
                    top_jobs = retrieve_top_jobs(cleaned_resume, k=1000)
                
                all_scores = []
                job_df_with_scores = []
                
                for job_info in top_jobs:
                    all_scores.append(job_info['similarity_score'])
                    job_df_with_scores.append({
                        'Job Title': job_info['job_title'],
                        'Job Description': job_info['job_description'],
                        'cleaned_job_description': job_info['cleaned_description'],
                        'semantic_score': job_info['similarity_score']
                    })
                
                job_df = pd.DataFrame(job_df_with_scores)
                
                # Get best match
                best_job = job_df.sort_values(by="semantic_score", ascending=False).iloc[0]
                best_job_title = best_job["Job Title"]
                best_job_description = best_job["cleaned_job_description"]
                semantic_score = best_job["semantic_score"]
                
                # Extract job skills
                job_skill_result = extract_skills(best_job_description, enable_llm=False)
                job_skills = job_skill_result["extracted_skills"]
                
                # Calculate scores
                from matching.ats_scorer import calculate_skill_overlap, calculate_final_ats_score
                skill_overlap_score = calculate_skill_overlap(resume_skills, job_skills)
                ats_score = calculate_final_ats_score(
                    semantic_score * 100,
                    skill_overlap_score,
                    quality_report["ats_score"]
                )
                
                matched_skills = list(set(resume_skills).intersection(set(job_skills)))
                missing_skills = list(set(job_skills) - set(resume_skills))

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

    # Use new skill extraction pipeline for job skills (LLM disabled by default)
    job_skill_result = extract_skills(best_job_description, enable_llm=False)
    job_skills = job_skill_result["extracted_skills"]

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
    # ATS SCORING (if not already calculated by API)
    # ---------------------------------------------------

    if 'skill_overlap_score' not in locals():
        from matching.ats_scorer import calculate_skill_overlap, calculate_resume_quality, calculate_final_ats_score
        skill_overlap_score = calculate_skill_overlap(resume_skills, job_skills)
        quality_score = calculate_resume_quality(cleaned_resume)
        ats_score = calculate_final_ats_score(semantic_score * 100, skill_overlap_score, quality_score)
    else:
        # Already calculated by API
        pass

    final_ats_score = ats_score

    # ---------------------------------------------------
    # EXPLAINABILITY
    # ---------------------------------------------------

    explanation = generate_match_explanation(

        resume_skills,

        job_skills,

        semantic_score * 100 if semantic_score < 1 else semantic_score,

        ats_score if 'ats_score' in locals() else skill_overlap_score
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
    # PDF EXTRACTION METADATA
    # ==================================================
    
    st.subheader("PDF Extraction Details")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Parser Used",
            extraction_result.get("parser_used", "Unknown")
        )
    
    with col2:
        st.metric(
            "Extraction Confidence",
            f"{extraction_result.get('confidence', 0)}%"
        )
    
    with col3:
        st.metric(
            "OCR Used",
            "Yes" if extraction_result.get("ocr_used", False) else "No"
        )
    
    with col4:
        st.metric(
            "Fallback Count",
            extraction_result.get("fallback_count", 0)
        )
    
    with st.expander("View Extraction Details"):
        st.write(f"**Success:** {extraction_result.get('success', False)}")
        st.write(f"**Text Length:** {len(extraction_result.get('text', ''))} characters")
        
        if extraction_result.get("quality_metrics"):
            st.write("**Quality Metrics:**")
            for metric, value in extraction_result["quality_metrics"].items():
                st.write(f"- {metric}: {value}")
        
        if extraction_result.get("all_results"):
            st.write("**All Parser Attempts:**")
            for result in extraction_result["all_results"]:
                status_icon = "✅" if result["success"] else "❌"
                st.write(f"{status_icon} {result['parser']}: {result['text_length']} chars")
    
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
Use a single-column layout
Use clear section headings
Avoid excessive graphics
Keep skills in a dedicated section
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
    
    # Display skill extraction metadata
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Skills", skill_extraction_result["skill_count"])
    with col2:
        st.metric("Extraction Confidence", f"{skill_confidence}%")
    
    st.write(resume_skills)
    
    # Display categorized skills
    if categorized_skills:
        st.subheader("Skills by Category")
        
        for category, skills in categorized_skills.items():
            if skills:  # Only show non-empty categories
                with st.expander(f"{category} ({len(skills)})"):
                    st.write(skills)

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
