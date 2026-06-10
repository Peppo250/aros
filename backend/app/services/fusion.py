import ollama

from app.services.retriever import retrieve
def fuse_knowledge(
    topic,
    repositories,
    model="qwen3:8b"
):

    chunks = retrieve(
        topic,
        limit=10
    )

    paper_context = ""

    for chunk in chunks:

        if chunk.payload:
            paper_context += (
                chunk.payload["content"][:500]
                + "\n\n"
            )

    github_context = ""

    for repo in repositories:

        github_context += (
            f"Repo: {repo.repo_name}\n"
            f"Description: {repo.description}\n"
            f"Stars: {repo.stars}\n\n"
        )

    prompt = f"""
You are a research strategist.

Research Literature:

{paper_context}

GitHub Implementations:

{github_context}

Analyze:

1. What areas are well researched?
2. What areas are well implemented?
3. What research lacks implementations?
4. What implementations lack research?
5. What opportunities exist?

Return a structured report.
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

