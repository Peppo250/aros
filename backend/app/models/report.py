import uuid

from sqlalchemy import Column,String,Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Report(Base):

    __tablename__ = "reports"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )

    report_type = Column(String)

    content = Column(Text)