
### Validation test

> "Excellent. Now, let's perform a full **End-to-End Validation Run** to prove the new 'Persistent Library' architecture works.
> **Please execute this exact sequence in the terminal:**
> 1. **Phase 2 (Search):**
> `./.venv/bin/python3 1_search_omni.py --query "Spatial Audio" --year_start 2023 --count 5`
> 2. **Phase 3 (Cluster):**
> `./.venv/bin/python3 2_cluster_taxonomy.py --topic "Spatial_Audio"`
> 3. **Phase 4 (Download & Export):**
> `./.venv/bin/python3 3_download_library.py`
> 
> 
> **After the scripts finish, run these verification commands and show me the output:**
> 1. `ls -R Library/` -> *(I want to verify that categories are strictly inside `Library/Spatial_Audio/` and NO ghost folders exist at the root).*
> 2. `ls -lh Library_Spatial_Audio.zip` -> *(To prove the focused zip was created).*
> 3. `head -n 20 Library/Spatial_Audio/Catalog_Spatial_Audio.md` -> *(To verify the YYYY/MM/DD date format).*
> 
> 
> If this run succeeds, we are ready to merge."

