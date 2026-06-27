import uuid

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    paper_id = Column(
        UUID(as_uuid=True),
        ForeignKey("papers.id"),
        nullable=True
    )

    patent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patents.id"),
        nullable=True
    )

    chunk_index = Column(Integer)

    content = Column(Text)
    embedded = Column(
        Boolean,
        default=False
    )