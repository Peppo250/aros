import ollama

from app.services.retriever import retrieve


def generate_gap_analysis(
    topic: str,
    fusion_report: str | None = None,
    model: str = "qwen3:8b"
):

    chunks = retrieve(
        query=topic,
        limit=15
    )

    context = ""

    for chunk in chunks:

        if not chunk.payload:
            continue

        content = chunk.payload.get(
            "content",
            ""
        )

        context += (
            content[:800]
            + "\n\n"
        )

    fusion_section = ""

    if fusion_report:

        fusion_section = f"""
FUSION ANALYSIS:

{fusion_report}
"""

    prompt = f"""
You are a senior research strategist.

Analyze the supplied research literature and fusion report.

Your task is to identify:

1. Major research themes
2. Key limitations
3. Open challenges
4. Research gaps
5. Novel research opportunities
6. Potential IEEE publication directions
7. Potential patent opportunities

Return a structured report.

LITERATURE CONTEXT:

{context}

{fusion_section}

TOPIC:

{topic}
"""

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]