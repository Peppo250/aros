import feedparser
import requests
import datetime
import time
import re

def search_trends(
    topic: str,
    limit: int = 20
):
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{topic}",
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            results = []
            
            bonus_keywords = [
                "distributed", "decentralized", "peer-to-peer", "p2p", "federated",
                "edge computing", "edge intelligence", "mesh network", "mesh networking",
                "multi-agent", "autonomous agents"
            ]

            for entry in feed.entries:
                title = entry.title
                summary = entry.get("summary", "")

                title_lower = title.lower() if title else ""
                summary_lower = summary.lower() if summary else ""
                combined_text = f"{title_lower} {summary_lower}"

                # Mandatory Rule: Must contain BOTH 'edge' and 'ai' as distinct words
                has_edge = re.search(r"\bedge\b", combined_text) is not None
                has_ai = re.search(r"\bai\b", combined_text) is not None

                if not (has_edge and has_ai):
                    continue

                # Core Keyword Scoring
                # base: edge = +3, ai = +3, mesh = +4
                # title bonus: +2, abstract only bonus: +1
                score = 0
                matched_kws = []

                # edge scoring
                if re.search(r"\bedge\b", title_lower):
                    score += 3 + 2
                    matched_kws.append("edge (title)")
                elif re.search(r"\bedge\b", summary_lower):
                    score += 3 + 1
                    matched_kws.append("edge (abstract)")

                # ai scoring
                if re.search(r"\bai\b", title_lower):
                    score += 3 + 2
                    matched_kws.append("ai (title)")
                elif re.search(r"\bai\b", summary_lower):
                    score += 3 + 1
                    matched_kws.append("ai (abstract)")

                # mesh scoring
                if re.search(r"\bmesh\b", title_lower):
                    score += 4 + 2
                    matched_kws.append("mesh (title)")
                elif re.search(r"\bmesh\b", summary_lower):
                    score += 4 + 1
                    matched_kws.append("mesh (abstract)")

                # Bonus Keywords Scoring: +2 for each occurrence
                for bk in bonus_keywords:
                    matches = re.findall(rf"\b{re.escape(bk)}\b", combined_text)
                    if matches:
                        bonus_score = len(matches) * 2
                        score += bonus_score
                        matched_kws.append(f"{bk} (x{len(matches)})")

                # Threshold Check: score >= 8
                if score < 8:
                    continue

                # Log details for every kept paper
                print(f"[DEBUG_LOG] Topic: '{topic}'")
                print(f"[DEBUG_LOG] Title: '{title}'")
                print(f"[DEBUG_LOG] Relevance Score: {score}")
                print(f"[DEBUG_LOG] Matched Keywords: {', '.join(matched_kws)}")
                print("-" * 50)

                published_struct = entry.get("published_parsed")
                published_dt = None
                if published_struct:
                    published_dt = datetime.datetime.fromtimestamp(
                        time.mktime(published_struct),
                        datetime.timezone.utc
                    )

                entry_url = entry.get("id") or entry.get("link")
                raw_item = {k: v for k, v in entry.items()}

                results.append({
                    "source": "arxiv",
                    "title": title,
                    "description": summary,
                    "url": entry_url,
                    "published_at": published_dt,
                    "trend_score": 1.0,
                    "relevance_score": float(score),
                    "raw_data": raw_item
                })
            
            # Sort results descending by score, then published date
            results.sort(key=lambda x: (x["relevance_score"], x["published_at"] or datetime.datetime.min), reverse=True)
            return results
        else:
            print(f"ArXiv API returned status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"ArXiv API request failed: {e}")

    return []
