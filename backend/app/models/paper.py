import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Paper(Base):

    __tablename__ = "papers"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True
    )

    local_pdf_path = Column(
        String,
        nullable=True
    )    
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id")
    )
    
    __table_args__ = (
    UniqueConstraint(
        "project_id",
        "pdf_url",
        name="uq_project_pdf"
    ),
)
    
    title = Column(String)

    authors = Column(Text)

    abstract = Column(Text)

    pdf_url = Column(Text)

    source = Column(String)

    year = Column(Integer)

    local_pdf_path = Column(String)