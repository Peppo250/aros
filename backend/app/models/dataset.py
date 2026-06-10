import uuid

from sqlalchemy import Column,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Dataset(Base):

    __tablename__ = "datasets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )

    name = Column(String)

    source = Column(String)

    url = Column(String)