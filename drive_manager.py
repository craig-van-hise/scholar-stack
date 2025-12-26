from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from tqdm import tqdm

class DriveManager:
    def __init__(self, credentials=None):
        """
        Initializes the Drive Manager with user credentials.
        :param credentials: A valid google.oauth2.credentials.Credentials object (from the user login).
        """
        self.creds = credentials
        self.service = None
        
        if self.creds:
            self.service = build('drive', 'v3', credentials=self.creds)
    
    def get_or_create_folder(self, folder_name):
        """Finds a folder by name or creates it if it doesn't exist."""
        if not self.service:
            raise ValueError("Drive Service not initialized. User not logged in.")

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            # Create folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            return file.get('id')
        else:
            return items[0]['id']

    def upload_library(self, local_library_path):
        """Recursively uploads PDF files from the local library path to Drive."""
        if not self.service:
             raise ValueError("Drive Service not initialized. User not logged in.")
            
        root_folder_id = self.get_or_create_folder('_Research_Assistant_Imports')
        print(f"Target Drive Folder ID: {root_folder_id}")
        
        uploaded_count = 0
        
        # Walk through the local directory
        for root, dirs, files in os.walk(local_library_path):
            for filename in files:
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(root, filename)
                    
                    file_metadata = {
                        'name': filename,
                        'parents': [root_folder_id]
                    }
                    media = MediaFileUpload(file_path, mimetype='application/pdf')
                    
                    try:
                        self.service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id'
                        ).execute()
                        uploaded_count += 1
                    except Exception as e:
                        print(f"Failed to upload {filename}: {e}")
                        
        return uploaded_count
