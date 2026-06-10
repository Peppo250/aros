from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.trend import TrendSignal
from app.services.trend_search import search_trends
from app.services.trend_retrieval import get_trends

router = APIRouter()


@router.post("/project/{project_id}")
def collect_trends(
    project_id: UUID,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    results = search_trends(topic)

    inserted = 0

    for item in results:
        title = item.get("title")
        if not title:
            continue

        # Prevent duplicate inserts for the same project & title
        existing = (
            db.query(TrendSignal)
            .filter(
                TrendSignal.project_id == project_id,
                TrendSignal.title == title
            )
            .first()
        )

        if existing:
            continue

        row = TrendSignal(
            project_id=project_id,
            topic=topic,
            source=item["source"],
            title=title,
            description=item["description"],
            url=item["url"],
            trend_score=item["trend_score"],
            relevance_score=item["relevance_score"],
            published_at=item["published_at"],
            raw_data=item["raw_data"]
        )

        db.add(row)
        inserted += 1

    db.commit()

    return {
        "inserted": inserted
    }


@router.get("/project/{project_id}")
def retrieve_trends(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    return (
        db.query(TrendSignal)
        .filter(TrendSignal.project_id == project_id)
        .order_by(
            TrendSignal.relevance_score.desc(),
            TrendSignal.published_at.desc()
        )
        .all()
    )
