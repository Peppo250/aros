from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.citation import CitationRecord
from app.services.citation_search import search_citations
from app.services.citation_retrieval import get_citations

router = APIRouter()


@router.post("/project/{project_id}")
def collect_citations(
    project_id: UUID,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    results = search_citations(topic)

    inserted = 0

    for item in results:
        title = item.get("paper_title")
        if not title:
            continue

        # Prevent duplicate inserts for the same project & paper title
        existing = (
            db.query(CitationRecord)
            .filter(
                CitationRecord.project_id == project_id,
                CitationRecord.paper_title == title
            )
            .first()
        )

        if existing:
            continue

        row = CitationRecord(
            project_id=project_id,
            topic=topic,
            paper_title=title,
            authors=item.get("authors"),
            authors_json=item.get("authors_json"),
            year=item.get("year"),
            citation_count=item.get("citation_count"),
            influential_citation_count=item.get("influential_citation_count"),
            source=item.get("source"),
            url=item.get("url"),
            raw_data=item.get("raw_data")
        )

        db.add(row)
        inserted += 1

    db.commit()

    return {
        "inserted": inserted
    }


@router.get("/project/{project_id}")
def retrieve_citations(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    return get_citations(db, str(project_id))
