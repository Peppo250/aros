import uuid

from sqlalchemy import Column,String,Integer,ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Repository(Base):

    __tablename__ = "repositories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )

    repo_name = Column(String)

    url = Column(String)

    stars = Column(Integer)