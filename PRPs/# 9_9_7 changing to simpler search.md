
### PRP: The "Direct Expansion" Refactor

**Role:** Senior Search Architect
**Task:** Delete the `search_via_citation_backdoor` complexity. Replace it with a **High-Fidelity Topic Expansion Search**.

#### 1. Phase 1: High-Quality Topic Expansion (LLM)

* **Goal:** Generate 15-20 specific sub-fields for the User's Topic.
* **Prompt Logic:** "The user is researching **{topic}**. Provide 20 academic synonyms, sub-disciplines, or related technical fields. (e.g., for 'Spatial Audio', include 'Binaural', 'Ambisonics', 'Wave Field Synthesis', 'HRTF', '3D Audio'). Return a clean list."

#### 2. Phase 2: The Direct "AND" Query

* **Logic:** Construct the OpenAlex query to require the **Primary Keyword** AND at least **One Topic Synonym**.
* **Query String:** `("crosstalk cancellation") AND ("Spatial Audio" OR "Binaural" OR "Ambisonics" OR "Wave Field Synthesis" ...)`
* **Why this wins:** This is the specific logic that catches the Choueiri paper (which is about "Crosstalk" in the context of "3D Audio") while killing the DSL papers (which are "Crosstalk" in the context of "Subscriber Lines").

#### 3. Phase 3: The Section-Aware PDF Gate

* **Action:** We still download the PDF and check the **First 2 Pages** for the fuzzy regex of the keyword.
* **Why:** OpenAlex abstracts are still untrustworthy. The API gets us to the right *file*, but the **PDF Auditor** confirms the *content*.

---

### Implementation Block for the Agent

Give this code to the agent. It replaces the entire complex "Backdoor" mess with your streamlined logic.

```python
    def search_via_direct_expansion(self):
        """
        Streamlined Strategy:
        1. Expand 'Topic' into ~20 high-quality sub-fields using LLM.
        2. Query: (Keyword) AND (Topic OR SubField1 OR SubField2...)
        3. Validate: PDF Front-Matter Audit.
        """
        print(f"\n🚀 STARTING DIRECT EXPANSION SEARCH for: '{self.raw_topic}' + '{self.keywords_list[0]}'")
        
        # --- STEP 1: HIGH-FIDELITY TOPIC EXPANSION ---
        print("   🧠 expanding topic scope with LLM...")
        prompt = (
            f"Generate 20 specific academic synonyms, sub-disciplines, or technical fields related to '{self.raw_topic}'. "
            f"Examples: If topic is 'Spatial Audio', include 'Binaural', 'Ambisonics', 'Wave Field Synthesis', 'HRTF'. "
            f"Return ONLY a comma-separated list."
        )
        # Assume self.llm_query handles the API call
        raw_synonyms = self.llm_query(prompt)
        topic_synonyms = [s.strip().replace('"', '') for s in raw_synonyms.split(',') if len(s.strip()) > 3]
        
        print(f"   ✅ Generated {len(topic_synonyms)} Domain Anchors: {topic_synonyms[:5]}...")

        # --- STEP 2: CONSTRUCT THE SUPER-QUERY ---
        # Logic: (Keyword) AND (Topic OR Synonym1 OR Synonym2...)
        # This mathematically eliminates 'Alien Crosstalk' (DSL) because DSL papers won't match the Topic synonyms.
        
        clean_keyword = self.keywords_list[0].replace('"', '')
        
        # Build the OR block for topics
        topic_block = " OR ".join([f'"{t}"' for t in ([self.raw_topic] + topic_synonyms)])
        
        # Final Query
        final_query = f'("{clean_keyword}") AND ({topic_block})'
        
        print(f"   🔎 Executing Query: {final_query[:100]}...")
        
        # --- STEP 3: EXECUTE & VALIDATE ---
        filters = "is_oa:true,type:article|conference-paper"
        if self.date_start: filters += f",publication_year:>{self.year_start-1}"
        
        # This calls the standard execution loop which now uses the ROBUST PDF AUDITOR
        self.execute_openalex_query("Direct Expansion", filters, final_query)

```

