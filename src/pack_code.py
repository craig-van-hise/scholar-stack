import os

# --- CONFIGURATION ---
# Files to ignore (add any specific files you want to skip)
IGNORE_FILES = {'.env', 'secrets.toml', 'package-lock.json', '.DS_Store', 'client_secrets.json'}

# Folders to ignore (crucial to skip virtual environments and git)
IGNORE_DIRS = {'venv', 'env', '.git', '__pycache__', '.idea', 'node_modules', 'bin', 'lib', 'include'}

# The name of the output file
OUTPUT_FILE = "ai_context_bundle.txt"

def is_text_file(filename):
    """Checks if a file is a text file based on extension."""
    return filename.endswith(('.py', '.txt', '.md', '.toml', '.json'))

def pack_project():
    root_dir = os.getcwd()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"--- PROJECT CONTEXT FOR AI ---\n\n")
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Modify dirnames in-place to skip ignored directories
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            for filename in filenames:
                if filename in IGNORE_FILES or filename == "pack_code.py" or filename == OUTPUT_FILE:
                    continue
                
                if not is_text_file(filename):
                    continue

                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)

                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        
                        # simple heuristic: only include files that might be relevant
                        # (Remove this if block if you want ALL code regardless of size)
                        if "streamlit" not in content and filename != "requirements.txt":
                            # logic: if it doesn't mention streamlit, and isn't requirements, 
                            # we might want to skip it to save tokens, BUT 
                            # often helper files don't import streamlit directly but return data for it.
                            # So I will default to INCLUDING everything for safety.
                            pass 

                        outfile.write(f"\n{'='*50}\n")
                        outfile.write(f"FILE: {rel_path}\n")
                        outfile.write(f"{'='*50}\n")
                        outfile.write(content + "\n")
                        print(f"Packed: {rel_path}")
                        
                except Exception as e:
                    print(f"Skipping {rel_path} (could not read): {e}")

    print(f"\nDone! All code saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    pack_project()