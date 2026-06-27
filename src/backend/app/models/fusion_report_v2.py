import uuid

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database.db import Base


class FusionReportV2(Base):

    __tablename__ = "fusion_reports_v2"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    topic = Column(
        Text,
        nullable=False
    )

    research_landscape = Column(Text)
    influential_work = Column(Text)
    implementations = Column(Text)
    patent_activity = Column(Text)
    datasets = Column(Text)
    emerging_trends = Column(Text)
    knowledge_graph_insights = Column(Text)
    consensus_findings = Column(Text)
    contradictions = Column(Text)
    research_opportunities = Column(Text)
    executive_summary = Column(Text)
    
    full_report = Column(Text)

    # Source Counts (Upgrade 1)
    papers_count = Column(Integer, default=0)
    repositories_count = Column(Integer, default=0)
    patents_count = Column(Integer, default=0)
    datasets_count = Column(Integer, default=0)
    trends_count = Column(Integer, default=0)
    citations_count = Column(Integer, default=0)
    graph_nodes_count = Column(Integer, default=0)
    graph_relationships_count = Column(Integer, default=0)

    # Supporting Evidence (Upgrade 3)
    supporting_evidence = Column(JSONB)

    # Generation Metadata (Upgrade 1 of new requests)
    model_used = Column(String)
    generation_time_ms = Column(Integer)
    context_length = Column(Integer)

    # Retrieval Metadata (Upgrade 2 of new requests)
    retrieval_metadata = Column(JSONB)

    # Confidence Score (Upgrade 3 of new requests)
    confidence = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
