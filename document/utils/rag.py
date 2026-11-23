import re
import ollama
from .v_db import search_documents

# Check `ollama list` for your exact tag (e.g., "qwen3:8b")
QWEN_MODEL = "qwen3:8b"


def quest(question: str, file_id: int, top_k: int = 3) -> dict:
    # 1. Retrieve relevant chunks from ChromaDB for this specific file_id
    matches = search_documents(query=question, top_k=top_k, file_id=file_id)

    if not matches:
        return {
            "answer": "No relevant content was found in this document.",
            "sources": [],
        }

    # 2. Combine retrieved chunk texts into context
    context_text = "\n\n---\n\n".join(
        f"[Chunk {m['metadata'].get('chunk_id')}]: {m['text']}" for m in matches
    )

    # 3. Build a grounded RAG prompt
    system_prompt = (
        "You are a helpful document assistant. Answer the user's question using ONLY "
        "the provided context. If the answer is not in the context, reply with "
        "'I could not find that information in the document.' Do not guess or make up facts."
    )

    user_prompt = f"""Context:
{context_text}

Question:
{question}"""

    # 4. Call local Qwen 8B (think=False gives fast, direct answers without <think> blocks)
    response = ollama.chat(
        model=QWEN_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        think=False,
        options={"temperature": 0.1},
    )

    raw_answer = response["message"]["content"]
    # Strip any <think>...</think> block if present
    clean_answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()

    return {
        "answer": clean_answer,
        "sources": matches,
    }
