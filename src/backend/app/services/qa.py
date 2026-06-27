import re
import ollama

from app.services.retriever import retrieve


def answer_question(
    question: str,
    top_k: int = 10,
    model: str = "qwen3:8b"
):

    # Retrieve relevant chunks
    results = retrieve(
        query=question,
        limit=top_k
    )

    # Deduplicate chunks
    unique_chunks = []
    seen_content = set()

    for result in results:

        if not result.payload:
            continue

        content = result.payload.get("content")

        if not content:
            continue

        if content in seen_content:
            continue

        seen_content.add(content)
        unique_chunks.append(result)

    # Build context with size limit
    MAX_CONTEXT_CHARS = 4000

    context_parts = []
    current_size = 0

    for chunk in unique_chunks:

        content = chunk.payload.get(
            "content",
            ""
        )

        if not content:
            continue

        if current_size + len(content) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(content)

        current_size += len(content)

    context = "\n\n".join(context_parts)

    # Remove problematic control characters
    context = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
        "",
        context
    )

    if not context:

        return {
            "question": question,
            "answer": "No relevant context found.",
            "sources_used": 0,
            "retrieved_chunks": []
        }

    prompt = f"""
You are a senior research assistant.

Answer ONLY using the supplied context.

Rules:
- Do not invent facts.
- If information is missing, say so.
- Be concise and accurate.
- Cite findings from the context when possible.

CONTEXT:

{context}

QUESTION:

{question}
"""

    print("=" * 60)
    print("Question:", question)
    print("Unique Chunks:", len(unique_chunks))
    print("Context Length:", len(context))
    print("Prompt Length:", len(prompt))
    print("=" * 60)

    try:

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

    except Exception as e:

        return {
            "question": question,
            "error": str(e),
            "sources_used": len(unique_chunks)
        }

    return {
        "question": question,
        "answer": answer,
        "sources_used": len(unique_chunks),
        "retrieved_chunks": [
            {
                "paper_id": chunk.payload.get("paper_id"),
                "chunk_id": chunk.payload.get("chunk_id"),
                "chunk_index": chunk.payload.get("chunk_index"),
                "score": getattr(chunk, "score", None)
            }
            for chunk in unique_chunks
        ]
    }