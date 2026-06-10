from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.patent_opportunity import PatentOpportunity
from app.services.patent_opportunity import generate_patent_opportunity

router = APIRouter()

@router.post("/project/{project_id}")
def run_patent_opportunity(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        report = generate_patent_opportunity(
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
                "opportunity_score": report.opportunity_score,
                "patentability_score": report.patentability_score,
                "prior_art_risk_score": report.prior_art_risk_score,
                "commercial_value_score": report.commercial_value_score,
                "confidence_score": report.confidence_score
            },
            "sections": {
                "white_space_analysis": report.white_space_analysis,
                "closest_prior_art": report.closest_prior_art,
                "independent_claim_draft": report.independent_claim_draft,
                "dependent_claims_draft": report.dependent_claims_draft,
                "novel_technical_contributions": report.novel_technical_contributions,
                "commercial_value_analysis": report.commercial_value_analysis,
                "filing_strategy": report.filing_strategy,
                "recommended_jurisdictions": report.recommended_jurisdictions,
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
        raise HTTPException(status_code=500, detail=f"Failed to generate Patent Opportunity report: {str(e)}")


@router.get("/project/{project_id}")
def get_latest_patent_opportunity(
    project_id: str,
    db: Session = Depends(get_db)
):
    report = (
        db.query(PatentOpportunity)
        .filter(PatentOpportunity.project_id == project_id)
        .order_by(PatentOpportunity.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No Patent Opportunity report found for this project")

    return {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "topic": report.topic,
        "created_at": report.created_at,
        "scores": {
            "opportunity_score": report.opportunity_score,
            "patentability_score": report.patentability_score,
            "prior_art_risk_score": report.prior_art_risk_score,
            "commercial_value_score": report.commercial_value_score,
            "confidence_score": report.confidence_score
        },
        "sections": {
            "white_space_analysis": report.white_space_analysis,
            "closest_prior_art": report.closest_prior_art,
            "independent_claim_draft": report.independent_claim_draft,
            "dependent_claims_draft": report.dependent_claims_draft,
            "novel_technical_contributions": report.novel_technical_contributions,
            "commercial_value_analysis": report.commercial_value_analysis,
            "filing_strategy": report.filing_strategy,
            "recommended_jurisdictions": report.recommended_jurisdictions,
            "recommended_next_steps": report.recommended_next_steps
        },
        "supporting_evidence": report.supporting_evidence,
        "metadata": {
            "model_used": report.model_used,
            "generation_time_ms": report.generation_time_ms
        }
    }
