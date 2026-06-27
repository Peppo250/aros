from app.database.db import engine

from app.models.project import Project
from app.models.paper import Paper
from app.models.patent import Patent
from app.models.dataset import Dataset
from app.models.research_run import ResearchRun
from app.models.document_chunk import DocumentChunk
from app.models.research_gap import ResearchGap
from app.models.github_repo import GithubRepo
from app.models.fusion_report import FusionReport
from app.models.trend import TrendSignal
from app.models.citation import CitationRecord
from app.models.fusion_report_v2 import FusionReportV2
from app.models.research_gap_v2 import ResearchGapReportV2
from app.models.novelty_report import NoveltyReport
from app.models.patent_opportunity import PatentOpportunity
from app.models.report_v1 import ReportV1
FusionReport.metadata.create_all(bind=engine)
GithubRepo.metadata.create_all(bind=engine)
ResearchGap.metadata.create_all(bind=engine)
DocumentChunk.metadata.create_all(bind=engine)
ResearchRun.metadata.create_all(bind=engine)
Project.metadata.create_all(bind=engine)
Paper.metadata.create_all(bind=engine)
Patent.metadata.create_all(bind=engine)
Dataset.metadata.create_all(bind=engine)
TrendSignal.metadata.create_all(bind=engine)
CitationRecord.metadata.create_all(bind=engine)
FusionReportV2.metadata.create_all(bind=engine)
ResearchGapReportV2.metadata.create_all(bind=engine)
NoveltyReport.metadata.create_all(bind=engine)
PatentOpportunity.metadata.create_all(bind=engine)
ReportV1.metadata.create_all(bind=engine)

from sqlalchemy import text
with engine.connect() as conn:
    columns_to_add = [
        ("relevance_score", "DOUBLE PRECISION"),
        ("novelty_contribution_score", "DOUBLE PRECISION"),
        ("commercial_impact_score", "DOUBLE PRECISION"),
        ("prior_art_overlap_score", "DOUBLE PRECISION"),
        ("validation_score", "DOUBLE PRECISION"),
        ("jurisdiction", "VARCHAR"),
        ("status", "VARCHAR"),
        ("patent_family", "TEXT"),
        ("citations_count", "INTEGER"),
        ("is_verified", "BOOLEAN"),
        ("verification_source", "VARCHAR"),
        ("verification_timestamp", "TIMESTAMP WITH TIME ZONE")
    ]
    for col_name, col_type in columns_to_add:
        try:
            conn.execute(text(f"ALTER TABLE patents ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
            conn.commit()
            print(f"Verified column: {col_name}")
        except Exception as e:
            print(f"Skipped/Error adding column {col_name}: {e}")

    try:
        conn.execute(text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS patent_id UUID REFERENCES patents(id)"))
        conn.commit()
        print("Verified column patent_id on document_chunks")
    except Exception as e:
        print(f"Skipped/Error adding patent_id to document_chunks: {e}")

print("Database initialized")