from pathlib import Path
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.paper import Paper
from app.services.pdf_downloader import download_pdf

router = APIRouter()

@router.post("/project/{project_id}")
def download_project_pdfs(
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

    base_dir = Path(f"data/pdfs/{project_id}")
    base_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = 0

    for paper in papers:

        try:

            filename = f"{paper.id}.pdf"

            destination = base_dir / filename

            if destination.exists():

                paper.local_pdf_path = str(destination)

                continue

            download_pdf(
                paper.pdf_url,
                str(destination)
            )

            paper.local_pdf_path = str(destination)

            downloaded += 1

        except Exception:
            failed += 1

    db.commit()

    return {
        "project_id": str(project_id),
        "downloaded": downloaded,
        "failed": failed
    }