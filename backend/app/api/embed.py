from uuid import UUID
import time

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db

from app.models.paper import Paper
from app.models.document_chunk import DocumentChunk

from app.services.qdrant_embedder import store_chunk

router = APIRouter()


@router.post("/project/{project_id}")
def embed_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):

    chunks = (
        db.query(DocumentChunk)
        .join(
            Paper,
            DocumentChunk.paper_id == Paper.id
        )
        .filter(
            Paper.project_id == project_id,
            DocumentChunk.embedded == False
        )
        .all()
    )

    if not chunks:
        return {
            "project_id": str(project_id),
            "embedded": 0,
            "failed": 0,
            "seconds": 0,
            "message": "No new chunks to embed"
        }
    import uuid
    print(
    f"Project {project_id} has {len(chunks)} chunks"
)
    job_id = str(uuid.uuid4())[:8]

    print(
        f"START JOB {job_id}"
    )
    start = time.time()

    count = 0
    failed = 0

    for chunk in chunks:

        try:
            store_chunk(chunk)
            count += 1
            setattr(
    chunk,
    "embedded",
    True
)
            if count % 100 == 0:
                print(f"Embedded {count} chunks")

        except Exception as e:
            failed += 1
            print(
                f"Failed chunk {chunk.id}: {e}"
            )

    elapsed = round(
        time.time() - start,
        2
    )

    return {
        "project_id": str(project_id),
        "embedded": count,
        "failed": failed,
        "seconds": elapsed
    }