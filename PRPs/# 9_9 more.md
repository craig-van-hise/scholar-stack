

### PRP: Refactoring to High-Yield PDF Auditor

**Role:** Senior Data Systems Engineer
**Task:** Refactor the `ResearchCrawler` to fix the thread-crashes and improve "Expert Panel" targeting.

## 1. Deeper Expert Discovery

* **Action:** Increase the "Probe" count from 50 to **200**.
* **Action:** Select the **Top 15** experts instead of 10.
* **Goal:** This forces the inclusion of specialized authors like Choueiri who might be cited less than the "Founding Fathers" like Blauert.

## 2. Technical Synonym Sanitization

* **Filter:** Discard any learned synonym that matches a "Stop Phrase" list (of the, for the, based on, results of).
* **Requirement:** Learned synonyms must be **at least 2 words long** and contain at least one word longer than 6 characters.

## 3. Robust "Front-Matter" PDF Audit

Refactor the PDF check to be "Crash-Proof":

* **Extraction:** Use `page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE | fitz.TEXT_DEHYPHENATE)`.
* **Stability:** Specifically ignore "Movie" or "Widget" annotations which are triggering the MuPDF errors.
* **Scope:** Search for the **Fuzzy Regex** (`cross[\s\-]*talk[\s\-]*cancellations?`) only in the first **10,000 characters** of the PDF (the Front-Matter).

---

### The Corrected "Front-Matter" Logic for the Agent

Give this specific code to the agent to replace the current failing PDF check:

```python
import fitz  # PyMuPDF

def robust_front_matter_audit(pdf_path, target_pattern):
    """Audits the first ~2 pages of a PDF without crashing on annotations."""
    try:
        # Open with 'repair' logic ignored to prevent 'Movie' annotation crashes
        doc = fitz.open(pdf_path)
        text_block = ""
        
        # Limit to first 2 pages (The "Gate")
        for i in range(min(2, doc.page_count)):
            page = doc.load_page(i)
            # Use 'text' mode to ignore non-textual streams (Movies, Widgets)
            text_block += page.get_text("text")
            
        doc.close()

        # Fuzzy Regex Check (Title/Abstract/Keywords area)
        if re.search(target_pattern, text_block, re.IGNORECASE):
            return True
        return False
    except Exception as e:
        # Log the error but don't stop the script
        print(f"   ⚠️ Skipping corrupt/complex PDF {pdf_path}: {e}")
        return False

```

