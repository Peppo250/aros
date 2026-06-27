from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.dataset import Dataset
from app.services.dataset_search import search_datasets
from app.services.dataset_retrieval import get_datasets

router = APIRouter()


@router.post("/project/{project_id}")
def collect_datasets(
    project_id: UUID,
    payload: dict,
    db: Session = Depends(get_db)
):
    topic = payload.get("topic")
    results, search_term = search_datasets(topic)

    inserted = 0

    for item in results:
        name = item.get("id")
        if not name:
            continue

        # Prevent duplicate inserts for the same project & dataset name
        existing = (
            db.query(Dataset)
            .filter(
                Dataset.project_id == project_id,
                Dataset.name == name
            )
            .first()
        )

        if existing:
            continue

        # Safely extract description
        description = (
            item.get("description")
            or item.get("cardData", {}).get("description")
            or item.get("cardData", {}).get("dataset_info", {}).get("description")
            if item.get("cardData")
            else item.get("description")
        )

        # Safely extract task
        task = item.get("pipeline_tag")
        if not task:
            task_cats = item.get("cardData", {}).get("task_categories")
            if task_cats:
                if isinstance(task_cats, list) and len(task_cats) > 0:
                    task = task_cats[0]
                elif isinstance(task_cats, str):
                    task = task_cats
        if not task:
            for tag in item.get("tags", []):
                if tag.startswith("task_categories:"):
                    task = tag.split("task_categories:", 1)[1]
                    break

        # Safely extract license
        license = None
        card_license = item.get("cardData", {}).get("license")
        if card_license:
            if isinstance(card_license, list) and len(card_license) > 0:
                license = card_license[0]
            elif isinstance(card_license, str):
                license = card_license
        if not license:
            for tag in item.get("tags", []):
                if tag.startswith("license:"):
                    license = tag.split("license:", 1)[1]
                    break

        # Safely extract modality
        modality = None
        for tag in item.get("tags", []):
            if tag.startswith("modality:"):
                modality = tag.split("modality:", 1)[1]
                break

        # Construct Hugging Face dataset URL
        url_str = f"https://huggingface.co/datasets/{name}"

        row = Dataset(
            project_id=project_id,
            name=name,
            description=description,
            task=task,
            modality=modality,
            license=license,
            source="Hugging Face",
            url=url_str,
            topic=topic,
            search_term=search_term,
            raw_data=item
        )

        db.add(row)
        inserted += 1

    db.commit()

    return {
        "inserted": inserted
    }


@router.get("/project/{project_id}")
def retrieve_datasets(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    return get_datasets(db, str(project_id))
