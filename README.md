
# ScholarStack: Your AI Research Librarian

**ScholarStack** is an intelligent, AI-driven automation pipeline that acts as a digital librarian for building comprehensive academic libraries. It retrieves, reads, and organizes research papers, transforming a simple query into a **structured, downloadable library** categorized by AI.

## 🚀 Features

* **Omni-Channel Search**: Your librarian leverages **OpenAlex** to query a massive global index of research papers, utilizing **Unpaywall** to resolve open-access PDF links.
* **Topic Expansion**: Uses **Google Gemini** to generate intelligent search verticals (e.g., "Spatial Audio" -> "Ambisonics", "Binaural") to find papers that keyword matching often misses.
* **Smart Retrieval**: Aggressively acquires PDFs and validates file headers to ensure you receive high-quality, readable documents. Uses parallel processing for max speed.
* **Strict Taxonomy**: Powered by **Google Gemini**, the agent reads abstracts and organizes papers into precise, technical sub-fields (e.g., "Ambisonics" instead of "General Audio").
* **Search History & Persistence**: The app "remembers" your settings between sessions. A **Mission Log** lets you review and reload past search configurations instantly.
* **Curated Packaging**: Packages your research into a **downloadable ZIP file** or syncs it directly to **Google Drive**.
* **Modern Interface**: A Streamlit web app with **Research Modes** (Fast vs. Deep), sortable history, and granular controls.
* **Storage Management**: Automatically manages disk space by cleaning up old missions and serving large files efficiently.

---

---

## 📂 Project Structure

*   **`src/`**: Core application code (`app.py`, pipelines).
*   **`data/`**: Application state (`search_history.json`, `user_settings.json`), search cache, and `Library/` output.
*   **`scripts/`**: Utility scripts for verification and debugging (e.g., `verify_density.py`).
*   **`tests/`**: Unit tests and test data.
*   **`PRPs/`**: Product Requirements Prompts (Feature backlog).

## 📂 The "Stacked" Output

ScholarStack organizes your research into a clean, logical structure. Whether you download the **ZIP** or sync to **Drive**, you get:

```text
Library_Topic_Name/
├── Catalog_Summary.md          # A master manifest (includes Search Settings, Date Range, Sort Method)
├── Keyword_Folder/             # (Optional) Segregated by your specific search term
│   ├── Category_A/             # Precise AI Cluster (e.g., "Diffraction Modeling")
│   │   ├── paper_1.pdf
│   │   └── index.json          # Metadata
│   └── Category_B/             # (e.g., "Binaural Rendering")
│       └── paper_2.pdf
└── ...

```

---

## 🛠️ Setup & Installation

### Prerequisites

1. **Python 3.10+**
2. **Google Cloud Project (for Auth & Drive Sync):**
* Create a project at [console.cloud.google.com](https://console.cloud.google.com).
* Enable **Google Drive API**.
* Create OAuth 2.0 Credentials (Web Application).
* Download the JSON and save it as `client_secrets.json` in the project root.


3. **Gemini API Key (Optional but Recommended):**
* Get a free key from [aistudio.google.com](https://aistudio.google.com).
* **Important:** Ensure your key is in a `.env` file as `GOOGLE_API_KEY=...`. The system is configured to prioritize this file over shell variables to prevent key exhaustion errors.



### Installation

```bash
git clone https://github.com/craig-van-hise/scholar-stack.git
cd scholar-stack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

---

## 💻 Running the Web App

To launch the interface:

```bash
source .venv/bin/activate && streamlit run src/app.py

```

* **Search & Curate**: Enter your topic and watch the librarian agent work in real-time.
* **Export**: Once the pipeline completes, download the organized **ZIP file** or click to sync the folder to your **Google Drive**.
* **AI Power**: Add your Gemini API Key in the "Settings" sidebar to enable the intelligent folder categorization.

---

## ⚠️ Notes

* **Data Privacy**: ScholarStack processes data locally and only exports to Google Drive if authorized.
* **Storage**: The app manages a local cache of recent missions. Older missions are automatically cleaned up to save space.
* **Rate Limits**: Includes automatic backoff for Semantic Scholar to prevent API interruptions.

## License

MIT License

---

