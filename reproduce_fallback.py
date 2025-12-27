
import arxiv
import requests
import os

TOPIC = "Spatial Audio"
KEYWORDS = ["crosstalk cancellation"]
LOGIC = "any"

def test_arxiv():
    print(f"\n--- Testing ArXiv ---")
    kw_parts = [f'all:"{k}"' for k in KEYWORDS]
    if LOGIC == 'all':
        kw_group = " AND ".join(kw_parts)
    else:
        kw_group = " OR ".join(kw_parts)
    
    final_query = f'all:"{TOPIC}" AND ({kw_group})'
    print(f"Query: {final_query}")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=final_query,
        max_results=50,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    count = 0
    for r in client.results(search):
        count += 1
        print(f"[{count}] {r.title} ({r.pdf_url})")
    
    print(f"Total ArXiv Found: {count}")

def test_semantic():
    print(f"\n--- Testing Semantic Scholar ---")
    topic_phrase = f'"{TOPIC}"'
    quoted_keywords = [f'"{k}"' for k in KEYWORDS]
    
    if LOGIC == 'all':
        combined_k = " ".join(quoted_keywords)
        search_terms = [f"{topic_phrase} {combined_k}"]
    else:
        search_terms = [f'{topic_phrase} "{k}"' for k in KEYWORDS]
        
    print(f"Terms: {search_terms}")
    
    for term in search_terms:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": term,
            "limit": 50,
            "fields": "title,url,openAccessPdf"
        }
        r = requests.get(url, params=params)
        data = r.json()
        print(f"Status: {r.status_code}")
        if 'data' in data:
            print(f"Found: {len(data['data'])}")
            for item in data['data']:
                print(f"- {item.get('title')} ({item.get('openAccessPdf')})")
        else:
            print(f"Response: {data}")

if __name__ == "__main__":
    test_arxiv()
    test_semantic()
