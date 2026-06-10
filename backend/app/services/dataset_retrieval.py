from sqlalchemy.orm import Session
from app.models.dataset import Dataset

def get_datasets(
    db: Session,
    project_id: str
):
    return (
        db.query(Dataset)
        .filter(
            Dataset.project_id == project_id
        )
        .all()
    )
