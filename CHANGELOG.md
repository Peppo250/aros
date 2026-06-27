# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to Semantic Versioning.

---

## [1.1.0] - 2026-06-27

### Added
- **Common LLM Utilities**:
  - `src/backend/app/services/ollama_client.py`: Houses the unified `run_ollama_chat` controller, eliminating duplicate chatbot wrappers.
  - `src/backend/app/services/json_parser.py`: Centralizes the `extract_json_from_text` helper to securely parse JSON objects, lists, and metadata from raw text.
- **Modular Patent Service**:
  - `src/backend/app/services/patent_providers.py`: Segments individual scraping clients (USPTO, Lens, Google Patents, Europe PMC) and includes a local DNS format validation fallback.
  - `src/backend/app/services/patent_scoring.py`: Encapsulates relevance, novelty, priority art, and commercialization metrics.
- **Visuals & Logs**:
  - `docs/assets/`: Embedded visual screenshots illustrating the workspace, project archives, new research setup, and compiled report viewer.
  - `docs/test_results.md`: Integration logs verifying the Europe PMC fallback and Citations duplicate checks.
- **Project Configs**:
  - `.editorconfig`: Codestyle guidelines.
  - `LICENSE`: MIT License.

### Changed
- **Folder Structure Reorganization**:
  - Relocated backend source to `src/backend` and frontend React code to `src/frontend`.
  - Re-routed verification and benchmark scripts into `tests/`.
  - Moved collection scripts to `scripts/create_qdrant_collection.py`.
- **Patent Search Orchestrator**:
  - `src/backend/app/services/patent_search.py`: Refactored to act as a clean coordinator executing imports from `patent_providers.py` and `patent_scoring.py`.
- **Service Simplification**:
  - Refactored `fusion_v2.py`, `report_v1.py`, `novelty.py`, `patent_opportunity.py`, and `research_gap_v2.py` to import common clients, reducing duplicate code.
- **Orchestration Hook**:
  - Updated `orchestrator.py` to trigger n8n's production webhook (`/webhook/research`) rather than test endpoints.
- **Infrastructure Expansion**:
  - Added the Neo4j database service integration container into `docker-compose.yml`.

### Fixed
- **Frontend Dashboard Render Crash**:
  - `src/frontend/src/services/api.js`: Mapped Project schemas returned by the API to fit the UI `Run` properties (solving an `undefined` `run_id` TypeError that caused a black screen crash).
- **ORM Column Conflicts**:
  - `src/backend/app/models/paper.py`: Removed duplicate properties mapping `id` and `local_pdf_path` which were creating silent column collisions in SQLAlchemy.
- **Database Initializations**:
  - `src/backend/app/database/init_db.py`: Cleared obsolete model tables registration.

### Removed
- **Unused Schemas**:
  - Deleted obsolete model definitions `Repository`, `Report`, and `ResearchOpportunity` from `src/backend/app/models/`.
