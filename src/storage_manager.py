import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class StorageManager:
    """Manages local storage of research missions with automatic cleanup."""
    
    def __init__(self, base_dir: str = "./ScholarStack", max_missions: int = 2):
        self.base_dir = Path(base_dir)
        self.max_missions = max_missions
        self.metadata_file = Path("data/missions.json")
        self.metadata_file.parent.mkdir(exist_ok=True)
        
    def _load_metadata(self) -> Dict:
        """Load mission metadata from JSON file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"missions": []}
    
    def _save_metadata(self, data: Dict):
        """Save mission metadata to JSON file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_folder_size(self, folder_path: Path) -> float:
        """Calculate folder size in MB."""
        total_size = 0
        try:
            for item in folder_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size / (1024 * 1024)  # Convert to MB
    
    def register_mission(self, topic: str, paper_count: int, exported_to_drive: bool = False):
        """Register a new mission in metadata."""
        metadata = self._load_metadata()
        
        # Create mission ID from topic and timestamp
        topic_sanitized = topic.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mission_id = f"{topic_sanitized}_{timestamp}"
        
        folder_path = self.base_dir / topic_sanitized
        
        mission = {
            "id": mission_id,
            "topic": topic,
            "created": datetime.now().isoformat(),
            "paper_count": paper_count,
            "size_mb": self._get_folder_size(folder_path) if folder_path.exists() else 0,
            "exported_to_drive": exported_to_drive,
            "folder_path": str(folder_path)
        }
        
        metadata["missions"].append(mission)
        self._save_metadata(metadata)
        
        # Auto-cleanup after registering
        self.cleanup_excess_missions()
        
        return mission_id
    
    def cleanup_excess_missions(self):
        """Remove oldest missions, keeping only max_missions most recent."""
        metadata = self._load_metadata()
        missions = metadata["missions"]
        
        if len(missions) <= self.max_missions:
            return 0  # Nothing to clean
        
        # Sort by creation date (newest first)
        missions.sort(key=lambda x: x["created"], reverse=True)
        
        # Keep only the most recent missions
        missions_to_keep = missions[:self.max_missions]
        missions_to_delete = missions[self.max_missions:]
        
        # Delete old mission folders
        deleted_count = 0
        for mission in missions_to_delete:
            folder_path = Path(mission["folder_path"])
            if folder_path.exists():
                try:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                    print(f"🗑️ Deleted old mission: {mission['topic']} ({mission['created'][:10]})")
                except Exception as e:
                    print(f"⚠️ Failed to delete {folder_path}: {e}")
        
        # Update metadata
        metadata["missions"] = missions_to_keep
        self._save_metadata(metadata)
        
        return deleted_count
    
    def clear_all_missions(self):
        """Delete all missions (for manual cleanup)."""
        metadata = self._load_metadata()
        deleted_count = 0
        
        for mission in metadata["missions"]:
            folder_path = Path(mission["folder_path"])
            if folder_path.exists():
                try:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to delete {folder_path}: {e}")
        
        # Clear metadata
        metadata["missions"] = []
        self._save_metadata(metadata)
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict:
        """Get current storage statistics."""
        metadata = self._load_metadata()
        missions = metadata["missions"]
        
        total_size_mb = 0
        oldest_date = None
        
        for mission in missions:
            total_size_mb += mission.get("size_mb", 0)
            created = datetime.fromisoformat(mission["created"])
            if oldest_date is None or created < oldest_date:
                oldest_date = created
        
        return {
            "mission_count": len(missions),
            "total_size_mb": round(total_size_mb, 2),
            "total_size_gb": round(total_size_mb / 1024, 2),
            "oldest_mission_date": oldest_date.strftime('%Y-%m-%d') if oldest_date else "N/A",
            "missions": missions
        }
    
    def update_mission_export_status(self, topic: str, exported: bool = True):
        """Mark a mission as exported to Google Drive."""
        metadata = self._load_metadata()
        topic_sanitized = topic.replace(' ', '_').replace('/', '_')
        
        for mission in metadata["missions"]:
            if topic_sanitized in mission["id"]:
                mission["exported_to_drive"] = exported
                break
        
        self._save_metadata(metadata)

    def open_mission_folder(self, folder_path: str):
        """Opens the mission folder in the OS file explorer."""
        import subprocess
        import sys
        
        path = str(folder_path) # Ensure string
        if not os.path.exists(path): return False
        
        try:
            if sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            elif sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', path])
            return True
        except Exception as e:
            print(f"Error opening folder: {e}")
            return False
