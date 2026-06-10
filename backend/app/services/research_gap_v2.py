import json
import re
import time
import ollama
from sqlalchemy.orm import Session

from app.models.fusion_report_v2 import FusionReportV2
from app.services.research_gap_v2_storage import save_research_gap_report_v2

def extract_json(text: str) -> dict:
    fields = [
        "saturated_areas", "underexplored_areas", "missing_implementations",
        "missing_datasets", "patent_white_spaces", "emerging_opportunities",
        "high_impact_research_directions", "ieee_publication_opportunities",
        "commercial_opportunities", "recommended_research_projects",
        "executive_summary"
    ]
    
    # helper to process fields and confidence
    def clean_data(d):
        if not isinstance(d, dict):
            return {}
        for f in fields:
            if f not in d:
                d[f] = ""
        if "confidence_score" in d:
            try:
                d["confidence_score"] = float(d["confidence_score"])
            except (ValueError, TypeError):
                d["confidence_score"] = 0.0
        else:
            d["confidence_score"] = 0.0
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
        pattern = rf'"{field}"\s*:\s*"([\s\S]*?)"(?=\s*(?:,|}}))'
        match_field = re.search(pattern, text)
        if match_field:
            val = match_field.group(1)
            val = val.replace('\\"', '"').replace('\\n', '\n')
            parsed[field] = val
        else:
            parsed[field] = ""

    # Parse confidence score field
    pattern_conf = r'"confidence_score"\s*:\s*(\d+(?:\.\d+)?)'
    match_conf = re.search(pattern_conf, text)
    if match_conf:
        try:
            parsed["confidence_score"] = float(match_conf.group(1))
        except:
            parsed["confidence_score"] = 0.0
    else:
        parsed["confidence_score"] = 0.0

    # If any keys were successfully parsed, return it
    if any(parsed.values()):
        return parsed

    # 5. Last resort fallback
    res = {field: "" if field != "executive_summary" else text for field in fields}
    res["confidence_score"] = 0.0
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


def generate_research_gap_v2(
    db: Session,
    project_id: str,
    topic: str
):
    # Retrieve latest Fusion V2 report
    fusion_report = (
        db.query(FusionReportV2)
        .filter(FusionReportV2.project_id == project_id)
        .order_by(FusionReportV2.created_at.desc())
        .first()
    )
    
    if not fusion_report:
        raise ValueError(f"No Fusion V2 report found for project_id {project_id}. Please generate Fusion V2 first.")

    # Format synthesis text
    fusion_report_v2_text = (
        f"Topic: {fusion_report.topic}\n\n"
        f"RESEARCH LANDSCAPE:\n{fusion_report.research_landscape or 'N/A'}\n\n"
        f"INFLUENTIAL WORK:\n{fusion_report.influential_work or 'N/A'}\n\n"
        f"IMPLEMENTATIONS:\n{fusion_report.implementations or 'N/A'}\n\n"
        f"PATENT ACTIVITY:\n{fusion_report.patent_activity or 'N/A'}\n\n"
        f"DATASETS:\n{fusion_report.datasets or 'N/A'}\n\n"
        f"EMERGING TRENDS:\n{fusion_report.emerging_trends or 'N/A'}\n\n"
        f"KNOWLEDGE GRAPH INSIGHTS:\n{fusion_report.knowledge_graph_insights or 'N/A'}\n\n"
        f"CONSENSUS FINDINGS:\n{fusion_report.consensus_findings or 'N/A'}\n\n"
        f"CONTRADICTIONS:\n{fusion_report.contradictions or 'N/A'}\n\n"
        f"RESEARCH OPPORTUNITIES:\n{fusion_report.research_opportunities or 'N/A'}\n\n"
        f"EXECUTIVE SUMMARY:\n{fusion_report.executive_summary or 'N/A'}\n"
    )

    system_prompt = (
        "You are a senior research strategist, IEEE reviewer, R&D director, and patent analyst.\n\n"
        "Analyze the supplied Fusion V2 report.\n\n"
        "Identify:\n"
        "1. Saturated Areas\n"
        "2. Underexplored Areas\n"
        "3. Missing Implementations\n"
        "4. Missing Datasets\n"
        "5. Patent White Spaces\n"
        "6. Emerging Opportunities\n"
        "7. High Impact Research Directions\n"
        "8. IEEE Publication Opportunities\n"
        "9. Commercial Opportunities\n"
        "10. Recommended Research Projects\n"
        "11. Executive Summary\n"
        "12. Confidence Score\n\n"
        "Use only supplied evidence. Do not invent facts. Explain reasoning clearly.\n\n"
        "You MUST return a JSON object containing these 12 exact fields: "
        "\"saturated_areas\", \"underexplored_areas\", \"missing_implementations\", "
        "\"missing_datasets\", \"patent_white_spaces\", \"emerging_opportunities\", "
        "\"high_impact_research_directions\", \"ieee_publication_opportunities\", "
        "\"commercial_opportunities\", \"recommended_research_projects\", "
        "\"executive_summary\", and \"confidence_score\" (float between 0.0 and 1.0 based on evidence depth/quality)."
    )

    user_prompt = f"""Analyze the following Fusion V2 report for the topic "{topic}":

{fusion_report_v2_text}

You MUST return a JSON object with the following fields:
{{
  "saturated_areas": "detailed reasoning...",
  "underexplored_areas": "detailed reasoning...",
  "missing_implementations": "detailed reasoning...",
  "missing_datasets": "detailed reasoning...",
  "patent_white_spaces": "detailed reasoning...",
  "emerging_opportunities": "detailed reasoning...",
  "high_impact_research_directions": "detailed reasoning...",
  "ieee_publication_opportunities": "detailed reasoning...",
  "commercial_opportunities": "detailed reasoning...",
  "recommended_research_projects": "detailed reasoning...",
  "executive_summary": "detailed reasoning...",
  "confidence_score": 0.88
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
    confidence_score_val = sections.pop("confidence_score", 0.0)

    # Save
    report = save_research_gap_report_v2(
        db=db,
        project_id=project_id,
        topic=topic,
        sections=sections,
        confidence_score=confidence_score_val,
        model_used=model_used,
        generation_time_ms=generation_time_ms,
        full_report=raw_response
    )

    return report
