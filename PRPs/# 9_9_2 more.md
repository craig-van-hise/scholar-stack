

# PRP: Refined Semantic Discovery Logic

**Role:** Senior AI Prompt Engineer
**Task:** Refactor the `get_technical_synonyms_from_llm` method to prevent title-copying and maximize technical "bait" variety.

## 1. Multi-Stage Topic Expansion (Level 1+)

The user wants **more** of these.

* **Requirement:** Increase the topic expansion from 5 to **10-12 terms**.
* **Instruction:** Tell the LLM to include "Signal Processing" and "Acoustic Engineering" sub-disciplines to ensure we catch Choueiri's more mathematical papers.

## 2. Technical Phrase Extraction (Level 2 Fix)

Refactor the prompt for the Expert Vocabulary phase:

* **Constraint 1:** "Do NOT return full paper titles."
* **Constraint 2:** "Return only technical phrases between 2 and 4 words long."
* **Constraint 3:** "Focus on the **Mathematical Methods** and **Hardware Configurations** mentioned (e.g., 'Recursive Filters', 'Stereo Dipole', 'Transaural Synthesis')."
* **Constraint 4:** "Include common abbreviations (e.g., 'CTC', 'XTC', 'BRIR', 'HRTF')."

## 3. The "Broad Net" Final Search

* **Query Construction:** Use the ~10 Topic terms and the ~10 Method terms.
* **Logic:** `(Keyword OR Method1 OR Method2...) AND (Topic1 OR Topic2 OR Topic3...)`

---

### Corrected Implementation Block for the Agent

Give this code to the agent to fix the "Regurgitation" bug:

```python
def get_technical_synonyms_from_llm(self, titles, seed_keyword):
    prompt = (
        f"Goal: Identify 10 high-leverage search terms for the topic '{seed_keyword}'.\n"
        f"Context: Here are 150 titles from top experts in this field:\n"
        f"{' | '.join(titles[:150])}\n\n"
        f"TASKS:\n"
        f"1. Identify the CORE MATHEMATICAL METHODS or FILTER TYPES used.\n"
        f"2. Identify the HARDWARE SETUP terms (e.g., 'loudspeaker array', 'dipole').\n"
        f"3. Identify common ACRONYMS (e.g., CTC, XTC).\n"
        f"\nRULES:\n"
        f"- NO FULL TITLES.\n"
        f"- PHRASES MUST BE 2-4 WORDS MAX.\n"
        f"- RETURN ONLY A COMMA-SEPARATED LIST."
    )
    # Get response and clean it
    raw_response = self.llm_query(prompt)
    synonyms = [s.strip().lower() for s in raw_response.split(',') if len(s.strip().split()) > 1]
    return synonyms[:12] # Return more terms as requested

```
