from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.services.graph_builder import build_graph, Neo4jClient

router = APIRouter()


@router.post("/project/{project_id}")
def run_graph_build(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Build or rebuild the knowledge graph for a project by merging entity nodes and relationships.
    
    Returns:
    - **papers**: Number of papers processed
    - **repositories**: Number of repositories processed
    - **patents**: Number of patents processed
    - **datasets**: Number of datasets processed
    - **trends**: Number of trend signals processed
    - **nodes_processed**: Total number of nodes processed in Neo4j
    - **relationships_processed**: Total number of relationships processed in Neo4j
    """
    counts = build_graph(db, str(project_id))
    return counts


@router.get("/project/{project_id}")
def get_graph_summary(
    project_id: UUID
):
    client = Neo4jClient()
    summary = client.get_summary(str(project_id))
    client.close()
    return summary


@router.get("/health")
def get_graph_health():
    client = Neo4jClient()
    health = client.check_health()
    client.close()
    return health
