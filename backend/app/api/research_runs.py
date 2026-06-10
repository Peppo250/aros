from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.research_run import ResearchRun
from app.schemas.research_run import (
    ResearchRunCreate,
    ResearchRunUpdate
)

router = APIRouter()

@router.post("/")
def create_run(
    payload: ResearchRunCreate,
    db: Session = Depends(get_db)
):

    run = ResearchRun(
        project_id=payload.project_id,
        status="queued"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run

@router.get("/{run_id}")
def get_run(
    run_id: UUID,
    db: Session = Depends(get_db)
):

    run = (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return run

@router.patch("/{run_id}")
def update_run(
    run_id: UUID,
    payload: ResearchRunUpdate,
    db: Session = Depends(get_db)
):

    run = (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    run.status = payload.status

    db.commit()

    return run

