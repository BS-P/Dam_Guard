"""
Script to update PROJECT_RESULTS_MAP in frontend/src/hooks/useStore.ts
with real organic river-conforming GeoJSON contours for all project datasets.
"""

import json
import re

def main():
    use_store_path = "frontend/src/hooks/useStore.ts"
    
    with open("all_scenarios_geojson.json", "r") as f:
        all_geojson = json.load(f)

    with open(use_store_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We will update flowPathGeoJSON for each project in useStore.ts
    for proj_id, geojson in all_geojson.items():
        geojson_str = json.dumps(geojson, indent=6)
        
        # Regex replacement pattern for project flowPathGeoJSON
        pattern = re.compile(
            rf'("{proj_id}":\s*\{{.*?"flowPathGeoJSON":\s*)\{{.*?\}}',
            re.DOTALL
        )
        
        if pattern.search(content):
            content = pattern.sub(rf'\1{geojson_str}', content, count=1)
            print(f"Updated {proj_id} flowPathGeoJSON")
        else:
            print(f"Warning: pattern for {proj_id} not matched directly")

    with open(use_store_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Updated useStore.ts successfully!")

if __name__ == "__main__":
    main()
