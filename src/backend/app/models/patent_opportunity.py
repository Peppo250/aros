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


class PatentOpportunity(Base):

    __tablename__ = "patent_opportunities"

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

    opportunity_score = Column(Float)
    patentability_score = Column(Float)
    prior_art_risk_score = Column(Float)
    commercial_value_score = Column(Float)

    white_space_analysis = Column(Text)
    closest_prior_art = Column(Text)
    independent_claim_draft = Column(Text)
    dependent_claims_draft = Column(Text)
    novel_technical_contributions = Column(Text)
    commercial_value_analysis = Column(Text)
    filing_strategy = Column(Text)
    recommended_jurisdictions = Column(Text)
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
