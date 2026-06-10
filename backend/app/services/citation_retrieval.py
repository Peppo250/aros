from sqlalchemy.orm import Session
from app.models.citation import CitationRecord

def get_citations(
    db: Session,
    project_id: str
):
    return (
        db.query(CitationRecord)
        .filter(
            CitationRecord.project_id == project_id
        )
        .all()
    )
