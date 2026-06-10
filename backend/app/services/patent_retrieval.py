from sqlalchemy.orm import Session
from app.models.patent import Patent

def get_patents(
    db: Session,
    project_id: str
):
    return (
        db.query(Patent)
        .filter(
            Patent.project_id == project_id
        )
        .all()
    )
