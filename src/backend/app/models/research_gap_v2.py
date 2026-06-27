import uuid

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.db import Base


class ResearchGapReportV2(Base):

    __tablename__ = "research_gap_reports_v2"

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
        String,
        nullable=False
    )

    saturated_areas = Column(Text)
    underexplored_areas = Column(Text)
    missing_implementations = Column(Text)
    missing_datasets = Column(Text)
    patent_white_spaces = Column(Text)
    emerging_opportunities = Column(Text)
    high_impact_research_directions = Column(Text)
    ieee_publication_opportunities = Column(Text)
    commercial_opportunities = Column(Text)
    recommended_research_projects = Column(Text)
    executive_summary = Column(Text)

    confidence_score = Column(Float)
    model_used = Column(String)
    generation_time_ms = Column(Integer)
    full_report = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
