import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.services.citation_search import search_citations

def test_search():
    topic = "edge ai"
    print(f"Running citation search validation for: '{topic}'...")
    results = search_citations(topic, limit=5)
    
    status = "SUCCESS" if len(results) > 0 else "FAILURE"
    print(f"Status: {status}")
    print(f"Number of records: {len(results)}")
    if results:
        print("First record:")
        rec = results[0].copy()
        raw = rec.pop("raw_data")
        print(f"Normalized metadata: {rec}")
        print(f"Raw data fields available: {list(raw.keys())}")
    else:
        print("No records returned.")

if __name__ == "__main__":
    test_search()
