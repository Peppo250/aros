import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from app.database.db import Base


class Project(Base):

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title = Column(String, nullable=False)

    topic = Column(String, nullable=False)

    status = Column(
        String,
        default="created"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )