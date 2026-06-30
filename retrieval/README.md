# FAISS-based Semantic Retrieval Module

## Overview

This module provides efficient vector-based semantic retrieval using FAISS (Facebook AI Similarity Search) for the TalentSync AI platform. It replaces the brute-force cosine similarity search with a scalable, production-ready solution.

## Architecture

### Components

- **`faiss_retriever.py`**: Core retrieval logic
  - `build_faiss_index()`: Builds FAISS index from job descriptions
  - `save_faiss_index()`: Persists index and metadata to disk
  - `load_faiss_index()`: Loads pre-built index from disk
  - `search_faiss_index()`: Performs similarity search
  - `retrieve_top_jobs()`: Complete retrieval pipeline

### Key Design Decisions

1. **Index Type**: `IndexFlatIP` (Inner Product)
   - Uses normalized embeddings for cosine similarity
   - Exact search (no approximation)
   - Suitable for medium-sized datasets

2. **Embedding Reuse**: Leverages existing `semantic_matcher.py` functions
   - No duplication of embedding logic
   - Consistent with current pipeline
   - Uses `all-MiniLM-L6-v2` model

3. **Persistence**: Index saved to `faiss_index/` directory
   - `job_index.faiss`: FAISS index file
   - `job_metadata.pkl`: Job metadata (title, description, etc.)
   - Enables fast startup without rebuilding

## Usage

### Building the Index

Run the index building script once to create the FAISS index:

```bash
python build_index.py
```

This will:
1. Load `datasets/jobs.csv`
2. Clean job descriptions using existing pipeline
3. Generate embeddings using Sentence Transformers
4. Build and save FAISS index to `faiss_index/`

### Integration in Streamlit App

The Streamlit app (`app/streamlit_app.py`) now uses FAISS retrieval:

```python
from retrieval.faiss_retriever import retrieve_top_jobs

# Retrieve top jobs using FAISS
top_jobs = retrieve_top_jobs(
    cleaned_resume,
    k=1000  # Number of jobs to retrieve
)
```

## Performance Benefits

### Before (Brute-Force)
- O(n) complexity per query
- Must compute similarity against every job
- Slow for large job datasets

### After (FAISS)
- O(log n) complexity with IndexFlatIP
- Pre-computed embeddings
- Sub-millisecond search times
- Scales to millions of jobs

## API Reference

### `build_faiss_index(job_descriptions, job_metadata)`

Builds FAISS index from job descriptions.

**Parameters:**
- `job_descriptions` (List[str]): Cleaned job description texts
- `job_metadata` (List[Dict]): Metadata for each job

**Returns:**
- `Tuple[faiss.Index, np.ndarray]`: Index and normalized embeddings

### `save_faiss_index(index, job_metadata, index_dir)`

Saves index and metadata to disk.

**Parameters:**
- `index` (faiss.Index): FAISS index object
- `job_metadata` (List[Dict]): Job metadata
- `index_dir` (Path): Directory to save files (default: `faiss_index/`)

### `load_faiss_index(index_dir)`

Loads pre-built index from disk.

**Parameters:**
- `index_dir` (Path): Directory containing index files

**Returns:**
- `Tuple[faiss.Index, List[Dict]]`: Index and job metadata

### `search_faiss_index(index, query_embedding, k)`

Searches index for top-k similar jobs.

**Parameters:**
- `index` (faiss.Index): FAISS index object
- `query_embedding` (np.ndarray): Query embedding
- `k` (int): Number of results to return

**Returns:**
- `Tuple[np.ndarray, np.ndarray]`: (distances, indices)

### `retrieve_top_jobs(resume_text, k, index_dir)`

Complete retrieval pipeline.

**Parameters:**
- `resume_text` (str): Cleaned resume text
- `k` (int): Number of top jobs to retrieve
- `index_dir` (Path): Directory containing index files

**Returns:**
- `List[Dict]`: Job metadata with similarity scores

## File Structure

```
retrieval/
├── __init__.py          # Module exports
├── faiss_retriever.py   # Core implementation
└── README.md            # This file

faiss_index/             # Created after running build_index.py
├── job_index.faiss      # FAISS index file
└── job_metadata.pkl     # Job metadata

build_index.py           # Script to build the index
```

## Dependencies

Added to `requirements.txt`:
- `faiss-cpu`: CPU-optimized FAISS library

## Notes

- The index must be built before running the Streamlit app
- Rebuild the index if the jobs dataset changes
- For very large datasets (>1M jobs), consider using `IndexIVFFlat` or `IndexHNSW`
- GPU acceleration is available with `faiss-gpu` if needed

## Future Enhancements

- Add incremental index updates
- Support for approximate search with `IndexIVFFlat`
- GPU acceleration option
- Multi-index support for different job categories
