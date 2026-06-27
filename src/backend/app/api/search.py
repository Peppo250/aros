from fastapi import APIRouter

from app.services.retriever import retrieve

router = APIRouter()


@router.post("/")
def search(payload: dict):

    results = retrieve(
        payload["query"]
    )

    output = []

    for result in results:

        if not result.payload:
            continue

        content = result.payload.get("content")

        if not content:
            continue

        output.append({
            "score": result.score,
            "content": content[:500]
        })

    return output