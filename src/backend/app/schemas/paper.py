from pydantic import BaseModel


class PaperCreate(BaseModel):
    project_id: str
    title: str
    authors: str
    abstract: str
    pdf_url: str
    source: str
    year: int | None = None
    