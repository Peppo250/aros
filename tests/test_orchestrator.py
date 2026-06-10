import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.project import Project
from app.models.research_run import ResearchRun
from app.models.report_v1 import ReportV1

client = TestClient(app)

def verify_orchestrator_flow():
    print("=" * 60)
    print("1. POST: Starting Autonomous Research Orchestrator...")
    
    # Run START orchestrator
    payload = {"topic": "edge ai mesh"}
    resp = client.post("/research/start", json=payload)
    print(f"POST /research/start Status: {resp.status_code}")
    print(f"POST Response: {resp.json()}")
    assert resp.status_code == 200, f"POST /research/start failed: {resp.text}"
    
    data = resp.json()
    run_id = data.get("run_id")
    project_id = data.get("project_id")
    status = data.get("status")
    
    assert run_id is not None, "Missing run_id"
    assert project_id is not None, "Missing project_id"
    assert status == "queued", f"Unexpected status: {status}"

    print("Orchestrator queued successfully!")
    print("=" * 60)

    # 2. Verify Database Records
    print("2. Verifying database records exist...")
    db = SessionLocal()
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        assert db_project is not None, "Project was not created in DB!"
        assert db_project.topic == "edge ai mesh"
        
        db_run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
        assert db_run is not None, "ResearchRun was not created in DB!"
        assert db_run.status == "queued"
        print("Database Project and ResearchRun verified!")
    finally:
        db.close()
    print("=" * 60)

    # 3. Verify Progress Endpoint
    print("3. GET: Checking initial progress (queued = 0%)...")
    progress_resp = client.get(f"/research-runs/{run_id}")
    print(f"Progress Response: {progress_resp.json()}")
    assert progress_resp.status_code == 200
    p_data = progress_resp.json()
    assert p_data.get("status") == "queued"
    assert p_data.get("progress") == 0

    # Simulate transition to fusion_completed and check progress
    print("Simulating status update to 'fusion_completed' (80%)...")
    db = SessionLocal()
    try:
        db_run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
        db_run.status = "fusion_completed"
        db.commit()
    finally:
        db.close()

    progress_resp2 = client.get(f"/research-runs/{run_id}")
    print(f"Updated Progress Response: {progress_resp2.json()}")
    assert progress_resp2.status_code == 200
    p_data2 = progress_resp2.json()
    assert p_data2.get("status") == "fusion_completed"
    assert p_data2.get("progress") == 80
    print("Progress mapping verified successfully!")
    print("=" * 60)

    # 4. Verify Result Endpoint
    print("4. GET: Testing Result dossier endpoint...")
    # Seed a dummy report in database matching project_id
    db = SessionLocal()
    try:
        mock_report = ReportV1(
            project_id=project_id,
            topic="edge ai mesh",
            executive_summary="Mock summary",
            research_landscape="Mock landscape",
            research_gaps="Mock gaps",
            novelty_assessment="Mock novelty",
            patent_opportunities="Mock patent ops",
            ieee_publication_plan="Mock IEEE",
            patent_filing_plan="Mock filing",
            commercialization_strategy="Mock comm",
            research_roadmap="Mock roadmap",
            next_actions="Mock actions",
            confidence_score=0.85,
            model_used="qwen3:8b",
            generation_time_ms=1000,
            supporting_evidence={"mock": True},
            full_report="Mock full report"
        )
        db.add(mock_report)
        db.commit()
        print("Mock ReportV1 seeded in database.")
    finally:
        db.close()

    result_resp = client.get(f"/research-runs/{run_id}/result")
    print(f"Result Response Status: {result_resp.status_code}")
    assert result_resp.status_code == 200, f"GET result failed: {result_resp.text}"
    r_data = result_resp.json()
    
    assert r_data.get("topic") == "edge ai mesh"
    assert r_data.get("confidence_score") == 0.85
    assert r_data.get("sections", {}).get("executive_summary") == "Mock summary"
    assert r_data.get("sections", {}).get("research_roadmap") == "Mock roadmap"
    assert r_data.get("sections", {}).get("ieee_publication_plan") == "Mock IEEE"
    assert r_data.get("sections", {}).get("patent_filing_plan") == "Mock filing"
    assert r_data.get("sections", {}).get("commercialization_strategy") == "Mock comm"
    print("Result dossier endpoint verified successfully!")
    print("=" * 60)
    print("ORCHESTRATOR FLOW VERIFIED COMPLETED!")

if __name__ == "__main__":
    verify_orchestrator_flow()
