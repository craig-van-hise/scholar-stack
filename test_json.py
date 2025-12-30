
import importlib.util
import sys
import json

# Import module manually because it starts with a number
spec = importlib.util.spec_from_file_location("cluster_mod", "src/2_cluster_taxonomy.py")
cluster_mod = importlib.util.module_from_spec(spec)
sys.modules["cluster_mod"] = cluster_mod
spec.loader.exec_module(cluster_mod)

clean_json_string = cluster_mod.clean_json_string

test_str_markdown = """```json
{"id": "123"}
```"""

test_str_raw = """
{"id": "456"}
"""

assert json.loads(clean_json_string(test_str_markdown))['id'] == "123"
assert json.loads(clean_json_string(test_str_raw))['id'] == "456"

print("✅ clean_json_string tests passed.")
