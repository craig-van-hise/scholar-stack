

# Product Requirements Prompt: Implement Citation Backward-Chaining Search

**Role:** Senior Python Engineer / Search Architect
**Task:** Refactor the provided `ResearchCrawler` script to replace the current "Hybrid RAG/Topic" search logic with a new "Citation Backward-Chaining" (Backdoor) discovery algorithm.

## Context

The current script uses a `HybridTreeSearch` (RAG) approach to map user queries to OpenAlex topics. This approach fails for niche or drifting terminology (e.g., "Crosstalk Cancellation" vs "Personal Sound Zones"). We need to replace this with a heuristic approach that finds the "Godfathers" of a field via citation analysis and uses their recent vocabulary to engineer the final search query.

## Core Requirement: The "Backdoor" Algorithm

You must delete the `search_openalex_multi_pass` method and the `HybridTreeSearch` imports. Replace them with a new workflow, `search_via_citation_backdoor`, which implements the following logic:

### Phase 1: The "Junk" Harvest (Find the Ghost)

1. **Search:** Perform a lightweight API call to OpenAlex `works` using the user's raw `topic` and `keywords`.
* *Constraint:* Do not filter for PDFs or Open Access yet. We just need metadata.
* *Params:* `per-page=50`, `select=referenced_works`.


2. **Analyze:** Iterate through these 50 results. Collect every ID found in their `referenced_works` list.
3. **Identify:** Use a `Counter` to find the single most frequently cited paper ID (The "Ghost" paper).

### Phase 2: The Pivot (Find the VIP)

1. **Fetch:** Retrieve the metadata for that "Ghost" paper ID.
2. **Extract:** Identify the primary author (The "VIP") from that paper.

### Phase 3: Terminology Expansion (Learn the Vocabulary)

1. **Query:** Search OpenAlex for works by this VIP Author ID, filtered to `publication_year > 2020` (Recent works).
2. **Extract:** Analyze the **titles** of these recent works. Extract the most frequent 2-word and 3-word phrases (N-grams) that are *not* the original seed keywords.
3. **Output:** A list of "Modern Synonyms" (e.g., discovering "BRIR" from "Crosstalk").

### Phase 4: The Final Dragnet

1. **Construct:** Create a new Boolean OR query string: `(Original Keywords) OR (New Modern Synonyms)`.
2. **Execute:** Pass this new engineered query into the existing `execute_openalex_query` method to perform the actual PDF downloading and strict filtering using the existing infrastructure.

## Technical Specifications & Changes

1. **Remove Dependencies:**
* Remove `from hybrid_search_client import HybridTreeSearch`.
* Remove any code related to `openalex_tree.json` or `chroma_db`.


2. **New Method Implementation:**
* Implement `search_via_citation_backdoor(self)` inside the `ResearchCrawler` class.
* Ensure strict error handling: If Phase 1 yields no results (no citations found), fall back gracefully to a standard text search using the original keywords.


3. **Refine `run` Loop:**
* Update the `run()` method to call `self.search_via_citation_backdoor()` instead of `self.search_openalex_multi_pass()`.


4. **Preserve Existing filters:**
* Do **not** modify `_check_accessibility`, `_pre_filter`, or `_process_batch`. We still need to strictly validate the final PDFs.
* Ensure the "Final Dragnet" (Phase 4) still respects the user's `date_start`, `date_end`, and `is_oa:true` requirements.



## Expected Behavior

If I search for "Crosstalk Cancellation":

1. The script finds 50 mediocre papers.
2. It notices they all cite Edgar Choueiri's 2008 paper.
3. It pivots to Choueiri's profile.
4. It sees his 2024 paper titled "...Binaural Room Impulse Response...".
5. It adds "Binaural Room Impulse Response" to the search.
6. It downloads the Choueiri 2024 paper (which the previous script missed).

## Input Code

[Insert the code I provided above here]