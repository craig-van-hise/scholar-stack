
### ** Fix 4 **

**Please rewrite `2_cluster_taxonomy.py` with this exact logic:**
1. **Input:**
* Use `argparse` to accept a required argument: `--topic` (e.g., "Spatial Audio").
* Load `research_catalog.csv`.


2. **The "Bouncer" (Gemini):**
* Update the prompt: *'The user is researching "{topic}". Review these abstracts. If a paper is NOT primarily about {topic}, assign the category "DISCARD". For valid papers, group them into 4-6 technical categories.'*


3. **The Filter:**
* Drop rows where Category is 'DISCARD'.
* Print 'Rejected X off-topic papers.'


4. **The Structure:**
* **Root:** Set the base directory to `./Library/{topic_sanitized}/`.
* Create sub-folders there.


5. **The Output:**
* Add a column `Topic` to the DataFrame and set it to the provided argument.
* Save to `research_catalog_categorized.csv`."
 

