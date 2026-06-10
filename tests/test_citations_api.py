import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.citation import CitationRecord

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

def verify_citations_api():
    print(f"Project ID used for verification: {project_id}")
    print("=" * 60)

    # 1. First run of POST (Collection)
    payload = {"topic": "edge ai mesh"}
    print("First run: Collecting citations...")
    resp1 = client.post(f"/citations/project/{project_id}", json=payload)
    print(f"First run Response: {resp1.json()}")
    inserted1 = resp1.json().get("inserted", 0)
    
    # 2. Second run of POST (Duplicate check)
    print("Second run: Re-collecting to verify duplicate prevention...")
    resp2 = client.post(f"/citations/project/{project_id}", json=payload)
    print(f"Second run Response: {resp2.json()}")
    inserted2 = resp2.json().get("inserted", 0)
    
    assert inserted1 > 0, "No citations were inserted in the first run!"
    assert inserted2 == 0, "Duplicate prevention failed! Re-running inserted duplicate records."
    print("Duplicate prevention check: SUCCESS")
    print("=" * 60)

    # 3. GET request to retrieve all citation records
    print("Retrieving citation records via GET...")
    get_resp = client.get(f"/citations/project/{project_id}")
    records = get_resp.json()
    print(f"GET Response status: {get_resp.status_code}")
    print(f"Number of retrieved records: {len(records)}")
    if records:
        print("First retrieved record metadata:")
        rec = records[0]
        # Display key fields including authors_json
        print(f"  Title: {rec.get('paper_title')}")
        print(f"  Authors String: {rec.get('authors')}")
        print(f"  Authors JSON list: {rec.get('authors_json')}")
        print(f"  Source: {rec.get('source')}")
        print(f"  Citation count: {rec.get('citation_count')}")
    print("=" * 60)

    # 4. SQL Verification simulation (SQL verification query using SQLAlchemy)
    print("SQL verification query results (top 20 citations ordered by citation_count DESC):")
    db = SessionLocal()
    try:
        results = (
            db.query(CitationRecord)
            .filter(CitationRecord.project_id == project_id)
            .order_by(CitationRecord.citation_count.desc())
            .limit(20)
            .all()
        )
        print(f"{'Paper Title':<55} | {'Citations':<10} | {'Influential':<12} | {'Source':<15} | {'Year':<6}")
        print("-" * 110)
        for row in results:
            title_trunc = row.paper_title[:52] + "..." if len(row.paper_title) > 55 else row.paper_title
            print(f"{title_trunc:<55} | {row.citation_count:<10} | {row.influential_citation_count:<12} | {row.source:<15} | {row.year:<6}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_citations_api()
