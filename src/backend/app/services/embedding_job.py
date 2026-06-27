import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from app.database.db import Base


class EmbeddingJob(Base):

    __tablename__ = "embedding_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True)
    )

    status = Column(
        String,
        default="queued"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )