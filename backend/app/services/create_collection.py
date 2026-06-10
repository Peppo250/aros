from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)

client = QdrantClient(
    host="localhost",
    port=6333
)

client.recreate_collection(
    collection_name="research_chunks",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)

print("Collection Created")