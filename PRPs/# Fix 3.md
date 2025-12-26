
### ** Fix 3 **

The cleanup logic is still failing because the `index.json` file makes the folders appear 'not empty.' Also, the date format is wrong.
**Please rewrite the cleanup and output section of `3_download_library.py` with this specific logic:**
1. **Strict Cleanup:**
* Iterate through all category folders in `./Library`.
* Check if the folder contains any files ending in `.pdf`.
* **If NO `.pdf` files exist:** Delete the entire folder (using `shutil.rmtree`), even if `index.json` exists.


2. **Date Formatting:**
* In the `Library_Catalog.md` output, ensure the date is strictly formatted as **YYYY/MM/DD**.
* Do not just show the Year. If the date is missing, use 'Unknown'.


3. **Order of Operations:**
* Run downloads.
* Run the PDF-based cleanup.
* **Only then** zip the remaining folders into `Library_Export.zip`.




