from fastapi import APIRouter

from app.services.arxiv_parser import parse_arxiv

router = APIRouter()


@router.post("/parse")
def parse_xml(payload: dict):

    xml = payload["xml"]

    papers = parse_arxiv(xml)

    return papers