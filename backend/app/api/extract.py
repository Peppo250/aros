from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db

from app.models.paper import Paper
from app.models.document_chunk import DocumentChunk

from app.services.pdf_extractor import extract_text
from app.services.chunker import chunk_text

router = APIRouter()

@router.post("/project/{project_id}")
def extract_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):

    papers = (
        db.query(Paper)
        .filter(Paper.project_id == project_id)
        .all()
    )

    if not papers:
        raise HTTPException(
            status_code=404,
            detail="No papers found"
        )

    total_chunks = 0

    for paper in papers:

        if not paper.local_pdf_path:
            continue

        existing_chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.paper_id == paper.id
            )
            .count()
        )

        if existing_chunks > 0:
            continue

        text = extract_text(
            paper.local_pdf_path
        )

        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):

            db_chunk = DocumentChunk(
                paper_id=paper.id,
                chunk_index=idx,
                content=chunk
            )

            db.add(db_chunk)

            total_chunks += 1

    db.commit()

    return {
        "project_id": str(project_id),
        "papers": len(papers),
        "chunks_created": total_chunks
    }