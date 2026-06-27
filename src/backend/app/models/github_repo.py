import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.db import Base


class GithubRepo(Base):

    __tablename__ = "github_repos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    repo_name = Column(String)

    owner = Column(String)

    description = Column(String)

    stars = Column(Integer)

    language = Column(String)

    html_url = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )