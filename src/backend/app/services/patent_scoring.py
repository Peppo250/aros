import re
import json
from app.services.ollama_client import run_ollama_chat

def validate_patents_batch(patents: list, topic: str) -> dict:
    """
    Validates retrieved patents in batch using LLM reasoning and filters weak matches.
    """
    if not patents:
        return {}
        
    patents_list_text = ""
    for p in patents:
        patents_list_text += f"Number: {p.get('patent_number')}\nTitle: {p.get('title')}\nAbstract: {p.get('abstract')}\n\n"
        
    system_prompt = (
        "You are a Patent Validation Agent.\n"
        "For each patent in the provided list, assess if it is genuinely relevant to the research topic.\n"
        "Assign a validation score from 0 to 10 (where >=6 means relevant, and <6 means irrelevant or weak match).\n"
        "Be strict: for 'edge ai mesh', patents on medical meshes, mechanical meshes, or 3D graphics mesh renderers are NOT relevant (score < 6).\n"
        "You MUST return a JSON object mapping each patent_number to its validation_score (integer 0-10) and a brief reasoning string: {\"US10452382B2\": {\"validation_score\": 8, \"reasoning\": \"...\"}}"
    )
    user_prompt = f"Topic: {topic}\n\nPatents:\n{patents_list_text}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        raw_response, _ = run_ollama_chat(messages, primary_model="qwen2.5:1.5b", fallback_model="qwen3:8b")
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw_response)
        json_str = match.group(1).strip() if match else raw_response.strip()
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Validation Agent batch parsing failed: {e}. Defaulting all to score 8.")
        return {p.get("patent_number"): {"validation_score": 8, "reasoning": "Fallback passing"} for p in patents}

def calculate_scores(patents: list, topic: str, queries: list) -> list:
    """
    Calculates relevance, novelty, priority art overlap, and commercial scores for a patent dataset.
    """
    scored_patents = []
    for p in patents:
        abstract = p.get("abstract") or ""
        title = p.get("title") or ""
        
        topic_words = set(re.findall(r'\w+', topic.lower()))
        abstract_words = set(re.findall(r'\w+', abstract.lower() + " " + title.lower()))
        
        stopwords = {"the", "a", "of", "and", "in", "to", "for", "with", "on", "at", "by", "an", "is", "this", "that", "it"}
        topic_words = topic_words - stopwords
        abstract_words = abstract_words - stopwords
        
        intersection = topic_words.intersection(abstract_words)
        union = topic_words.union(abstract_words)
        semantic_sim = len(intersection) / len(union) if union else 0.0
        semantic_sim = min(semantic_sim * 3.0, 1.0)
        
        matched_queries = 0
        for q in queries:
            if q.lower() in abstract.lower() or q.lower() in title.lower():
                matched_queries += 1
        keyword_overlap = matched_queries / len(queries) if queries else 0.0
        
        citations = p.get("citations_count") or 0
        citation_strength = min(citations / 50.0, 1.0)
        
        date_str = p.get("publication_date") or ""
        year_match = re.search(r'\d{4}', date_str)
        if year_match:
            year = int(year_match.group(0))
            if year >= 2024:
                recency = 1.0
            elif year >= 2020:
                recency = 0.8
            elif year >= 2015:
                recency = 0.5
            else:
                recency = 0.2
        else:
            recency = 0.5
            
        assignee_name = str(p.get("assignee") or "").lower()
        tech_leaders = ["google", "apple", "microsoft", "intel", "samsung", "qualcomm", "huawei", "ibm", "cisco", "nvidia", "amazon", "ericsson", "nokia"]
        is_leader = any(leader in assignee_name for leader in tech_leaders)
        assignee_importance = 1.0 if is_leader else 0.5
        
        relevance_score = (
            0.50 * semantic_sim +
            0.20 * keyword_overlap +
            0.15 * citation_strength +
            0.10 * recency +
            0.05 * assignee_importance
        )
        
        prior_art_overlap = min(semantic_sim * 0.7 + keyword_overlap * 0.3, 1.0)
        novelty_contribution = 1.0 - prior_art_overlap
        commercial_impact = (assignee_importance * 0.4) + (citation_strength * 0.4) + (recency * 0.2)
        
        p["relevance_score"] = float(round(relevance_score, 3))
        p["novelty_contribution_score"] = float(round(novelty_contribution, 3))
        p["commercial_impact_score"] = float(round(commercial_impact, 3))
        p["prior_art_overlap_score"] = float(round(prior_art_overlap, 3))
        
        scored_patents.append(p)
        
    return scored_patents
