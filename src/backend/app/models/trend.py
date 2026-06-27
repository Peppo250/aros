import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database.db import Base


class TrendSignal(Base):

    __tablename__ = "trend_signals"

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

    topic = Column(String)

    source = Column(String)

    title = Column(Text)

    description = Column(Text)

    url = Column(String)

    trend_score = Column(Float)

    relevance_score = Column(Float)

    published_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    raw_data = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
