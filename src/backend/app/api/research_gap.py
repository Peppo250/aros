from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.db import get_db

from app.models.fusion_report import (
    FusionReport
)

from app.services.research_gap import (
    generate_gap_analysis
)

router = APIRouter()


@router.post("/")
def generate_gap(
    payload: dict,
    db: Session = Depends(get_db)
):

    fusion_report = (
        db.query(FusionReport)
        .filter(
            FusionReport.project_id ==
            payload["project_id"]
        )
        .order_by(
            FusionReport.created_at.desc()
        )
        .first()
    )

    result = generate_gap_analysis(
        topic=payload["topic"],
        fusion_report=(
            fusion_report.analysis
            if fusion_report
            else None
        )
    )

    return {
        "project_id": payload["project_id"],
        "topic": payload["topic"],
        "analysis": result
    }