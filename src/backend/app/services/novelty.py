import json
import re
from sqlalchemy.orm import Session

from app.models.fusion_report_v2 import FusionReportV2
from app.models.research_gap_v2 import ResearchGapReportV2
from app.models.patent import Patent
from app.models.github_repo import GithubRepo
from app.models.citation import CitationRecord
from app.services.novelty_storage import save_novelty_report
from app.services.ollama_client import run_ollama_chat
from app.services.json_parser import extract_json_from_text

MAX_CONTEXT_CHARS = 12000

def extract_json(text: str) -> dict:
    text_fields = [
        "research_novelty_analysis", "implementation_novelty_analysis",
        "patent_novelty_analysis", "commercial_novelty_analysis",
        "competitive_landscape", "prior_art_risk", "implementation_difficulty",
        "publication_potential", "recommended_next_steps"
    ]
    score_fields = [
        "research_novelty_score", "implementation_novelty_score",
        "patent_novelty_score", "commercial_novelty_score",
        "overall_novelty_score", "patentability_score"
    ]
    return extract_json_from_text(text, text_fields=text_fields, number_fields=score_fields, confidence_field="confidence_score")


def generate_novelty_report(
    db: Session,
    project_id: str,
    topic: str
):
    # Fetch latest Fusion V2
    fusion_report = (
        db.query(FusionReportV2)
        .filter(FusionReportV2.project_id == project_id)
        .order_by(FusionReportV2.created_at.desc())
        .first()
    )
    if not fusion_report:
        raise ValueError(f"No Fusion V2 report found for project_id {project_id}. Please generate Fusion V2 first.")

    # Fetch latest Research Gap V2
    gap_report = (
        db.query(ResearchGapReportV2)
        .filter(ResearchGapReportV2.project_id == project_id)
        .order_by(ResearchGapReportV2.created_at.desc())
        .first()
    )
    if not gap_report:
        raise ValueError(f"No Research Gap V2 report found for project_id {project_id}. Please generate Research Gap V2 first.")

    # Fetch top 20 Patents
    patents = db.query(Patent).filter(Patent.project_id == project_id, Patent.is_verified == True).all()
    def patent_key(p):
        if p.publication_date:
            return p.publication_date
        if p.created_at:
            return str(p.created_at)
        return ""
    patents_sorted = sorted(patents, key=patent_key, reverse=True)
    top_patents = patents_sorted[:20]

    # Fetch top 20 GithubRepos
    repos = db.query(GithubRepo).filter(GithubRepo.project_id == project_id).all()
    repos_sorted = sorted(repos, key=lambda x: x.stars or 0, reverse=True)
    top_repos = repos_sorted[:20]

    # Fetch top 20 Citations
    citations = db.query(CitationRecord).filter(CitationRecord.project_id == project_id).all()
    citations_sorted = sorted(citations, key=lambda x: x.citation_count or 0, reverse=True)
    top_citations = citations_sorted[:20]

    # Deterministic density scores calculation (0-100)
    patents_total = len(patents)
    repos_total = len(repos)
    citations_total = len(citations)
    
    patent_density_score = min(patents_total * 5, 100)
    github_density_score = min(repos_total * 5, 100)
    citation_density_score = min(citations_total * 5, 100)

    # Context assembly
    context_parts = []
    
    # Fusion V2
    fusion_text = (
        f"FUSION V2 REPORT:\n"
        f"- Executive Summary: {fusion_report.executive_summary or 'N/A'}\n"
        f"- Research Landscape: {fusion_report.research_landscape or 'N/A'}\n"
        f"- Implementations: {fusion_report.implementations or 'N/A'}\n"
        f"- Patent Activity: {fusion_report.patent_activity or 'N/A'}\n"
        f"- Research Opportunities: {fusion_report.research_opportunities or 'N/A'}\n"
    )
    context_parts.append(fusion_text)
    
    # Research Gap V2
    gap_text = (
        f"RESEARCH GAP V2 REPORT:\n"
        f"- Underexplored Areas: {gap_report.underexplored_areas or 'N/A'}\n"
        f"- Missing Implementations: {gap_report.missing_implementations or 'N/A'}\n"
        f"- Patent White Spaces: {gap_report.patent_white_spaces or 'N/A'}\n"
        f"- Emerging Opportunities: {gap_report.emerging_opportunities or 'N/A'}\n"
        f"- High Impact Research Directions: {gap_report.high_impact_research_directions or 'N/A'}\n"
        f"- Recommended Research Projects: {gap_report.recommended_research_projects or 'N/A'}\n"
    )
    context_parts.append(gap_text)
    
    # Patents
    if top_patents:
        pat_text = "TOP PATENTS:\n"
        for pat in top_patents:
            abs_snippet = pat.abstract[:150] if pat.abstract else "No abstract"
            pat_text += f"- Title: {pat.title} | Patent #: {pat.patent_number} | Abstract: {abs_snippet}...\n"
        context_parts.append(pat_text)
        
    # GitHub
    if top_repos:
        repo_text = "TOP GITHUB REPOSITORIES:\n"
        for repo in top_repos:
            desc_snippet = repo.description[:150] if repo.description else "No description"
            repo_text += f"- Repo: {repo.repo_name} | Stars: {repo.stars} | Desc: {desc_snippet}\n"
        context_parts.append(repo_text)
        
    # Citations
    if top_citations:
        cit_text = "TOP CITED PAPERS:\n"
        for cit in top_citations:
            cit_text += f"- Title: {cit.paper_title} | Citations: {cit.citation_count} (Influential: {cit.influential_citation_count or 0})\n"
        context_parts.append(cit_text)

    # Join and check limit
    full_context = ""
    for part in context_parts:
        if len(full_context) + len(part) + 50 > MAX_CONTEXT_CHARS:
            full_context += "\n...[Context truncated to stay within character limits]...\n"
            break
        full_context += part + "\n"

    # Supporting evidence dictionary to store
    supporting_evidence = {
        "top_papers": [
            {
                "title": p.get("title"),
                "authors": p.get("authors"),
                "year": p.get("year"),
                "source": p.get("source"),
                "pdf_url": p.get("pdf_url")
            } for p in fusion_report.supporting_evidence.get("top_papers", [])[:20]
        ] if fusion_report.supporting_evidence else [],
        "top_patents": [
            {
                "title": pat.title,
                "patent_number": pat.patent_number,
                "assignee": pat.assignee,
                "publication_date": pat.publication_date
            } for pat in top_patents
        ],
        "top_repositories": [
            {
                "repo_name": repo.repo_name,
                "owner": repo.owner,
                "stars": repo.stars,
                "description": repo.description
            } for repo in top_repos
        ],
        "top_citations": [
            {
                "paper_title": cit.paper_title,
                "authors": cit.authors,
                "citation_count": cit.citation_count,
                "influential_citation_count": cit.influential_citation_count
            } for cit in top_citations
        ]
    }

    # Prompts
    system_prompt = (
        "You are:\n"
        "- Senior Research Director\n"
        "- Patent Examiner\n"
        "- IEEE Reviewer\n"
        "- Technology Scout\n"
        "- Venture Capital Technical Analyst\n\n"
        "Evaluate the novelty of the proposed research topic using the supplied evidence and deterministic baseline density scores only.\n\n"
        "Density Scores Context:\n"
        "- A high density score indicates the area is crowded (e.g. many patents, high stars, many citations).\n"
        "- A low density score indicates a possible white space or lack of prior work.\n\n"
        "Assess:\n"
        "1. Research Novelty (Score 0-100: is this heavily researched?)\n"
        "2. Implementation Novelty (Score 0-100: do open-source implementations already exist?)\n"
        "3. Patent Novelty (Score 0-100: are similar patents present?)\n"
        "4. Commercial Novelty (Score 0-100: is commercial market activity crowded?)\n"
        "5. Competitive Landscape\n"
        "6. Prior Art Risk\n"
        "7. Implementation Difficulty\n"
        "8. Publication Potential\n"
        "9. Patentability (Score 0-100)\n"
        "10. Recommended Next Steps\n"
        "11. Overall Novelty Score (Weighted average of Research, Implementation, Patent, and Commercial Novelty)\n"
        "12. Confidence Score (Float 0.0-1.0 based on evidence quality)\n\n"
        "Do not invent facts. Use only supplied evidence.\n\n"
        "You MUST return a JSON object with the following fields:\n"
        "- \"research_novelty_score\" (integer 0-100)\n"
        "- \"implementation_novelty_score\" (integer 0-100)\n"
        "- \"patent_novelty_score\" (integer 0-100)\n"
        "- \"commercial_novelty_score\" (integer 0-100)\n"
        "- \"overall_novelty_score\" (integer 0-100)\n"
        "- \"research_novelty_analysis\" (string)\n"
        "- \"implementation_novelty_analysis\" (string)\n"
        "- \"patent_novelty_analysis\" (string)\n"
        "- \"commercial_novelty_analysis\" (string)\n"
        "- \"competitive_landscape\" (string)\n"
        "- \"prior_art_risk\" (string)\n"
        "- \"implementation_difficulty\" (string)\n"
        "- \"publication_potential\" (string)\n"
        "- \"patentability_score\" (integer 0-100)\n"
        "- \"recommended_next_steps\" (string)\n"
        "- \"confidence_score\" (float 0.0-1.0)"
    )

    user_prompt = f"""Analyze the novelty for the topic "{topic}".

EVIDENCE SOURCES:

{full_context}

DETERMINISTIC DENSITY SCORES (0-100):
- Patent Density Score: {patent_density_score} (calculated from {patents_total} patents)
- GitHub Density Score: {github_density_score} (calculated from {repos_total} repositories)
- Citation Density Score: {citation_density_score} (calculated from {citations_total} citations)

You MUST return a JSON object with the following fields:
{{
  "research_novelty_score": 85,
  "implementation_novelty_score": 75,
  "patent_novelty_score": 90,
  "commercial_novelty_score": 60,
  "overall_novelty_score": 78,
  "research_novelty_analysis": "reasoning...",
  "implementation_novelty_analysis": "reasoning...",
  "patent_novelty_analysis": "reasoning...",
  "commercial_novelty_analysis": "reasoning...",
  "competitive_landscape": "reasoning...",
  "prior_art_risk": "reasoning...",
  "implementation_difficulty": "reasoning...",
  "publication_potential": "reasoning...",
  "patentability_score": 80,
  "recommended_next_steps": "reasoning...",
  "confidence_score": 0.85
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    start_time = time.time()
    raw_response, model_used = run_ollama_chat(messages)
    generation_time_ms = int((time.time() - start_time) * 1000)

    # Parse
    sections = extract_json(raw_response)

    # Save
    report = save_novelty_report(
        db=db,
        project_id=project_id,
        topic=topic,
        sections=sections,
        model_used=model_used,
        generation_time_ms=generation_time_ms,
        supporting_evidence=supporting_evidence,
        full_report=raw_response
    )

    return report
