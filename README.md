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
