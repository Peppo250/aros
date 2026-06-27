from sqlalchemy.orm import Session

from app.models.github_repo import GithubRepo


def get_repositories(
    db: Session,
    project_id: str
):

    return (
        db.query(GithubRepo)
        .filter(
            GithubRepo.project_id == project_id
        )
        .all()
    )