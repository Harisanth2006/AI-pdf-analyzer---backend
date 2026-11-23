# document/utils.py
from sentence_transformers import SentenceTransformer

# Loads a fast, lightweight 384-dimension embedding model once at startup
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(chunks: list[dict]) -> list[dict]:
    texts = [item["text"] for item in chunks]
    # Convert numpy arrays to standard Python lists so JSON serialization works
    vectors = embedding_model.encode(texts).tolist()

    for item, vector in zip(chunks, vectors):
        item["embedding"] = vector

    return chunks

def embed_query(query: str) -> list[list[float]]:
    return embedding_model.encode([query]).tolist()
