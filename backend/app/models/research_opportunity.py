import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class ResearchOpportunity(Base):

    __tablename__ = "research_opportunities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )

    title = Column(String)

    novelty_score = Column(Float)

    impact_score = Column(Float)

    difficulty_score = Column(Float)

    description = Column(Text)