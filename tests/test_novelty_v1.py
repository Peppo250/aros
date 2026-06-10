import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.novelty_report import NoveltyReport

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

def verify_novelty_api():
    print(f"Project ID used for verification: {project_id}")
    print("=" * 60)

    # 1. POST request to generate the report
    payload = {"topic": "edge ai mesh"}
    print("POST: Requesting Novelty V1 generation...")
    resp = client.post(f"/novelty/project/{project_id}", json=payload)
    
    print(f"POST Response status: {resp.status_code}")
    assert resp.status_code == 200, f"Failed generation: {resp.text}"
    
    data = resp.json()
    print("Generation successful!")
    print(f"Report ID: {data.get('report_id')}")
    print(f"Topic: {data.get('topic')}")
    
    # 2. Check scores
    scores = data.get("scores", {})
    print("\nGenerated Scores:")
    for k, v in scores.items():
        print(f"  {k}: {v}")
        
    for k in [
        "research_novelty_score", "implementation_novelty_score",
        "patent_novelty_score", "commercial_novelty_score",
        "overall_novelty_score", "patentability_score"
    ]:
        assert k in scores, f"Score {k} missing from response"
        score_val = scores.get(k)
        assert isinstance(score_val, (int, float)) and 0.0 <= score_val <= 100.0, f"Invalid score {k}: {score_val}"

    confidence = scores.get("confidence_score")
    assert isinstance(confidence, float) and 0.0 <= confidence <= 1.0, f"Invalid confidence_score: {confidence}"

    # 3. Check analyses
    analyses = data.get("analyses", {})
    print("\nGenerated Analyses (length of text):")
    for k, v in analyses.items():
        print(f"  {k}: {len(v) if v else 0} chars")
        
    for k in [
        "research_novelty_analysis", "implementation_novelty_analysis",
        "patent_novelty_analysis", "commercial_novelty_analysis",
        "competitive_landscape", "prior_art_risk", "implementation_difficulty",
        "publication_potential", "recommended_next_steps"
    ]:
        assert k in analyses, f"Analysis {k} missing from response"
        assert analyses.get(k) is not None and len(analyses.get(k)) > 0, f"Analysis {k} is empty"

    # 4. Check metadata & supporting evidence
    metadata = data.get("metadata", {})
    print("\nMetadata:")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    
    assert metadata.get("model_used") in ["qwen3:14b", "qwen3:8b"], f"Unexpected model used: {metadata.get('model_used')}"
    assert isinstance(metadata.get("generation_time_ms"), int) and metadata.get("generation_time_ms") > 0, "Invalid generation_time_ms"

    evidence = data.get("supporting_evidence", {})
    print("\nSupporting Evidence lists:")
    for k, v in evidence.items():
        print(f"  {k}: {len(v)} items")
        
    assert "top_papers" in evidence, "Missing top_papers in evidence"
    assert "top_repositories" in evidence, "Missing top_repositories in evidence"
    assert "top_citations" in evidence, "Missing top_citations in evidence"
    assert "top_patents" in evidence, "Missing top_patents in evidence"

    # 5. GET request to verify retrieval of latest report
    print("\nGET: Retrieving latest Novelty report...")
    get_resp = client.get(f"/novelty/project/{project_id}")
    assert get_resp.status_code == 200, f"Failed retrieval: {get_resp.text}"
    get_data = get_resp.json()
    
    assert get_data.get("report_id") == data.get("report_id"), "GET retrieved ID does not match POST generated ID"
    assert get_data.get("scores", {}).get("confidence_score") == confidence, "GET confidence_score does not match POST confidence_score"
    print("Latest report retrieved matches generated report successfully!")
    print("=" * 60)

    # 6. Database direct query verification
    print("Database Query Verification:")
    db = SessionLocal()
    try:
        db_report = db.query(NoveltyReport).filter(NoveltyReport.id == data.get("report_id")).first()
        assert db_report is not None, "Report not found in database!"
        print(f"Report verified in PostgreSQL with ID: {db_report.id}")
        print(f"Postgres model: {db_report.model_used}, duration: {db_report.generation_time_ms} ms, overall_novelty_score: {db_report.overall_novelty_score}")
        assert db_report.overall_novelty_score == scores.get("overall_novelty_score"), "DB overall_novelty_score mismatch"
        assert db_report.model_used == metadata.get("model_used"), "DB model mismatch"
    finally:
        db.close()
    print("=" * 60)
    print("VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_novelty_api()
