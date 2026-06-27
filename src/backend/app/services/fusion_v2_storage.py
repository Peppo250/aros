from sqlalchemy.orm import Session
from app.models.fusion_report_v2 import FusionReportV2

def save_fusion_report_v2(
    db: Session,
    project_id: str,
    topic: str,
    sections: dict,
    counts: dict,
    supporting_evidence: dict,
    full_report: str,
    model_used: str = None,
    generation_time_ms: int = None,
    context_length: int = None,
    retrieval_metadata: dict = None,
    confidence: float = None
):
    report = FusionReportV2(
        project_id=project_id,
        topic=topic,
        
        research_landscape=sections.get("research_landscape"),
        influential_work=sections.get("influential_work"),
        implementations=sections.get("implementations"),
        patent_activity=sections.get("patent_activity"),
        datasets=sections.get("datasets"),
        emerging_trends=sections.get("emerging_trends"),
        knowledge_graph_insights=sections.get("knowledge_graph_insights"),
        consensus_findings=sections.get("consensus_findings"),
        contradictions=sections.get("contradictions"),
        research_opportunities=sections.get("research_opportunities"),
        executive_summary=sections.get("executive_summary"),
        
        full_report=full_report,
        
        papers_count=counts.get("papers_count", 0),
        repositories_count=counts.get("repositories_count", 0),
        patents_count=counts.get("patents_count", 0),
        datasets_count=counts.get("datasets_count", 0),
        trends_count=counts.get("trends_count", 0),
        citations_count=counts.get("citations_count", 0),
        graph_nodes_count=counts.get("graph_nodes_count", 0),
        graph_relationships_count=counts.get("graph_relationships_count", 0),
        
        supporting_evidence=supporting_evidence,

        model_used=model_used,
        generation_time_ms=generation_time_ms,
        context_length=context_length,
        retrieval_metadata=retrieval_metadata,
        confidence=confidence
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
