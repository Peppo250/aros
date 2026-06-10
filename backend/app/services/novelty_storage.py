from sqlalchemy.orm import Session
from app.models.novelty_report import NoveltyReport

def save_novelty_report(
    db: Session,
    project_id: str,
    topic: str,
    sections: dict,
    model_used: str,
    generation_time_ms: int,
    supporting_evidence: dict,
    full_report: str
):
    report = NoveltyReport(
        project_id=project_id,
        topic=topic,
        
        research_novelty_score=sections.get("research_novelty_score", 0.0),
        implementation_novelty_score=sections.get("implementation_novelty_score", 0.0),
        patent_novelty_score=sections.get("patent_novelty_score", 0.0),
        commercial_novelty_score=sections.get("commercial_novelty_score", 0.0),
        overall_novelty_score=sections.get("overall_novelty_score", 0.0),
        
        research_novelty_analysis=sections.get("research_novelty_analysis"),
        implementation_novelty_analysis=sections.get("implementation_novelty_analysis"),
        patent_novelty_analysis=sections.get("patent_novelty_analysis"),
        commercial_novelty_analysis=sections.get("commercial_novelty_analysis"),
        
        competitive_landscape=sections.get("competitive_landscape"),
        prior_art_risk=sections.get("prior_art_risk"),
        implementation_difficulty=sections.get("implementation_difficulty"),
        publication_potential=sections.get("publication_potential"),
        
        patentability_score=sections.get("patentability_score", 0.0),
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
