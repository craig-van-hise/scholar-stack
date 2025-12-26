
### **The Code Update**

I need to update Phase 3 and 4 to support a persistent library where multiple topics can coexist.
**Please rewrite `2_cluster_taxonomy.py`:**
1. **Arguments:** Keep the `--topic` argument.
2. **Paths:** Set the root for this batch to `./Library/{args.topic}/`. Use `os.makedirs(..., exist_ok=True)` to allow adding to existing topics.
3. **The 'Golden Path':** Add a column `Directory_Path` to the CSV containing the full relative path for each paper's category.
4. **The Bouncer:** Keep the 'DISCARD' logic to filter irrelevant papers.


**Please rewrite `3_download_library.py`:**
1. **Targeted Logic:** Read `Directory_Path` from the CSV to know exactly where to save each file.
2. **Surgical Cleanup:**
* After downloading, iterate **only** through the unique paths listed in the `Directory_Path` column of the current CSV.
* If one of *those* folders has no PDF files, delete it.
* **Crucial:** Do NOT iterate through the entire `./Library` root. Do not touch other topic folders.


3. **Focused Export:**
* Create a zip file named `Library_{Topic}.zip` (e.g., `Library_Spatial_Audio.zip`) that contains only the folder for the current topic.


4. **Catalog:**
* Generate a markdown catalog named `Catalog_{Topic}.md` inside the topic folder.
* Use `YYYY/MM/DD` date format.




