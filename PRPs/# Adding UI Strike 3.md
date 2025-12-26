
### **Strike 3: The Interface (Prompt)**


> "Strike 2 is done. Now, let's build **Strike 3: The User Interface**.
> **Create a file named `app.py` using the `streamlit` library.**
> **Goal:** A browser-based UI that collects inputs and triggers the `4_pipeline_manager.py`.
> **UI Layout & Logic:**
> 1. **Title:** 'Universal Research Librarian'.
> 2. **Sidebar Inputs:**
> * **Topic:** Text Input (Required).
> * **Keywords:** Text Input (Optional).
> * **Author:** Text Input (Optional).
> * **Date Range:** Date Input (Two dates, allow 'None').
> * **Publication:** Text Input (Optional).
> * **Sites:** Multiselect (Options: ArXiv, Scholar, CORE, DOAJ). Default to All.
> * **Paper Count:** Number Input (Default 10, Min 1, Max 150).
> 
> 
> 3. **Action:**
> * Add a big 'Start Research Mission' button.
> * When clicked, use `st.spinner` to show 'Research Agent is working...'.
> * Call `pipeline_manager.run_full_pipeline(...)`.
> 
> 
> 4. **Output:**
> * Display a live log of the process if possible (or just success/fail messages).
> * **Success:** Show a big `st.download_button` labeled 'Download Library' that links to the resulting Zip file.
> * **Preview:** Display the contents of the generated Markdown catalog (`Catalog_{Topic}.md`) directly in the browser so the user can read the summary before downloading."
> 
> 
> 
> 


