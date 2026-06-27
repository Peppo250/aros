import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

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
        nullable=False,
        index=True
    )

    name = Column(Text)

    description = Column(Text)

    task = Column(String)

    modality = Column(String)

    license = Column(String)

    source = Column(String)

    url = Column(String)

    topic = Column(String)

    search_term = Column(String)

    raw_data = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )