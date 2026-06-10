import json
import re
import time
import ollama
from sqlalchemy.orm import Session

from app.models.fusion_report_v2 import FusionReportV2
from app.models.research_gap_v2 import ResearchGapReportV2
from app.models.novelty_report import NoveltyReport
from app.models.patent_opportunity import PatentOpportunity
from app.services.report_v1_storage import save_report_v1

MAX_CONTEXT_CHARS = 12000

def extract_json(text: str) -> dict:
    text_fields = [
        "executive_summary", "research_landscape", "research_gaps",
        "novelty_assessment", "patent_opportunities", "ieee_publication_plan",
        "patent_filing_plan", "commercialization_strategy", "research_roadmap",
        "next_actions"
    ]
    
    def clean_data(d):
        if not isinstance(d, dict):
            return {}
        res = {}
        for f in text_fields:
            res[f] = str(d.get(f, ""))
        
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


def generate_report_v1(
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

    # Fetch latest Patent Opportunity Report
    patent_op = (
        db.query(PatentOpportunity)
        .filter(PatentOpportunity.project_id == project_id)
        .order_by(PatentOpportunity.created_at.desc())
        .first()
    )
    if not patent_op:
        raise ValueError(f"No Patent Opportunity report found for project_id {project_id}. Please generate Patent Opportunity report first.")

    # Context assembly
    context_parts = []
    
    # Fusion V2
    fusion_text = (
        f"FUSION V2 REPORT SUMMARY:\n"
        f"- Executive Summary: {fusion_report.executive_summary or 'N/A'}\n"
        f"- Research Landscape: {fusion_report.research_landscape or 'N/A'}\n"
        f"- Patent Activity: {fusion_report.patent_activity or 'N/A'}\n"
        f"- Research Opportunities: {fusion_report.research_opportunities or 'N/A'}\n"
    )
    context_parts.append(fusion_text)
    
    # Research Gap V2
    gap_text = (
        f"RESEARCH GAP V2 REPORT SUMMARY:\n"
        f"- Underexplored Areas: {gap_report.underexplored_areas or 'N/A'}\n"
        f"- Missing Implementations: {gap_report.missing_implementations or 'N/A'}\n"
        f"- Patent White Spaces: {gap_report.patent_white_spaces or 'N/A'}\n"
        f"- Recommended Research Projects: {gap_report.recommended_research_projects or 'N/A'}\n"
    )
    context_parts.append(gap_text)
    
    # Novelty Report
    novelty_text = (
        f"NOVELTY ASSESSMENT SUMMARY:\n"
        f"- Overall Novelty Score: {novelty_report.overall_novelty_score}\n"
        f"- Research Novelty Analysis: {novelty_report.research_novelty_analysis or 'N/A'}\n"
        f"- Implementation Novelty Analysis: {novelty_report.implementation_novelty_analysis or 'N/A'}\n"
        f"- Competitive Landscape: {novelty_report.competitive_landscape or 'N/A'}\n"
        f"- Prior Art Risk: {novelty_report.prior_art_risk or 'N/A'}\n"
    )
    context_parts.append(novelty_text)
    
    # Patent Opportunity Report
    patent_text = (
        f"PATENT OPPORTUNITY REPORT SUMMARY:\n"
        f"- Opportunity Score: {patent_op.opportunity_score}\n"
        f"- Patentability Score: {patent_op.patentability_score}\n"
        f"- White Space Analysis: {patent_op.white_space_analysis or 'N/A'}\n"
        f"- Closest Prior Art: {patent_op.closest_prior_art or 'N/A'}\n"
        f"- Independent Claim Draft: {patent_op.independent_claim_draft or 'N/A'}\n"
        f"- Filing Strategy: {patent_op.filing_strategy or 'N/A'}\n"
        f"- Recommended Jurisdictions: {patent_op.recommended_jurisdictions or 'N/A'}\n"
    )
    context_parts.append(patent_text)

    # Join and check limit
    full_context = ""
    for part in context_parts:
        if len(full_context) + len(part) + 50 > MAX_CONTEXT_CHARS:
            full_context += "\n...[Context truncated to stay within character limits]...\n"
            break
        full_context += part + "\n"

    # Supporting Evidence
    supporting_evidence = {
        "fusion_report_id": str(fusion_report.id),
        "research_gap_report_id": str(gap_report.id),
        "novelty_report_id": str(novelty_report.id),
        "patent_opportunity_report_id": str(patent_op.id)
    }

    # Prompts
    system_prompt = (
        "You are a lead research director, deep tech investor, USPTO patent attorney, and chief science officer.\n\n"
        "Synthesize the provided reports (Fusion V2, Research Gap V2, Novelty Report, and Patent Opportunity Report) into a final comprehensive research dossier for the topic.\n\n"
        "Identify:\n"
        "1. Executive Summary\n"
        "2. Research Landscape\n"
        "3. Research Gaps\n"
        "4. Novelty Assessment\n"
        "5. Patent Opportunities\n"
        "6. IEEE Publication Plan\n"
        "7. Patent Filing Plan\n"
        "8. Commercialization Strategy\n"
        "9. Research Roadmap\n"
        "10. Next Actions\n"
        "11. Confidence Score (Float 0.0-1.0 based on evidence depth/quality)\n\n"
        "Do not invent facts. Use only supplied evidence.\n\n"
        "You MUST return a JSON object with the following fields:\n"
        "- \"executive_summary\" (string)\n"
        "- \"research_landscape\" (string)\n"
        "- \"research_gaps\" (string)\n"
        "- \"novelty_assessment\" (string)\n"
        "- \"patent_opportunities\" (string)\n"
        "- \"ieee_publication_plan\" (string)\n"
        "- \"patent_filing_plan\" (string)\n"
        "- \"commercialization_strategy\" (string)\n"
        "- \"research_roadmap\" (string)\n"
        "- \"next_actions\" (string)\n"
        "- \"confidence_score\" (float 0.0-1.0)"
    )

    user_prompt = f"""Synthesize the final research dossier for the topic "{topic}".

EVIDENCE SOURCES:

{full_context}

You MUST return a JSON object with the following fields:
{{
  "executive_summary": "detailed synthesis...",
  "research_landscape": "detailed synthesis...",
  "research_gaps": "detailed synthesis...",
  "novelty_assessment": "detailed synthesis...",
  "patent_opportunities": "detailed synthesis...",
  "ieee_publication_plan": "detailed synthesis...",
  "patent_filing_plan": "detailed synthesis...",
  "commercialization_strategy": "detailed synthesis...",
  "research_roadmap": "detailed synthesis...",
  "next_actions": "detailed synthesis...",
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
    report = save_report_v1(
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
