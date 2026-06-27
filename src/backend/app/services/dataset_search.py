import os
import requests

def search_datasets(
    topic: str,
    limit: int = 20
):
    url = os.getenv(
        "HF_DATASET_API_URL",
        "https://huggingface.co/api/datasets"
    )

    # Split the topic into individual words to support progressive word-chopping
    words = topic.split()
    queries = []
    while len(words) > 0:
        queries.append(" ".join(words))
        words.pop()

    # Add default global fallback topic
    fallback = "artificial intelligence"
    if fallback not in queries:
        queries.append(fallback)

    # Perform progressive search
    for query in queries:
        print(f"Attempting Hugging Face datasets search with query: '{query}'")
        try:
            response = requests.get(
                url,
                params={
                    "search": query,
                    "limit": limit,
                    "full": "true"
                },
                timeout=10
            )
            if response.status_code == 200:
                results = response.json()
                print(f"Query '{query}' returned {len(results)} results")
                if len(results) > 0:
                    return results, query
            else:
                print(f"Hugging Face API returned status {response.status_code} for query '{query}': {response.text}")
        except Exception as e:
            print(f"Hugging Face API request failed for query '{query}': {e}")

    return [], None
