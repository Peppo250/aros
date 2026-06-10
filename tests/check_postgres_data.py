import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.database.db import SessionLocal
from app.models.project import Project
from app.models.paper import Paper
from app.models.github_repo import GithubRepo
from app.models.patent import Patent
from app.models.dataset import Dataset
from app.models.trend import TrendSignal

db = SessionLocal()
try:
    projects = db.query(Project).all()
    print(f"Total projects: {len(projects)}")
    for p in projects:
        papers = db.query(Paper).filter(Paper.project_id == p.id).count()
        repos = db.query(GithubRepo).filter(GithubRepo.project_id == p.id).count()
        patents = db.query(Patent).filter(Patent.project_id == p.id).count()
        datasets = db.query(Dataset).filter(Dataset.project_id == p.id).count()
        trends = db.query(TrendSignal).filter(TrendSignal.project_id == p.id).count()
        print(f"Project ID: {p.id}, Title: {p.title}")
        print(f"  Papers: {papers}, Repos: {repos}, Patents: {patents}, Datasets: {datasets}, Trends: {trends}")
except Exception as e:
    print(f"Error checking Postgres data: {e}")
finally:
    db.close()
