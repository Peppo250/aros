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


class ReportV1(Base):

    __tablename__ = "reports_v1"

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

    executive_summary = Column(Text)
    research_landscape = Column(Text)
    research_gaps = Column(Text)
    novelty_assessment = Column(Text)
    patent_opportunities = Column(Text)
    ieee_publication_plan = Column(Text)
    patent_filing_plan = Column(Text)
    commercialization_strategy = Column(Text)
    research_roadmap = Column(Text)
    next_actions = Column(Text)

    confidence_score = Column(Float)
    model_used = Column(String)
    generation_time_ms = Column(Integer)
    
    supporting_evidence = Column(JSONB)
    full_report = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
