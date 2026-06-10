from sqlalchemy.orm import Session
from app.models.trend import TrendSignal

def get_trends(
    db: Session,
    project_id: str
):
    return (
        db.query(TrendSignal)
        .filter(
            TrendSignal.project_id == project_id
        )
        .all()
    )
