from sqlalchemy.orm import Session
from app.models.report_v1 import ReportV1

def save_report_v1(
    db: Session,
    project_id: str,
    topic: str,
    sections: dict,
    model_used: str,
    generation_time_ms: int,
    supporting_evidence: dict,
    full_report: str
):
    report = ReportV1(
        project_id=project_id,
        topic=topic,
        
        executive_summary=sections.get("executive_summary"),
        research_landscape=sections.get("research_landscape"),
        research_gaps=sections.get("research_gaps"),
        novelty_assessment=sections.get("novelty_assessment"),
        patent_opportunities=sections.get("patent_opportunities"),
        ieee_publication_plan=sections.get("ieee_publication_plan"),
        patent_filing_plan=sections.get("patent_filing_plan"),
        commercialization_strategy=sections.get("commercialization_strategy"),
        research_roadmap=sections.get("research_roadmap"),
        next_actions=sections.get("next_actions"),
        
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
