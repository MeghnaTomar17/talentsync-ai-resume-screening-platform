# TalentSync AI   
### AI-Powered Resume Screening & Skill Gap Analysis Platform

TalentSync AI is an end-to-end NLP and semantic AI-based hiring intelligence system designed to automate resume screening, candidate-job matching, ATS-style scoring, and skill-gap analysis. The project focuses heavily on real-world AI engineering workflows such as preprocessing pipelines, semantic embeddings, modular architecture, and explainable AI rather than only model training.

---

##  Features

-  PDF Resume Parsing using `pdfplumber`
-  Advanced NLP preprocessing pipeline
-  Token-aware skill extraction & normalization
-  TF-IDF based similarity matching
-  Semantic embedding matching using Sentence Transformers
-  ATS-style weighted scoring system
-  Skill-gap analysis & recommendations
-  Resume ranking & intelligent job recommendations
-  Modular production-style architecture
-  Real-world recruiter workflow simulation

---

#  AI & NLP Techniques Used

## Classical NLP
- Text Cleaning
- Regex Normalization
- Tokenization
- Stopword Removal
- Lemmatization
- TF-IDF Vectorization
- Cosine Similarity

## Modern NLP / Semantic AI
- Sentence Embeddings
- HuggingFace Sentence Transformers
- Semantic Similarity Search
- Embedding-based Ranking

---

#  Tech Stack

## Languages
- Python

## AI / NLP Libraries
- NLTK
- Sentence Transformers
- HuggingFace Transformers
- Scikit-learn

## Data Handling & Visualization
- Pandas
- Matplotlib
- Seaborn

## Parsing & Utilities
- pdfplumber
- BeautifulSoup
- Regex

## Tools & Platforms
- VS Code
- Git
- GitHub
- Jupyter Notebook

---

#  Project Structure

```bash
TalentSyncAI/
│
├── app/
│   ├── streamlit_app.py

├── datasets/
│   ├── resumes.csv
│   ├── jobs.csv
│
├── matching/
│   ├── semantic_matcher.py
│   ├── ats_scorer.py
│
├── pdf_parser/
│   ├── pdf_reader.py
│
├── preprocessing/
│   ├── text_cleaner.py
│   ├── skill_extractor.py
│
├── notebooks/
│   ├── preprocessing_pipeline.ipynb
│   ├── pdf_resume_parser.ipynb
│
├── sample_resume/
├── synthetic_data/
├── visuals/
├── outputs/
│
├── README.md
└── requirements.txt

## Interactive Resume Analysis Dashboard

The project now includes an interactive Streamlit-based dashboard that allows users to upload PDF resumes and receive real-time analysis.

### Dashboard Features

* PDF Resume Upload
* Automated Resume Parsing
* NLP-Based Resume Cleaning
* Skill Extraction & Normalization
* Semantic Job Matching
* ATS Score Calculation
* Explainable AI Insights
* Missing Skill Detection
* Resume Quality Analysis
* Top Job Recommendations
* Interactive Visual Analytics
* Real-Time Progress Tracking

### User Workflow

Resume Upload
→ PDF Parsing
→ Text Cleaning
→ Skill Extraction
→ Semantic Matching
→ ATS Scoring
→ Explainability Layer
→ Job Recommendations

This transforms TalentSync AI from a notebook-based NLP project into an end-to-end AI-powered hiring intelligence application.

## Project Status

Current Version: v0.2

TalentSync AI has evolved from a notebook-based NLP pipeline into a modular AI application featuring semantic resume-job matching, ATS-style scoring, explainable AI, PDF resume analysis, and an interactive Streamlit dashboard.

# Upcoming Enhancements

* Gemini-Powered Resume Feedback
* Personalized Skill Gap Analysis
* AI Learning Roadmap Generator
* Recruiter Candidate Ranking Dashboard
* FAISS Vector Search Integration
* Multi-Resume Candidate Comparison
* Resume Improvement Suggestions
* Interview Readiness Assessment
* Cloud Deployment
* User Authentication & Profiles

