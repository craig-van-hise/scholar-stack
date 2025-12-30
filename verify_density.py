
import pandas as pd

try:
    df = pd.read_csv("research_catalog_categorized.csv")
    if 'Search_Vertical' not in df.columns:
        print("Error: Search_Vertical column missing.")
    else:
        # Group
        groups = df.groupby(['Search_Vertical', 'Category']).size()
        
        print("\n--- Density Check ---")
        fail = False
        for (vertical, category), count in groups.items():
            print(f"[{vertical}] -> [{category}]: {count}")
            if category not in ["Miscellaneous", "DISCARD", "Unsorted"] and count < 2:
                print(f"❌ VIOLATION: {category} has {count} paper(s)!")
                fail = True
        
        if not fail:
            print("\n✅ All Folders satisfy density rule (>= 2).")
        else:
            print("\n❌ Minimum Density Rule Failed.")

except Exception as e:
    print(f"Error: {e}")
