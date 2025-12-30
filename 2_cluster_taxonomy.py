import pandas as pd
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import time
import re
import argparse
import shutil
from collections import Counter
import sys

# Load environment variables
# Load environment variables (Force override to prevent stale shell keys)
load_dotenv(override=True)

def clean_json_string(s):
    """Helper to clean markdown formatting from JSON string."""
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    if s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def sanitize_folder_name(name):
    """Sanitizes category names for file system compatibility."""
    clean = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in name])
    return clean.strip().replace(' ', '_')





def get_best_model():
    """Dynamically finds the best available Flash model."""
    try:
        available_models = []
        for m in genai.list_models():
            # Filter for generation models with 'flash' in name
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
                available_models.append(m.name)
        
        if not available_models: 
            return 'models/gemini-pro' # Fallback if no flash
        
        available_models.sort()
        # Phase 1 logic picks the last one (usually latest)
        best_model = available_models[-1]
        print(f"Selected Model: {best_model}", flush=True)
        return best_model
    except:
        return 'models/gemini-1.5-flash'

def cluster_and_categorize(topic, sort_method="Most Relevant", limit=100, no_llm=False, use_keywords=False):
    print("=== Phase 3: The Smart Architect (Improved Clustering) ===", flush=True)
    print(f"Topic: {topic}")
    print(f"Prioritize By: {sort_method}, Limit: {limit}", flush=True)
    

        
    # --- AUTOMATED CLEANUP ---

        

    csv_path = "research_catalog.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 1. Pre-Processing
    initial_count = len(df)
    df = df[df['Title'].str.len() > 15] 
    df = df[~df['Title'].str.lower().isin(['audio', 'spatial audio', 'introduction', 'front matter', 'back matter', 'index'])]
    
    # --- SORTING LOGIC ---
    if sort_method in ["Date: Newest", "Date: Oldest"]:
        # Ensure date format
        df['Publication_Date'] = pd.to_datetime(df['Publication_Date'], errors='coerce')
        
        if sort_method == "Date: Newest":
            print("Sorting papers by Date (Newest First)...")
            df = df.sort_values(by='Publication_Date', ascending=False)
        else: # Oldest
            print("Sorting papers by Date (Oldest First)...")
            df = df.sort_values(by='Publication_Date', ascending=True)
            
    # --- LIMITING LOGIC (BUFFERED) ---
    # We buffer input to AI because some papers might be DISCARDED.
    # User calls this "Musical Chairs". We need to ensure we have enough valid papers left.
    # Buffer Strategy: Double the limit or add 50, whichever is safer.
    process_limit = max(limit * 2, limit + 50)
    if len(df) > process_limit:
        print(f"Trimming {len(df)} papers to {process_limit} for AI processing (Buffer included)...")
        df = df.head(process_limit)
    
    print(f"Loaded {len(df)} valid papers from catalog.")

    if df.empty:
        print("No valid papers to categorize.")
        return

    # 2. AI Categorization Logic
    api_key = os.getenv("GOOGLE_API_KEY")
    taxonomy_map = {}
    ai_success = False

    if not api_key or no_llm:
        if no_llm: print("⚠️ AI Disabled by --no_llm flag.")
        else: print("⚠️ No Google API Key found. Skipping AI Categorization.")
        print(">> Falling back to single folder structure.")
    else:

        # Valid API Key case (Standardized Init)
        genai.configure(api_key=api_key)
        
        # Valid API Key case (Standardized Init)
        genai.configure(api_key=api_key)
        
        # Get unique verticals (handles case where column might be missing)
        if 'Search_Vertical' not in df.columns:
            df['Search_Vertical'] = 'Unsorted'
        unique_verticals = df['Search_Vertical'].unique()
        print(f"DEBUG: Processing {len(unique_verticals)} Keyword Groups for Taxonomy...", flush=True)

        for vertical in unique_verticals:
            print(f"\n   -> Analyzing Group: '{vertical}'...", flush=True)
            v_df = df[df['Search_Vertical'] == vertical]
            
            if v_df.empty: continue

            # Create Payload for this vertical
            papers_payload = []
            for index, row in v_df.iterrows():
                # Use DOI as robust ID
                paper_id = row['DOI'] if pd.notna(row['DOI']) and str(row['DOI']).strip() else row['Title']
                papers_payload.append({
                    "id": paper_id,
                    "title": row['Title'],
                    "description": str(row['Description'])[:500]
                })

            num_papers_v = len(v_df)
            
            # --- Logic for Small Groups ---
            if num_papers_v < 6:
                print(f"      Small group ({num_papers_v} papers). Assigning to '{vertical} Overview'.")
                for p in papers_payload:
                    taxonomy_map[p['id']] = f"{vertical} Overview"
                continue # Skip LLM

            # --- Logic for Large Groups (LLM) ---
            # Dynamic prompt constraints based on group size
            if num_papers_v < 20:
                 target_cats = "exactly 2"
                 density_note = f"roughly {int(num_papers_v/2)} papers"
            elif num_papers_v < 60:
                 target_cats = "exactly 4"
                 density_note = f"roughly {int(num_papers_v/4)} papers"
            else:
                 target_cats = "5-8"
                 density_note = "balanced distribution"

            model_name = get_best_model()

            prompt = f"""
            You are an expert academic librarian organizing a specific sub-folder of papers on: "{vertical}" (Topic: {topic}).
            Input: {num_papers_v} academic papers.
            
            Task:
            1. **Analyze**: Identify **{target_cats}** distinct technical themes within this specific sub-field.
            2. **Assign**: Assign EVERY paper to one of these themes.
            3. **Filter**: If a paper is unrelated to "{vertical}", assign "DISCARD".
            
            Critical Constraints:
            1. **Context**: These papers are ALREADY filtered by keyword "{vertical}". Do NOT create a category named "{vertical}". Break it down further (e.g. if "{vertical}"="HRTF", use "HRTF Measurement", "HRTF Personalization").
            2. **Broad Clusters**: Do NOT map 1-to-1.
            3. **Forbidden**: "General", "Miscellaneous", "Other".
            4. **Density**: Each theme should have {density_note}.
            
            Output Format:
            Return strictly a JSON object. 
            KEYS = The exact "id" provided in the input. VALUES = Category Name.
            
            Papers:
            {json.dumps(papers_payload, indent=2)}
            """

            # Retry Loop (Per Vertical)
            model = genai.GenerativeModel(model_name)
            local_success = False
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    if response.text:
                        cleaned_response = clean_json_string(response.text)
                        local_map = json.loads(cleaned_response)
                        taxonomy_map.update(local_map)
                        local_success = True
                        print(f"      Refined into {len(set(local_map.values()))} categories.", flush=True)
                        break
                except Exception as e:
                     if "429" in str(e):
                        time.sleep(10) # 429 backoff
                     elif attempt == max_retries - 1:
                        print(f"      ❌ Failed to categorize '{vertical}': {e}")

            if not local_success:
                 # Fallback for this vertical ONLY
                 print(f"      Falling back to '{vertical} Overview'.")
                 for p in papers_payload:
                     taxonomy_map[p['id']] = f"{vertical} Overview"

            time.sleep(2) # Rate limit hygiene

        if len(taxonomy_map) > 0:
            ai_success = True
        else:
             print(">> Global AI Failure: No categories generated.")


    # Debug: Print Raw Categories
    if ai_success:
        raw_counts = Counter(taxonomy_map.values())
        print("DEBUG RAW AI CATEGORIES:")
        for k, v in raw_counts.items():
            print(f"   '{k}': {v}")
            
    # 3. Post-Processing / Fallback Assignment
    if ai_success:
        # Enforce Orphan Rules
        # Enforce Orphan Rules (Folder Density Check)
        # We must ensure that every FOLDER has at least 2 papers. 
        # If use_keywords=True, a Global Category might satisfy count > 2, 
        # but split across keywords, it might result in size 1 folders.
        
        # 1. Map current AI categories to the DataFrame temporarily
        mapped_count = 0
        total_rows = len(df)
        for idx, row in df.iterrows():
             pid = row['DOI'] if pd.notna(row['DOI']) and str(row['DOI']).strip() else row['Title']
             cat = taxonomy_map.get(pid, "Miscellaneous")
             if cat != "Miscellaneous": mapped_count += 1
             df.at[idx, '_Temp_Cat'] = cat
        
        print(f"DEBUG: Mapped {mapped_count}/{total_rows} papers to categories. (Rest are Miscellaneous)")

        # 2. Check Density
        if use_keywords:
             # Check (Vertical, Category) pairs
             # Ensure Search_Vertical is present
             if 'Search_Vertical' not in df.columns:
                 df['Search_Vertical'] = 'Unsorted'
                 
             groups = df.groupby(['Search_Vertical', '_Temp_Cat']).size()
             global_counts = df['_Temp_Cat'].value_counts()
             
             for (vertical, category), local_count in groups.items():
                 if category == "DISCARD": continue
                 
                 # Density Rule (Relaxed for Small Pools): 
                 # Only merge if the category is a global orphan (Total < 2).
                 # If the category exists validly (>=2 papers globally), allow it to exist 
                 # in local keyword folders even as a singleton (Size 1) to preserve taxonomy.
                 global_count = global_counts.get(category, 0)
                 
                 is_globally_weak = global_count < 2
                 
                 if is_globally_weak:
                     # Update the main taxonomy map for these specific items to 'Miscellaneous'
                     mask = (df['Search_Vertical'] == vertical) & (df['_Temp_Cat'] == category)
                     to_fix = df[mask]
                     for _, r in to_fix.iterrows():
                         pid = r['DOI'] if pd.notna(r['DOI']) and str(r['DOI']).strip() else r['Title']
                         taxonomy_map[pid] = "Miscellaneous"
        else:
            # Global Density Check (Original)
            counts = Counter([cat for cat in taxonomy_map.values() if cat != "DISCARD"])
            orphans = [cat for cat, count in counts.items() if count < 2]
            if orphans:
                general_cat = "Miscellaneous"
                for doc_id, cat in taxonomy_map.items():
                    if cat in orphans:
                        taxonomy_map[doc_id] = general_cat
    else:
        # Fallback Mode
        pass

    # 4. Organization
    df['Topic'] = topic
    
    # Base Root (Topic Level)
    topic_sanitized = sanitize_folder_name(topic)
    base_library_root = f"./Library/{topic_sanitized}"
    
    categories_found = set()
    rows_to_drop = []
    df['Directory_Path'] = None

    for index, row in df.iterrows():
        # Robust Lookup
        paper_id = row['DOI'] if pd.notna(row['DOI']) and str(row['DOI']).strip() else row['Title']
        
        # Check taxonomy map
        category = "Miscellaneous"
        if ai_success:
            category = taxonomy_map.get(paper_id, "Miscellaneous")
            
        if category == "DISCARD":
            rows_to_drop.append(index)
            continue
        
        df.at[index, 'Category'] = category
        categories_found.add(category)
        
        # Construct Path
        safe_category = sanitize_folder_name(category)
        
        # Logic: <Topic>/<Keyword?>/<Category>
        # Logic: <Topic>/<Keyword?>/<Category>
        current_root = base_library_root
        
        # Use Keywords as Sub-folders?
        if use_keywords:
            raw_vertical = row.get('Search_Vertical', 'Unsorted')
            safe_vertical = sanitize_folder_name(str(raw_vertical))
            
            # If the keyword IS the topic, put it in a general folder so it doesn't clutter root
            # But generally, we treat the Search Vertical as the Level 2 folder.
            if safe_vertical.lower() == topic_sanitized.lower():
                 current_root = os.path.join(base_library_root, "_General")
            else:
                 current_root = os.path.join(base_library_root, safe_vertical)
        
        # Determine Final Directory
        # Logic: current_root is now <Topic>/<Keyword> (or <Topic> if not using keywords)
        # We ALWAYS append the Category.
        # User explicitly requested strict "Library/Topic/Keyword/Category".
        
        dir_path = os.path.join(current_root, safe_category)
            
        os.makedirs(dir_path, exist_ok=True)
        df.at[index, 'Directory_Path'] = dir_path

    if rows_to_drop:
        print(f"\n--- 🗑️ Rejected Papers Audit ({len(rows_to_drop)}) ---")
        for idx in rows_to_drop:
            print(f"   [Discarded] {df.loc[idx, 'Title']}")
        print("------------------------------------------\n")
        
        df = df.drop(rows_to_drop)
        print(f"Rejected {len(rows_to_drop)} off-topic papers.")

    # --- FINAL TRIM TO EXACT LIMIT ---
    # Now that we've filtered, strictly enforce the user limit
    if len(df) > limit:
         print(f"Final Count {len(df)} > Requested {limit}. Trimming excess to match quota.")
         df = df.head(limit)

    output_csv = "research_catalog_categorized.csv"
    df.to_csv(output_csv, index=False)
    
    print("\n=== Categorization Complete ===")
    if ai_success:
        print(f"AI Organized into {len(categories_found)} Categories.")
    else:
        print("Fallback Mode: Papers saved to 'Miscellaneous'.")
        
    print(f"Structure ready in '{base_library_root}/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Architect: Cluster and Filter Papers")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--sort", default="Most Relevant")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--no_llm", action="store_true")
    parser.add_argument("--use_keywords", action="store_true")
    args = parser.parse_args()
    
    cluster_and_categorize(args.topic, args.sort, args.limit, args.no_llm, args.use_keywords)

