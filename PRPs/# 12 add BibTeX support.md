
### **PRP: BibTeX Export Support**

**Context:**
We are upgrading `ScholarStack`. Currently, we output a `Catalog_Summary.md` and `index.json` files. We need to add a **BibTeX export** feature to support users who write in LaTeX.

**The Task:**
Implement a `generate_bibtex(papers)` function and integrate it into the final "Packaging" phase of the pipeline.

**Technical Requirements:**

1. **File Creation:** The app must generate a single file named `library.bib` at the root of the export package (Zip/Drive).
2. **Citation Key Generation:** You must generate a unique "Citation Key" for every paper.
* **Format:** `[FirstAuthorLastName][Year][FirstWordOfTitle]` (e.g., `Vaswani2017Attention`).
* **Sanitization:** Ensure the key contains only alphanumeric characters (no spaces or hyphens).
* **Collision Handling:** If a key already exists (e.g., two papers by Smith in 2023), append a suffix (e.g., `Smith2023Deep_a`, `Smith2023Deep_b`).


3. **Entry Format:** Use the standard `@article{...}` structure.
* Map `title`  `title`
* Map `authors`  `author` (Format: `Lastname, Firstname and Lastname, Firstname...`)
* Map `year`  `year`
* Map `journal`  `journal`
* Map `doi`  `doi`
* Map `url`  `url`
* Map `abstract`  `abstract`


4. **Integration:** Ensure this file is included in the final ZIP archive and the Google Drive upload logic.

**Output:**
Return the Python code for the BibTeX generator function and show where to call it within the `package_library()` function.



