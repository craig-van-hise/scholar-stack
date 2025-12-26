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
load_dotenv()

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
    print("Searching for available Gemini models...")
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
                available_models.append(m.name)
        
        if not available_models:
            return 'models/gemini-pro'

        available_models.sort()
        best_model = available_models[-1]
        print(f"Selected Model: {best_model}")
        return best_model
    except Exception as e:
        print(f"Error listing models: {e}. Defaulting to 'gemini-1.5-flash'.")
        return 'gemini-1.5-flash'

def cluster_and_categorize(topic):
    print("=== Phase 3: The Smart Architect (Improved Clustering) ===")
    print(f"Topic: {topic}")
    
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
    
    if len(df) > 100:
        print(f"Trimming {len(df)} papers to top 100 for AI processing...")
        df = df.head(100)
    
    print(f"Loaded {len(df)} valid papers from catalog.")

    if df.empty:
        print("No valid papers to categorize.")
        return

    # 2. AI Categorization Logic
    api_key = os.getenv("GOOGLE_API_KEY")
    taxonomy_map = {}
    ai_success = False

    if not api_key:
        print("⚠️ No Google API Key found. Skipping AI Categorization.")
        print(">> Falling back to single folder structure.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            papers_payload = []
            for index, row in df.iterrows():
                papers_payload.append({
                    "Title": row['Title'],
                    "Description": str(row['Description'])[:400]
                })

            num_papers = len(df)
            if num_papers < 10:
                cat_count_msg = "2-3 broad categories"
            elif num_papers < 30:
                cat_count_msg = "3-5 distinct categories"
            else:
                cat_count_msg = "5-8 distinct categories"

            model_name = get_best_model()
            print(f"Consulting {model_name} to generate taxonomy...")
            
            prompt = f"""
            You are an expert academic librarian organizing a library on the topic: "{topic}".
            Input: {num_papers} academic paper abstracts.
            Task:
            1. **Filter**: Review abstracts. If a paper is NOT primarily about "{topic}" or is generic junk, assign "DISCARD".
            2. **Cluster**: Group the remaining papers into {cat_count_msg}.
            
            Critical Constraints:
            1. **No Redundancy**: Do NOT use the words "{topic}" in the category names.
            2. **Consolidation**: Merge similar topics.
            3. **Cluster Size**: Every category MUST contain at least 2 papers.
            
            Output Format:
            Return strictly a JSON object. 
            Keys = Exact "Title". Values = Category Name.
            Papers:
            {json.dumps(papers_payload, indent=2)}
            """

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            cleaned_response = clean_json_string(response.text)
            taxonomy_map = json.loads(cleaned_response)
            ai_success = True
            print("Taxonomy generated successfully.")
            
        except Exception as e:
            print(f"❌ AI Processing Failed: {e}")
            print(">> Falling back to single folder structure.")
            ai_success = False

    # 3. Post-Processing / Fallback Assignment
    if ai_success:
        # Enforce Orphan Rules
        counts = Counter([cat for cat in taxonomy_map.values() if cat != "DISCARD"])
        orphans = [cat for cat, count in counts.items() if count < 2]
        if orphans:
            general_cat = "General_Research"
            for title, cat in taxonomy_map.items():
                if cat in orphans:
                    taxonomy_map[title] = general_cat
    else:
        # Fallback Mode: All papers go to "General_Collection"
        for title in df['Title']:
            taxonomy_map[title] = "General_Collection"

    # 4. Organization
    df['Topic'] = topic
    topic_sanitized = sanitize_folder_name(topic)
    library_topic_root = f"./Library/{topic_sanitized}"
    os.makedirs(library_topic_root, exist_ok=True)
    
    categories_found = set()
    rows_to_drop = []
    df['Directory_Path'] = None

    for index, row in df.iterrows():
        title = row['Title']
        category = taxonomy_map.get(title, "General_Collection") # Default if AI missed one
        
        if category == "DISCARD":
            rows_to_drop.append(index)
            continue
        
        df.at[index, 'Category'] = category
        categories_found.add(category)
        
        safe_category = sanitize_folder_name(category)
        dir_path = os.path.join(library_topic_root, safe_category)
        os.makedirs(dir_path, exist_ok=True)
        df.at[index, 'Directory_Path'] = dir_path

    if rows_to_drop:
        df = df.drop(rows_to_drop)
        print(f"Rejected {len(rows_to_drop)} off-topic papers.")

    output_csv = "research_catalog_categorized.csv"
    df.to_csv(output_csv, index=False)
    
    print("\n=== Categorization Complete ===")
    if ai_success:
        print(f"AI Organized into {len(categories_found)} Categories.")
    else:
        print("Fallback Mode: Papers saved to 'General_Collection'.")
        
    print(f"Structure ready in '{library_topic_root}/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Architect: Cluster and Filter Papers")
    parser.add_argument("--topic", required=True, help="The specific research topic (e.g., 'Spatial Audio')")
    args = parser.parse_args()
    
    cluster_and_categorize(args.topic)
