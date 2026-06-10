from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.report_v1 import ReportV1
from app.services.report_v1 import generate_report_v1

router = APIRouter()

@router.post("/project/{project_id}")
def run_report_v1(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        report = generate_report_v1(
            db=db,
            project_id=project_id,
            topic=topic
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
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Report V1 report: {str(e)}")


@router.get("/project/{project_id}")
def get_latest_report_v1(
    project_id: str,
    db: Session = Depends(get_db)
):
    report = (
        db.query(ReportV1)
        .filter(ReportV1.project_id == project_id)
        .order_by(ReportV1.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No Report V1 report found for this project")

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
