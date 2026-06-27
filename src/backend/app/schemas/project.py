from pydantic import BaseModel


class ProjectCreate(BaseModel):

    title: str
    topic: str