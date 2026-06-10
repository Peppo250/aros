import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.fusion_report_v2 import FusionReportV2

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

def verify_fusion_v2_api():
    print(f"Project ID used for verification: {project_id}")
    print("=" * 60)

    # 1. POST request to generate the report
    payload = {"topic": "edge ai mesh"}
    print("POST: Requesting Fusion V2 generation...")
    resp = client.post(f"/fusion-v2/project/{project_id}", json=payload)
    
    print(f"POST Response status: {resp.status_code}")
    assert resp.status_code == 200, f"Failed generation: {resp.text}"
    
    data = resp.json()
    print("Generation successful!")
    print(f"Report ID: {data.get('report_id')}")
    print(f"Topic: {data.get('topic')}")
    
    # 2. Check counts
    counts = data.get("counts", {})
    print("Source Counts:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
        
    assert counts.get("papers_count") is not None, "Missing papers_count"
    assert counts.get("repositories_count") is not None, "Missing repositories_count"
    assert counts.get("patents_count") is not None, "Missing patents_count"
    assert counts.get("datasets_count") is not None, "Missing datasets_count"
    assert counts.get("trends_count") is not None, "Missing trends_count"
    assert counts.get("citations_count") is not None, "Missing citations_count"
    assert counts.get("graph_nodes_count") is not None, "Missing graph_nodes_count"
    assert counts.get("graph_relationships_count") is not None, "Missing graph_relationships_count"

    # 3. Check sections
    sections = data.get("sections", {})
    print("\nGenerated Sections (length of text):")
    for k, v in sections.items():
        print(f"  {k}: {len(v) if v else 0} chars")
        
    for k in [
        "research_landscape", "influential_work", "implementations",
        "patent_activity", "datasets", "emerging_trends",
        "knowledge_graph_insights", "consensus_findings", "contradictions",
        "research_opportunities", "executive_summary"
    ]:
        assert k in sections, f"Section {k} missing from response"

    # 4. Check supporting evidence
    evidence = data.get("supporting_evidence", {})
    print("\nSupporting Evidence lists:")
    for k, v in evidence.items():
        print(f"  {k}: {len(v)} items")
        
    assert "top_papers" in evidence, "Missing top_papers in evidence"
    assert "top_repositories" in evidence, "Missing top_repositories in evidence"
    assert "top_cited_papers" in evidence, "Missing top_cited_papers in evidence"
    assert "top_patents" in evidence, "Missing top_patents in evidence"
    assert "top_datasets" in evidence, "Missing top_datasets in evidence"
    assert "top_trends" in evidence, "Missing top_trends in evidence"

    # 4.5. Check metadata
    metadata = data.get("metadata", {})
    print("\nGeneration & Retrieval Metadata:")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    
    assert metadata.get("model_used") in ["qwen3:14b", "qwen3:8b"], f"Unexpected model used: {metadata.get('model_used')}"
    assert isinstance(metadata.get("generation_time_ms"), int) and metadata.get("generation_time_ms") > 0, "Invalid generation_time_ms"
    assert isinstance(metadata.get("context_length"), int) and metadata.get("context_length") > 0, "Invalid context_length"
    
    confidence = metadata.get("confidence")
    assert isinstance(confidence, float) and 0.0 <= confidence <= 1.0, f"Invalid confidence score: {confidence}"
    
    ret_meta = metadata.get("retrieval_metadata", {})
    assert "papers_count" in ret_meta, "retrieval_metadata missing papers_count"
    assert "repositories_count" in ret_meta, "retrieval_metadata missing repositories_count"
    assert "patents_count" in ret_meta, "retrieval_metadata missing patents_count"
    assert "datasets_count" in ret_meta, "retrieval_metadata missing datasets_count"
    assert "trends_count" in ret_meta, "retrieval_metadata missing trends_count"
    assert "citations_count" in ret_meta, "retrieval_metadata missing citations_count"

    # 5. GET request to verify retrieval of latest report
    print("\nGET: Retrieving latest Fusion V2 report...")
    get_resp = client.get(f"/fusion-v2/project/{project_id}")
    assert get_resp.status_code == 200, f"Failed retrieval: {get_resp.text}"
    get_data = get_resp.json()
    
    assert get_data.get("report_id") == data.get("report_id"), "GET retrieved ID does not match POST generated ID"
    assert get_data.get("metadata", {}).get("confidence") == confidence, "GET confidence does not match POST confidence"
    print("Latest report retrieved matches generated report successfully!")
    print("=" * 60)

    # 6. Database direct query verification
    print("Database Query Verification:")
    db = SessionLocal()
    try:
        db_report = db.query(FusionReportV2).filter(FusionReportV2.id == data.get("report_id")).first()
        assert db_report is not None, "Report not found in database!"
        print(f"Report verified in PostgreSQL with ID: {db_report.id}")
        print(f"Postgres model: {db_report.model_used}, duration: {db_report.generation_time_ms} ms, confidence: {db_report.confidence}")
        assert db_report.confidence == confidence, "DB confidence mismatch"
        assert db_report.model_used == metadata.get("model_used"), "DB model mismatch"
    finally:
        db.close()
    print("=" * 60)
    print("VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_fusion_v2_api()
