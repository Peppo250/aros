# Setup & Environment Configuration

This document provides in-depth guidelines for setting up the local environment, system tools, databases, and LLM models.

---

## 🛠️ Prerequisites

* **OS**: Linux, macOS, or Windows (10/11)
* **Python**: `3.12.x`
* **Node.js**: `v18` or higher (tested on React 19)
* **Docker**: Docker Desktop or Docker engine with Compose support

---

## 🤖 Ollama LLM Configuration

AROS requires Ollama to be running locally or on a reachable network host.

### 1. Download & Install Ollama
Download and run the installer for your platform from [Ollama's official page](https://ollama.com/).

### 2. Pull Required Models
AROS uses specific models for embedding, lightweight extraction, and complex synthesis:
```bash
# Vector embedding model (768 dimensions)
ollama pull nomic-embed-text

# Fallback/Extraction models
ollama pull qwen3:8b

# Primary synthesis/Reasoning model
ollama pull qwen3:14b
```

### 3. Verify Connection
Confirm Ollama is running and responding on port 11434 (default):
```bash
curl http://localhost:11434/api/tags
```

---

## ⚙️ Environment Variables

Copy [src/backend/.env.example](file:///C:/Users/Porchezhian/Documents/Github%20Local/aros/src/backend/.env.example) to `.env` and fill out the values:

```ini
# Database Connection
DATABASE_URL=postgresql://aros:aros123@localhost:5432/aros

# Vector DB Settings
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Graph DB Settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# APIs and Keys (Optional but recommended for full coverage)
PATENTSVIEW_API_KEY=
LENS_API_KEY=
USPTO_API_KEY=

# Ollama Endpoint (If not running on default localhost:11434)
OLLAMA_HOST=http://localhost:11434
```

---

## 🐳 Docker Services Setup

The root [docker-compose.yml](file:///C:/Users/Porchezhian/Documents/Github%20Local/aros/docker-compose.yml) spins up all secondary dependencies:

1. **aros-postgres**: Exposes port `5432` for structured SQL facts.
2. **aros-qdrant**: Exposes port `6333` for vector search and indexing.
3. **aros-neo4j**: Exposes port `7474` (browser admin) and `7687` (bolt connection).
4. **aros-redis**: Exposes port `6379`.
5. **aros-n8n**: Exposes port `5678` for workflow automation.

To run these services in the background:
```bash
docker-compose up -d
```
To view logs:
```bash
docker-compose logs -f
```
