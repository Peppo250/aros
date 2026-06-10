from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.novelty_report import NoveltyReport
from app.services.novelty import generate_novelty_report

router = APIRouter()

@router.post("/project/{project_id}")
def run_novelty(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        report = generate_novelty_report(
            db=db,
            project_id=project_id,
            topic=topic
        )
        return {
            "report_id": str(report.id),
            "project_id": str(report.project_id),
            "topic": report.topic,
            "created_at": report.created_at,
            "scores": {
                "research_novelty_score": report.research_novelty_score,
                "implementation_novelty_score": report.implementation_novelty_score,
                "patent_novelty_score": report.patent_novelty_score,
                "commercial_novelty_score": report.commercial_novelty_score,
                "overall_novelty_score": report.overall_novelty_score,
                "patentability_score": report.patentability_score,
                "confidence_score": report.confidence_score
            },
            "analyses": {
                "research_novelty_analysis": report.research_novelty_analysis,
                "implementation_novelty_analysis": report.implementation_novelty_analysis,
                "patent_novelty_analysis": report.patent_novelty_analysis,
                "commercial_novelty_analysis": report.commercial_novelty_analysis,
                "competitive_landscape": report.competitive_landscape,
                "prior_art_risk": report.prior_art_risk,
                "implementation_difficulty": report.implementation_difficulty,
                "publication_potential": report.publication_potential,
                "recommended_next_steps": report.recommended_next_steps
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
        raise HTTPException(status_code=500, detail=f"Failed to generate Novelty report: {str(e)}")


@router.get("/project/{project_id}")
def get_latest_novelty_report(
    project_id: str,
    db: Session = Depends(get_db)
):
    report = (
        db.query(NoveltyReport)
        .filter(NoveltyReport.project_id == project_id)
        .order_by(NoveltyReport.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No Novelty report found for this project")

    return {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "topic": report.topic,
        "created_at": report.created_at,
        "scores": {
            "research_novelty_score": report.research_novelty_score,
            "implementation_novelty_score": report.implementation_novelty_score,
            "patent_novelty_score": report.patent_novelty_score,
            "commercial_novelty_score": report.commercial_novelty_score,
            "overall_novelty_score": report.overall_novelty_score,
            "patentability_score": report.patentability_score,
            "confidence_score": report.confidence_score
        },
        "analyses": {
            "research_novelty_analysis": report.research_novelty_analysis,
            "implementation_novelty_analysis": report.implementation_novelty_analysis,
            "patent_novelty_analysis": report.patent_novelty_analysis,
            "commercial_novelty_analysis": report.commercial_novelty_analysis,
            "competitive_landscape": report.competitive_landscape,
            "prior_art_risk": report.prior_art_risk,
            "implementation_difficulty": report.implementation_difficulty,
            "publication_potential": report.publication_potential,
            "recommended_next_steps": report.recommended_next_steps
        },
        "supporting_evidence": report.supporting_evidence,
        "metadata": {
            "model_used": report.model_used,
            "generation_time_ms": report.generation_time_ms
        }
    }
