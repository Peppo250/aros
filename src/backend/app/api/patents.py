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

    if isinstance(results, dict) and results.get("status") == "retrieval_failed":
        return results

    inserted = 0

    for p in results:
        patent_id = p.get("patent_number") or p.get("patent_id")
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
        if isinstance(assignee_list, list):
            assignee_orgs = [
                a.get("assignee_organization")
                for a in assignee_list
                if isinstance(a, dict) and a.get("assignee_organization")
            ]
            assignee_str = ", ".join(assignee_orgs) if assignee_orgs else None
        else:
            assignee_str = str(p.get("assignee") or "") or None

        # Extract and format inventors
        inventor_list = p.get("inventors", [])
        if isinstance(inventor_list, list):
            inventor_names = [
                f"{i.get('inventor_name_first', '')} {i.get('inventor_name_last', '')}".strip()
                for i in inventor_list
                if isinstance(i, dict)
            ]
            inventor_str = ", ".join([name for name in inventor_names if name]) if inventor_names else None
        else:
            inventor_str = str(p.get("inventor") or "") or None

        # Format source URL
        url_str = p.get("url") or f"https://patents.google.com/patent/{patent_id}/en"

        row = Patent(
            project_id=project_id,
            title=p.get("patent_title"),
            patent_number=patent_id,
            assignee=assignee_str,
            inventors=inventor_str,
            abstract=p.get("patent_abstract"),
            publication_date=p.get("patent_date"),
            source=p.get("source") or "PatentsView",
            url=url_str,
            topic=topic,
            raw_data=p,
            relevance_score=p.get("relevance_score"),
            novelty_contribution_score=p.get("novelty_contribution_score"),
            commercial_impact_score=p.get("commercial_impact_score"),
            prior_art_overlap_score=p.get("prior_art_overlap_score"),
            validation_score=p.get("validation_score"),
            jurisdiction=p.get("jurisdiction"),
            status=p.get("status"),
            patent_family=p.get("patent_family"),
            citations_count=p.get("citations_count"),
            is_verified=p.get("is_verified", False),
            verification_source=p.get("verification_source"),
            verification_timestamp=p.get("verification_timestamp")
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
