import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.research_gap_v2 import ResearchGapReportV2

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

def verify_research_gap_v2_api():
    print(f"Project ID used for verification: {project_id}")
    print("=" * 60)

    # 1. POST request to generate the report
    payload = {"topic": "edge ai mesh"}
    print("POST: Requesting Research Gap V2 generation...")
    resp = client.post(f"/research-gap-v2/project/{project_id}", json=payload)
    
    print(f"POST Response status: {resp.status_code}")
    assert resp.status_code == 200, f"Failed generation: {resp.text}"
    
    data = resp.json()
    print("Generation successful!")
    print(f"Report ID: {data.get('report_id')}")
    print(f"Topic: {data.get('topic')}")
    
    # 2. Check sections
    sections = data.get("sections", {})
    print("\nGenerated Sections (length of text):")
    for k, v in sections.items():
        print(f"  {k}: {len(v) if v else 0} chars")
        
    for k in [
        "saturated_areas", "underexplored_areas", "missing_implementations",
        "missing_datasets", "patent_white_spaces", "emerging_opportunities",
        "high_impact_research_directions", "ieee_publication_opportunities",
        "commercial_opportunities", "recommended_research_projects",
        "executive_summary"
    ]:
        assert k in sections, f"Section {k} missing from response"
        assert sections.get(k) is not None and len(sections.get(k)) > 0, f"Section {k} is empty"

    # 3. Check confidence score and metadata
    confidence = data.get("confidence_score")
    print(f"\nConfidence Score: {confidence}")
    assert isinstance(confidence, float) and 0.0 <= confidence <= 1.0, f"Invalid confidence_score: {confidence}"

    metadata = data.get("metadata", {})
    print("Metadata:")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    
    assert metadata.get("model_used") in ["qwen3:14b", "qwen3:8b"], f"Unexpected model used: {metadata.get('model_used')}"
    assert isinstance(metadata.get("generation_time_ms"), int) and metadata.get("generation_time_ms") > 0, "Invalid generation_time_ms"

    # 4. GET request to verify retrieval of latest report
    print("\nGET: Retrieving latest Research Gap V2 report...")
    get_resp = client.get(f"/research-gap-v2/project/{project_id}")
    assert get_resp.status_code == 200, f"Failed retrieval: {get_resp.text}"
    get_data = get_resp.json()
    
    assert get_data.get("report_id") == data.get("report_id"), "GET retrieved ID does not match POST generated ID"
    assert get_data.get("confidence_score") == confidence, "GET confidence_score does not match POST confidence_score"
    print("Latest report retrieved matches generated report successfully!")
    print("=" * 60)

    # 5. Database direct query verification
    print("Database Query Verification:")
    db = SessionLocal()
    try:
        db_report = db.query(ResearchGapReportV2).filter(ResearchGapReportV2.id == data.get("report_id")).first()
        assert db_report is not None, "Report not found in database!"
        print(f"Report verified in PostgreSQL with ID: {db_report.id}")
        print(f"Postgres model: {db_report.model_used}, duration: {db_report.generation_time_ms} ms, confidence_score: {db_report.confidence_score}")
        assert db_report.confidence_score == confidence, "DB confidence mismatch"
        assert db_report.model_used == metadata.get("model_used"), "DB model mismatch"
    finally:
        db.close()
    print("=" * 60)
    print("VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_research_gap_v2_api()
