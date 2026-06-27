from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.db import get_db

from app.services.github_retrieval import (
    get_repositories
)
from app.services.fusion_storage import (
    save_fusion_report
)
from app.models.fusion_report import (
    FusionReport
)
from app.services.fusion import (
    fuse_knowledge
)

router = APIRouter()

@router.post("/project/{project_id}")
def fusion(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):

    repos = get_repositories(
        db,
        project_id
    )

    result = fuse_knowledge(
        payload["topic"],
        repos
    )

    report = save_fusion_report(
        db=db,
        project_id=project_id,
        topic=payload["topic"],
        analysis=result
    )

    return {
        "report_id": str(report.id),
        "analysis": result
    }

@router.get("/project/{project_id}")
def get_latest_fusion_report(
    project_id: str,
    db: Session = Depends(get_db)
):

    report = (
        db.query(FusionReport)
        .filter(
            FusionReport.project_id == project_id
        )
        .order_by(
            FusionReport.created_at.desc()
        )
        .first()
    )

    if not report:
        return {
            "message": "No fusion report found."
        }

    return {
        "id": str(report.id),
        "topic": report.topic,
        "analysis": report.analysis,
        "created_at": report.created_at
    }