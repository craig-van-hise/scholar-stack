
### ** Phase 3 **


"Phase 2 is a success! I have a `research_catalog.csv` with 17 papers. Now, let's build **Phase 3: The Smart Architect**.
1. **Create `2_cluster_taxonomy.py**`:
* This script must load `research_catalog.csv`.
* It must use the **Gemini 1.5 Flash** model (via `google-generativeai`) using the `GOOGLE_API_KEY` from our `.env` file.


2. **The AI Logic**:
* Send the list of Titles and Descriptions (Abstracts) to Gemini.
* Ask Gemini to: *'Analyze these papers and create 4-6 logical technical categories (Taxonomy) for a library. Return a JSON mapping of each Paper Title to a Category.'*


3. **The Organization (In Workspace)**:
* Update the `Category` column in the DataFrame based on Gemini's response.
* **Create a root directory named `./Library**` in the current workspace.
* Inside that, create sub-folders for each category (e.g., `./Library/Spatial_Audio_Reconstruction/`).
* Save the updated CSV as `research_catalog_categorized.csv`.


4. **Safety**: Ensure it handles API errors gracefully and uses a wait timer if the abstract list is long."
