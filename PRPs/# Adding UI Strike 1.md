
### ** Strike 1: Upgrade the Search Engine**

> "We are moving to a UI-based application. I need to upgrade `1_search_omni.py` to handle granular inputs.
> **Please rewrite `1_search_omni.py` to accept these new arguments via `argparse`:**
> 1. `--topic` (Required): The main search query.
> 2. `--keywords` (Optional): Additional keywords to append to the query.
> 3. `--author` (Optional): Filter results by this author name.
> 4. `--publication` (Optional): Filter by specific venue/journal.
> 5. `--date_start` and `--date_end` (Optional): Date range filtering.
> 6. `--sites` (Optional List): A comma-separated list of sources to use (options: `arxiv`, `scholar`, `core`, `doaj`). Default to 'all'.
> 
> 
> **Logic Updates:**
> * **Query Construction:** Combine Topic + Keywords + Author into a smart search string optimized for each API.
> * **Source Filtering:** If `--sites` is provided, only call the search functions for those specific APIs.
> * **Date Filtering:** Ensure the results are strictly within the provided date range (checking `date_start` and `date_end`).
> 
> 
> Keep the existing save logic (`research_catalog.csv`)."

