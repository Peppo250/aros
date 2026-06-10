import json
import re
import time
import ollama
from sqlalchemy.orm import Session

from app.models.fusion_report_v2 import FusionReportV2
from app.models.research_gap_v2 import ResearchGapReportV2
from app.models.novelty_report import NoveltyReport
from app.models.patent import Patent
from app.services.patent_opportunity_storage import save_patent_opportunity

MAX_CONTEXT_CHARS = 12000

def extract_json(text: str) -> dict:
    text_fields = [
        "white_space_analysis", "closest_prior_art", "independent_claim_draft",
        "dependent_claims_draft", "novel_technical_contributions",
        "commercial_value_analysis", "filing_strategy",
        "recommended_jurisdictions", "recommended_next_steps"
    ]
    score_fields = [
        "opportunity_score", "patentability_score",
        "prior_art_risk_score", "commercial_value_score"
    ]
    
    def clean_data(d):
        if not isinstance(d, dict):
            return {}
        res = {}
        for f in text_fields:
            res[f] = str(d.get(f, ""))
        for f in score_fields:
            try:
                res[f] = float(d.get(f, 0.0))
            except (ValueError, TypeError):
                res[f] = 0.0
        
        # confidence_score
        try:
            res["confidence_score"] = float(d.get("confidence_score", 0.0))
        except (ValueError, TypeError):
            res["confidence_score"] = 0.0
        return res

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

    # 4. Fallback parser: Regex extraction of values
    parsed = {}
    for field in text_fields:
        pattern = rf'"{field}"\s*:\s*"([\s\S]*?)"(?=\s*(?:,|}}))'
        match_field = re.search(pattern, text)
        if match_field:
            val = match_field.group(1)
            val = val.replace('\\"', '"').replace('\\n', '\n')
            parsed[field] = val
        else:
            parsed[field] = ""

    for field in score_fields:
        pattern = rf'"{field}"\s*:\s*(\d+(?:\.\d+)?)'
        match_field = re.search(pattern, text)
        if match_field:
            try:
                parsed[field] = float(match_field.group(1))
            except:
                parsed[field] = 0.0
        else:
            parsed[field] = 0.0

    pattern_conf = r'"confidence_score"\s*:\s*(\d+(?:\.\d+)?)'
    match_conf = re.search(pattern_conf, text)
    if match_conf:
        try:
            parsed["confidence_score"] = float(match_conf.group(1))
        except:
            parsed["confidence_score"] = 0.0
    else:
        parsed["confidence_score"] = 0.0

    return parsed


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


def generate_patent_opportunity(
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

    # Fetch latest Novelty Report
    novelty_report = (
        db.query(NoveltyReport)
        .filter(NoveltyReport.project_id == project_id)
        .order_by(NoveltyReport.created_at.desc())
        .first()
    )
    if not novelty_report:
        raise ValueError(f"No Novelty Report found for project_id {project_id}. Please generate Novelty Report first.")

    # Fetch top 20 Patents
    patents = db.query(Patent).filter(Patent.project_id == project_id).all()
    def patent_key(p):
        if p.publication_date:
            return p.publication_date
        if p.created_at:
            return str(p.created_at)
        return ""
    patents_sorted = sorted(patents, key=patent_key, reverse=True)
    top_patents = patents_sorted[:20]

    # Context assembly
    context_parts = []
    
    # Fusion V2
    fusion_text = (
        f"FUSION V2 REPORT:\n"
        f"- Executive Summary: {fusion_report.executive_summary or 'N/A'}\n"
        f"- Research Landscape: {fusion_report.research_landscape or 'N/A'}\n"
        f"- Patent Activity: {fusion_report.patent_activity or 'N/A'}\n"
        f"- Research Opportunities: {fusion_report.research_opportunities or 'N/A'}\n"
    )
    context_parts.append(fusion_text)
    
    # Research Gap V2
    gap_text = (
        f"RESEARCH GAP V2 REPORT:\n"
        f"- Patent White Spaces: {gap_report.patent_white_spaces or 'N/A'}\n"
        f"- Underexplored Areas: {gap_report.underexplored_areas or 'N/A'}\n"
        f"- High Impact Research Directions: {gap_report.high_impact_research_directions or 'N/A'}\n"
        f"- Recommended Research Projects: {gap_report.recommended_research_projects or 'N/A'}\n"
    )
    context_parts.append(gap_text)
    
    # Novelty Report
    novelty_text = (
        f"NOVELTY ASSESSMENT REPORT:\n"
        f"- Research Novelty Score: {novelty_report.research_novelty_score}\n"
        f"- Implementation Novelty Score: {novelty_report.implementation_novelty_score}\n"
        f"- Patent Novelty Score: {novelty_report.patent_novelty_score}\n"
        f"- Commercial Novelty Score: {novelty_report.commercial_novelty_score}\n"
        f"- Overall Novelty Score: {novelty_report.overall_novelty_score}\n"
        f"- Patentability Score: {novelty_report.patentability_score}\n"
        f"- Competitive Landscape: {novelty_report.competitive_landscape or 'N/A'}\n"
        f"- Prior Art Risk: {novelty_report.prior_art_risk or 'N/A'}\n"
        f"- Recommended Next Steps: {novelty_report.recommended_next_steps or 'N/A'}\n"
    )
    context_parts.append(novelty_text)
    
    # Patents
    if top_patents:
        pat_text = "TOP PATENTS:\n"
        for pat in top_patents:
            abs_snippet = pat.abstract[:150] if pat.abstract else "No abstract"
            pat_text += f"- Title: {pat.title} | Patent #: {pat.patent_number} | Abstract: {abs_snippet}...\n"
        context_parts.append(pat_text)

    # Join and check limit
    full_context = ""
    for part in context_parts:
        if len(full_context) + len(part) + 50 > MAX_CONTEXT_CHARS:
            full_context += "\n...[Context truncated to stay within character limits]...\n"
            break
        full_context += part + "\n"

    # Supporting Evidence
    supporting_evidence = {
        "top_patents": [
            {
                "title": pat.title,
                "patent_number": pat.patent_number,
                "assignee": pat.assignee,
                "publication_date": pat.publication_date
            } for pat in top_patents
        ],
        "fusion_sections": {
            "executive_summary": fusion_report.executive_summary,
            "research_landscape": fusion_report.research_landscape,
            "patent_activity": fusion_report.patent_activity,
            "research_opportunities": fusion_report.research_opportunities
        },
        "novelty_scores": {
            "research_novelty_score": novelty_report.research_novelty_score,
            "implementation_novelty_score": novelty_report.implementation_novelty_score,
            "patent_novelty_score": novelty_report.patent_novelty_score,
            "commercial_novelty_score": novelty_report.commercial_novelty_score,
            "overall_novelty_score": novelty_report.overall_novelty_score,
            "patentability_score": novelty_report.patentability_score
        },
        "gap_sections": {
            "patent_white_spaces": gap_report.patent_white_spaces,
            "underexplored_areas": gap_report.underexplored_areas,
            "high_impact_research_directions": gap_report.high_impact_research_directions,
            "recommended_research_projects": gap_report.recommended_research_projects
        }
    }

    # Prompts
    system_prompt = (
        "You are:\n"
        "- USPTO Patent Examiner\n"
        "- Patent Attorney\n"
        "- R&D Director\n"
        "- Deep Tech Investor\n\n"
        "Analyze the evidence. Identify patent opportunities, claims, and filing strategies based on Fusion V2, Research Gap V2, Novelty Report, and Top Patents.\n\n"
        "Identify:\n"
        "1. White Space Analysis\n"
        "2. Closest Prior Art\n"
        "3. Novel Technical Contributions\n"
        "4. Independent Claim Draft\n"
        "5. Dependent Claim Drafts\n"
        "6. Commercial Value\n"
        "7. Filing Strategy\n"
        "8. Recommended Jurisdictions\n"
        "9. Patent Opportunity Score (0-100)\n"
        "10. Patentability Score (0-100)\n"
        "11. Prior Art Risk Score (0-100)\n"
        "12. Commercial Value Score (0-100)\n"
        "13. Recommended Next Steps\n"
        "14. Confidence Score (Float 0.0-1.0 based on evidence depth/quality)\n\n"
        "Use only supplied evidence. Do not invent prior patents.\n\n"
        "You MUST return a JSON object with the following fields:\n"
        "- \"opportunity_score\" (integer 0-100)\n"
        "- \"patentability_score\" (integer 0-100)\n"
        "- \"prior_art_risk_score\" (integer 0-100)\n"
        "- \"commercial_value_score\" (integer 0-100)\n"
        "- \"white_space_analysis\" (string)\n"
        "- \"closest_prior_art\" (string)\n"
        "- \"independent_claim_draft\" (string)\n"
        "- \"dependent_claims_draft\" (string)\n"
        "- \"novel_technical_contributions\" (string)\n"
        "- \"commercial_value_analysis\" (string)\n"
        "- \"filing_strategy\" (string)\n"
        "- \"recommended_jurisdictions\" (string)\n"
        "- \"recommended_next_steps\" (string)\n"
        "- \"confidence_score\" (float 0.0-1.0)"
    )

    user_prompt = f"""Analyze the patent opportunities for the topic "{topic}".

EVIDENCE SOURCES:

{full_context}

You MUST return a JSON object with the following fields:
{{
  "opportunity_score": 85,
  "patentability_score": 80,
  "prior_art_risk_score": 30,
  "commercial_value_score": 75,
  "white_space_analysis": "reasoning...",
  "closest_prior_art": "reasoning...",
  "independent_claim_draft": "reasoning...",
  "dependent_claims_draft": "reasoning...",
  "novel_technical_contributions": "reasoning...",
  "commercial_value_analysis": "reasoning...",
  "filing_strategy": "reasoning...",
  "recommended_jurisdictions": "reasoning...",
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
    report = save_patent_opportunity(
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
