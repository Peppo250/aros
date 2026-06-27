import os
from qdrant_client import QdrantClient

from app.services.embedder import embed

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

client = QdrantClient(
    host=qdrant_host,
    port=qdrant_port
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