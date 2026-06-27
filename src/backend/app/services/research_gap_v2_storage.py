from sqlalchemy.orm import Session
from app.models.research_gap_v2 import ResearchGapReportV2

def save_research_gap_report_v2(
    db: Session,
    project_id: str,
    topic: str,
    sections: dict,
    confidence_score: float,
    model_used: str,
    generation_time_ms: int,
    full_report: str
):
    report = ResearchGapReportV2(
        project_id=project_id,
        topic=topic,
        
        saturated_areas=sections.get("saturated_areas"),
        underexplored_areas=sections.get("underexplored_areas"),
        missing_implementations=sections.get("missing_implementations"),
        missing_datasets=sections.get("missing_datasets"),
        patent_white_spaces=sections.get("patent_white_spaces"),
        emerging_opportunities=sections.get("emerging_opportunities"),
        high_impact_research_directions=sections.get("high_impact_research_directions"),
        ieee_publication_opportunities=sections.get("ieee_publication_opportunities"),
        commercial_opportunities=sections.get("commercial_opportunities"),
        recommended_research_projects=sections.get("recommended_research_projects"),
        executive_summary=sections.get("executive_summary"),
        
        confidence_score=confidence_score,
        model_used=model_used,
        generation_time_ms=generation_time_ms,
        full_report=full_report
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
