from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.research_gap_v2 import ResearchGapReportV2
from app.services.research_gap_v2 import generate_research_gap_v2

router = APIRouter()

@router.post("/project/{project_id}")
def run_research_gap_v2(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        report = generate_research_gap_v2(
            db=db,
            project_id=project_id,
            topic=topic
        )
        return {
            "report_id": str(report.id),
            "project_id": str(report.project_id),
            "topic": report.topic,
            "created_at": report.created_at,
            "sections": {
                "saturated_areas": report.saturated_areas,
                "underexplored_areas": report.underexplored_areas,
                "missing_implementations": report.missing_implementations,
                "missing_datasets": report.missing_datasets,
                "patent_white_spaces": report.patent_white_spaces,
                "emerging_opportunities": report.emerging_opportunities,
                "high_impact_research_directions": report.high_impact_research_directions,
                "ieee_publication_opportunities": report.ieee_publication_opportunities,
                "commercial_opportunities": report.commercial_opportunities,
                "recommended_research_projects": report.recommended_research_projects,
                "executive_summary": report.executive_summary
            },
            "confidence_score": report.confidence_score,
            "metadata": {
                "model_used": report.model_used,
                "generation_time_ms": report.generation_time_ms
            }
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Research Gap V2 report: {str(e)}")


@router.get("/project/{project_id}")
def get_latest_research_gap_report_v2(
    project_id: str,
    db: Session = Depends(get_db)
):
    report = (
        db.query(ResearchGapReportV2)
        .filter(ResearchGapReportV2.project_id == project_id)
        .order_by(ResearchGapReportV2.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No Research Gap V2 report found for this project")

    return {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "topic": report.topic,
        "created_at": report.created_at,
        "sections": {
            "saturated_areas": report.saturated_areas,
            "underexplored_areas": report.underexplored_areas,
            "missing_implementations": report.missing_implementations,
            "missing_datasets": report.missing_datasets,
            "patent_white_spaces": report.patent_white_spaces,
            "emerging_opportunities": report.emerging_opportunities,
            "high_impact_research_directions": report.high_impact_research_directions,
            "ieee_publication_opportunities": report.ieee_publication_opportunities,
            "commercial_opportunities": report.commercial_opportunities,
            "recommended_research_projects": report.recommended_research_projects,
            "executive_summary": report.executive_summary
        },
        "confidence_score": report.confidence_score,
        "metadata": {
            "model_used": report.model_used,
            "generation_time_ms": report.generation_time_ms
        }
    }
