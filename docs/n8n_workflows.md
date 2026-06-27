# n8n Orchestration & Workflows

AROS uses **n8n** as an autonomous agent orchestrator to run long-running collection, validation, embedding, and synthesis pipelines.

---

## ❓ Why n8n?

Orchestrating agentic research requires coordinating:
1. Long API requests with timeout fallbacks.
2. Interlocking processing steps (scraping -> database insertions -> vector embedding -> LLM summarization).
3. Complex conditional logic and retry structures.

n8n offers visual node structures, built-in rate-limiting, SQLite logging, and instant API webhook endpoints.

---

## 🛠️ n8n Webhook Entry Point

When a user clicks "Start Research" on the frontend, the FastAPI backend processes the request and POSTs a payload to the n8n webhook:

* **Webhook Endpoint**: `http://localhost:5678/webhook-test/research` (or production endpoint `/webhook/research`)
* **Trigger Payload**:
  ```json
  {
    "project_id": "84906553-9a61-4abd-9f36-df37a29fa51c",
    "run_id": "a7b7d374-2380-4228-b2f3-1e7a3e4b7c67",
    "topic": "Edge AI Mesh Networks"
  }
  ```

---

## 🚀 Rebuilding the Workflow Sequence

Because n8n workflows are stored inside the local SQLite docker volume, new repository clones start with a blank n8n setup. 

To configure n8n to execute the pipeline, create an n8n workflow with the following nodes:

### 1. Webhook Node (Trigger)
* **Method**: `POST`
* **Path**: `research`
* **Response Mode**: `Immediately (200 OK)`

### 2. Research Steps & API Calls
The workflow should perform the following actions sequentially. Each step calls the backend REST API to perform the work, and then updates the run status:

```mermaid
graph TD
    Trigger[1. Webhook Triggered] --> Step1[2. Search Literature]
    Step1 -->|POST /papers/project/{id}| Step2[3. Search Patents]
    Step2 -->|POST /patents/project/{id}| Step3[4. Search Datasets]
    Step3 -->|POST /datasets/project/{id}| Step4[5. Retrieve Trends]
    Step4 -->|POST /trends/project/{id}| Step5[6. Retrieve Citations]
    Step5 -->|POST /citations/project/{id}| Step6[7. Rebuild Graph]
    Step6 -->|POST /graph/project/{id}| Step7[8. Generate Fusion V2]
    Step7 -->|POST /fusion-v2/project/{id}| Step8[9. Analyze Research Gap]
    Step8 -->|POST /research-gap-v2/project/{id}| Step9[10. Assess Novelty]
    Step9 -->|POST /novelty/project/{id}| Step10[11. Assess Patent Opportunity]
    Step10 -->|POST /patent-opportunity/project/{id}| Step11[12. Compile Final Report]
    Step11 -->|POST /report-v1/project/{id}| Step12[13. Complete Run]
    
    classDef api fill:#4f46e5,stroke:#fff,color:#fff;
    class Step1,Step2,Step3,Step4,Step5,Step6,Step7,Step8,Step9,Step10,Step11 api;
```

For each step, configure n8n to call a `PATCH` request to `/research-runs/{run_id}` updating status to the current step (e.g. `papers_completed`, `patents_completed`, `fusion_completed`) to update the frontend progress bar in real-time.
