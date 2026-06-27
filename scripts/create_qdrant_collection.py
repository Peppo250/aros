import os
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

client = QdrantClient(
    host=qdrant_host,
    port=qdrant_port
)

client.recreate_collection(
    collection_name="research_chunks",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)

print("Collection Created")