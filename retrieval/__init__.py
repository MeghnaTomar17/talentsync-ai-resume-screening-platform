"""
FAISS-based Semantic Retrieval Module for TalentSync AI

This module provides efficient vector-based retrieval using FAISS
for semantic resume-job matching.
"""

from .faiss_retriever import (
    build_faiss_index,
    save_faiss_index,
    load_faiss_index,
    search_faiss_index
)

__all__ = [
    'build_faiss_index',
    'save_faiss_index',
    'load_faiss_index',
    'search_faiss_index'
]
