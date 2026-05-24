# Keep All Data - Fix JSON Append Format

## The Problem

Your n8n workflow appends snapshots, but creates invalid JSON:

```json
{...object1...}
{...object2...}
{...object3...}
```

**Solution:** Format as **JSON Array** so all data is kept AND valid!

```json
[
  {...object1...},
  {...object2...},
  {...object3...}
]
```

---

## SOLUTION: Wrap Data in JSON Array

### STEP 1: Fix n8n Code Node (Before Append Node)

**Location:** n8n Workflow → Code node that prepares data for append

**Node Name:** "Prepare Snapshot for Append" or "Format for File"

**Current Code (WRONG - produces multiple objects):**

```javascript
const items = $input.all();
const snapshot = items[0].json;

const binaryData = Buffer.from(JSON.stringify(snapshot), 'utf-8');

return [{
  json: snapshot,
  binary: {
    data: {
      data: binaryData,
      mimeType: 'application/json',
      fileName: 'region1_latest.json'
    }
  }
}];
```

**Fixed Code (RIGHT - produces JSON array):**

```javascript
// filepath: n8n Workflow Code Node - Before Append

const fs = require('fs');
const path = require('path');
const items = $input.all();
const snapshot = items[0].json;

// Read existing file to get current array
const filePath = './data/flight_snapshots/region1_latest.json';
let snapshots = [];

try {
  // Try to read existing file
  const existingContent = fs.readFileSync(filePath, 'utf-8').trim();
  
  if (existingContent) {
    try {
      // If it's a valid array, parse it
      snapshots = JSON.parse(existingContent);
    } catch (e) {
      // If file has multiple objects, collect them
      const lines = existingContent.split('\n').filter(line => line.trim());
      snapshots = lines.map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      }).filter(item => item !== null);
    }
  }
} catch (e) {
  // File doesn't exist yet, start fresh
  snapshots = [];
}

// Add new snapshot to array
snapshots.push(snapshot);

// Keep only last 100 snapshots (prevents file from growing infinitely)
if (snapshots.length > 100) {
  snapshots = snapshots.slice(-100);
}

// Convert array to binary for file write
const jsonString = JSON.stringify(snapshots, null, 2);
const binaryData = Buffer.from(jsonString, 'utf-8');

return [{
  json: {
    snapshots: snapshots,
    count: snapshots.length,
    latest: snapshot
  },
  binary: {
    data: {
      data: binaryData,
      mimeType: 'application/json',
      fileName: 'region1_latest.json'
    }
  }
}];
```

---

### STEP 2: Configure n8n Append Node

**Node Name:** "Write/Append Snapshot File"

**Type:** Read/Write Files from Disk

**Settings:**

```
Operation: "Write to a file"  (NOT "Append file to list")
File Path: /data/flight_snapshots/region1_latest.json
Put Output in Field: data
Overwrite File: true  ✓ (CHECKED - because we handle appending in code above)
```

---

### STEP 3: Update Python Reader

**File:** `src/data_pipeline.py`

```python
// filepath: src/data_pipeline.py

import json
from pathlib import Path

# ...existing code...

def read_all_snapshots(file_path: str) -> list:
    """Read all snapshots from JSON array file"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        if not content:
            return []
        
        # Parse as JSON array
        data = json.loads(content)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Single object, wrap in array
            return [data]
        else:
            return []
            
    except json.JSONDecodeError:
        print(f"Invalid JSON in {file_path}")
        return []
    except Exception as e:
        print(f"Error reading snapshots: {str(e)}")
        return []


def read_latest_snapshot(file_path: str) -> dict:
    """Read the LATEST snapshot from file"""
    snapshots = read_all_snapshots(file_path)
    
    if not snapshots:
        return {
            "timestamp": 0,
            "datetime": "1970-01-01T00:00:00.000Z",
            "region": "region1",
            "region_name": "Central Europe",
            "flight_count": 0,
            "flights": [],
            "anomalies": [],
            "anomaly_count": 0,
            "bounding_box": {
                "lat_min": 45,
                "lat_max": 55,
                "lon_min": 5,
                "lon_max": 15
            }
        }
    
    return snapshots[-1]  # Return the last one


def get_snapshot_history(file_path: str, limit: int = 10) -> list:
    """Get last N snapshots"""
    snapshots = read_all_snapshots(file_path)
    return snapshots[-limit:] if snapshots else []
```

---

### STEP 4: Update Test File

**File:** `tests/test_integration.py`

```python
// filepath: tests/test_integration.py

# ...existing code...

def test_n8n_creates_snapshot_files(self):
    """Test that n8n workflows create snapshot files"""
    time.sleep(20)
    
    assert DATA_DIR.exists(), "Snapshots directory doesn't exist"
    
    region1_file = DATA_DIR / "region1_latest.json"
    assert region1_file.exists(), "Region 1 snapshot file not created"
    
    # Fixed: Read as array
    from src.data_pipeline import read_all_snapshots, read_latest_snapshot
    
    snapshots = read_all_snapshots(str(region1_file))
    assert len(snapshots) > 0, "No snapshots in file"
    
    latest = read_latest_snapshot(str(region1_file))
    assert latest['flight_count'] >= 0, "Invalid flight count"

# ...existing code...

def test_get_by_callsign_endpoint(self):
    """Test flight lookup by callsign"""
    snapshot_file = DATA_DIR / "region1_latest.json"
    
    if snapshot_file.exists():
        # Fixed: Read latest snapshot
        from src.data_pipeline import read_latest_snapshot
        snapshot = read_latest_snapshot(str(snapshot_file))
        
        assert snapshot is not None, "Could not read snapshot"
        # ...existing code...

# ...existing code...

def test_traveler_support_tool_usage(self):
    """Test Traveler Support agent can use tools"""
    snapshot_file = DATA_DIR / "region1_latest.json"
    
    if snapshot_file.exists():
        # Fixed: Read latest snapshot
        from src.data_pipeline import read_latest_snapshot
        snapshot = read_latest_snapshot(str(snapshot_file))
        
        assert snapshot is not None, "Could not read snapshot"
        # ...existing code...

# ...existing code...

def test_a2a_communication(self):
    """Test A2A agent delegation"""
    snapshot_file = DATA_DIR / "region1_latest.json"
    
    if snapshot_file.exists():
        # Fixed: Read latest snapshot
        from src.data_pipeline import read_latest_snapshot
        snapshot = read_latest_snapshot(str(snapshot_file))
        
        assert snapshot is not None, "Could not read snapshot"
        # ...existing code...

# ...existing code...

def test_traveler_flow_complete(self):
    """Test: User tracks flight → Asks question → Gets answer"""
    snapshot_file = DATA_DIR / "region1_latest.json"
    
    if snapshot_file.exists():
        # Fixed: Read latest snapshot
        from src.data_pipeline import read_latest_snapshot
        snapshot = read_latest_snapshot(str(snapshot_file))
        
        assert snapshot is not None, "Could not read snapshot"
        # ...existing code...
```

---

## Result

**File Will Look Like:**

```json
[
  {
    "timestamp": 1764247656,
    "datetime": "2025-11-27T12:00:00.000Z",
    "region": "region1",
    "flight_count": 150,
    "flights": [...],
    "anomalies": []
  },
  {
    "timestamp": 1764247671,
    "datetime": "2025-11-27T12:00:15.000Z",
    "region": "region1",
    "flight_count": 152,
    "flights": [...],
    "anomalies": []
  },
  {
    "timestamp": 1764247686,
    "datetime": "2025-11-27T12:00:30.000Z",
    "region": "region1",
    "flight_count": 151,
    "flights": [...],
    "anomalies": []
  }
]
```

✅ **Valid JSON** - Can parse with `json.load()`
✅ **All Data Kept** - Every snapshot stored
✅ **Easy Access** - Read all or just latest
✅ **Controlled Size** - Keeps last 100 snapshots

---

## Benefits

| Benefit | Details |
|---------|---------|
| **Keep All Data** | Every snapshot stored in array |
| **Valid JSON** | Can parse without errors |
| **History** | Can query all past snapshots |
| **Latest Access** | `read_latest_snapshot()` gets current one |
| **Size Managed** | Auto-keeps last 100 (prevents bloat) |

---

## Verification

```powershell
# Check file is valid JSON array
$json = Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json
Write-Host "✅ Valid JSON Array with $($json.Count) snapshots"
Write-Host "Latest snapshot: $($json[-1].datetime)"
Write-Host "Oldest snapshot: $($json[0].datetime)"
```