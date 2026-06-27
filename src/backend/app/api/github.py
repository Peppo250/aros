from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database.db import get_db
from app.models.github_repo import GithubRepo
from app.services.github_search import (
    search_github
)

router = APIRouter()

@router.post("/search")
def github_search(
    payload: dict
):

    return search_github(
        payload["topic"]
    )

@router.post("/project/{project_id}")
def collect_repositories(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):

    results = search_github(
        payload["topic"]
    )

    inserted = 0

    for repo in results["items"]:

        row = GithubRepo(
            project_id=project_id,
            repo_name=repo["name"],
            owner=repo["owner"]["login"],
            description=repo.get("description"),
            stars=repo["stargazers_count"],
            language=repo.get("language"),
            html_url=repo["html_url"]
        )

        db.add(row)

        inserted += 1

    db.commit()

    return {
        "inserted": inserted
    }