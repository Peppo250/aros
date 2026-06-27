import requests

def test_europe_pmc_queries():
    queries = [
        "edge ai mesh",
        "edge artificial intelligence mesh",
        "decentralized inference mesh",
        "federated edge learning"
    ]
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    
    for q in queries:
        # Query without double quotes
        full_query = f"({q}) AND (SRC:PAT)"
        params = {
            "query": full_query,
            "format": "json",
            "pageSize": 5
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("resultList", {}).get("result", [])
                print(f"Query: '{q}' -> Found {len(results)} results.")
                for r in results[:2]:
                    print(f"  ID: {r.get('id')} | Title: {r.get('title')[:60]}")
            else:
                print(f"Query: '{q}' failed with status {response.status_code}")
        except Exception as e:
            print(f"Query: '{q}' error: {e}")

if __name__ == "__main__":
    test_europe_pmc_queries()
