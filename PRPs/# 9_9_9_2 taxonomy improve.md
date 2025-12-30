
# PRP: Refactor Taxonomy Logic to Structured Output

**Context:**
The current implementation of `src/2_cluster_taxonomy.py` relies on manual JSON parsing and regex cleaning (`clean_json_string`), which is fragile. Furthermore, the categorization logic allows "hallucinations" where the LLM assigns categories that do not align with the paper's text, or generates overly verbose category names.

**Objective:**
Refactor the `cluster_and_categorize` function to use **Gemini's Native Structured Output (`response_schema`)**. This will enforce strict JSON generation and require the LLM to provide "evidence" for every category assignment.

**Target File:** `src/2_cluster_taxonomy.py`

## 🛠️ Engineering Requirements

### 1. Dependency Updates

* Import `typing_extensions` at the top of the file to support schema definitions.

### 2. Schema Definition

Define a strict `TypedDict` schema outside the main function to enforce the output structure:

```python
class PaperClassification(typing_extensions.TypedDict):
    id: str
    category_name: str
    justification_quote: str  # Forces the LLM to prove its work

class TaxonomyResponse(typing_extensions.TypedDict):
    assignments: list[PaperClassification]

```

### 3. Prompt Logic Refactor

Inside `cluster_and_categorize`, specifically within the "Logic for Large Groups (LLM)" loop:

* **Remove:** The legacy `clean_json_string` function call and manual `json.loads` on `response.text`.
* **Update Prompt:** Change the prompt to explicitly request the `justification_quote` (a snippet from the abstract) that supports the categorization.
* **Update API Call:** Modify `model.generate_content` to use the `response_schema` parameter:
```python
response = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=TaxonomyResponse
    )
)

```



### 4. Implementation Details

* **Input Data:** Continue using `papers_payload` (id, title, description).
* **Processing:** Instead of regex cleaning, directly access `json.loads(response.text)['assignments']`.
* **Sanitization:** Ensure the `category_name` is still truncated to max 4 words programmatically (as a fail-safe), even though the schema encourages brevity.
* **Logging:** Add a `print` statement in the loop to display the `category_name` alongside the `justification_quote` to the console. This serves as a "sanity check" for the user to see *why* a paper was categorized a certain way.

### 5. Cleanup

* Delete the now obsolete `clean_json_string` helper function.

## ✅ Definition of Done

1. The code runs without `json.JSONDecodeError`.
2. Every categorized paper includes an internal "proof" (quote) used by the LLM to make the decision.
3. Category names are concise (Noun Phrases, < 4 words).
4. The fallback logic (retries and "Overview" assignment) remains intact for API failures.