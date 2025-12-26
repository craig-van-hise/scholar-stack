
### Phase 2:

Write the modular search script named `1_search_omni.py`.
**1. Data Structure (Crucial):**
The script must initialize a pandas DataFrame with **exactly** these columns. Ensure every row adheres to this schema:

* `Title`: (String) Cleaned title.
* `Original_Filename`: (String) Attempt to parse this from the URL (e.g., '1706.03762.pdf'). If not obvious in the URL, set to 'Pending_Header_Check'. **Do NOT invent a filename.**
* `Publication_Date`: (String) Format strictly as **YYYY/MM/DD**. (If source only gives year, default to YYYY/01/01).
* `Category`: (String) Initialize as 'Unsorted'.
* `Description`: (String) Abstract or Summary.
* `Is_Paywalled`: (Boolean) True if no direct PDF link found; False if direct link exists.
* `Is_Downloaded`: (Boolean) Initialize as **False** for all.
* `Source_URL`: (String) Direct PDF link or landing page.
* `DOI`: (String) Digital Object Identifier.

**2. Architecture:**
Create a class `ResearchCrawler` with a method for each source. It should accept `--query`, `--year_start`, and `--count`.
**3. Source Modules (Implement logic for ALL of these):**

* **1. Google Scholar:** Use `scholarly`. **Crucial:** Add a 10-second sleep between requests to avoid IP bans. If it fails, log error and skip.
* **2. Semantic Scholar:** Use the API. Search broadly.
* **3. BASE (Bielefeld):** Use `sickle` to query the BASE OAI-PMH endpoint.
* **4. CORE:** Use the CORE API (requires generic API key logic) or search their open dataset.
* **5. Preprint Servers:**
* **arXiv:** Query specifically in `eess.AS`, `cs.SD`, and `physics.gen-ph`.
* **OSF Preprints:** Use `requests` to hit the OSF API v2 (filter by 'preprint').
* **Zenodo:** Search the Zenodo API (keywords + year).
* **6. Open Access Journals:**
* **DOAJ:** Query the DOAJ public API.
* **PLOS:** Query the PLOS Search API.
* **7. Conference Archives (Scrapers):**
* **DAFx:** Write a `BeautifulSoup` scraper to parse the DAFx archive page for titles matching the query.
* **ISMIR:** Scrape the ISMIR proceedings list.
* **8. The "Unlocker" (For AES/IEEE/Paywalled):**
* For any result found above that lacks a direct PDF link, take its DOI.
* Run the DOI through `pyunpaywall` AND `Open Access Button` API.
* If a free version is found, update `Source_URL` and set `Is_Paywalled` to False.

**4. Output:**

* Combine all results into one Pandas DataFrame.
* **Deduplicate:** Aggressively remove duplicates based on normalized Title/DOI.
* Save to `research_catalog.csv`.
* Print a summary: 'Found [X] papers total: [A] from ArXiv, [B] from Scholar, [C] from BASE...'

