"""
Build FAISS Index from Jobs Dataset

This script builds and saves a FAISS index from the jobs.csv dataset
for efficient semantic retrieval in TalentSync AI.
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from preprocessing.text_cleaner import advanced_clean_text
from retrieval.faiss_retriever import build_faiss_index, save_faiss_index


def build_job_index():
    """
    Build FAISS index from jobs dataset and save to disk.
    """
    print("Loading jobs dataset...")
    job_df = pd.read_csv("datasets/jobs.csv")
    
    print(f"Loaded {len(job_df)} job descriptions")
    
    # Clean job descriptions
    print("Cleaning job descriptions...")
    job_df["cleaned_job_description"] = (
        job_df["Job Description"]
        .astype(str)
        .apply(advanced_clean_text)
    )
    
    # Prepare job metadata
    job_metadata = []
    for idx, row in job_df.iterrows():
        job_metadata.append({
            'index': idx,
            'job_title': row['Job Title'],
            'job_description': row['Job Description'],
            'cleaned_description': row['cleaned_job_description']
        })
    
    # Build FAISS index
    job_descriptions = job_df["cleaned_job_description"].tolist()
    index, embeddings = build_faiss_index(job_descriptions, job_metadata)
    
    # Save index and metadata
    save_faiss_index(index, job_metadata)
    
    print("\n✅ FAISS index built and saved successfully!")
    print(f"Index contains {index.ntotal} job vectors")
    print(f"Embedding dimension: {embeddings.shape[1]}")


if __name__ == "__main__":
    build_job_index()
