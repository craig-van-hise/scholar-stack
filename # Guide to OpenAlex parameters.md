In the context of the OpenAlex API, "args" are the **query parameters** you append to the URL (e.g., `?search=...&filter=...`).

Because OpenAlex is a REST API, these arguments are universal across all endpoints (Works, Authors, Sources, etc.), but the *values* they accept change depending on what you are searching.

Here is the complete reference guide to the input arguments, categorized by function.

---

### **1. The "Big Six" Control Arguments**

These are the top-level parameters you will use to control *what* you get back and *how* it looks.

| Argument | Purpose | Example Value |
| --- | --- | --- |
| **`search`** | The "Google" bar. Searches titles, abstracts, and full text. | `?search=generative+ai` |
| **`filter`** | Precise constraints. The most powerful argument (see §2). | `?filter=is_oa:true,year:2024` |
| **`select`** | Limits the response fields (reduces JSON size/latency). | `?select=id,title,doi` |
| **`sort`** | Controls the order of results. | `?sort=cited_by_count:desc` |
| **`per-page`** | Number of results per request (Max: 200). | `?per-page=200` |
| **`page`** | Pagination (Works for the first 10k results). | `?page=2` |

---

### **2. Deep Dive: The `filter` Argument**

The `filter` argument is a container for dozens of specific "keys." You verify these by appending them as a comma-separated string: `filter=key1:value1,key2:value2`.

**Common Filter Keys for Papers (Works):**

| Category | Filter Key | Description |
| --- | --- | --- |
| **Access** | `is_oa` | `true`/`false`. Is the paper free to read? |
|  | `has_doi` | `true`/`false`. Does it have a valid DOI? |
|  | `open_access.oa_status` | `gold`, `green`, `bronze`, `hybrid`. |
| **Dates** | `publication_year` | E.g., `2023` or `>2020` (ranges supported). |
|  | `from_publication_date` | `2023-01-01` (Specific start date). |
|  | `to_publication_date` | `2023-12-31` (Specific end date). |
| **Impact** | `cited_by_count` | `>100`. Papers with high citations. |
|  | `has_fulltext` | `true`. Works where OpenAlex indexed the full text. |
| **Identity** | `authorships.author.id` | Search for a specific author by OpenAlex ID. |
|  | `primary_location.source.id` | Search for a specific Journal/Conference ID. |
|  | `institutions.id` | Search for papers from a specific university. |
| **Content** | `type` | `article`, `book-chapter`, `dissertation`. |
|  | `language` | `en`, `fr`, `zh`, etc. |

---

### **3. Deep Dive: The `search` Argument**

While `?search=` searches everything, you can also be surgical by attaching `.search` to specific fields within the filter parameter (a common "power user" trick).

* **Standard:** `?search=dna` (Searches title, abstract, and full text).
* **Title Only:** `?filter=title.search:dna` (Ignores mentions in the abstract).
* **Abstract Only:** `?filter=abstract.search:dna` (Only looks inside the abstract).
* **Affiliation:** `?filter=raw_affiliation_string.search:harvard` (Finds strings like "Harvard Medical School").

---

### **4. Advanced & Utility Arguments**

These are less common but critical for specific scraping tasks.

| Argument | Purpose |
| --- | --- |
| **`cursor`** | **Critical for Deep Scraping.** Used instead of `page` to retrieve >10,000 results. You pass the `next_cursor` string returned in the previous API response. |
| **`sample`** | Returns a random sample of  papers. `?sample=50`. Great for testing pipelines. |
| **`seed`** | Used with `sample`. Ensures the "random" sample is the same every time you run it (reproducibility). |
| **`group_by`** | Returns summary statistics instead of a list of papers. E.g., `?group_by=publication_year` returns a count of papers per year. |
| **`mailto`** | Not a query param, but **highly recommended**. Add `&mailto=your@email.com` to get into the "polite pool" (faster response times). |

### **5. Valid Sort Options**

You can sort by almost any numerical or date field. Add `:desc` (descending) or `:asc` (ascending).

* `relevance_score` (Default when searching)
* `publication_year`
* `publication_date`
* `cited_by_count` (Find the most influential papers)
* `title` (Alphabetical)

### **Example: The "Perfect" Query**

If you want **50 highly-cited Open Access papers on LLMs from 2024**, your URL inputs would look like this:

```http
https://api.openalex.org/works?
  search=Large Language Models
  &filter=is_oa:true,publication_year:2024,cited_by_count:>10
  &sort=cited_by_count:desc
  &per-page=50
  &select=id,title,open_access,cited_by_count
  &mailto=yourname@example.com

```