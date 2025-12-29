
# Product Requirements Prompt (PRP)

**Role:** Senior Python Engineer
**Task:** Implement the "Broad Net / Strict Gate" Backdoor Search logic with detailed debug visibility.

## Logic Flow

1. **Backdoor Discovery:**
* Use the "Contextual Probe" (`Original Keyword` AND `User Topic`) to find seed papers.
* Analyze bibliographies to identify the **Top 10 Most Influential Authors** (The Panel).
* **Debug Requirement:** You must print the `display_name` of these 10 authors to the console so the user can verify the expert list.
* **Vocabulary:** Extract the **Top 10** most frequent N-grams (2-3 words) from their recent titles (2020+). These are the "Fishing Synonyms."


2. **The Dragnet (Broad Retrieval):**
* Construct an API query using: `(Original Keyword OR Synonym 1 OR ... Synonym 10) AND (User Topic)`.
* *Purpose:* Use the weak synonyms to pull metadata from the API that might have a truncated index.


3. **The Strict Gate (Local Retention):**
* **Constraint:** Do **NOT** add the synonyms to `self.keywords_list`.
* *Purpose:* The system must strictly enforce that the *Original Keyword* appears in the returned metadata. If a paper is caught via a synonym but lacks the original keyword in its Title/Abstract, it must be rejected by the local filter.



## Implementation Details

* Fetch **Top 10** Authors and **Top 10** Synonyms.
* Ensure the console output clearly lists: `   ✅ Identified Panel of 10 Experts: [Name 1, Name 2...]`.
* Pass the expanded query to the API, but keep the `ResearchCrawler` validation list strict.

---

### Updated Code: `search_via_citation_backdoor`

Replace the method in `research_crawler.py` with this version.

```python
    def search_via_citation_backdoor(self):
        """
        BROAD NET / STRICT GATE Algorithm:
        1. Contextual Probe -> Find 'Seed' papers (Keyword + Topic).
        2. Citation Analysis -> Identify Top 10 Experts (The Panel).
        3. Vocabulary Expansion -> Learn Top 10 Synonyms (Fishing Bait).
        4. Broad Dragnet -> Search API using Synonyms.
        5. Strict Gate -> Local filter rejects papers missing the ORIGINAL keyword.
        """
        print(f"\n🕵️ STARTING BACKDOOR CITATION SEARCH for: '{self.raw_topic}'")
        
        # --- PHASE 1: THE CONTEXTUAL SEED ---
        clean_topic = self.raw_topic.replace('"', '')
        clean_keyword = self.keywords_list[0].replace('"', '')
        
        # Probe: Keyword AND Topic (e.g., "Crosstalk" AND "Spatial Audio")
        seed_query = f'("{clean_keyword}") AND ("{clean_topic}")'
        print(f"   1. Probing with Context: {seed_query}")
        
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"title_and_abstract.search:{seed_query}",
            "per-page": 50,  
            "select": "referenced_works" 
        }
        
        try:
            r = self.session.get(url, params=params, timeout=10)
            seed_results = r.json().get('results', [])
        except:
            print("   ⚠️ Probe failed. Falling back to standard search.")
            self.execute_openalex_query("Fallback", "is_oa:true", f'"{clean_keyword}"')
            return

        if not seed_results:
            print(f"   ⚠️ No seed papers found for context. Trying keyword only...")
            params["filter"] = f"title_and_abstract.search:{clean_keyword}"
            r = self.session.get(url, params=params, timeout=10)
            seed_results = r.json().get('results', [])
            
        if not seed_results:
             print("   ⚠️ No results found even for keywords.")
             return

        # --- PHASE 2: IDENTIFY THE PANEL (Top 10 Experts) ---
        print("   2. Analyzing Citations to identify the Expert Panel...")
        
        from collections import Counter
        cited_ids_counter = Counter()
        
        for work in seed_results:
            for ref_id in work.get('referenced_works', []):
                cited_ids_counter[ref_id] += 1
        
        # Get Top 30 Ghost Papers (Canon)
        top_ghost_ids = [id for id, count in cited_ids_counter.most_common(30)]
        
        if not top_ghost_ids:
            print("   ⚠️ No citations found to analyze.")
            self.execute_openalex_query("Fallback", "is_oa:true", f'"{clean_keyword}"')
            return

        # Fetch authors of these Ghost Papers
        ghost_ids_str = "|".join(top_ghost_ids)
        r = self.session.get(url, params={"filter": f"openalex_id:{ghost_ids_str}", "select": "authorships"}, timeout=10)
        
        author_counter = Counter()
        author_names = {} # Map ID to Name for display
        
        for work in r.json().get('results', []):
            for authorship in work.get('authorships', []):
                aid = authorship['author']['id']
                name = authorship['author']['display_name']
                author_counter[aid] += 1
                author_names[aid] = name
                
        # SELECT THE PANEL: Top 10 Authors
        top_panel = author_counter.most_common(10)
        panel_ids = [id for id, count in top_panel]
        
        print(f"   ✅ Identified Panel of {len(panel_ids)} Experts:")
        for pid in panel_ids:
            print(f"      - {author_names.get(pid, 'Unknown')} (ID: {pid})")

        # --- PHASE 3: CONSENSUS LEARNING (Top 10 Fishing Terms) ---
        print(f"   3. Harvesting vocabulary from Panel's recent work (2020+)...")
        
        panel_str = "|".join(panel_ids)
        vocab_params = {
            "filter": f"authorships.author.id:{panel_str},publication_year:>2019",
            "per-page": 150, # Get a good sample size
            "select": "title"
        }
        
        r = self.session.get(url, params=vocab_params, timeout=10)
        recent_titles = [w['title'] for w in r.json().get('results', [])]
        
        # N-Gram Extraction
        import re
        phrase_counter = Counter()
        
        for title in recent_titles:
            if not title: continue
            words = re.findall(r'\w+', title.lower())
            for n in [2, 3]:
                for i in range(len(words) - n + 1):
                    phrase = " ".join(words[i:i+n])
                    # Filter: Must not contain seed, >5 chars
                    if clean_keyword.lower() not in phrase and len(phrase) > 5:
                        phrase_counter[phrase] += 1
        
        # EXTRACT TOP 10 TERMS (Broad Net)
        new_synonyms = [f'"{p}"' for p, c in phrase_counter.most_common(50) if c > 1][:10]
        
        print(f"   🧠 Learned Fishing Synonyms (Top 10): {new_synonyms}")

        # --- PHASE 4: THE DRAGNET (Broad Net / Strict Gate) ---
        print("   4. Executing Final Engineered Search...")
        
        # 1. The Net (API Query): Use ALL terms to fish
        expansion_query = " OR ".join([f'"{clean_keyword}"'] + new_synonyms)
        final_query = f"({expansion_query}) AND ({clean_topic})"
        
        # 2. The Gate (Local Filter): STRICTLY enforce Original Keyword
        # We do NOT add synonyms to self.keywords_list.
        print(f"   🔒 Local Filter remains STRICT: Only papers containing '{clean_keyword}' will survive.")
        
        filters = "is_oa:true,type:article|conference-paper" 
        if self.date_start: filters += f",publication_year:>{self.year_start-1}"
        
        self.execute_openalex_query("Engineered Dragnet", filters, final_query)

```