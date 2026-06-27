import re
import random
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def clean_html(raw_html: str) -> str:
    # Remove script and style tags
    clean = re.sub(r'<(script|style)[^>]*>([\s\S]*?)</\1>', ' ', raw_html)
    # Remove other HTML tags
    clean = re.sub(r'<[^>]+>', ' ', clean)
    # Replace common HTML entities
    clean = (clean.replace("&nbsp;", " ")
                  .replace("&amp;", "&")
                  .replace("&lt;", "<")
                  .replace("&gt;", ">")
                  .replace("&quot;", '"')
                  .replace("&#39;", "'"))
    # Collapse multiple whitespaces
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def extract_patent_text(patent_number: str) -> str:
    # Normalize patent number (e.g. uppercase, remove slashes/spaces)
    p_num = patent_number.strip().upper().replace("/", "").replace(" ", "")
    # Add US prefix if it is purely numeric
    if p_num.isdigit():
        p_num = f"US{p_num}"
        
    url = f"https://patents.google.com/patent/{p_num}/en"
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    
    try:
        print(f"Fetching patent page: {url}")
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            print(f"Failed to fetch patent {p_num} from Google Patents. Status: {response.status_code}")
            return ""
            
        html = response.text
        
        abstract_text = ""
        description_text = ""
        claims_text = ""
        
        # 1. Extract abstract
        abs_match = re.search(r'<section\s+[^>]*itemprop=["\']abstract["\'][^>]*>', html)
        if abs_match:
            end_idx = html.find("</section>", abs_match.start())
            if end_idx != -1:
                abstract_text = clean_html(html[abs_match.start():end_idx])
                
        # 2. Extract description
        desc_match = re.search(r'<section\s+[^>]*itemprop=["\']description["\'][^>]*>', html)
        if desc_match:
            end_idx = html.find("</section>", desc_match.start())
            if end_idx != -1:
                description_text = clean_html(html[desc_match.start():end_idx])
                
        # 3. Extract claims
        claims_match = re.search(r'<section\s+[^>]*itemprop=["\']claims["\'][^>]*>', html)
        if claims_match:
            end_idx = html.find("</section>", claims_match.start())
            if end_idx != -1:
                claims_text = clean_html(html[claims_match.start():end_idx])
                
        # Combine the text
        parts = []
        if abstract_text:
            parts.append(f"Abstract:\n{abstract_text}")
        if description_text:
            parts.append(f"Description:\n{description_text}")
        if claims_text:
            parts.append(f"Claims:\n{claims_text}")
            
        combined_text = "\n\n".join(parts)
        if not combined_text:
            # Fallback: clean the whole HTML but just return visible text
            combined_text = clean_html(html)
            
        return combined_text
    except Exception as e:
        print(f"Error extracting patent {p_num} text: {e}")
        return ""
