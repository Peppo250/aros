import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.services.embedder import embed

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

client = QdrantClient(
    host=qdrant_host,
    port=qdrant_port
)


def store_chunk(chunk):

    vector = embed(chunk.content)

    client.upsert(
        collection_name="research_chunks",
        points=[
            PointStruct(
                id=str(chunk.id),
                vector=vector,
                payload={
                    "paper_id": str(chunk.paper_id) if chunk.paper_id else None,
                    "patent_id": str(chunk.patent_id) if chunk.patent_id else None,
                    "chunk_id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content
                }
            )
        ]
    )

    return True