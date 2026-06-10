import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.report_v1 import ReportV1

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

def verify_report_v1_api():
    print(f"Project ID used for verification: {project_id}")
    print("=" * 60)

    # 1. POST request to generate the report
    payload = {"topic": "edge ai mesh"}
    print("POST: Requesting Report V1 generation...")
    resp = client.post(f"/report-v1/project/{project_id}", json=payload)
    
    print(f"POST Response status: {resp.status_code}")
    assert resp.status_code == 200, f"Failed generation: {resp.text}"
    
    data = resp.json()
    print("Generation successful!")
    print(f"Report ID: {data.get('report_id')}")
    print(f"Topic: {data.get('topic')}")
    
    # 2. Check confidence score and metadata
    confidence = data.get("confidence_score")
    print(f"\nConfidence Score: {confidence}")
    assert isinstance(confidence, float) and 0.0 <= confidence <= 1.0, f"Invalid confidence_score: {confidence}"

    metadata = data.get("metadata", {})
    print("Metadata:")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    
    assert metadata.get("model_used") in ["qwen3:14b", "qwen3:8b"], f"Unexpected model used: {metadata.get('model_used')}"
    assert isinstance(metadata.get("generation_time_ms"), int) and metadata.get("generation_time_ms") > 0, "Invalid generation_time_ms"

    # 3. Check sections
    sections = data.get("sections", {})
    print("\nGenerated Sections (length of text):")
    for k, v in sections.items():
        print(f"  {k}: {len(v) if v else 0} chars")
        
    for k in [
        "executive_summary", "research_landscape", "research_gaps",
        "novelty_assessment", "patent_opportunities", "ieee_publication_plan",
        "patent_filing_plan", "commercialization_strategy", "research_roadmap",
        "next_actions"
    ]:
        assert k in sections, f"Section {k} missing from response"
        assert sections.get(k) is not None and len(sections.get(k)) > 0, f"Section {k} is empty"

    # 4. Check supporting evidence
    evidence = data.get("supporting_evidence", {})
    print("\nSupporting Evidence lists:")
    for k, v in evidence.items():
        print(f"  {k}: {v}")
        
    assert "fusion_report_id" in evidence, "Missing fusion_report_id in evidence"
    assert "research_gap_report_id" in evidence, "Missing research_gap_report_id in evidence"
    assert "novelty_report_id" in evidence, "Missing novelty_report_id in evidence"
    assert "patent_opportunity_report_id" in evidence, "Missing patent_opportunity_report_id in evidence"

    # 5. GET request to verify retrieval of latest report
    print("\nGET: Retrieving latest Report V1 report...")
    get_resp = client.get(f"/report-v1/project/{project_id}")
    assert get_resp.status_code == 200, f"Failed retrieval: {get_resp.text}"
    get_data = get_resp.json()
    
    assert get_data.get("report_id") == data.get("report_id"), "GET retrieved ID does not match POST generated ID"
    assert get_data.get("confidence_score") == confidence, "GET confidence_score does not match POST confidence_score"
    print("Latest report retrieved matches generated report successfully!")
    print("=" * 60)

    # 6. Database direct query verification
    print("Database Query Verification:")
    db = SessionLocal()
    try:
        db_report = db.query(ReportV1).filter(ReportV1.id == data.get("report_id")).first()
        assert db_report is not None, "Report not found in database!"
        print(f"Report verified in PostgreSQL with ID: {db_report.id}")
        print(f"Postgres model: {db_report.model_used}, duration: {db_report.generation_time_ms} ms, confidence_score: {db_report.confidence_score}")
        assert db_report.confidence_score == confidence, "DB confidence_score mismatch"
        assert db_report.model_used == metadata.get("model_used"), "DB model mismatch"
    finally:
        db.close()
    print("=" * 60)
    print("VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_report_v1_api()
