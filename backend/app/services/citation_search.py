import os
import requests

def search_citations(
    topic: str,
    limit: int = 20
) -> list[dict]:
    ss_url = os.getenv(
        "SEMANTIC_SCHOLAR_URL",
        "https://api.semanticscholar.org/graph/v1/paper/search"
    )
    openalex_url = os.getenv(
        "OPENALEX_URL",
        "https://api.openalex.org/works"
    )

    use_fallback = False
    results = []

    print(f"Searching citations for topic: '{topic}' via Semantic Scholar")
    try:
        response = requests.get(
            ss_url,
            params={
                "query": topic,
                "limit": limit,
                "fields": "title,authors,year,citationCount,influentialCitationCount,url"
            },
            timeout=10
        )
        print(f"Semantic Scholar responded with status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            for item in data:
                # Normalize author list
                authors_list = item.get("authors", [])
                authors_names = [a.get("name") for a in authors_list if a.get("name")]
                authors_str = ", ".join(authors_names)
                
                normalized = {
                    "paper_title": item.get("title") or "Untitled",
                    "authors": authors_str or "Unknown",
                    "authors_json": authors_names,
                    "year": item.get("year"),
                    "citation_count": item.get("citationCount") or 0,
                    "influential_citation_count": item.get("influentialCitationCount") or 0,
                    "url": item.get("url"),
                    "source": "semantic_scholar",
                    "raw_data": item
                }
                results.append(normalized)
            return results
        elif response.status_code in [403, 429, 500]:
            print(f"Semantic Scholar returned status {response.status_code}. Activating OpenAlex fallback.")
            use_fallback = True
        else:
            print(f"Semantic Scholar returned unexpected status {response.status_code}: {response.text}")
            use_fallback = True
    except Exception as e:
        print(f"Semantic Scholar request failed with error: {e}. Activating OpenAlex fallback.")
        use_fallback = True

    if use_fallback:
        print(f"Searching citations for topic: '{topic}' via OpenAlex fallback")
        try:
            response = requests.get(
                openalex_url,
                params={
                    "search": topic,
                    "per_page": limit
                },
                timeout=10
            )
            print(f"OpenAlex responded with status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json().get("results", [])
                for item in data:
                    authorships = item.get("authorships", [])
                    authors_names = [
                        auth.get("author", {}).get("display_name")
                        for auth in authorships
                        if auth.get("author", {}).get("display_name")
                    ]
                    authors_str = ", ".join(authors_names)
                    
                    normalized = {
                        "paper_title": item.get("title") or "Untitled",
                        "authors": authors_str or "Unknown",
                        "authors_json": authors_names,
                        "year": item.get("publication_year"),
                        "citation_count": item.get("cited_by_count") or 0,
                        "influential_citation_count": 0,
                        "url": item.get("doi") or item.get("id"),
                        "source": "openalex",
                        "raw_data": item
                    }
                    results.append(normalized)
                return results
            else:
                print(f"OpenAlex API returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"OpenAlex request failed with error: {e}")

    return []
