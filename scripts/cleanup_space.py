import os
import shutil
import tempfile
import glob

def clean_temp():
    # 1. System Temp
    try:
        temp_dir = tempfile.gettempdir()
        # Pattern: scholar_stack_mission_* and urp_mission_* (old name)
        patterns = [
            os.path.join(temp_dir, "scholar_stack_mission_*"),
            os.path.join(temp_dir, "urp_mission_*")
        ]
        
        folders = []
        for p in patterns:
            folders.extend(glob.glob(p))
            
        print(f"Scanning for orphaned missions in: {temp_dir}")
        total_deleted = 0
        
        for f in folders:
            if os.path.isdir(f):
                size = 0
                for dirpath, dirnames, filenames in os.walk(f):
                    for filename in filenames:
                        fp = os.path.join(dirpath, filename)
                        if not os.path.islink(fp):
                            size += os.path.getsize(fp)
                
                size_gb = size/(1024**3)
                print(f"Found Orphan: {os.path.basename(f)} - {size_gb:.2f} GB")
                
                # Delete it
                try:
                    shutil.rmtree(f)
                    print(f"  -> Deleted: {os.path.basename(f)}")
                    total_deleted += size_gb
                except Exception as e:
                    print(f"  -> Failed to delete: {e}")

        print(f"Reclaimed from Temp: {total_deleted:.2f} GB\n")
    except Exception as e:
        print(f"Error scanning temp: {e}")

    # 2. Static Folder
    try:
        project_static = os.path.abspath("static")
        print(f"Scanning static folder: {project_static}")
        
        static_deleted = 0
        if os.path.exists(project_static):
            for f in os.listdir(project_static):
                if f.endswith(".zip"):
                    fp = os.path.join(project_static, f)
                    if os.path.islink(fp):
                        os.unlink(fp)
                        print(f"Removed Symlink: {f}")
                    else:
                        size = os.path.getsize(fp)
                        os.remove(fp)
                        static_deleted += size/(1024**3)
                        print(f"Deleted Static Zip: {f} - {size/(1024**3):.2f} GB")
        
        print(f"Reclaimed from Static: {static_deleted:.2f} GB")
        
    except Exception as e:
        print(f"Error scanning static: {e}")

if __name__ == "__main__":
    clean_temp()
