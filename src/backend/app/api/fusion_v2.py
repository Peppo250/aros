from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.fusion_report_v2 import FusionReportV2
from app.services.fusion_v2 import generate_fusion_report_v2

router = APIRouter()

@router.post("/project/{project_id}")
def run_fusion_v2(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Missing required 'topic' field in payload")
        
    try:
        report = generate_fusion_report_v2(
            db=db,
            project_id=project_id,
            topic=topic
        )
        return {
            "report_id": str(report.id),
            "project_id": str(report.project_id),
            "topic": report.topic,
            "created_at": report.created_at,
            "counts": {
                "papers_count": report.papers_count,
                "repositories_count": report.repositories_count,
                "patents_count": report.patents_count,
                "datasets_count": report.datasets_count,
                "trends_count": report.trends_count,
                "citations_count": report.citations_count,
                "graph_nodes_count": report.graph_nodes_count,
                "graph_relationships_count": report.graph_relationships_count
            },
            "sections": {
                "research_landscape": report.research_landscape,
                "influential_work": report.influential_work,
                "implementations": report.implementations,
                "patent_activity": report.patent_activity,
                "datasets": report.datasets,
                "emerging_trends": report.emerging_trends,
                "knowledge_graph_insights": report.knowledge_graph_insights,
                "consensus_findings": report.consensus_findings,
                "contradictions": report.contradictions,
                "research_opportunities": report.research_opportunities,
                "executive_summary": report.executive_summary
            },
            "supporting_evidence": report.supporting_evidence,
            "metadata": {
                "model_used": report.model_used,
                "generation_time_ms": report.generation_time_ms,
                "context_length": report.context_length,
                "retrieval_metadata": report.retrieval_metadata,
                "confidence": report.confidence
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Fusion V2 report: {str(e)}")


@router.get("/project/{project_id}")
def get_latest_fusion_report_v2(
    project_id: str,
    db: Session = Depends(get_db)
):
    report = (
        db.query(FusionReportV2)
        .filter(FusionReportV2.project_id == project_id)
        .order_by(FusionReportV2.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="No Fusion V2 report found for this project")

    return {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "topic": report.topic,
        "created_at": report.created_at,
        "counts": {
            "papers_count": report.papers_count,
            "repositories_count": report.repositories_count,
            "patents_count": report.patents_count,
            "datasets_count": report.datasets_count,
            "trends_count": report.trends_count,
            "citations_count": report.citations_count,
            "graph_nodes_count": report.graph_nodes_count,
            "graph_relationships_count": report.graph_relationships_count
        },
        "sections": {
            "research_landscape": report.research_landscape,
            "influential_work": report.influential_work,
            "implementations": report.implementations,
            "patent_activity": report.patent_activity,
            "datasets": report.datasets,
            "emerging_trends": report.emerging_trends,
            "knowledge_graph_insights": report.knowledge_graph_insights,
            "consensus_findings": report.consensus_findings,
            "contradictions": report.contradictions,
            "research_opportunities": report.research_opportunities,
            "executive_summary": report.executive_summary
        },
        "supporting_evidence": report.supporting_evidence,
        "metadata": {
            "model_used": report.model_used,
            "generation_time_ms": report.generation_time_ms,
            "context_length": report.context_length,
            "retrieval_metadata": report.retrieval_metadata,
            "confidence": report.confidence
        }
    }
