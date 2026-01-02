
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Removed failing import 
# The file is 2_cluster_taxonomy.py which has invalid chars for import.
# I will use importlib to import it.

import importlib.util
spec = importlib.util.spec_from_file_location("cluster_taxonomy", "src/2_cluster_taxonomy.py")
cluster_taxonomy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cluster_taxonomy)

class TestClustering(unittest.TestCase):
    def test_cluster_subfolder_batching(self):
        """Test that cluster_subfolder handles large inputs by batching or at least doesn't crash."""
        
        # Mock model
        mock_model = MagicMock()
        
        # Create a large payload (e.g., 60 items)
        payload = [{"id": f"paper_{i}", "title": f"Title {i}", "description": "desc"} for i in range(60)]
        
        # Mock response to return valid JSON for a subset
        # If the code batches (size 50), it should call generate_content twice.
        # We'll set up the side_effect to return valid JSONs.
        
        response1_text = json.dumps({
            "assignments": [{"id": f"paper_{i}", "category_name": "Cat A", "justification_quote": "..."} for i in range(50)]
        })
        response2_text = json.dumps({
            "assignments": [{"id": f"paper_{i}", "category_name": "Cat B", "justification_quote": "..."} for i in range(50, 60)]
        })
        
        mock_response1 = MagicMock()
        mock_response1.text = response1_text
        
        mock_response2 = MagicMock()
        mock_response2.text = response2_text
        
        # Currently the code DOES NOT batch, so it will call it once with all 60.
        # If I change it to batch, it should make multiple calls.
        # For now, let's just assert that the current implementation calls it once with all papers
        # AND that if we pass a huge mock response that mimics truncation, it fails.
        
        mock_model.generate_content.side_effect = [mock_response1, mock_response2]
        
        # Run function
        assignments = cluster_taxonomy.cluster_subfolder(mock_model, payload, "Parent")
        
        # Assert called twice
        self.assertEqual(mock_model.generate_content.call_count, 2)
        
        # Assert full results
        self.assertEqual(len(assignments), 60)
        self.assertEqual(assignments["paper_0"], "Cat A")
        self.assertEqual(assignments["paper_55"], "Cat B")

    def test_clean_json_string(self):
        raw = "```json\n{\"a\": 1}\n```"
        clean = cluster_taxonomy.clean_json_string(raw)
        self.assertEqual(clean, "{\"a\": 1}")

if __name__ == '__main__':
    unittest.main()
