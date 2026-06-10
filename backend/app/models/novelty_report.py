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


class NoveltyReport(Base):

    __tablename__ = "novelty_reports"

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

    research_novelty_score = Column(Float)
    implementation_novelty_score = Column(Float)
    patent_novelty_score = Column(Float)
    commercial_novelty_score = Column(Float)
    overall_novelty_score = Column(Float)

    research_novelty_analysis = Column(Text)
    implementation_novelty_analysis = Column(Text)
    patent_novelty_analysis = Column(Text)
    commercial_novelty_analysis = Column(Text)

    competitive_landscape = Column(Text)
    prior_art_risk = Column(Text)
    implementation_difficulty = Column(Text)
    publication_potential = Column(Text)

    patentability_score = Column(Float)
    recommended_next_steps = Column(Text)
    
    confidence_score = Column(Float)
    model_used = Column(String)
    generation_time_ms = Column(Integer)
    
    supporting_evidence = Column(JSONB)
    full_report = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
