from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.paper import Paper
from app.schemas.paper import PaperCreate
from app.schemas.paper_bulk import (
    PaperBulkCreate,
    PaperItem
)

router = APIRouter()


@router.post("/")
def create_paper(
    paper: PaperCreate,
    db: Session = Depends(get_db)
):

    new_paper = Paper(
        project_id=paper.project_id,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        pdf_url=paper.pdf_url,
        source=paper.source,
        year=paper.year
    )

    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    return {
        "id": str(new_paper.id)
    }


@router.post("/bulk")
def create_papers_bulk(
    payload: PaperBulkCreate,
    db: Session = Depends(get_db)
):
    created = 0
    skipped = 0

    for paper in payload.papers:

        existing = (
            db.query(Paper)
            .filter(
                Paper.project_id == payload.project_id,
                Paper.pdf_url == paper.pdf_url
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        new_paper = Paper(
            project_id=payload.project_id,
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            pdf_url=paper.pdf_url,
            source=paper.source,
            year=paper.year
        )

        db.add(new_paper)

        created += 1

    db.commit()

    return {
        "inserted": created,
        "skipped": skipped
    }

@router.get("/")
def get_all_papers(
    db: Session = Depends(get_db)
):
    return db.query(Paper).all()