"""
Retrieval Service

Handles FAISS-based semantic job retrieval.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import csv
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from retrieval.faiss_retriever import retrieve_top_jobs
from backend.core.config import settings
from backend.core.logger import logger


class RetrievalService:
    """Service for FAISS-based job retrieval."""
    
    def __init__(self, index_dir: str = settings.faiss_index_dir):
        """
        Initialize the retrieval service.
        
        Args:
            index_dir: Directory containing FAISS index and metadata
        """
        self.index_dir = Path(index_dir)
    
    def retrieve_jobs(self, resume_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k jobs matching the resume.
        
        Args:
            resume_text: Cleaned resume text
            k: Number of jobs to retrieve
            
        Returns:
            List of job dictionaries with metadata
        """
        try:
            jobs = retrieve_top_jobs(resume_text, k=k, index_dir=self.index_dir)
            method = "faiss"
        except Exception as exc:
            logger.warning("faiss_retrieval_failed index_dir=%s error=%s", self.index_dir, exc)
            jobs = self._retrieve_jobs_with_tfidf(resume_text, k=k)
            method = "tfidf"
        logger.info("job_retrieval_completed method=%s requested=%s returned=%s", method, k, len(jobs))
        
        # Format for API response
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                "job_title": job["job_title"],
                "job_description": job["job_description"],
                "cleaned_description": job["cleaned_description"],
                "semantic_score": round(job["similarity_score"] * 100, 2),
                "index": job["index"]
            })
        
        return formatted_jobs
    
    def get_best_match(self, resume_text: str) -> Dict[str, Any]:
        """
        Get the single best matching job.
        
        Args:
            resume_text: Cleaned resume text
            
        Returns:
            Best matching job dictionary
        """
        jobs = self.retrieve_jobs(resume_text, k=1)
        return jobs[0] if jobs else None

    def _retrieve_jobs_with_tfidf(self, resume_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Local fallback when the embedding model or FAISS retrieval is unavailable.

        This keeps the API usable in offline environments while preserving the
        same return shape as FAISS retrieval.
        """
        jobs_path = settings.jobs_path
        if not jobs_path.exists():
            logger.error("jobs_dataset_missing path=%s", jobs_path)
            return []

        rows = []
        with open(jobs_path, newline="", encoding="utf-8") as jobs_file:
            reader = csv.DictReader(jobs_file)
            for idx, row in enumerate(reader):
                description = row.get("Job Description", "")
                rows.append({
                    "index": idx,
                    "job_title": row.get("Job Title", "Unknown Role"),
                    "job_description": description,
                    "cleaned_description": self._clean_for_tfidf(description),
                })

        if not rows:
            return []

        corpus = [self._clean_for_tfidf(resume_text)] + [
            row["cleaned_description"] for row in rows
        ]
        vectors = TfidfVectorizer(stop_words="english").fit_transform(corpus)
        scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        top_indices = scores.argsort()[::-1][:k]

        results = []
        for idx in top_indices:
            job = rows[int(idx)].copy()
            job["similarity_score"] = float(scores[int(idx)])
            results.append(job)

        return results

    def _clean_for_tfidf(self, text: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9+#.\s]", " ", str(text))).strip().lower()
