"""
Utility script to fix malformed JSON snapshot files
Converts multiple concatenated JSON objects into a single latest snapshot
"""
import json
import os
from pathlib import Path

SNAPSHOTS_DIR = Path("./data/flight_snapshots")

def fix_json_file(file_path: Path):
    """Fix a malformed JSON file by extracting the latest snapshot"""
    print(f"Fixing {file_path}...")
    
    if not file_path.exists():
        print(f"  File does not exist, skipping")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        print(f"  File is empty, skipping")
        return
    
    # Try to parse as single JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            print(f"  File is already valid JSON object")
            return
        elif isinstance(data, list):
            # Extract latest
            latest = data[-1] if data else {}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(latest, f, indent=2)
            print(f"  Converted array to single object (kept latest)")
            return
    except json.JSONDecodeError:
        pass
    
    # Parse multiple concatenated objects
    lines = content.split('\n')
    parsed_objects = []
    current_obj = ""
    brace_count = 0
    
    for line in lines:
        current_obj += line + "\n"
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and current_obj.strip():
            try:
                obj = json.loads(current_obj.strip())
                parsed_objects.append(obj)
                current_obj = ""
            except json.JSONDecodeError:
                current_obj = ""
                continue
    
    if parsed_objects:
        # Keep only the latest snapshot
        latest = parsed_objects[-1]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(latest, f, indent=2)
        print(f"  Fixed: Extracted latest snapshot from {len(parsed_objects)} objects")
    else:
        print(f"  ERROR: Could not parse any valid JSON objects")

def main():
    """Fix all snapshot files"""
    print("Fixing JSON snapshot files...")
    
    for region in ["region1", "region2", "region3"]:
        file_path = SNAPSHOTS_DIR / f"{region}_latest.json"
        fix_json_file(file_path)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
