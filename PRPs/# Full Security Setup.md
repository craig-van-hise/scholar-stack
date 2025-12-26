
### The "Full Security" Setup (`.env`)

 I need to set up the `.env` file correctly for both the search tools and the AI agents.
 1. **Create `.gitignore`:** Ensure `.env` is listed here so I never accidentally publish my keys.
 2. **Create `.env`:** Create this file in the root with the following variables:
 ```bash
 # The Brain (Required for Phase 3)
 GOOGLE_API_KEY=your_google_api_key_here
 
 ``` 

 ```
 # The Search Tools (Required for Phase 2)
 UNPAYWALL_EMAIL=your_email@gmail.com
 
 ```
 
 

 ```
 # Optional Keys (Leave empty if not using yet)
 SEMANTIC_SCHOLAR_KEY=
 CORE_API_KEY=
 ```
 
 ```
 
 
 3. **Update the Script:** Update `1_search_omni.py` to load these variables using `dotenv`. It should use `UNPAYWALL_EMAIL` for the 'Unlocker' step.
 4. **Instructions:** Tell me exactly where to paste my Google API Key once the file is created.
 
 


