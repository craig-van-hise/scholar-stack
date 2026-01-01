# Project Status Report

**Date:** 2025-12-30
**Status:** Operational / Polished
**Current Phase:** Final Verification & Documentation

## Executive Summary
**ScholarStack** is now a robust, user-aligned research agent with a strictly organized codebase. We have refined the **Taxonomy Logic** (Per-Keyword), overhauled the **Search History UI**, and formally refactored the project structure into modular directories (`src`, `data`, `scripts`, `tests`). Recent additions include a **Fast Mode** for rapid research and a **Storage Management System** to handle large datasets efficiently.

## Implemented Architecture

### 1. The Omni-Search Module (`src/1_search_omni.py`)
*   **Search Verticals:** Successfully creates 15+ sub-topic queries (e.g. "Spatial Audio" -> "HRTF", "Ambisonics").
*   **Parallel Processing:** Uses `ThreadPoolExecutor` for high-speed OpenAlex querying.
*   **Metadata Capture:** Captures `Citation_Count` and maps Search Verticals to results.

### 2. The Interface (`src/app.py`)
*   **Research Modes:** Toggle between "Fast Mode" (Direct Download, ~15m) and "Deep Mode" (Full AI Clustering, ~90m).
*   **Persistence:** Automatically saves state to `data/user_settings.json`.
*   **Search History V2:** Multi-row selection table with explicit "Load" and "Delete" actions. History stored in `data/search_history.json`.
*   **Structure:** Code explicitly separated from data.

### 3. Core Pipeline (`src/2_cluster_taxonomy.py`)
*   **Per-Keyword Taxonomy:** AI categorization runs *per Search Vertical* for higher relevance.
*   **Count Stability:** Buffer logic (`Limit * 2`) prevents "Musical Chairs" paper loss.
*   **Paths:** Scripts auto-detect input/output paths in `data/` if running manually.

## Recent Accomplishments
*   **Fast Mode:** Implemented a high-speed research option that bypasses AI clustering for quick results.
*   **Storage Management:** Added automated cleanup of old missions and large file handling (serving direct downloads from disk) to prevent server crashes.
*   **Project Refactor:** Cleaned root directory. Moved source code to `src/`, data to `data/`, tools to `scripts/`.
*   **UI Polish:** "Zombie Modal" fixed. Search History uses native multi-select and persistent resizing.

## Technical Notes
*   **Launch Command:** `source .venv/bin/activate && streamlit run src/app.py`
*   **Data Storage:** All generated files (Library, CSVs, Cache) now reside in `data/`.

