from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# LOAD MODEL ONLY ONCE
model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

# ---------------------------------------------------
# GET SINGLE EMBEDDING
# ---------------------------------------------------

def get_embedding(text):

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    return embedding

# ---------------------------------------------------
# GET MULTIPLE EMBEDDINGS
# ---------------------------------------------------

def get_embeddings(text_list):

    embeddings = model.encode(
        text_list,
        convert_to_numpy=True
    )

    return embeddings

# ---------------------------------------------------
# CALCULATE SIMILARITY
# ---------------------------------------------------

def calculate_similarity(
    embedding1,
    embedding2
):

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return round(similarity * 100, 2)