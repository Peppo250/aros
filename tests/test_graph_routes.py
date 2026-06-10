import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_health():
    print("Testing GET /graph/health...")
    response = client.get("/graph/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_build():
    project_id = uuid.uuid4()
    print(f"Testing POST /graph/project/{project_id}...")
    response = client.post(f"/graph/project/{project_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_summary():
    project_id = uuid.uuid4()
    print(f"Testing GET /graph/project/{project_id}...")
    response = client.get(f"/graph/project/{project_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

if __name__ == "__main__":
    test_health()
    print("-" * 50)
    test_build()
    print("-" * 50)
    test_summary()
