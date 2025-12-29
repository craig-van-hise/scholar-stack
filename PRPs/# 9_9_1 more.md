
### PRP: LLM-Augmented Research Crawler

**Role:** Senior AI Systems Architect
**Task:** Refactor the `ResearchCrawler` to use LLM-based semantic expansion at both the Topic and Keyword stages.

#### 1. Semantic Topic Expansion (Pre-Search)

* **Logic:** Use the existing `expand_topic_with_llm` method (or create a better prompt) to turn the raw topic into a Boolean string of 3-4 academic synonyms.
* **Goal:** Increase the recall of the "Expert Panel" by searching for "3D Audio" and "Immersive Sound" simultaneously.

#### 2. Technical Vocabulary Synthesis (Expert-Driven)

* **Action:** Instead of counting N-grams, send the list of 150 titles from the Expert Panel to the LLM.
* **Prompt Logic:** *"I am looking for papers about [Keyword]. Below are recent titles from experts in this field. Identify 10 highly specific technical terms, methods, or filter types used in these titles that are synonymous or closely related to [Keyword]. Exclude generic filler like 'dataset' or 'analysis'."*

#### 3. Consolidated Multi-Term Dragnet

* **The Net:** Construct the final query using the LLM's technical synonyms + the LLM's topic synonyms.
* **The Gate:** Apply the **Robust PDF Front-Matter Audit** (ignoring annotations) to find the fuzzy regex of the *original* keyword.

---

### Implementation Block for the Agent

Give this code to the agent to replace the "N-Gram junk" with LLM-curated technical synonyms.

```python
def get_technical_synonyms_from_llm(self, titles, seed_keyword):
    """Uses LLM to clean the 'junk' out of the panel's vocabulary."""
    if not titles: return []
    
    prompt = (
        f"I am researching '{seed_keyword}'. Here is a list of recent titles from the top experts in this field:\n"
        f"{' | '.join(titles[:100])}\n\n"
        f"Based on these titles, provide a comma-separated list of the 10 most specific technical synonyms, "
        f"mathematical methods, or alternative names for '{seed_keyword}'. "
        f"Strictly avoid generic phrases like 'dataset', 'system', 'audio', or 'study'. "
        f"Return ONLY the comma-separated list."
    )
    
    # Trigger your LLM generation method here
    response = self.llm_query(prompt) 
    synonyms = [s.strip().lower() for s in response.split(',') if len(s.strip()) > 5]
    return synonyms

# --- UPDATED SEARCH FLOW ---
# 1. Topic expansion: "Spatial Audio" -> "3D Audio"
# 2. Expert Probe: Find Nelson, Choueiri, etc.
# 3. Titles -> LLM -> Technical Synonyms (e.g., "Recursive Ambiophonics", "Stereo Dipole")
# 4. Dragnet -> PDF Audit

```

