

> **Context:**
>  I want to add a feature to save research papers directly to the user's Google Drive so they can be easily imported into NotebookLM later.
> **Task:**
> Create a new "Save to Drive" feature in the UI and implement the necessary backend logic using the Google Drive API.
> **1. UI Requirements:**
> * **Button Location:** Place a new button immediately to the right of the existing "Download Full Library (ZIP)" button.
> * **Button Style:** Use a secondary style (outline or distinct color) to differentiate it from the direct download. Use a "Google Drive" icon or a "Cloud Upload" icon.
> * **Label:** The button text should read "Save to Drive".
> * **Feedback:** When clicked, show a "Saving..." loading state on the button. On success, show a toast notification: "Saved to 'Research Assistant' folder in Drive."
> 
> 
> **2. Authentication & Scopes (Critical):**
> * Update the existing Firebase Google Auth provider configuration.
> * We need to request an additional scope: `https://www.googleapis.com/auth/drive.file`.
> * *Note:* This scope is "non-sensitive" relative to full Drive access because it only allows the app to access/edit files created *by the app itself*, which is perfect for this use case.
> 
> 
> **3. Logic Flow:**
> * **Check Auth:** When the button is clicked, check if the current user has granted the Drive scope. If not, trigger a re-authentication flow to ask for permission.
> * **Folder Management:** Check if a folder named `_Research_Assistant_Imports` exists in the root of their Drive. If not, create it.
> * **Upload Process:**
> * Take the list of papers (PDFs) that are currently staged for the ZIP download.
> * Loop through them and upload each PDF to the `_Research_Assistant_Imports` folder.
> * Ensure the MIME type is set to `application/pdf` so NotebookLM recognizes them correctly.
> 
> 
> **4. Implementation Details:**
> * Use the Google Drive API v3.
> * Reuse the existing data fetching logic used for the ZIP creator; do not fetch the papers a second time if they are already in memory.
> 
> 

