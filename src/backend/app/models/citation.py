import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database.db import Base

class CitationRecord(Base):
    __tablename__ = "citation_records"

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

    topic = Column(String)
    
    paper_title = Column(Text)
    
    authors = Column(Text)
    
    authors_json = Column(JSONB)
    
    year = Column(Integer)
    
    citation_count = Column(Integer)
    
    influential_citation_count = Column(Integer)
    
    source = Column(String)
    
    url = Column(String)
    
    raw_data = Column(JSONB)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
