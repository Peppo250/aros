from qdrant_client import QdrantClient

from app.services.embedder import embed

client = QdrantClient(
    host="localhost",
    port=6333
)


def retrieve(
    query: str,
    limit: int = 10
):

    query_vector = embed(query)

    results = client.query_points(
        collection_name="research_chunks",
        query=query_vector,
        limit=limit
    )

    return results.points