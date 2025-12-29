
### Updated PRP 

**Role:** Search Architect
**Task:** Refactor the Final Dragnet construction to maximize recall by removing the Topic constraint.

**Requirements:**

1. **Drop the Topic Constraint:** In Phase 4 (The Final Dragnet), the API search query must consist **only** of the `(Original Keyword OR Technical Synonyms)`. Do not append `AND Topic`.
2. **Rely on the Gate:** Trust the **Section-Aware PDF Auditor** to do the heavy lifting. Since the auditor only looks for the original keyword in the front-matter of the PDF, it will automatically discard any non-topic papers caught by the broad synonyms.
3. **Synonym Quality:** Ensure the LLM provides **15 technical synonyms** (2-4 words each) to ensure the dragnet is wide enough to find the 100-paper quota.

