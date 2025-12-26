
### **The Fix: Smart Cleanup & Readable Catalog**

I need to refine `3_download_library.py` to fix two issues:
1. **Ghost Folder Cleanup (Critical):**
* The script currently zips *all* folders, even empty ones.
* **New Logic:** After the download loop finishes, iterate through `./Library`.
* If a category folder is empty (contains no files), **delete it** from the file system.
* *Then* create the `Library_Export.zip`. This ensures the zip only contains folders with actual papers.


2. **Human-Readable CSV:**
* The current CSV is hard to read.
* **New Logic:** When saving `final_library_catalog.csv`, reorder the columns to put the most important info first:
* `Category`, `Title`, `Publication_Date`, `Original_Filename`, `Source_URL`


* **Sort** the rows by `Category` so related papers are grouped together.
* (Optional) If possible, use a tab-separator (`sep='\t'`) or just standard comma, but ensure newlines in the Description don't break the format.




