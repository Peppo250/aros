from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.research_run import ResearchRun
from app.schemas.research_run import (
    ResearchRunCreate,
    ResearchRunUpdate
)

router = APIRouter()

@router.post("/")
def create_run(
    payload: ResearchRunCreate,
    db: Session = Depends(get_db)
):

    run = ResearchRun(
        project_id=payload.project_id,
        status="queued"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run

PROGRESS_MAP = {
    "queued": 0,
    "papers_completed": 10,
    "github_completed": 20,
    "patents_completed": 30,
    "datasets_completed": 40,
    "trends_completed": 50,
    "citations_completed": 60,
    "graph_completed": 70,
    "fusion_completed": 80,
    "gap_completed": 85,
    "novelty_completed": 90,
    "patent_completed": 95,
    "report_completed": 99,
    "completed": 100,
    "failed": 0
}

@router.get("/{run_id}")
def get_run_progress(
    run_id: UUID,
    db: Session = Depends(get_db)
):
    run = (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    progress = PROGRESS_MAP.get(run.status, 0)

    return {
        "run_id": str(run.id),
        "status": run.status,
        "progress": progress
    }

@router.get("/{run_id}/result")
def get_run_result(
    run_id: UUID,
    db: Session = Depends(get_db)
):
    from app.models.report_v1 import ReportV1
    
    run = (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    report = (
        db.query(ReportV1)
        .filter(ReportV1.project_id == run.project_id)
        .order_by(ReportV1.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report dossier result not found for this research run"
        )

    return {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "topic": report.topic,
        "created_at": report.created_at,
        "confidence_score": report.confidence_score,
        "sections": {
            "executive_summary": report.executive_summary,
            "research_landscape": report.research_landscape,
            "research_gaps": report.research_gaps,
            "novelty_assessment": report.novelty_assessment,
            "patent_opportunities": report.patent_opportunities,
            "ieee_publication_plan": report.ieee_publication_plan,
            "patent_filing_plan": report.patent_filing_plan,
            "commercialization_strategy": report.commercialization_strategy,
            "research_roadmap": report.research_roadmap,
            "next_actions": report.next_actions
        },
        "supporting_evidence": report.supporting_evidence,
        "metadata": {
            "model_used": report.model_used,
            "generation_time_ms": report.generation_time_ms
        }
    }

@router.patch("/{run_id}")
def update_run(
    run_id: UUID,
    payload: ResearchRunUpdate,
    db: Session = Depends(get_db)
):
    run = (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    run.status = payload.status
    db.commit()

    return run

