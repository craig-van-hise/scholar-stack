
### ** Phase 4 **

"Phase 3 is complete. I have the folder structure and categorized CSV. Now, let's build the final **Phase 4: The Physical Librarian**.
1. **Create `3_download_library.py**`:
* Load `research_catalog_categorized.csv`.
* Iterate through every row where `Is_Paywalled` is False.


2. **The Smart Download Logic (Crucial)**:
* Use `requests` to stream the file. **Use a standard browser User-Agent.**
* **Determine Filename:**
* First, check the `Content-Disposition` header in the response for the true filename.
* If missing, parse the filename from the end of the URL.
* **Sanitize:** Remove illegal characters.
* **Fallback:** If the name is generic (like 'download.pdf' or 'view'), append the first 20 chars of the Title to make it unique.


* **Save:** Save to `./Library/{Category}/{Final_Filename}`.
* **Update Catalog:** Update the `Original_Filename` column in the DataFrame with the actual saved name, and set `Is_Downloaded` = True.


3. **The Export Logic (For Firebase)**:
* After the loop finishes, **create a JSON index file** (`index.json`) inside each Category folder listing the papers in that folder.
* **Zip the entire library:** Use `shutil.make_archive` to create `Library_Export.zip` from the `./Library` directory.
* Print: 'READY FOR DOWNLOAD: Library_Export.zip'.


4. **Final Output**: Save the final dataframe to `final_library_catalog.csv`."



