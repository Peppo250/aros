from pydantic import BaseModel


class ResearchRunCreate(BaseModel):
    project_id: str


class ResearchRunUpdate(BaseModel):
    status: str