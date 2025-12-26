import argparse
import time
import pandas as pd
import requests
import arxiv
from semanticscholar import SemanticScholar
from scholarly import scholarly
from habanero import Crossref
from unpywall import Unpywall
from sickle import Sickle
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
from urllib.parse import urlparse
import datetime
from dotenv import load_dotenv
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

# --- Configuration & Constants ---
CORE_API_KEY = os.getenv("CORE_API_KEY")
os.environ["UNPAYWALL_EMAIL"] = os.getenv("UNPAYWALL_EMAIL", "")

if not os.getenv("UNPAYWALL_EMAIL"):
    print("Warning: UNPAYWALL_EMAIL not found in .env. Unpaywall functionality will be limited.")

COLUMNS = [
    'Title', 'Authors', 'Original_Filename', 'Publication_Date', 'Category', 
    'Description', 'Is_Paywalled', 'Is_Downloaded', 'Source_URL', 'DOI'
]

# Robust Request Session
def get_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class ResearchCrawler:
    def __init__(self, topic, keywords, author, publication, date_start, date_end, count, sites, keyword_logic='any'):
        if os.path.exists("research_catalog.csv"):
            os.remove("research_catalog.csv")

        self.raw_topic = topic
        raw_keywords = [k.strip() for k in keywords.split(',')] if keywords else []
        
        self.keywords_list = list(raw_keywords)
        for k in raw_keywords:
            if "personal sound zone" in k.lower():
                if "sound zone" not in [x.lower() for x in self.keywords_list]:
                    self.keywords_list.append("Sound Zone")
            if "psz" in k.lower():
                pass 

        self.author = author
        self.publication = publication
        
        print(f"DEBUG: Keywords: {self.keywords_list}")
        
        self.date_start = date_start
        self.date_end = date_end
        self.year_start = int(date_start[:4]) if date_start else 2000
        
        self.final_target_count = int(count)
        self.target_count = int(self.final_target_count * 1.2) + 5
        
        self.sites = sites if sites else ['all']
        self.results = []
        
        self.offsets = {
            'crossref': 0,
            'semantic': 0,
            'arxiv': 0
        }
        
        # Use session for stability
        self.session = get_session()
        
        sem_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
        # Patch Semantic Scholar client if possible, or rely on our direct requests
        self.sch = SemanticScholar(api_key=sem_key) if sem_key else SemanticScholar()
        self.crossref = Crossref()
        self.keyword_logic = keyword_logic if keyword_logic else 'any'

    def _normalize_date(self, date_str):
        if not date_str:
            return f"{self.year_start}/01/01"
        try:
            if re.match(r'^\d{4}$', str(date_str)):
                return f"{date_str}/01/01"
            if re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_str)):
                return str(date_str).replace('-', '/')
            return f"{self.year_start}/01/01"
        except:
             return f"{self.year_start}/01/01"

    def _is_date_in_range(self, date_str):
        try:
            norm_date = self._normalize_date(date_str)
            d = datetime.datetime.strptime(norm_date, "%Y/%m/%d").date()
            
            start = datetime.datetime.strptime(self.date_start, "%Y-%m-%d").date() if self.date_start else None
            end = datetime.datetime.strptime(self.date_end, "%Y-%m-%d").date() if self.date_end else None
            
            if start and d < start:
                return False
            if end and d > end:
                return False
            return True
        except:
            return True

    def _parse_filename(self, url):
        if not url:
            return 'Pending_Header_Check'
        path = urlparse(url).path
        filename = os.path.basename(path)
        if filename and (filename.lower().endswith('.pdf') or 'pdf' in url.lower()):
            if not filename.lower().endswith('.pdf'):
                return filename + ".pdf"
            return filename
        return 'Pending_Header_Check'

    def _contains_keywords(self, text):
        if not self.keywords_list:
            return True
        if not text:
            return False
        text_lower = text.lower()
        
        # ANY Logic: Return True if ANY keyword phrase matches
        if self.keyword_logic == 'any':
            for k in self.keywords_list:
                k_lower = k.lower()
                if k_lower in text_lower:
                    return True
                words = k_lower.split()
                if len(words) > 1 and all(w in text_lower for w in words):
                    return True
            return False
            
        # ALL Logic: Return True ONLY if ALL keyword phrases match
        elif self.keyword_logic == 'all':
            for k in self.keywords_list:
                k_lower = k.lower()
                match = False
                if k_lower in text_lower:
                    match = True
                else:
                    words = k_lower.split()
                    if len(words) > 1 and all(w in text_lower for w in words):
                        match = True
                
                if not match:
                    return False
            return True
            
        return False

    def _pre_filter(self, title, date, description):
        """Cheap CPU-bound checks before network calls"""
        full_text = f"{title} {description}"
        status, reason = self._is_date_in_range(date) if hasattr(self, '_is_date_in_range_tuple') else (self._is_date_in_range(date), "Date out of range")
        
        # Compat with existing _is_date_in_range returning bool
        if isinstance(status, bool) and not status:
             return False, "Date out of range"
        
        if not self._contains_keywords(full_text):
            return False, "Keywords missing"
        
        norm_title = re.sub(r'[^a-z0-9]', '', str(title).lower())
        for existing in self.results:
            existing_norm = re.sub(r'[^a-z0-9]', '', str(existing['Title']).lower())
            if existing_norm == norm_title:
                return False, "Duplicate found"
        
        return True, "Passed"

    def _verify_candidate(self, candidate):
        """Worker function for parallel execution"""
        is_accessible, best_url = self._check_accessibility(candidate['url'], candidate['doi'])
        if is_accessible:
            candidate['final_url'] = best_url
            return candidate
        return None

    def _process_batch(self, candidates):
        """Process a batch of candidates in parallel"""
        print(f"DEBUG: Processing batch of {len(candidates)} candidates...", flush=True)
        
        # 1. CPU Filter
        valid_candidates = []
        for c in candidates:
            # Basic validation
            if not c.get('title'): continue
            
            passed, reason = self._pre_filter(c['title'], c['date'], c['description'])
            if passed:
                valid_candidates.append(c)
            else:
                # Optional: Verbose logging for rejections?
                pass

        if not valid_candidates:
            print("DEBUG: No candidates passed pre-filter.", flush=True)
            return

        print(f"DEBUG: {len(valid_candidates)} candidates passed pre-filter. Checking accessibility concurrently...", flush=True)

        # 2. Parallel I/O Check
        added_count = 0
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_cand = {executor.submit(self._verify_candidate, c): c for c in valid_candidates}
            
            for future in as_completed(future_to_cand):
                try:
                    result = future.result()
                    if result:
                        self._add_final_result(result)
                        added_count += 1
                except Exception as e:
                    print(f"Error in worker: {e}", flush=True)
        
        print(f"DEBUG: Batch complete. Added {added_count} papers.", flush=True)

    def _add_final_result(self, c):
        entry = {
            'Title': c['title'].strip() if c['title'] else "Unknown Title",
            'Authors': c['authors'] if c['authors'] else "Unknown Authors",
            'Original_Filename': self._parse_filename(c['final_url']),
            'Publication_Date': self._normalize_date(c['date']),
            'Category': 'Unsorted',
            'Description': c['description'][:500] + "..." if c['description'] and len(c['description']) > 500 else c['description'],
            'Is_Paywalled': False,
            'Is_Downloaded': False,
            'Source_URL': c['final_url'],
            'DOI': c['doi'],
            '_Source': c['source_name']
        }
        self.results.append(entry)
        print(f"[Accepted] {entry['Title'][:60]}...", flush=True)

    def _check_accessibility(self, url, doi):
        if url:
            url_lower = url.lower()
            if url_lower.endswith('.pdf'):
                return True, url
            if 'arxiv.org/pdf/' in url_lower:
                return True, url
            if 'openaccess' in url_lower:
                return True, url

        if doi:
            try:
                print(f"DEBUG: Checking Unpywall for {doi}...", flush=True)
                res = Unpywall.doi(doi)
                print(f"DEBUG: Unpywall check done.", flush=True)
                if res and res.best_oa_location and res.best_oa_location.url:
                    return True, res.best_oa_location.url
            except:
                pass
        
        return False, url

    def _add_result(self, title, authors, url, date, description, doi, source_name):
        print(f"[Checking] {title[:60]}...", flush=True)
        if not self._is_date_in_range(date):
            print(f"[Rejected] Date out of range: {date}", flush=True)
            return False

        full_text = f"{title} {description}"
        if not self._contains_keywords(full_text):
            print(f"[Rejected] Keywords missing.", flush=True)
            return False

        norm_title = re.sub(r'[^a-z0-9]', '', str(title).lower())
        for existing in self.results:
            existing_norm = re.sub(r'[^a-z0-9]', '', str(existing['Title']).lower())
            if existing_norm == norm_title:
                print(f"[Rejected] Duplicate found.", flush=True)
                return False

        is_accessible, best_url = self._check_accessibility(url, doi)
        
        if not is_accessible:
            print(f"[Rejected] Not accessible/Paywalled.", flush=True)
            return False

        entry = {
            'Title': title.strip() if title else "Unknown Title",
            'Authors': authors if authors else "Unknown Authors",
            'Original_Filename': self._parse_filename(best_url),
            'Publication_Date': self._normalize_date(date),
            'Category': 'Unsorted',
            'Description': description[:500] + "..." if description and len(description) > 500 else description,
            'Is_Paywalled': False,
            'Is_Downloaded': False,
            'Source_URL': best_url,
            'DOI': doi,
            '_Source': source_name
        }
        self.results.append(entry)
        print(f"[Accepted] +1", flush=True)
        return True

    def search_arxiv(self):
        if self.offsets['arxiv'] > 0:
            return 

        print(f"Searching ArXiv...", flush=True)
        try:
            if self.keywords_list:
                # User requested Topic AND Keywords
                # Split phrases into individual terms for ArXiv to improve recall
                # e.g. "crosstalk cancellation" -> all:crosstalk AND all:cancellation
                kw_parts = []
                for k in self.keywords_list:
                    words = k.split()
                    if len(words) > 1:
                        # (all:word1 AND all:word2)
                        sub_query = " AND ".join([f'all:"{w}"' for w in words])
                        kw_parts.append(f"({sub_query})")
                    else:
                        kw_parts.append(f'all:"{k}"')
                
                kw_group = " OR ".join(kw_parts)
                # If Logic is ALL, use AND instead of OR
                if self.keyword_logic == 'all':
                    kw_group = " AND ".join(kw_parts)
                
                final_query = f'all:"{self.raw_topic}" AND ({kw_group})'
            else:
                final_query = f'all:"{self.raw_topic}"'

            if self.author:
                final_query += f' AND au:"{self.author}"'
            
            client = arxiv.Client()
            search = arxiv.Search(
                query=final_query,
                max_results=self.target_count * 2, 
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            candidates = []
            for result in tqdm(client.results(search), desc="ArXiv"):
                pdf_link = result.pdf_url
                if pdf_link and 'arxiv.org/abs/' in pdf_link:
                    pdf_link = pdf_link.replace('abs', 'pdf')
                
                authors = ", ".join([a.name for a in result.authors])
                pub_date = str(result.published.date())
                
                candidates.append({
                    'title': result.title,
                    'authors': authors,
                    'url': pdf_link,
                    'date': pub_date,
                    'description': result.summary,
                    'doi': result.doi,
                    'source_name': 'ArXiv'
                })
            
            self._process_batch(candidates)
            
            self.offsets['arxiv'] = 1 
                
        except Exception as e:
            print(f"Error searching ArXiv: {e}")

    def search_semantic_scholar(self):
        print(f"Searching Semantic Scholar (Offset: {self.offsets['semantic']})...", flush=True)
        try:
            # User requested Topic AND Keywords
            if self.keywords_list:
                if self.keyword_logic == 'all':
                    # Single query with ALL keywords
                    combined_k = " ".join(self.keywords_list)
                    search_terms = [f"{self.raw_topic} {combined_k}"]
                else:
                    # Separate queries for ANY keyword (OR logic)
                    search_terms = [f"{self.raw_topic} {k}" for k in self.keywords_list]
            else:
                search_terms = [self.raw_topic]
            limit_per_call = 20
            
            for term in search_terms:
                url = "https://api.semanticscholar.org/graph/v1/paper/search"
                
                params = {
                    "query": term,
                    "offset": self.offsets['semantic'],
                    "limit": limit_per_call, 
                    "fields": "title,authors,abstract,publicationDate,url,openAccessPdf,externalIds,venue"
                }
                
                headers = {}
                sem_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
                if sem_key: headers["x-api-key"] = sem_key

                try:
                    # Use robust session
                    r = self.session.get(url, params=params, headers=headers, timeout=10)
                    
                    if r.status_code == 429:
                        time.sleep(5)
                        continue
                    
                    data = r.json()
                    papers = data.get("data", [])
                    if papers:
                        candidates = []
                        for item in papers:
                            item_authors = item.get("authors", [])
                            author_names = ", ".join([a.get("name","") for a in item_authors])
                            
                            if self.author and self.author.lower() not in author_names.lower():
                                continue

                            pdf_url = item.get("url")
                            oa_pdf = item.get("openAccessPdf")
                            if oa_pdf and oa_pdf.get("url"):
                                pdf_url = oa_pdf.get("url")

                            candidates.append({
                                'title': item.get("title"),
                                'authors': author_names,
                                'url': pdf_url,
                                'date': str(item.get("publicationDate")),
                                'description': item.get("abstract"),
                                'doi': (item.get("externalIds") or {}).get("DOI"),
                                'source_name': 'Semantic Scholar'
                            })
                        
                        self._process_batch(candidates)
                except Exception:
                    pass
            
            self.offsets['semantic'] += limit_per_call

        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")

    def search_crossref(self):
        print(f"Searching Crossref (Offset: {self.offsets['crossref']})...")
        try:
            q_str = self.raw_topic
            if self.keywords_list:
                q_str += " " + " ".join(self.keywords_list)
            if self.author:
                q_str += f" {self.author}"

            limit_per_call = 100
            
            # Crossref wrapper doesn't use requests session directly usually,
            # but is generally robust. We rely on habanero's retries if any.
            results = self.crossref.works(query=q_str, limit=limit_per_call, offset=self.offsets['crossref'])
            items = results.get('message', {}).get('items', [])
            
            self.offsets['crossref'] += limit_per_call
            
            candidates = []
            for item in items:
                title = item.get('title', [''])[0]
                authors_list = item.get('author', [])
                authors = ", ".join([f"{a.get('given','')} {a.get('family','')}" for a in authors_list])
                
                issued = item.get('issued', {}).get('date-parts', [[None]])[0]
                date_str = None
                if issued[0]:
                    date_str = f"{issued[0]}-01-01"

                doi = item.get('DOI')
                url = item.get('URL')
                
                candidates.append({
                    'title': title,
                    'authors': authors,
                    'url': url,
                    'date': date_str,
                    'description': "", 
                    'doi': doi,
                    'source_name': 'Crossref'
                })
            
            self._process_batch(candidates)
                    
        except Exception as e:
            print(f"Error searching Crossref: {e}")

    def save_results(self):
        df = pd.DataFrame(self.results)
        if df.empty:
            print("No results found or processed.")
            df.to_csv("research_catalog.csv", index=False)
            return

        df['norm_title'] = df['Title'].apply(lambda x: re.sub(r'[^a-z0-9]', '', str(x).lower()) if x else '')
        df = df.drop_duplicates(subset=['norm_title'], keep='first')
        
        if len(df) > self.final_target_count:
            print(f"Trimming results from {len(df)} to requested {self.final_target_count}...")
            df = df.head(self.final_target_count)
            
        df = df.drop(columns=['norm_title'], errors='ignore')

        df.to_csv("research_catalog.csv", index=False)
        print(f"Saved {len(df)} papers to research_catalog.csv")

    def run(self):
        try:
            buffer_target = int(self.final_target_count * 1.2) + 5
            
            rounds = 0
            max_rounds = 30 
            
            while len(self.results) < buffer_target and rounds < max_rounds:
                rounds += 1
                current_count = len(self.results)
                print(f"\n--- Search Round {rounds} (Collected: {current_count}/{buffer_target} for target {self.final_target_count}) ---")
                
                self.search_crossref()
                self.search_arxiv()
                self.search_semantic_scholar()
                
                new_count = len(self.results)
                if new_count == current_count:
                    print(f">> Round {rounds}: No new papers added (rejected/dup). Digging deeper...")
            
        except KeyboardInterrupt:
            print("\nUser Interrupted.")
        except Exception:
            pass
        finally:
            self.save_results()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--keywords")
    parser.add_argument("--author")
    parser.add_argument("--publication")
    parser.add_argument("--date_start")
    parser.add_argument("--date_end")
    parser.add_argument("--count", default=10, type=int)
    parser.add_argument("--sites")
    parser.add_argument("--keyword_logic", default="any")
    args = parser.parse_args()
    
    sites_list = [s.strip().lower() for s in args.sites.split(',')] if args.sites else ['all']
    
    crawler = ResearchCrawler(
        topic=args.topic,
        keywords=args.keywords,
        author=args.author,
        publication=args.publication,
        date_start=args.date_start,
        date_end=args.date_end,
        count=args.count,
        sites=sites_list,
        keyword_logic=args.keyword_logic
    )
    crawler.run()
