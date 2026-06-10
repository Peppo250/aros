from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.orchestrator import start_research_run

router = APIRouter()


@router.post("/start")
def start_research(
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        result = start_research_run(db, topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start orchestrator run: {str(e)}")