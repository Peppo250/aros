import uuid

from sqlalchemy import Column,String,Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Patent(Base):

    __tablename__ = "patents"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )

    title = Column(String)

    patent_number = Column(String)

    assignee = Column(String)

    abstract = Column(Text)