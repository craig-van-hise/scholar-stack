import json
import os
import shutil
from typing import List, Dict, Any

import google.generativeai as genai
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from rank_bm25 import BM25Okapi

# --- 1. Custom Google Gemini Embedding Function ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Wrapper for Google's 'text-embedding-004'. 
    """
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        # Batch embedding with 'retrieval_document' task type
        result = genai.embed_content(
            model=self.model_name,
            content=input,
            task_type="retrieval_document",
            title="Taxonomy Node" 
        )
        return result['embedding']

    def embed_query(self, input: str) -> List[float]:
        # Single query embedding with 'retrieval_query' task type
        result = genai.embed_content(
            model=self.model_name,
            content=input,
            task_type="retrieval_query"
        )
        return result['embedding']


# --- 2. Main Hybrid Search Logic with Caching ---
class HybridTreeSearch:
    def __init__(self, google_api_key: str, persist_dir: str = "./tree_chroma_db"):
        self.persist_dir = persist_dir
        self.gemini_ef = GeminiEmbeddingFunction(api_key=google_api_key)
        
        # Initialize Persistent Client
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        
        # We always initialize the collection reference
        self.collection_name = "taxonomy_tree"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.gemini_ef
        )
        
        # In-memory stores for Lexical Search (BM25) and fast retrievals
        self.bm25 = None
        self.doc_store = {} 

    def ingest_tree(self, tree_data: Dict[str, Any], force_rebuild: bool = False):
        """
        Flattens tree and builds indices. 
        CACHE LOGIC: Checks if DB is empty or force_rebuild is True.
        """
        
        # 1. Flatten the tree first (we need this for BM25 regardless of Chroma caching)
        print("Flattening tree structure...")
        flat_nodes = []
        self._flatten_tree(tree_data, [], flat_nodes)
        
        # Populate doc_store and prepare text for BM25
        tokenized_corpus = []
        for i, node in enumerate(flat_nodes):
            node_id = str(i)
            self.doc_store[node_id] = node
            
            # Create rich text representation for search
            text_content = f"{node['node_name']} {node['full_path']}"
            tokenized_corpus.append(text_content.lower().split())

        # 2. Build BM25 Index (Fast, always rebuilt in-memory)
        print(f"Building BM25 index for {len(flat_nodes)} nodes...")
        self.bm25 = BM25Okapi(tokenized_corpus)

        # 3. Check ChromaDB Cache
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_rebuild:
            print(f"✅ Found {existing_count} cached embeddings in ChromaDB. Skipping ingestion.")
            return

        # 4. Ingestion Logic (Only runs if empty or forced)
        if force_rebuild and existing_count > 0:
            print("Force rebuild requested. Clearing existing collection...")
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name, 
                embedding_function=self.gemini_ef
            )

        print(f"🚀 Generating embeddings for {len(flat_nodes)} nodes using Gemini (this may take a while)...")
        
        ids = []
        documents = []
        metadatas = []

        for i, node in enumerate(flat_nodes):
            node_id = str(i)
            # Text specifically for the Embedding Model
            # We include context to help distinguishing "Plasma" (Blood) vs "Plasma" (Physics)
            text_for_embedding = f"{node['node_name']} (Context: {node['full_path']})"
            
            ids.append(node_id)
            documents.append(text_for_embedding)
            metadatas.append({
                "path": node['full_path'], 
                "name": node['node_name'], 
                "value": str(node['value']) # Metadata must be string, int, float, or bool
            })

        # Batch Upsert to respect API limits
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
            print(f"   Processed {min(i+batch_size, len(ids))}/{len(ids)}...")

        print("Ingestion complete.")

    def _flatten_tree(self, node, ancestry, result_list):
        current_path = ancestry + [node['name']]
        full_path_str = " > ".join(current_path)
        
        entry = {
            'node_name': node['name'],
            'full_path': full_path_str,
            'value': node.get('value', 0),
            'id_ref': node.get('id', '')
        }
        result_list.append(entry)

        if 'children' in node:
            for child in node['children']:
                self._flatten_tree(child, current_path, result_list)

    def search(self, query: str, top_k: int = 5):
        """
        Hybrid Search: BM25 + Gemini Embeddings + Reciprocal Rank Fusion
        """
        # A. BM25 Search
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # Get top 30 BM25 IDs
        bm25_ranked = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)[:30]
        bm25_ids = [str(idx) for idx, score in bm25_ranked if score > 0]

        # B. Semantic Search (Chroma)
        results = self.collection.query(
            query_texts=[query], # Chroma calls our Gemini class internally
            n_results=30
        )
        semantic_ids = results['ids'][0]

        # C. Reciprocal Rank Fusion (RRF)
        rrf_score = {}
        k_const = 60

        for rank, doc_id in enumerate(bm25_ids):
            rrf_score[doc_id] = rrf_score.get(doc_id, 0) + (1 / (k_const + rank))

        for rank, doc_id in enumerate(semantic_ids):
            rrf_score[doc_id] = rrf_score.get(doc_id, 0) + (1 / (k_const + rank))

        # Sort and retrieve
        sorted_ids = sorted(rrf_score.keys(), key=lambda x: rrf_score[x], reverse=True)
        
        final_results = []
        for doc_id in sorted_ids[:top_k]:
            if doc_id in self.doc_store:
                final_results.append(self.doc_store[doc_id])
            
        return final_results

# --- Usage ---

if __name__ == "__main__":
    # 1. Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        exit()
    FILE_PATH = 'openalex_tree.json'
    
    # 2. Safety Check
    if not os.path.exists(FILE_PATH):
        print(f"Error: '{FILE_PATH}' not found.")
        exit()

    # 3. Load Data
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        tree_data = json.load(f)

    # 4. Initialize & Ingest (Cached)
    # Set force_rebuild=True only if you changed the JSON file content
    searcher = HybridTreeSearch(GOOGLE_API_KEY)
    searcher.ingest_tree(tree_data, force_rebuild=False)
    
    # 5. Search Loop
    print("\n--- Search System Ready (Type 'q' to exit) ---")
    while True:
        user_query = input("\nQuery: ")
        if user_query.lower() in ['q', 'quit']:
            break
        
        results = searcher.search(user_query)
        
        print(f"Top results for '{user_query}':")
        for i, res in enumerate(results):
            print(f"{i+1}. {res['node_name']}")
            print(f"   Context: {res['full_path']}")