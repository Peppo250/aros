import json
import re
import ollama
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.github_repo import GithubRepo
from app.models.patent import Patent
from app.models.dataset import Dataset
from app.models.trend import TrendSignal
from app.models.citation import CitationRecord
from app.services.graph_builder import Neo4jClient
from app.services.fusion_v2_storage import save_fusion_report_v2

MAX_CONTEXT_CHARS = 12000

def extract_json(text: str) -> dict:
    fields = [
        "research_landscape", "influential_work", "implementations",
        "patent_activity", "datasets", "emerging_trends",
        "knowledge_graph_insights", "consensus_findings", "contradictions",
        "research_opportunities", "executive_summary"
    ]
    
    # helper to process confidence
    def clean_data(d):
        if not isinstance(d, dict):
            return {}
        for f in fields:
            if f not in d:
                d[f] = ""
        if "confidence" in d:
            try:
                d["confidence"] = float(d["confidence"])
            except (ValueError, TypeError):
                d["confidence"] = 0.0
        else:
            d["confidence"] = 0.0
        return d

    # 1. Try to load directly
    try:
        data = json.loads(text.strip())
        if isinstance(data, dict):
            return clean_data(data)
    except json.JSONDecodeError:
        pass

    # 2. Try to find a JSON block using regex
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict):
                return clean_data(data)
        except json.JSONDecodeError:
            pass

    # 3. Try to find first '{' and last '}'
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_candidate = text[start_idx:end_idx+1]
        try:
            data = json.loads(json_candidate.strip())
            if isinstance(data, dict):
                return clean_data(data)
        except json.JSONDecodeError:
            pass

    # 4. Fallback parser: Regex extraction of string values
    parsed = {}
    for field in fields:
        # Look for "field_name": "value"
        pattern = rf'"{field}"\s*:\s*"([\s\S]*?)"(?=\s*(?:,|}}))'
        match_field = re.search(pattern, text)
        if match_field:
            val = match_field.group(1)
            # Unescape newlines and quotes
            val = val.replace('\\"', '"').replace('\\n', '\n')
            parsed[field] = val
        else:
            parsed[field] = ""

    # Parse confidence field
    pattern_conf = r'"confidence"\s*:\s*(\d+(?:\.\d+)?)'
    match_conf = re.search(pattern_conf, text)
    if match_conf:
        try:
            parsed["confidence"] = float(match_conf.group(1))
        except:
            parsed["confidence"] = 0.0
    else:
        parsed["confidence"] = 0.0

    # If any keys were successfully parsed, return it
    if any(parsed.values()):
        return parsed

    # 5. Last resort: map the entire text to executive summary
    res = {field: "" if field != "executive_summary" else text for field in fields}
    res["confidence"] = 0.0
    return res


def run_ollama_chat(messages, primary_model="qwen3:14b", fallback_model="qwen3:8b"):
    try:
        response = ollama.chat(
            model=primary_model,
            messages=messages
        )
        return response["message"]["content"], primary_model
    except Exception as e:
        print(f"Ollama error with model {primary_model}: {e}. Retrying with fallback model {fallback_model}...")
        try:
            response = ollama.chat(
                model=fallback_model,
                messages=messages
            )
            return response["message"]["content"], fallback_model
        except Exception as fallback_err:
            print(f"Ollama fallback error with model {fallback_model}: {fallback_err}")
            raise fallback_err


def generate_fusion_report_v2(
    db: Session,
    project_id: str,
    topic: str
):
    # --- Upgrade 1: Fetch Counts ---
    papers_total = db.query(Paper).filter(Paper.project_id == project_id).count()
    repos_total = db.query(GithubRepo).filter(GithubRepo.project_id == project_id).count()
    patents_total = db.query(Patent).filter(Patent.project_id == project_id).count()
    datasets_total = db.query(Dataset).filter(Dataset.project_id == project_id).count()
    trends_total = db.query(TrendSignal).filter(TrendSignal.project_id == project_id).count()
    citations_total = db.query(CitationRecord).filter(CitationRecord.project_id == project_id).count()

    # Query Neo4j Client for graph stats & centrality
    neo4j_client = Neo4jClient()
    graph_insights = {
        "node_counts": {},
        "relationship_count": 0,
        "top_connected": [],
        "statistics": {"avg_overlap": 0.0, "max_overlap": 0},
        "most_connected_paper": None,
        "most_connected_repo": None,
        "most_connected_dataset": None
    }
    try:
        graph_insights = neo4j_client.get_graph_insights(project_id)
    except Exception as e:
        print(f"Failed to fetch Neo4j graph insights: {e}")
    finally:
        neo4j_client.close()

    graph_nodes_count = sum(graph_insights.get("node_counts", {}).values())
    graph_relationships_count = graph_insights.get("relationship_count", 0)

    # --- Upgrade 2: Preprocess & Rank Records ---
    
    # 1. Papers: Top 15 ranked by year DESC
    papers = db.query(Paper).filter(Paper.project_id == project_id).all()
    papers_sorted = sorted(papers, key=lambda x: x.year or 0, reverse=True)
    top_papers = papers_sorted[:15]

    # 2. GitHub repos: Top 15 ranked by stars DESC
    repos = db.query(GithubRepo).filter(GithubRepo.project_id == project_id).all()
    repos_sorted = sorted(repos, key=lambda x: x.stars or 0, reverse=True)
    top_repos = repos_sorted[:15]

    # 3. Citations: Top 10 ranked by citation_count DESC
    citations = db.query(CitationRecord).filter(CitationRecord.project_id == project_id).all()
    citations_sorted = sorted(citations, key=lambda x: x.citation_count or 0, reverse=True)
    top_citations = citations_sorted[:10]

    # 4. Trends: Top 10 newest (by published_at DESC or created_at DESC)
    trends = db.query(TrendSignal).filter(TrendSignal.project_id == project_id).all()
    def trend_key(t):
        if t.published_at:
            return t.published_at.timestamp()
        if t.created_at:
            return t.created_at.timestamp()
        return 0
    trends_sorted = sorted(trends, key=trend_key, reverse=True)
    top_trends = trends_sorted[:10]

    # 5. Patents: Top 10 newest (by publication_date DESC or created_at DESC)
    patents = db.query(Patent).filter(Patent.project_id == project_id).all()
    def patent_key(p):
        if p.publication_date:
            return p.publication_date
        if p.created_at:
            return str(p.created_at)
        return ""
    patents_sorted = sorted(patents, key=patent_key, reverse=True)
    top_patents = patents_sorted[:10]

    # 6. Datasets: Top 10 newest (by created_at DESC)
    datasets = db.query(Dataset).filter(Dataset.project_id == project_id).all()
    datasets_sorted = sorted(datasets, key=lambda x: x.created_at.timestamp() if x.created_at else 0, reverse=True)
    top_datasets = datasets_sorted[:10]

    # --- Build Context (Strict Max 12000 Chars limit) ---
    context_parts = []
    
    # Add Graph summary
    graph_summary_text = (
        f"KNOWLEDGE GRAPH SUMMARY:\n"
        f"- Total Nodes: {graph_nodes_count} (Paper: {graph_insights.get('node_counts', {}).get('Paper', 0)}, "
        f"Repository: {graph_insights.get('node_counts', {}).get('Repository', 0)}, "
        f"Patent: {graph_insights.get('node_counts', {}).get('Patent', 0)}, "
        f"Dataset: {graph_insights.get('node_counts', {}).get('Dataset', 0)}, "
        f"Trend: {graph_insights.get('node_counts', {}).get('Trend', 0)})\n"
        f"- Total Relationships: {graph_relationships_count}\n"
        f"- Most Connected Paper: {graph_insights.get('most_connected_paper') or 'N/A'}\n"
        f"- Most Connected Repo: {graph_insights.get('most_connected_repo') or 'N/A'}\n"
        f"- Most Connected Dataset: {graph_insights.get('most_connected_dataset') or 'N/A'}\n"
        f"- Graph Density Stats: Max Overlap: {graph_insights.get('statistics', {}).get('max_overlap', 0)}, "
        f"Avg Overlap: {graph_insights.get('statistics', {}).get('avg_overlap', 0.0):.2f}\n"
    )
    context_parts.append(graph_summary_text)

    # 1. Add Papers
    if top_papers:
        p_text = "RESEARCH PAPERS (Top 15):\n"
        for p in top_papers:
            abs_snippet = p.abstract[:200] if p.abstract else "No abstract"
            p_text += f"- {p.title} ({p.year}) by {p.authors or 'Unknown'}. Abstract: {abs_snippet}...\n"
        context_parts.append(p_text)

    # 2. Add Citations
    if top_citations:
        c_text = "INFLUENTIAL CITATIONS (Top 10):\n"
        for c in top_citations:
            c_text += f"- {c.paper_title} ({c.year}) - {c.citation_count} citations. Authors: {c.authors or 'Unknown'}\n"
        context_parts.append(c_text)

    # 3. Add GitHub Repos
    if top_repos:
        r_text = "GITHUB REPOSITORIES (Top 15):\n"
        for r in top_repos:
            desc_snippet = r.description[:200] if r.description else "No description"
            r_text += f"- {r.repo_name} ({r.stars} stars) by {r.owner or 'Unknown'}. Description: {desc_snippet}\n"
        context_parts.append(r_text)

    # 4. Add Patents
    if top_patents:
        pat_text = "PATENTS (Top 10):\n"
        for pat in top_patents:
            abs_snippet = pat.abstract[:200] if pat.abstract else "No abstract"
            pat_text += f"- {pat.title} ({pat.publication_date}) by {pat.assignee or 'Unknown'}. Abstract: {abs_snippet}...\n"
        context_parts.append(pat_text)

    # 5. Add Datasets
    if top_datasets:
        d_text = "DATASETS (Top 10):\n"
        for d in top_datasets:
            desc_snippet = d.description[:200] if d.description else "No description"
            d_text += f"- {d.name} (Modality: {d.modality or 'N/A'}, Task: {d.task or 'N/A'}). Desc: {desc_snippet}\n"
        context_parts.append(d_text)

    # 6. Add Trends
    if top_trends:
        t_text = "EMERGING TREND SIGNALS (Top 10):\n"
        for t in top_trends:
            desc_snippet = t.description[:200] if t.description else "No description"
            t_text += f"- {t.title} (Relevance Score: {t.relevance_score or 0.0}). Desc: {desc_snippet}\n"
        context_parts.append(t_text)

    # Join and check limit
    full_context = ""
    for part in context_parts:
        if len(full_context) + len(part) + 50 > MAX_CONTEXT_CHARS:
            # Add warning/truncation indicator
            full_context += "\n...[Context truncated to fit within token limit]...\n"
            break
        full_context += part + "\n"

    # --- Upgrade 3: Form Supporting Evidence Dict ---
    supporting_evidence = {
        "top_papers": [
            {
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "source": p.source,
                "pdf_url": p.pdf_url
            } for p in top_papers
        ],
        "top_repositories": [
            {
                "repo_name": r.repo_name,
                "owner": r.owner,
                "stars": r.stars,
                "description": r.description,
                "html_url": r.html_url
            } for r in top_repos
        ],
        "top_cited_papers": [
            {
                "paper_title": c.paper_title,
                "authors": c.authors,
                "year": c.year,
                "citation_count": c.citation_count,
                "source": c.source,
                "url": c.url
            } for c in top_citations
        ],
        "top_patents": [
            {
                "title": pat.title,
                "patent_number": pat.patent_number,
                "assignee": pat.assignee,
                "inventors": pat.inventors,
                "publication_date": pat.publication_date,
                "url": pat.url
            } for pat in top_patents
        ],
        "top_datasets": [
            {
                "name": d.name,
                "description": d.description,
                "task": d.task,
                "modality": d.modality,
                "license": d.license,
                "url": d.url
            } for d in top_datasets
        ],
        "top_trends": [
            {
                "title": t.title,
                "description": t.description,
                "source": t.source,
                "url": t.url,
                "trend_score": t.trend_score,
                "relevance_score": t.relevance_score
            } for t in top_trends
        ]
    }

    # --- Prompts ---
    system_prompt = (
        "You are an elite research intelligence analyst.\n"
        "Analyze all supplied evidence.\n"
        "Do not invent facts. Base conclusions only on the provided information.\n\n"
        "Analyze the following sections:\n"
        "1. Research Landscape\n"
        "2. Influential Work\n"
        "3. Existing Implementations\n"
        "4. Patent Activity\n"
        "5. Available Datasets\n"
        "6. Emerging Trends\n"
        "7. Knowledge Graph Insights\n"
        "8. Consensus Findings\n"
        "9. Contradictions\n"
        "10. Research Opportunities\n"
        "11. Executive Summary\n\n"
        "You MUST return a JSON object containing these 11 exact fields, plus a twelfth field \"confidence\" which is a float between 0.0 and 1.0 representing your confidence in the research findings based on the depth and quality of evidence provided (e.g. many papers and citations = high confidence, few papers or missing sources = low confidence)."
    )

    user_prompt = f"""Analyze the following evidence for the topic "{topic}":

{full_context}

You MUST return a JSON object with the following fields:
{{
  "research_landscape": "detailed analysis...",
  "influential_work": "detailed analysis...",
  "implementations": "detailed analysis...",
  "patent_activity": "detailed analysis...",
  "datasets": "detailed analysis...",
  "emerging_trends": "detailed analysis...",
  "knowledge_graph_insights": "detailed analysis...",
  "consensus_findings": "detailed analysis...",
  "contradictions": "detailed analysis...",
  "research_opportunities": "detailed analysis...",
  "executive_summary": "detailed analysis...",
  "confidence": 0.92
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # --- Upgrade 4: Call Ollama with Fallback ---
    import time
    start_time = time.time()
    raw_response, model_used = run_ollama_chat(messages)
    generation_time_ms = int((time.time() - start_time) * 1000)

    # Parse JSON
    sections = extract_json(raw_response)
    confidence_val = sections.pop("confidence", 0.0)

    # --- Prepare Counts Dict ---
    counts = {
        "papers_count": papers_total,
        "repositories_count": repos_total,
        "patents_count": patents_total,
        "datasets_count": datasets_total,
        "trends_count": trends_total,
        "citations_count": citations_total,
        "graph_nodes_count": graph_nodes_count,
        "graph_relationships_count": graph_relationships_count
    }

    # Retrieval Metadata
    retrieval_metadata = {
        "papers_count": papers_total,
        "repositories_count": repos_total,
        "patents_count": patents_total,
        "datasets_count": datasets_total,
        "trends_count": trends_total,
        "citations_count": citations_total
    }

    # Save to db
    report = save_fusion_report_v2(
        db=db,
        project_id=project_id,
        topic=topic,
        sections=sections,
        counts=counts,
        supporting_evidence=supporting_evidence,
        full_report=raw_response,
        model_used=model_used,
        generation_time_ms=generation_time_ms,
        context_length=len(full_context),
        retrieval_metadata=retrieval_metadata,
        confidence=confidence_val
    )

    return report
