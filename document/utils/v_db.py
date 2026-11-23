import chromadb
from .embedding import embed_query

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_documents")

def save_chunks(file_id: int, user_id: int, filename: str, embedded_chunks: list[dict]) -> None:
    if not embedded_chunks:
        return

    collection.upsert(
        ids=[f"file_{file_id}_chunk_{c['chunk_id']}" for c in embedded_chunks],
        embeddings=[c["embedding"] for c in embedded_chunks],
        documents=[c["text"] for c in embedded_chunks],
        metadatas=[
            {
                "file_id": int(file_id),
                "user_id": int(user_id),
                "filename": filename,
                "chunk_id": c["chunk_id"],
            }
            for c in embedded_chunks
        ],
    )

def search_documents(query: str, top_k: int = 3, file_id: int | None = None) -> list[dict]:
    query_vector = embed_query(query)
    where_filter = {"file_id": int(file_id)} if file_id is not None else None

    results = collection.query(
        query_embeddings=query_vector,
        n_results=top_k,
        where=where_filter,
    )

    matches = []
    docs = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx in range(len(docs)):
        matches.append({
            "id": ids[idx],
            "text": docs[idx],
            "metadata": metadatas[idx],
            "distance": distances[idx],
        })

    return matches


