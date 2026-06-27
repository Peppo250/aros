from sqlalchemy.orm import Session

from app.models.fusion_report import (
    FusionReport
)


def save_fusion_report(
    db: Session,
    project_id: str,
    topic: str,
    analysis: str
):

    report = FusionReport(
        project_id=project_id,
        topic=topic,
        analysis=analysis
    )

    db.add(report)

    db.commit()

    db.refresh(report)

    return report