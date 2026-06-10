import os
import requests
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.research_run import ResearchRun

def start_research_run(db: Session, topic: str) -> dict:
    # 1. Create Project
    project = Project(
        title=topic,
        topic=topic,
        status="created"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 2. Create Research Run
    run = ResearchRun(
        project_id=project.id,
        status="queued"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # 3. Trigger n8n webhook
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/research")
    
    payload = {
        "project_id": str(project.id),
        "run_id": str(run.id),
        "topic": topic
    }
    
    try:
        requests.post(
            webhook_url,
            json=payload,
            timeout=5
        )
    except Exception as e:
        print(f"Failed to trigger n8n webhook: {e}")

    return {
        "run_id": str(run.id),
        "project_id": str(project.id),
        "status": run.status
    }
