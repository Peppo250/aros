import os
import re
import json
import requests
from datetime import datetime, timezone

from app.services.ollama_client import run_ollama_chat
from app.services.patent_providers import (
    verify_patent_record,
    search_patentsview,
    search_lens,
    search_uspto,
    search_google_patents,
    search_europe_pmc
)
from app.services.patent_scoring import (
    validate_patents_batch,
    calculate_scores
)

def generate_expanded_queries_fallback(topic: str) -> list:
    words = [w.lower() for w in re.findall(r'\w+', topic) if len(w) > 2]
    tech_synonyms = {
        "edge": ["edge", "decentralized", "iot", "distributed", "local", "fog", "swarm", "boundary", "terminal"],
        "ai": ["ai", "artificial intelligence", "learning", "inference", "model", "intelligence", "neural", "cognitive"],
        "mesh": ["mesh", "network", "routing", "grid", "peer-to-peer", "topology", "communication", "ad-hoc", "interconnected"],
        "federated": ["federated", "collaborative", "decentralized", "distributed", "privacy-preserving"],
        "learning": ["learning", "training", "optimization", "adaptation"],
        "uav": ["uav", "drone", "unmanned", "autonomous", "quadcopter", "aerial"],
        "swarm": ["swarm", "fleet", "collective", "coordinated", "collaborative"],
        "disaster": ["disaster", "emergency", "crisis", "resilient", "backup", "recovery", "failure"],
        "communication": ["communication", "telecom", "transmission", "networking", "link", "relay"],
        "agents": ["agent", "agents", "autonomous", "actor", "decision-maker", "bot"],
        "smart": ["smart", "intelligent", "adaptive", "automated"],
        "city": ["city", "urban", "infrastructure", "municipal"],
    }
    
    extensions = []
    for w in words:
        found = False
        for key, syns in tech_synonyms.items():
            if w.startswith(key) or key.startswith(w):
                extensions.append(syns)
                found = True
                break
        if not found:
            extensions.append([w, f"{w} system", f"{w} technology"])
            
    queries = [topic]
    import itertools
    combinations = list(itertools.product(*extensions))
    for combo in combinations[:40]:
        query_str = " ".join(combo)
        if query_str not in queries:
            queries.append(query_str)
            
    extra_phrases = [
        "distributed intelligence network",
        "decentralized model execution",
        "autonomous mesh node",
        "intelligent infrastructure management",
        "collaborative edge computing",
        "fault-tolerant communication routing",
        "neural network optimization at edge"
    ]
    for p in extra_phrases:
        if len(queries) >= 45:
            break
        queries.append(p)
        
    return queries[:50]

def generate_expanded_queries(topic: str) -> list:
    system_prompt = (
        "You are a patent retrieval agent. Generate a list of 20 to 50 search query variations or domain-specific terminology "
        "for the given research topic. The queries should be optimized for patent keyword matching.\n"
        "You MUST return a JSON list of strings, for example: [\"query1\", \"query2\", ...]"
    )
    user_prompt = f"Topic: {topic}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        raw_response, _ = run_ollama_chat(messages, primary_model="qwen2.5:1.5b", fallback_model="qwen3:8b")
        match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", raw_response)
        json_str = match.group(1).strip() if match else raw_response.strip()
        queries = json.loads(json_str)
        if isinstance(queries, list) and len(queries) >= 5:
            if len(queries) < 20:
                fallback_queries = generate_expanded_queries_fallback(topic)
                for fq in fallback_queries:
                    if fq not in queries and len(queries) < 50:
                        queries.append(fq)
            return [str(q) for q in queries[:50]]
    except Exception as e:
        print(f"Failed to generate query expansions using LLM: {e}. Using rule-based fallback.")
    
    return generate_expanded_queries_fallback(topic)

def search_patents(topic: str, limit: int = 20):
    queries = generate_expanded_queries(topic)
    print(f"Expanded queries for '{topic}' ({len(queries)}): {queries}")
    
    unique_patents = {}
    
    # Tier 1: PatentsView
    try:
        pv_patents = search_patentsview(topic, limit=limit)
        for p in pv_patents:
            p_num = p["patent_number"]
            if p_num not in unique_patents:
                unique_patents[p_num] = p
    except Exception as e:
        print(f"PatentsView search exception: {e}")
        
    # Tier 2: Lens.org & USPTO
    try:
        lens_patents = search_lens(topic, limit=limit)
        for p in lens_patents:
            p_num = p["patent_number"]
            if p_num not in unique_patents:
                unique_patents[p_num] = p
    except Exception as e:
        print(f"Lens.org search exception: {e}")
        
    try:
        uspto_patents = search_uspto(topic, limit=limit)
        for p in uspto_patents:
            p_num = p["patent_number"]
            if p_num not in unique_patents:
                unique_patents[p_num] = p
    except Exception as e:
        print(f"USPTO search exception: {e}")

    # Tier 3: Google Patents & Europe PMC
    for q in queries[:5]:
        try:
            gp_patents = search_google_patents(q)
            for p in gp_patents:
                p_num = p["patent_number"]
                if p_num not in unique_patents:
                    unique_patents[p_num] = p
        except Exception as e:
            print(f"Google Patents scraper exception for query '{q}': {e}")
            
    try:
        epmc_patents = search_europe_pmc(queries, limit=limit)
        for p in epmc_patents:
            p_num = p["patent_number"]
            if p_num not in unique_patents:
                unique_patents[p_num] = p
    except Exception as e:
        print(f"Europe PMC search exception: {e}")

    # Fallback: Europe PMC keyless raw search
    if not unique_patents:
        try:
            print(f"No patents found. Trying keyless fallback on Europe PMC for raw topic: '{topic}'")
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            params = {
                "query": f"({topic}) AND (SRC:PAT)",
                "format": "json",
                "pageSize": limit
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("resultList", {}).get("result", [])
                for item in results:
                    p_num = item.get("id")
                    if p_num and p_num not in unique_patents:
                        unique_patents[p_num] = {
                            "patent_number": p_num,
                            "title": item.get("title") or "",
                            "abstract": item.get("abstractText") or item.get("title") or "",
                            "publication_date": item.get("firstPublicationDate") or f"{item.get('pubYear')}-01-01" if item.get('pubYear') else "2024-01-01",
                            "source": "Europe PMC Fallback",
                            "url": f"https://europepmc.org/article/PAT/{p_num}",
                            "assignee": item.get("patentDetails", {}).get("patentAssignee") or "",
                            "inventor": item.get("authorString") or "",
                            "jurisdiction": p_num[:2] if p_num[:2].isalpha() else "US",
                            "status": "active"
                        }
        except Exception as e:
            print(f"Europe PMC raw topic search exception: {e}")

    # Verification Stage
    verified_results = []
    verification_time = datetime.now(timezone.utc)
    for p_num, p in unique_patents.items():
        if verify_patent_record(p):
            p["is_verified"] = True
            p["verification_source"] = p["source"]
            p["verification_timestamp"] = verification_time
            verified_results.append(p)
        else:
            print(f"Discarded invalid patent: {p_num} from {p.get('source')}")

    if not verified_results:
        print("No verified patents retrieved from configured patent databases.")
        return []

    # Batch LLM Validation
    validation_results = validate_patents_batch(verified_results, topic)
    
    validated_results = []
    for r in verified_results:
        p_num = r.get("patent_number")
        val_info = validation_results.get(p_num, {})
        val_score = val_info.get("validation_score", 8)
        
        if val_score >= 6:
            r["validation_score"] = float(val_score)
            validated_results.append(r)
        else:
            print(f"Discarded weak match patent {p_num} (Score: {val_score})")

    if not validated_results and verified_results:
        validated_results = verified_results
        for r in validated_results:
            r["validation_score"] = 6.0
            
    # Scoring
    scored_results = calculate_scores(validated_results, topic, queries)
    scored_results.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
    
    return scored_results[:limit]
