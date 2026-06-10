import os
import requests

def search_patents(
    topic: str,
    limit: int = 20
):
    # Configurable URL via environment variable
    url = os.getenv(
        "PATENTSVIEW_URL",
        "https://search.patentsview.org/api/v1/patent/"
    )

    payload = {
        "q": {
            "_text_any": {
                "patent_title": topic
            }
        },
        "f": [
            "patent_id",
            "patent_title",
            "patent_date",
            "patent_abstract",
            "assignees.assignee_organization",
            "inventors.inventor_name_first",
            "inventors.inventor_name_last"
        ],
        "o": {
            "per_page": limit
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    api_key = os.getenv("PATENTSVIEW_API_KEY")
    if api_key:
        headers["X-Api-Key"] = api_key

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("patents", [])
        else:
            print(f"PatentsView API returned status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"PatentsView API request failed: {e}")

    return []
