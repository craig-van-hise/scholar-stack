## Quick Guide: `open_alex_topic_hybrid_search.py`

This script creates a powerful **Hybrid Search Engine** for your OpenAlex taxonomy tree. It combines:

1. **Lexical Search (BM25):** Finds exact keyword matches (e.g., "Nuclear Physics").
2. **Semantic Search (Gemini + ChromaDB):** Finds conceptual matches (e.g., "Heart Attack" → "Myocardial Infarction").
3. **Smart Caching:** Saves the database locally so you don't pay for or wait for embeddings every time you run it.

---

### 1. Prerequisites

You need Python installed and the following libraries:

```bash
pip install google-generativeai chromadb rank-bm25

```

You also need a **Google AI Studio API Key** (Free tier is sufficient).

### 2. Setup

Ensure your folder structure looks like this:

```text
/my_project_folder
  ├── open_alex_topic_hybrid_search.py   # The script provided above
  ├── openalex_tree.json                 # Your taxonomy data file
  └── tree_chroma_db/                    # (Created automatically after first run)

```

### 3. Configuration

Open the script `open_alex_topic_hybrid_search.py` in your code editor.

Scroll to the bottom `if __name__ == "__main__":` section and replace the placeholder with your actual key:

```python
GOOGLE_API_KEY = "AIzaSy..."  # <-- Paste your Google API Key here

```

### 4. Running the Search

Run the script from your terminal:

```bash
python open_alex_topic_hybrid_search.py

```

**What happens next?**

1. **First Run:** The script will detect that the database is empty. It will flatten your JSON tree and send the nodes to Google Gemini to generate embeddings. This might take a minute or two depending on the size of your tree.
2. **Subsequent Runs:** The script sees the `tree_chroma_db` folder. It **skips** the embedding generation and loads instantly.

### 5. Using the Search

Once loaded, you will see a prompt:

```text
--- Search System Ready (Type 'q' to exit) ---

Query: 

```

Type any term to test the hybrid capability:

* *Exact:* "Nuclear Fusion"
* *Vague:* "Clean energy sources"
* *Concept:* "Study of old coins" (Should find Numismatics or Archaeology)

### 6. Updating the Data

If you change `openalex_tree.json`, the cache will be outdated. To fix this, edit the script's usage section to force a rebuild **once**:

```python
# Change force_rebuild to True for one run
searcher.ingest_tree(tree_data, force_rebuild=True)

```

Run the script, then change it back to `False` to enjoy the caching again.