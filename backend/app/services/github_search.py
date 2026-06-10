import requests


def search_github(
    topic: str,
    limit: int = 20
):

    url = (
        "https://api.github.com/search/repositories"
    )

    response = requests.get(
        url,
        params={
            "q": topic,
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
    )

    return response.json()