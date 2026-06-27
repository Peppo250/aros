from sqlalchemy.orm import Session
from app.models.patent_opportunity import PatentOpportunity

def save_patent_opportunity(
    db: Session,
    project_id: str,
    topic: str,
    sections: dict,
    model_used: str,
    generation_time_ms: int,
    supporting_evidence: dict,
    full_report: str
):
    report = PatentOpportunity(
        project_id=project_id,
        topic=topic,
        
        opportunity_score=sections.get("opportunity_score", 0.0),
        patentability_score=sections.get("patentability_score", 0.0),
        prior_art_risk_score=sections.get("prior_art_risk_score", 0.0),
        commercial_value_score=sections.get("commercial_value_score", 0.0),
        
        white_space_analysis=sections.get("white_space_analysis"),
        closest_prior_art=sections.get("closest_prior_art"),
        independent_claim_draft=sections.get("independent_claim_draft"),
        dependent_claims_draft=sections.get("dependent_claims_draft"),
        novel_technical_contributions=sections.get("novel_technical_contributions"),
        commercial_value_analysis=sections.get("commercial_value_analysis"),
        filing_strategy=sections.get("filing_strategy"),
        recommended_jurisdictions=sections.get("recommended_jurisdictions"),
        recommended_next_steps=sections.get("recommended_next_steps"),
        
        confidence_score=sections.get("confidence_score", 0.0),
        
        model_used=model_used,
        generation_time_ms=generation_time_ms,
        supporting_evidence=supporting_evidence,
        full_report=full_report
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
