from app.database.db import engine

from app.models.project import Project
from app.models.paper import Paper
from app.models.patent import Patent
from app.models.repository import Repository
from app.models.dataset import Dataset
from app.models.report import Report
from app.models.research_opportunity import ResearchOpportunity
from app.models.research_run import ResearchRun
from app.models.document_chunk import DocumentChunk
from app.models.research_gap import ResearchGap
from app.models.github_repo import GithubRepo
from app.models.fusion_report import FusionReport
from app.models.trend import TrendSignal
from app.models.citation import CitationRecord
from app.models.fusion_report_v2 import FusionReportV2
from app.models.research_gap_v2 import ResearchGapReportV2
FusionReport.metadata.create_all(bind=engine)
GithubRepo.metadata.create_all(bind=engine)
ResearchGap.metadata.create_all(bind=engine)
DocumentChunk.metadata.create_all(bind=engine)
ResearchRun.metadata.create_all(bind=engine)
Project.metadata.create_all(bind=engine)
Paper.metadata.create_all(bind=engine)
Patent.metadata.create_all(bind=engine)
Repository.metadata.create_all(bind=engine)
Dataset.metadata.create_all(bind=engine)
Report.metadata.create_all(bind=engine)
ResearchOpportunity.metadata.create_all(bind=engine)
TrendSignal.metadata.create_all(bind=engine)
CitationRecord.metadata.create_all(bind=engine)
FusionReportV2.metadata.create_all(bind=engine)
ResearchGapReportV2.metadata.create_all(bind=engine)

print("Database initialized")