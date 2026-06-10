import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
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

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )