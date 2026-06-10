from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.services.embedder import embed


client = QdrantClient(
    host="localhost",
    port=6333
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
                    "paper_id": str(chunk.paper_id),
                    "chunk_id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content
                }
            )
        ]
    )

    return True