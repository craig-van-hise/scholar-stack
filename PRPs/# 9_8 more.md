
### The Real Architecture: "Dredge Metadata, Audit the PDF"

If we cannot trust OpenAlex's metadata to *prove* the paper is relevant, we can only use it to *suggest* it might be. The **only** way to get the Choueiri paper (and the other 90+ missing ones) is to move the "Gate" to the **actual source text of the PDF.**

The tool must stop trying to be "clever" with OpenAlex's broken snippets. It needs to become a **High-Volume Pipe** that fetches everything even remotely related and then runs the "Strict Gate" on the **Full Text of the PDF** itself.

---

# PRP: Refactoring to "Full-Text PDF Validation"

**Role:** Senior Lead Developer / Search Architect
**Task:** Refactor the `ResearchCrawler` to implement a "Broad Metadata Dredge" followed by a "Strict Full-Text PDF Audit."

## 1. The Broad Dredge (Phase 4 Retrieval)

* **Goal:** Maximize Recall. We don't care about noise here; we care about not missing the 100.
* **API Query:** Use the Expanded Boolean query: `("{keywords}" OR "{synonym1}" ... OR "{synonym10}") AND ("{topic}")`.
* **The Change:** **Disable** the strict local keyword filter during the `execute_openalex_query` phase. If a paper matches the API query, **Accept it into the Download Queue.**

## 2. The "Strict Gate" (Full-Text Validation)

The real "crosstalk cancellation" check happens **AFTER** the PDF is in local memory.

* **Requirement:** 1. Download the PDF to a temporary buffer/folder.
2. Extract the **Full Text** from the PDF (using `PyMuPDF` or `pdfplumber`).
3. Run the **Strict Regex Gate** (`cross[\s\-]*talk[\s\-]*cancellations?`) on the **entire document**.
4. **If found:** Keep the paper and add to `research_catalog.csv`.
5. **If not found:** Delete the PDF and discard the entry.

## 3. Backdoor Discovery (Unchanged)

* Identify the **10 Expert Authors** from the bibliography of the initial seed.
* Extract the **Top 15 technical N-grams** from their recent work to power the "Broad Dredge."
* **Debug:** Print the 10 Author names to the console so we can see the "Expert Panel."

---

### Why this is the ONLY way to solve the Choueiri problem:

1. **OpenAlex is the "Finder":** It finds the *existence* of a Choueiri paper because of its citations and topic.
2. **The PDF is the "Prover":** Since OpenAlex's abstract is garbage/truncated, we don't look at it. We go straight to the PDF, find the phrase "crosstalk cancellation" in the 5th sentence (or 5th page), and **confirm** it.

This architecture treats OpenAlex like a phone book (which is all it's good for) and the PDF as the source of truth. This is how you hit your 100-paper quota with 100% precision and zero "missed" papers.

