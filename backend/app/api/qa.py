from fastapi import APIRouter

from app.services.qa import answer_question

router = APIRouter()


@router.post("/")
def ask(payload: dict):

    return answer_question(
        payload["question"]
    )