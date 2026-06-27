from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db

from app.models.paper import Paper
from app.models.patent import Patent
from app.models.document_chunk import DocumentChunk

from app.services.pdf_extractor import extract_text
from app.services.chunker import chunk_text
from app.services.patent_extractor import extract_patent_text

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

    patents = (
        db.query(Patent)
        .filter(Patent.project_id == project_id)
        .all()
    )

    total_chunks = 0

    # 1. Process Papers
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

        try:
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
        except Exception as e:
            print(f"Failed to extract paper {paper.id}: {e}")

    # 2. Process Patents
    for patent in patents:

        existing_chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.patent_id == patent.id
            )
            .count()
        )

        if existing_chunks > 0:
            continue

        try:
            text = extract_patent_text(patent.patent_number)

            if not text:
                print(f"Scraper returned empty for {patent.patent_number}. Falling back to DB abstract.")
                text = f"Title: {patent.title}\nAbstract: {patent.abstract}"

            chunks = chunk_text(text)

            for idx, chunk in enumerate(chunks):

                db_chunk = DocumentChunk(
                    patent_id=patent.id,
                    chunk_index=idx,
                    content=chunk
                )

                db.add(db_chunk)

                total_chunks += 1
        except Exception as e:
            print(f"Failed to extract patent {patent.id}: {e}")

    db.commit()

    return {
        "project_id": str(project_id),
        "papers": len(papers),
        "patents": len(patents),
        "chunks_created": total_chunks
    }