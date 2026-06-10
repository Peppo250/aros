import requests

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.research_run import ResearchRun

router = APIRouter()


@router.post("/start")
def start_research(
    payload: dict,
    db: Session = Depends(get_db)
):

    project_id = payload["project_id"]
    topic = payload["topic"]

    run = ResearchRun(
        project_id=project_id,
        status="queued"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    webhook_url = "http://localhost:5678/webhook-test/research"

    requests.post(
        webhook_url,
        json={
            "run_id": str(run.id),
            "project_id": project_id,
            "topic": topic
        }
    )

    return {
        "run_id": str(run.id),
        "status": run.status
    }