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
import typing_extensions
import random  # Required for sampling

# Load environment variables (Force override to prevent stale shell keys)
load_dotenv(override=True)

# --- TYPING SCHEMAS ---
class TaxonomyList(typing_extensions.TypedDict):
    broad_categories: list[str]

class PaperClassification(typing_extensions.TypedDict):
    id: str
    category_name: str
    justification_quote: str 

class TaxonomyResponse(typing_extensions.TypedDict):
    assignments: list[PaperClassification]

# --- UTILS ---
def sanitize_folder_name(name):
    """Sanitizes category names for file system compatibility."""
    # Allow slash for internal path logic, but we handle that before calling this usually.
    # If this receives "Category/Subcat", we want to sanitize parts.
    clean = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in name])
    return clean.strip().replace(' ', '_')

def clean_json_string(json_str):
    json_str = json_str.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json_str.strip()

def get_best_model():
    """Dynamically finds the best available Flash model for large context."""
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
                available_models.append(m.name)
        
        if not available_models: 
            return 'models/gemini-1.5-flash' # Default fallback
        
        available_models.sort()
        best_model = available_models[-1] # Usually the latest version
        return best_model
    except:
        return 'models/gemini-1.5-flash'

# --- CORE LOGIC ---

def generate_root_taxonomy(model, titles, vertical, max_cats=12):
    """
    Phase 1: The Architect - Generates the Master List of Categories.
    
    SAFETY FIX: Uses 'Representative Sampling' to avoid Token Limits.
    Scanning 200 random titles is statistically sufficient to design the taxonomy.
    """
    
    # SAFETY: Cap the input to 200 titles to prevent Context/Token errors.
    if len(titles) > 200:
        print(f"      Sampling 200 representative titles from {len(titles)} to design taxonomy...", flush=True)
        # Use random.sample to get a diverse spread
        titles_subset = random.sample(titles, 200)
    else:
        titles_subset = titles

    titles_text = "\n".join([f"- {t}" for t in titles_subset])
    
    prompt = f"""
    You are a Senior Information Architect.
    I have a list of academic paper titles related to the search vertical: "{vertical}".
    
    Task:
    Create a **High-Level Taxonomy** of exactly 8 to {max_cats} Broad Domains that cover these papers.
    
    Rules:
    1. Categories must be **BROAD** (e.g., "Signal Processing", "Machine Learning", "Perception", "Hardware").
    2. **FORBIDDEN:** Do NOT use forward slashes (/) in names. Use "and" or "&" instead (e.g., "VR and AR", not "VR/AR").
    3. Do NOT create granular technical folders yet (e.g., avoid "Ambisonic Decoding Matrix").
    4. Return ONLY the list of category names.
    
    Sample Titles:
    {titles_text}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=TaxonomyList
            )
        )
        data = json.loads(clean_json_string(response.text))
        cats = data.get("broad_categories", [])
        
        # Fallback if model gets lazy and returns too few
        if len(cats) < 3:
             print("      ⚠️ Model returned too few categories. Forcing defaults.")
             return [f"{vertical} Theory", f"{vertical} Systems", f"{vertical} Evaluation", f"{vertical} Applications"]

        print(f"      ✅ Defined {len(cats)} Root Domains: {cats}")
        return cats
    except Exception as e:
        print(f"      ⚠️ Taxonomy Gen Failed: {e}. Using Default.")
        return [f"{vertical} General", f"{vertical} Theory", f"{vertical} Applications"]

def cluster_subfolder(model, papers_payload, parent_category):
    """Phase 3: The Specialist - Breaks down dense folders (Batched)."""
    print(f"      ⚡ Refining Dense Folder: '{parent_category}' ({len(papers_payload)} papers)...")
    
    BATCH_SIZE = 50
    num_batches = (len(papers_payload) + BATCH_SIZE - 1) // BATCH_SIZE
    all_assignments = {}

    for batch_idx in range(num_batches):
        batch = papers_payload[batch_idx * BATCH_SIZE : (batch_idx + 1) * BATCH_SIZE]
        
        prompt = f"""
        You are a Technical Specialist. 
        The folder "{parent_category}" has become too large.
        
        Task:
        1. Analyze these papers (Batch {batch_idx + 1}/{num_batches}).
        2. Identify **4 to 6 core themes**.
        3. Group papers into these themes. **Do NOT create single-paper categories.**
        4. Generalize the names (e.g., use "Ambisonic Comparison" instead of "Ambisonics vs Object-Based...").
        5. If a paper doesn't fit a specific theme, assign it to "General {parent_category}".
        
        Input Papers:
        {json.dumps(batch, indent=2)}
        """
        
        # Retry logic for sub-batches
        for attempt in range(3):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=TaxonomyResponse
                    )
                )
                data = json.loads(clean_json_string(response.text))
                batch_assignments = {item['id']: item['category_name'] for item in data.get('assignments', [])}
                all_assignments.update(batch_assignments)
                break # Success
            except Exception as e:
                if attempt == 2:
                    print(f"      ⚠️ Sub-clustering batch {batch_idx+1} failed: {e}")
                time.sleep(1)

    return all_assignments

def cluster_and_categorize(topic, sort_method="Most Relevant", limit=100, no_llm=False, use_keywords=False, fast_mode=False):
    print("=== Phase 3: The Smart Architect (Recursive Clustering) ===", flush=True)
    
    if fast_mode:
        print("⚡ Fast Mode Enabled: Skipping AI Clustering.", flush=True)
        no_llm = True

    # --- CSV LOAD ---
    csv_filename = "research_catalog.csv"
    data_dir_csv = os.path.join(os.path.dirname(__file__), "../data", csv_filename)
    csv_path = csv_filename if os.path.exists(csv_filename) else data_dir_csv
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_filename} not found.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Pre-Processing
    df = df[df['Title'].str.len() > 15] 
    df = df[~df['Title'].str.lower().isin(['audio', 'introduction', 'front matter', 'index'])]
    
    # Sorting
    if sort_method == "Date: Newest":
        df['Publication_Date'] = pd.to_datetime(df['Publication_Date'], errors='coerce')
        df = df.sort_values(by='Publication_Date', ascending=False)
    elif sort_method == "Date: Oldest":
        df['Publication_Date'] = pd.to_datetime(df['Publication_Date'], errors='coerce')
        df = df.sort_values(by='Publication_Date', ascending=True)

    # Limit
    process_limit = max(limit * 2, limit + 50)
    if len(df) > process_limit:
        df = df.head(process_limit)

    api_key = os.getenv("GOOGLE_API_KEY")
    taxonomy_map = {} # Maps DOI -> "Category" OR "Category/Subcategory"
    ai_success = False

    if not api_key or no_llm:
        print("⚠️ AI Disabled or Key Missing.")
    else:
        genai.configure(api_key=api_key)
        model_name = get_best_model()
        model = genai.GenerativeModel(model_name)
        
        if 'Search_Vertical' not in df.columns: df['Search_Vertical'] = 'Unsorted'
        unique_verticals = df['Search_Vertical'].unique()

        # --- MAIN CLUSTERING LOOP ---
        for vertical in unique_verticals:
            v_df = df[df['Search_Vertical'] == vertical]
            if v_df.empty: continue
            
            print(f"\n   -> Analyzing Vertical: '{vertical}' ({len(v_df)} papers)...", flush=True)

            # 1. Prepare Data
            papers_payload = []
            titles_only = []
            for index, row in v_df.iterrows():
                pid = row['DOI'] if pd.notna(row['DOI']) and str(row['DOI']).strip() else row['Title']
                desc = str(row['Description'])
                if len(desc) < 50: desc = f"Title: {row['Title']}"
                
                payload_item = {
                    "id": pid,
                    "title": row['Title'],
                    "description": desc[:500] # Cap context
                }
                papers_payload.append(payload_item)
                titles_only.append(row['Title'])

            # 2. Logic Gate: Small vs Large
            if len(v_df) < 15:
                # Too small for hierarchy
                for p in papers_payload: taxonomy_map[p['id']] = f"{vertical} Overview"
                continue

            # 3. PHASE 1: Generate Master Taxonomy (The Architect)
            # This ensures we don't have > 12 folders at the top level
            root_categories = generate_root_taxonomy(model, titles_only, vertical, max_cats=12)
            
            # 4. PHASE 2: Assign Papers to Root Categories (The Librarian)
            # We must batch this if > 50 papers to avoid output token limits
            BATCH_SIZE = 50
            num_batches = (len(papers_payload) + BATCH_SIZE - 1) // BATCH_SIZE
            
            broad_assignments = {} # PID -> Category
            
            for batch_idx in range(num_batches):
                batch = papers_payload[batch_idx * BATCH_SIZE : (batch_idx + 1) * BATCH_SIZE]
                
                prompt = f"""
                You are organizing papers into these SPECIFIC broad categories:
                {json.dumps(root_categories)}
                
                Input: {len(batch)} papers.
                Task: Assign every paper to exactly one of the categories above.
                If strictly unrelated, assign "DISCARD".
                
                Papers:
                {json.dumps(batch, indent=2)}
                """
                
                # Retry logic
                for attempt in range(3):
                    try:
                        resp = model.generate_content(
                            prompt,
                            generation_config=genai.GenerationConfig(
                                response_mime_type="application/json",
                                response_schema=TaxonomyResponse
                            )
                        )
                        data = json.loads(clean_json_string(resp.text))
                        for item in data.get('assignments', []):
                            broad_assignments[item['id']] = item['category_name']
                        print(f"      Batch {batch_idx+1}/{num_batches} sorted.")
                        break
                    except Exception as e:
                        if attempt == 2: print(f"      ❌ Batch failed: {e}")
                        time.sleep(2)
            
            # 5. PHASE 3: Density Check & Recursion (The Specialist)
            # Check which categories are too fat
            cat_counts = Counter(broad_assignments.values())
            
            for category, count in cat_counts.items():
                if category == "DISCARD": continue
                
                # Get all papers in this category
                category_pids = [pid for pid, cat in broad_assignments.items() if cat == category]
                
                # THRESHOLD: If > 15 papers, create Sub-Folders
                if count > 15:
                    # Filter payload for just these papers
                    sub_payload = [p for p in papers_payload if p['id'] in category_pids]
                    
                    # Call Sub-cluster routine
                    sub_map = cluster_subfolder(model, sub_payload, category)
                    
                    # Update Main Map
                    for pid in category_pids:
                        sub_cat = sub_map.get(pid, "General")
                        # FORMAT: "Parent/Child"
                        taxonomy_map[pid] = f"{category}/{sub_cat}"
                else:
                    # Keep as broad category
                    for pid in category_pids:
                        taxonomy_map[pid] = category
            
            ai_success = True

    # --- WRITING TO DISK ---
    
    # Base Root
    topic_sanitized = sanitize_folder_name(topic)
    base_library_root = os.path.join("./ScholarStack", topic_sanitized)
    
    rows_to_drop = []
    
    # Add new columns if they don't exist
    if 'Category' not in df.columns: df['Category'] = None
    if 'Directory_Path' not in df.columns: df['Directory_Path'] = None

    for index, row in df.iterrows():
        pid = row['DOI'] if pd.notna(row['DOI']) and str(row['DOI']).strip() else row['Title']
        
        # Get AI Category (or misc)
        full_category_path = taxonomy_map.get(pid, "Miscellaneous") if ai_success else "Miscellaneous"
        
        if full_category_path == "DISCARD":
            rows_to_drop.append(index)
            continue
            
        # Parse Parent/Child
        if "/" in full_category_path:
            parts = full_category_path.split("/")
            parent = sanitize_folder_name(parts[0])
            child = sanitize_folder_name(parts[1])
            final_rel_path = os.path.join(parent, child)
        else:
            final_rel_path = sanitize_folder_name(full_category_path)

        # Handle Vertical (Keyword) Folder
        current_root = base_library_root
        if use_keywords:
            raw_vertical = row.get('Search_Vertical', 'Unsorted')
            safe_vertical = sanitize_folder_name(str(raw_vertical))
            if safe_vertical.lower() != topic_sanitized.lower():
                current_root = os.path.join(base_library_root, safe_vertical)
            else:
                current_root = os.path.join(base_library_root, "_General")

        dir_path = os.path.join(current_root, final_rel_path)
        os.makedirs(dir_path, exist_ok=True)
        
        df.at[index, 'Category'] = full_category_path
        df.at[index, 'Directory_Path'] = dir_path

    # Cleanup
    if rows_to_drop:
        df = df.drop(rows_to_drop)
        print(f"Discarded {len(rows_to_drop)} papers.")

    if len(df) > limit:
         df = df.head(limit)

    # Ensure Topic column exists for downstream phases
    if 'Topic' not in df.columns:
        df['Topic'] = topic

    output_csv = "research_catalog_categorized.csv"
    df.to_csv(output_csv, index=False)
    print(f"\n=== Organization Complete in '{base_library_root}/' ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--sort", default="Most Relevant")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--no_llm", action="store_true")
    parser.add_argument("--use_keywords", action="store_true")
    parser.add_argument("--fast_mode", action="store_true")
    args = parser.parse_args()
    
    cluster_and_categorize(args.topic, args.sort, args.limit, args.no_llm, args.use_keywords, args.fast_mode)