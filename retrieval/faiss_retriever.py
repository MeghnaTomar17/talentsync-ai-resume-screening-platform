"""
FAISS-based Semantic Retriever

Provides efficient vector similarity search using FAISS IndexFlatIP
with normalized embeddings for cosine similarity.
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import Tuple, List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from matching.semantic_matcher import get_embeddings


# ---------------------------------------------------
# INDEX CONFIGURATION
# ---------------------------------------------------

INDEX_DIR = Path("faiss_index")
INDEX_FILE = INDEX_DIR / "job_index.faiss"
METADATA_FILE = INDEX_DIR / "job_metadata.pkl"


# ---------------------------------------------------
# NORMALIZE EMBEDDINGS
# ---------------------------------------------------

def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """
    Normalize embeddings to unit length for cosine similarity using IndexFlatIP.
    
    Args:
        embeddings: numpy array of shape (n, d)
        
    Returns:
        Normalized embeddings of same shape
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Avoid division by zero
    norms[norms == 0] = 1
    return embeddings / norms


# ---------------------------------------------------
# BUILD FAISS INDEX
# ---------------------------------------------------

def build_faiss_index(
    job_descriptions: List[str],
    job_metadata: List[Dict[str, Any]]
) -> Tuple[faiss.Index, np.ndarray]:
    """
    Build FAISS index from job descriptions using existing embedding functions.
    
    Args:
        job_descriptions: List of cleaned job description texts
        job_metadata: List of metadata dictionaries for each job
                       (e.g., job title, original description, etc.)
        
    Returns:
        Tuple of (FAISS index, normalized embeddings)
    """
    # Generate embeddings using existing semantic_matcher functions
    print("Generating embeddings for job descriptions...")
    embeddings = get_embeddings(job_descriptions)
    
    # Normalize embeddings for cosine similarity with IndexFlatIP
    print("Normalizing embeddings...")
    normalized_embeddings = normalize_embeddings(embeddings)
    
    # Get embedding dimension
    dimension = normalized_embeddings.shape[1]
    
    # Create FAISS index (IndexFlatIP for inner product = cosine similarity with normalized vectors)
    print(f"Building FAISS index with dimension {dimension}...")
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(normalized_embeddings)
    
    print(f"Index built with {index.ntotal} vectors")
    
    return index, normalized_embeddings


# ---------------------------------------------------
# SAVE FAISS INDEX
# ---------------------------------------------------

def save_faiss_index(
    index: faiss.Index,
    job_metadata: List[Dict[str, Any]],
    index_dir: Path = INDEX_DIR
) -> None:
    """
    Save FAISS index and job metadata to disk for reuse.
    
    Args:
        index: FAISS index object
        job_metadata: List of job metadata dictionaries
        index_dir: Directory to save index files
    """
    # Create directory if it doesn't exist
    index_dir.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    index_path = index_dir / "job_index.faiss"
    faiss.write_index(index, str(index_path))
    print(f"FAISS index saved to {index_path}")
    
    # Save job metadata
    metadata_path = index_dir / "job_metadata.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(job_metadata, f)
    print(f"Job metadata saved to {metadata_path}")


# ---------------------------------------------------
# LOAD FAISS INDEX
# ---------------------------------------------------

def load_faiss_index(
    index_dir: Path = INDEX_DIR
) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    """
    Load FAISS index and job metadata from disk.
    
    Args:
        index_dir: Directory containing index files
        
    Returns:
        Tuple of (FAISS index, job metadata)
        
    Raises:
        FileNotFoundError: If index files don't exist
    """
    index_path = index_dir / "job_index.faiss"
    metadata_path = index_dir / "job_metadata.pkl"
    
    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"FAISS index files not found in {index_dir}. "
            "Please build and save the index first."
        )
    
    # Load FAISS index
    index = faiss.read_index(str(index_path))
    print(f"FAISS index loaded from {index_path}")
    
    # Load job metadata
    with open(metadata_path, 'rb') as f:
        job_metadata = pickle.load(f)
    print(f"Job metadata loaded from {metadata_path}")
    
    return index, job_metadata


# ---------------------------------------------------
# SEARCH FAISS INDEX
# ---------------------------------------------------

def search_faiss_index(
    index: faiss.Index,
    query_embedding: np.ndarray,
    k: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Search FAISS index for top-k most similar jobs.
    
    Args:
        index: FAISS index object
        query_embedding: Normalized query embedding (shape: (d,) or (1, d))
        k: Number of top results to return
        
    Returns:
        Tuple of (distances, indices) - distances are similarity scores,
        indices are positions in the original job list
    """
    # Ensure query embedding is 2D
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    # Normalize query embedding
    query_embedding = normalize_embeddings(query_embedding)
    
    # Search index
    distances, indices = index.search(query_embedding, k)
    
    # Return first result (since we only have one query)
    return distances[0], indices[0]


# ---------------------------------------------------
# COMPLETE RETRIEVAL PIPELINE
# ---------------------------------------------------

def retrieve_top_jobs(
    resume_text: str,
    k: int = 5,
    index_dir: Path = INDEX_DIR
) -> List[Dict[str, Any]]:
    """
    Complete retrieval pipeline: load index, search resume, return top-k jobs.
    
    Args:
        resume_text: Cleaned resume text
        k: Number of top jobs to retrieve
        index_dir: Directory containing index files
        
    Returns:
        List of job metadata dictionaries with similarity scores added
    """
    # Load index and metadata
    index, job_metadata = load_faiss_index(index_dir)
    
    # Generate query embedding using existing function
    from matching.semantic_matcher import get_embedding
    query_embedding = get_embedding(resume_text)
    
    # Search index
    distances, indices = search_faiss_index(index, query_embedding, k)
    
    # Build results with metadata and scores
    results = []
    for idx, score in zip(indices, distances):
        if idx < len(job_metadata):  # Safety check
            job_info = job_metadata[idx].copy()
            job_info['similarity_score'] = float(score)
            results.append(job_info)
    
    return results
