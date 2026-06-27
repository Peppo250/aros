import uuid

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database.db import Base


class Patent(Base):

    __tablename__ = "patents"

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

    title = Column(Text)

    patent_number = Column(
        String,
        index=True
    )

    assignee = Column(String)

    inventors = Column(Text)

    abstract = Column(Text)

    publication_date = Column(String)

    source = Column(String)

    url = Column(String)

    topic = Column(String)

    raw_data = Column(JSONB)

    relevance_score = Column(Float)
    novelty_contribution_score = Column(Float)
    commercial_impact_score = Column(Float)
    prior_art_overlap_score = Column(Float)
    validation_score = Column(Float)
    
    jurisdiction = Column(String)
    status = Column(String)
    patent_family = Column(Text)
    citations_count = Column(Integer)

    # Verification Fields
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String)
    verification_timestamp = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )