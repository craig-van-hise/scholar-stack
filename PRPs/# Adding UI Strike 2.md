
### **Strike 2: The Orchestrator (Prompt)**

> "Strike 1 is done. Now, let's build **Strike 2: The Orchestrator**.
> **Create a new script named `4_pipeline_manager.py`.**
> **Goal:** This script will act as the master controller. It accepts all the user inputs, runs the underlying scripts (1, 2, and 3) in order using `subprocess`, and returns the final zip file path.
> **Requirements:**
> 1. **Function `run_full_pipeline(...)`:**
> * Arguments: `topic` (required), `keywords`, `author`, `publication`, `date_start`, `date_end`, `sites` (list), `count` (default 10).
> * **Step 1 (Search):** Construct the command for `1_search_omni.py`. Pass all relevant flags. (e.g., `--query` should combine topic + keywords).
> * **Step 2 (Cluster):** Run `2_cluster_taxonomy.py` using `--topic`.
> * **Step 3 (Download):** Run `3_download_library.py`.
> 
> 
> 2. **Autonomous Logic:**
> * Use `subprocess.run(..., check=True)` to execute each step.
> * If any step fails, catch the error and stop the pipeline.
> * Print clear status messages (e.g., '--- Starting Phase 2: Search ---').
> 
> 
> 3. **Output:**
> * The function should return the path to the final zip file (`Library_{Topic}.zip`).
> 
> 
> 4. **Test Block:** Add an `if __name__ == "__main__":` block that allows me to run this manager from the terminal with hardcoded test values to verify it works."
> 
> 
