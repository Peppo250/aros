from pydantic import BaseModel


class PaperItem(BaseModel):
    title: str
    authors: str
    abstract: str
    pdf_url: str
    source: str
    year: int | None = None


class PaperBulkCreate(BaseModel):
    project_id: str
    papers: list[PaperItem]