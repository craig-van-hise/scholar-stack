# Fast vs. Deep Mode: Implementation Proposal

## 1. Metrics Comparison (1,000 Papers)

| Feature | **Fast Mode** (The Skim) | **Deep Mode** (The Scholar) |
| :--- | :--- | :--- |
| **Est. Duration** | **~15 Minutes** | **~90 - 120 Minutes** |
| **Success Rate** | ~60-70% (Direct Only) | ~90-95% (Deep Web Hunt) |
| **Organization** | Flat Folder (Unsorted) | AI Categorized Folders |
| **Storage (Temp)** | Low | High |

---

## 2. Process Changes

### A. Phase 1: Search (No Change)
Both modes still fetch metadata from OpenAlex/ArXiv. (~5 mins)

### B. Phase 2: AI Clustering
*   **Deep**: Uses LLM provided taxonomy to sort papers into semantic folders. (~15 mins)
*   **Fast**: **CUT**. All papers go into a single "Unsorted" folder (or Year/Journal structure from metadata). Saves 15 mins.

### C. Phase 3: Downloading
*   **Deep**: Tries Direct -> Unpaywall -> Semantic Scholar -> DuckDuckGo -> Google -> Landing Page Scraping.
*   **Fast**: **CUT** all "Search" steps.
    *   Only attempts:
        1.  `Source URL` (Direct link from API)
        2.  `Unpaywall` (DOI lookup)
    *   If these fail, the paper is skipped immediately.

---

## 3. UI Implementation
Add a Radio Button to the Sidebar:

**Research Intensity:**
*   ( ) **⚡ Fast (Direct Downloads Only)**
    *   *Best for: Quick checks, gathering easy PDFs, saving time.*
*   (•) **🧠 Deep (AI Sort + Web Scrape)**
    *   *Best for: Comprehensive libraries, finding obscure papers, organized research.*

---

## 4. Why 15 Minutes?
*   **1000 Papers**:
    *   ~600 will have direct links. @ 2s/paper (4 threads) = **5 mins**.
    *   ~400 will fail instantly. @ 0.1s/paper = **<1 min**.
    *   Search/Overhead = **5 mins**.
    *   **Total**: ~11-15 Minutes.

## Decision
Does this meet your requirements? If yes, I will proceed to implement the UI toggle and backend logic.
