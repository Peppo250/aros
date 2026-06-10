import uuid

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.db import Base


class ResearchGap(Base):

    __tablename__ = "research_gaps"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    title = Column(Text)

    description = Column(Text)

    novelty_score = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )