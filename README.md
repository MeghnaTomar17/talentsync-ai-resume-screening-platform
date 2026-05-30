# TalentSync AI

## AI-Powered Resume Screening, Career Intelligence & Skill Gap Analysis Platform

TalentSync AI is an end-to-end AI-powered hiring intelligence platform that automates resume screening, semantic candidate-job matching, ATS-style evaluation, skill gap detection, and personalized career guidance.

Unlike traditional resume checkers that rely solely on keyword matching, TalentSync leverages Natural Language Processing (NLP), Sentence Embeddings, Explainable AI, and Large Language Models (LLMs) to provide recruiter-grade resume analysis and actionable career recommendations.

---

# Key Features

### Resume Analysis

* PDF Resume Parsing using `pdfplumber`
* Advanced NLP Preprocessing Pipeline
* Resume Text Cleaning & Normalization
* Automated Skill Extraction
* Resume Quality Assessment
* ATS Compatibility Analysis
* Resume Type Detection (ATS-Friendly, Modern, Canva-Style, Graphic Heavy)

### Semantic Matching Engine

* Sentence Transformer Embeddings
* Semantic Resume-Job Matching
* Embedding-Based Similarity Search
* Top Job Recommendation System
* Job Ranking & Relevance Scoring

### ATS Intelligence

* Weighted ATS Scoring System
* Skill Gap Analysis
* Matched Skills Detection
* Missing Skills Identification
* Resume Improvement Suggestions

### Explainable AI Layer

* Transparent ATS Scoring
* Resume Quality Warnings
* Extraction Quality Analysis
* ATS Compatibility Insights
* Actionable Recommendations

### LLM-Powered Career Intelligence

Powered by Google Gemini

* AI Resume Coach
* Resume Strength Analysis
* Resume Weakness Analysis
* ATS Improvement Suggestions
* Learning Recommendations
* Project Recommendations
* Certification Recommendations
* Interview Readiness Assessment
* Hiring Recommendation

### Career Growth Features

* Personalized Skill Gap Analysis
* AI Career Roadmap Generator
* 30-Day Learning Plan
* Weekly Skill Development Guidance
* Career Growth Recommendations

### Interactive Dashboard

Built with Streamlit

* PDF Resume Upload
* Real-Time Analysis
* Progress Tracking
* Interactive Visualizations
* Resume Insights Dashboard
* Career Guidance Dashboard

---

# AI & NLP Techniques Used

## Classical NLP

* Text Cleaning
* Regex Normalization
* Tokenization
* Stopword Removal
* Lemmatization
* TF-IDF Vectorization
* Cosine Similarity

## Semantic AI

* Sentence Embeddings
* Semantic Similarity Search
* Embedding-Based Retrieval
* Candidate-Job Matching
* Context-Aware Ranking

## Explainable AI

* ATS Score Decomposition
* Skill Gap Detection
* Matched vs Missing Skills Analysis
* Resume Quality Assessment

## Generative AI

* Prompt Engineering
* Gemini 2.5 Flash Integration
* Career Guidance Generation
* Resume Feedback Generation
* Learning Roadmap Generation

---

# Tech Stack

## Programming Language

* Python

## AI / NLP Libraries

* NLTK
* Sentence Transformers
* Hugging Face Transformers
* Scikit-Learn
* Google Generative AI

## Data Processing

* Pandas
* NumPy

## Visualization

* Matplotlib

## Parsing & Utilities

* pdfplumber
* BeautifulSoup
* Regex
* python-dotenv

## Frontend

* Streamlit

## Development Tools

* VS Code
* Jupyter Notebook
* Git
* GitHub

---

# Project Architecture

```text
Resume PDF
      ↓
PDF Parsing
      ↓
NLP Cleaning
      ↓
Skill Extraction
      ↓
Resume Quality Analysis
      ↓
ATS Compatibility Detection
      ↓
Sentence Embeddings
      ↓
Semantic Matching
      ↓
Job Recommendation Engine
      ↓
ATS Scoring Engine
      ↓
Explainable AI Layer
      ↓
Gemini Resume Coach
      ↓
Career Roadmap Generator
      ↓
Interactive Dashboard
```

---

# Project Structure

```bash
TalentSyncAI/
│
├── app/
│   └── streamlit_app.py
│
├── datasets/
│   ├── jobs.csv
│   └── resumes.csv
│
├── matching/
│   ├── semantic_matcher.py
│   ├── ats_scorer.py
│
├── pdf_parser/
│   └── pdf_reader.py
│
├── preprocessing/
│   ├── text_cleaner.py
│   ├── skill_extractor.py
│
├── utils/
│   ├── explainability.py
│   ├── extraction_quality.py
│   ├── llm_feedback.py
│   └── career_roadmap.py
│
├── notebooks/
│   ├── preprocessing_pipeline.ipynb
│   ├── pdf_resume_parser.ipynb
│
├── outputs/
├── visuals/
├── sample_resume/
├── synthetic_data/
│
├── README.md
├── requirements.txt
└── .env
```

---

# Interactive User Workflow

```text
Upload Resume
      ↓
Resume Parsing
      ↓
Text Cleaning
      ↓
Skill Extraction
      ↓
Resume Quality Analysis
      ↓
ATS Compatibility Evaluation
      ↓
Semantic Job Matching
      ↓
ATS Score Calculation
      ↓
Skill Gap Detection
      ↓
Top Job Recommendations
      ↓
AI Resume Coach
      ↓
Career Roadmap Generation
```

---

# Challenges Solved

### Resume Parsing Challenges

* Handled different resume formats
* Managed noisy PDF extraction
* Addressed Canva-style resume limitations

### NLP Challenges

* Preserved semantic meaning during cleaning
* Normalized skill representations
* Improved extraction consistency

### Explainability Challenges

* Provided reasoning behind ATS scores
* Highlighted missing skills and skill gaps
* Generated actionable recommendations

### LLM Integration Challenges

* Gemini API integration
* Prompt engineering for recruiter-style feedback
* Personalized career guidance generation

---

# Current Version

### TalentSync AI v0.4

Current Capabilities:

* Semantic Resume Matching
* ATS Evaluation
* Explainable AI Insights
* Resume Quality Analysis
* AI Resume Coaching
* Career Roadmap Generation
* Interactive Streamlit Dashboard

---

# Planned Enhancements

### AI Engineering Roadmap

* FAISS Vector Search
* Vector Database Integration
* Multi-Resume Candidate Ranking
* Recruiter Dashboard
* Resume Bullet Rewriter
* Interview Preparation Assistant
* Multi-Language Resume Analysis
* Docker Deployment
* Cloud Deployment
* User Authentication & Profiles

---

# Future Vision

TalentSync AI aims to evolve from a resume screening application into a complete AI-powered Career Intelligence Platform that assists candidates throughout their professional growth journey—from resume optimization and job matching to personalized learning and career planning.
