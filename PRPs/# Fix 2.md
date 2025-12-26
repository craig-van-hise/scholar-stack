# Fix 2

The previous cleanup logic failed, and the CSV is unreadable. Please completely rewrite `3_download_library.py` with this strict logic:
1. **The Cleanup (Aggressive):**
* After downloads attempt to finish, iterate through every subfolder in `./Library`.
* Count the number of **files** inside.
* **If a folder is empty OR only contains hidden system files**, delete the folder using `shutil.rmtree`.
* *Only after cleanup*, create the `Library_Export.zip`.


2. **The Output (Human-Readable):**
* Instead of *only* a CSV, generate a file named **`Library_Catalog.md`**.
* **Format:** Group papers by `Category`.
* For each Category, create a Heading (`## Category Name`).
* List each paper as a bullet point:
* **Title** (Year)
* *Status:* [Downloaded/Missing]
* *Filename:* [Original_Filename]
* *Source:* [URL]
* *Abstract:* (First 200 chars...)


3. **Keep the Download Logic:** Maintain the smart filename detection and user-agent logic we established previously.


