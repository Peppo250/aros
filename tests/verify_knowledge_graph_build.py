import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
project_id = "48f7c41b-e795-40a4-8500-3363ab565412"

print(f"Building graph for project: {project_id}...")
build_resp = client.post(f"/graph/project/{project_id}")
print("Build Graph API Response:")
print(build_resp.json())
print("=" * 60)

print(f"Fetching summary for project: {project_id}...")
summary_resp = client.get(f"/graph/project/{project_id}")
print("Get Summary API Response:")
print(summary_resp.json())
print("=" * 60)

print(f"Checking health...")
health_resp = client.get("/graph/health")
print("Health API Response:")
print(health_resp.json())
