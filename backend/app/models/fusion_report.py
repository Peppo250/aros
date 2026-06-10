import uuid

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.db import Base


class FusionReport(Base):

    __tablename__ = "fusion_reports"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    topic = Column(
        Text,
        nullable=False
    )

    analysis = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )