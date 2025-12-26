import pandas as pd
import requests
import os
import re
import json
import shutil
from urllib.parse import urlparse, unquote
from tqdm import tqdm
import time
import random

def sanitize_filename(name):
    """Sanitizes filenames to be OS-safe."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_filename_from_cd(cd):
    """Get filename from content-disposition header."""
    if not cd:
        return None
    fname = re.findall(r'filename=["\']?([^"\';]+)["\']?', cd)
    if len(fname) == 0:
        return None
    return fname[0].strip()

def create_markdown_catalog(df, topic, output_path):
    """Generates a human-readable Markdown catalog."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Library Catalog: {topic}\n\n")
        f.write(f"**Total Papers:** {len(df)}\n")
        f.write(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        for category, group in df.groupby('Category'):
            f.write(f"## {category}\n\n")
            
            for _, row in group.iterrows():
                title = row.get('Title', 'Unknown Title')
                authors = row.get('Authors', 'Unknown Authors')
                date = str(row.get('Publication_Date', 'Unknown Date'))
                status = "Downloaded" if row.get('Is_Downloaded') else "Missing/Paywalled"
                filename = row.get('Original_Filename', 'N/A')
                url = row.get('Source_URL', '#')
                desc = str(row.get('Description', ''))
                
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                desc = desc.replace('\n', ' ')

                f.write(f"*   **{title}** ({date})\n")
                f.write(f"    *   *Authors:* {authors}\n")
                f.write(f"    *   *Status:* {status}\n")
                if row.get('Is_Downloaded'):
                    f.write(f"    *   *Filename:* `{filename}`\n")
                f.write(f"    *   *Source:* [Link]({url})\n")
                f.write(f"    *   *Abstract:* {desc}\n\n")

def sanitize_folder_name(name):
    clean = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in name])
    return clean.strip().replace(' ', '_')

def download_file(url, local_path):
    """Robust download with retries and header validation."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
    ]
    
    for attempt in range(3):
        try:
            headers = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            
            # Check content type if available (but trust bytes more)
            # ct = response.headers.get('content-type', '').lower()
            
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Validate PDF Magic Bytes (first 1024 bytes scan)
            with open(local_path, 'rb') as f:
                head = f.read(1024)
                if b'%PDF' in head:
                    return True # Success
            
            # If not PDF, delete
            os.remove(local_path)
            return False # Corrupt or HTML login page
            
        except Exception:
            time.sleep(1)
            
    return False

def download_library():
    print("=== Phase 4: The Physical Librarian (V9: Robust) ===")
    
    csv_path = "research_catalog_categorized.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    if 'Is_Downloaded' not in df.columns:
        df['Is_Downloaded'] = False
        
    if 'Directory_Path' not in df.columns:
        print("Error: 'Directory_Path' column missing.")
        return

    if 'Topic' not in df.columns or df['Topic'].isnull().all():
        print("Error: 'Topic' column missing.")
        return
        
    current_topic = df['Topic'].iloc[0]
    print(f"Processing Topic: {current_topic}")
    
    success_count = 0
    fail_count = 0
    
    print(f"Found {len(df)} papers. Starting download process...")

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Downloading"):
        url = row.get('Source_URL')
        if pd.isna(url) or not str(url).startswith('http'):
            continue
            
        dest_folder = row.get('Directory_Path')
        if not dest_folder: continue
            
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)
            
        title = row.get('Title', 'Unknown_Paper')
        
        # Determine Filename
        filename = "document.pdf"
        try:
            # Try to get cleaner name from URL first
            parsed_url = urlparse(url)
            base = os.path.basename(unquote(parsed_url.path))
            if base and base.lower().endswith('.pdf'):
                filename = base
            
            filename = sanitize_filename(filename)
            name_part, ext = os.path.splitext(filename)
            
            # Ensure it ends in .pdf
            if not ext: 
                filename += ".pdf"
            
            # Prevent generic overwrites or bad names
            if len(name_part) < 4 or name_part.lower() in ['document', 'file', 'download', 'view']:
                safe_title = sanitize_filename(title)[:40].replace(' ', '_')
                filename = f"{safe_title}.pdf"
        except:
            filename = "document.pdf"

        local_path = os.path.join(dest_folder, filename)
        
        # Execute Download
        if download_file(url, local_path):
            df.at[index, 'Is_Downloaded'] = True
            df.at[index, 'Original_Filename'] = filename
            df.at[index, 'Is_Paywalled'] = False
            success_count += 1
        else:
            fail_count += 1

    print("\nStarting Clean Up and Export...")
    
    unique_paths = df['Directory_Path'].dropna().unique()
    
    # 1. Create JSON Indexes
    for folder_path in unique_paths:
        if not os.path.exists(folder_path): continue
        papers_in_folder = df[df['Directory_Path'] == folder_path]
        index_data = []
        for _, paper in papers_in_folder.iterrows():
            if paper.get('Is_Downloaded', False):
                index_data.append({
                    "Title": paper['Title'],
                    "Authors": paper.get('Authors', 'Unknown'),
                    "Filename": paper.get('Original_Filename'),
                    "Description": paper.get('Description'),
                    "Source_URL": paper.get('Source_URL')
                })
        
        if index_data:
            with open(os.path.join(folder_path, "index.json"), "w") as f:
                json.dump(index_data, f, indent=2)

    # 2. Cleanup Empty Folders
    print("Cleaning up target folders...")
    for folder_path in unique_paths:
        if not os.path.exists(folder_path): continue
        try:
            files = os.listdir(folder_path)
            has_pdf = any(f.lower().endswith('.pdf') for f in files)
            if not has_pdf:
                shutil.rmtree(folder_path)
        except Exception: pass

    topic_sanitized = sanitize_folder_name(current_topic)
    topic_root = os.path.join("./Library", topic_sanitized)
    zip_name = f"Library_{topic_sanitized}"
    
    # 3. Catalog (BEFORE Zip)
    print("Generating Library Catalog...")
    df = df.sort_values(by='Category')
    if os.path.exists(topic_root):
        catalog_path = os.path.join(topic_root, f"Catalog_{topic_sanitized}.md")
        create_markdown_catalog(df, current_topic, catalog_path)

    # 4. Zip
    if os.path.exists(topic_root):
        shutil.make_archive(zip_name, 'zip', topic_root)
        print(f"READY FOR DOWNLOAD: {zip_name}.zip")
    
    df.to_csv("final_library_catalog.csv", index=False)
    
    print("\n=== Process Complete ===")
    print(f"Successfully downloaded: {success_count} / {len(df)}")

if __name__ == "__main__":
    download_library()
