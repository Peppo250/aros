from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.patent import Patent
from app.services.patent_search import search_patents
from app.services.patent_retrieval import get_patents

router = APIRouter()


@router.post("/project/{project_id}")
def collect_patents(
    project_id: UUID,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    results = search_patents(topic)

    inserted = 0

    for p in results:
        patent_id = p.get("patent_id")
        if not patent_id:
            continue

        # Prevent duplicate inserts for the same project & patent number
        existing = (
            db.query(Patent)
            .filter(
                Patent.project_id == project_id,
                Patent.patent_number == patent_id
            )
            .first()
        )

        if existing:
            continue

        # Extract and format assignees
        assignee_list = p.get("assignees", [])
        assignee_orgs = [
            a.get("assignee_organization")
            for a in assignee_list
            if a.get("assignee_organization")
        ]
        assignee_str = ", ".join(assignee_orgs) if assignee_orgs else None

        # Extract and format inventors
        inventor_list = p.get("inventors", [])
        inventor_names = [
            f"{i.get('inventor_name_first', '')} {i.get('inventor_name_last', '')}".strip()
            for i in inventor_list
        ]
        inventor_str = ", ".join([name for name in inventor_names if name]) if inventor_names else None

        # Format source URL
        url_str = f"https://patents.google.com/patent/US{patent_id}/en"

        row = Patent(
            project_id=project_id,
            title=p.get("patent_title"),
            patent_number=patent_id,
            assignee=assignee_str,
            inventors=inventor_str,
            abstract=p.get("patent_abstract"),
            publication_date=p.get("patent_date"),
            source="PatentsView",
            url=url_str,
            topic=topic,
            raw_data=p
        )

        db.add(row)
        inserted += 1

    db.commit()

    return {
        "inserted": inserted
    }


@router.get("/project/{project_id}")
def retrieve_patents(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    return get_patents(db, str(project_id))
