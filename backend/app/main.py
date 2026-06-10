from fastapi import FastAPI

from app.api.projects import router
from app.api.research_runs import router as run_router
from app.api.research_runs import router as run_router
from app.api.downloads import router as downloads_router
from app.api.extract import router as extract_router

app = FastAPI(
    title="AROS"
)

app.include_router(
    extract_router,
    prefix="/extract",
    tags=["Extraction"]
)

app.include_router(
    downloads_router,
    prefix="/downloads",
    tags=["Downloads"]
)
app.include_router(
    run_router,
    prefix="/research-runs",
    tags=["Research Runs"]
)

app.include_router(
    router,
    prefix="/projects",
    tags=["Projects"]
)

from app.api.research import router as research_router

app.include_router(
    research_router,
    prefix="/research",
    tags=["Research"]
)

@app.get("/")
def root():
    return {
        "status": "running"
    }

from app.api.papers import router as paper_router

app.include_router(
    paper_router,
    prefix="/papers",
    tags=["Papers"]
)

from app.api.arxiv import router as arxiv_router

app.include_router(
    arxiv_router,
    prefix="/arxiv",
    tags=["arxiv"]
)

from app.api.embed import (
    router as embed_router
)

app.include_router(
    embed_router,
    prefix="/embed",
    tags=["Embedding"]
)

from app.api.search import (
    router as search_router
)

app.include_router(
    search_router,
    prefix="/search",
    tags=["Search"]
)

from app.api.qa import (
    router as qa_router
)

app.include_router(
    qa_router,
    prefix="/ask",
    tags=["QA"]
)

from app.api.research_gap import (
    router as gap_router
)

app.include_router(
    gap_router,
    prefix="/research-gap",
    tags=["Research Gap"]
)

from app.api.github import (
    router as github_router
)

app.include_router(
    github_router,
    prefix="/github",
    tags=["GitHub"]
)

from app.api.fusion import (
    router as fusion_router
)

app.include_router(
    fusion_router,
    prefix="/fusion",
    tags=["Fusion"]
)