from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from backend.core.config import settings

_model = None


def load_model():

    global _model

    if _model is None:

        _model = SentenceTransformer(
            settings.embedding_model
        )

    return _model


# ---------------------------------------------------
# SINGLE EMBEDDING
# ---------------------------------------------------

def get_embedding(text):

    model = load_model()

    return model.encode(
        text,
        convert_to_numpy=True
    )


# ---------------------------------------------------
# MULTIPLE EMBEDDINGS
# ---------------------------------------------------

def get_embeddings(text_list):

    model = load_model()

    return model.encode(
        text_list,
        convert_to_numpy=True
    )


# ---------------------------------------------------
# SIMILARITY
# ---------------------------------------------------

def calculate_similarity(

    embedding1,

    embedding2

):

    similarity = cosine_similarity(

        [embedding1],

        [embedding2]

    )[0][0]

    return round(
        similarity * 100,
        2
    )


# ---------------------------------------------------
# COMPLETE SEMANTIC MATCH
# ---------------------------------------------------

def calculate_semantic_similarity(

    text1,

    text2

):

    embedding1 = get_embedding(text1)

    embedding2 = get_embedding(text2)

    return calculate_similarity(
        embedding1,
        embedding2
    )
