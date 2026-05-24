# n8n Workflow Setup - Complete Fix Guide

## 🚨 Critical Fixes for Common Issues

This guide addresses the issues you'll encounter when setting up the n8n workflows.

---

## Issue 1: "Unrecognized node type: n8n-nodes-base.writeFile"

**Problem:** The imported JSON workflows contain deprecated node types.

**Solution:** You **cannot import the JSON workflows directly**. You must create the workflow manually in n8n.

---

## Issue 2: Node 3 "Check API Success" Always Returns False

**Problem:** The original documentation checks for `{{ $json.statusCode }}` which doesn't exist in the OpenSky API response.

**Solution:** Use this configuration instead:

### ✅ Correct Node 3 Configuration:

```
Node Type: IF
Name: Check API Success

Conditions:
  Value 1: {{ $json.states }}
  Operation: Is Not Empty
```

**Why this works:** The OpenSky API returns `{ "time": ..., "states": [...] }` without a `statusCode` field in the JSON body. Checking if `states` exists is more reliable.

---

## Issue 3: Node 4 Data Structure Mismatch

**Problem:** n8n wraps the API response in an array, so data is at `items[0].json[0].states` instead of `items[0].json.states`.

**Solution:** Use this updated code for Node 4.

---

## 📋 Complete Manual Workflow Setup

### Step 1: Create New Workflow

1. Go to http://localhost:5678
2. Click **"Add Workflow"**
3. Name it: `OpenSky Data Fetcher - Region 1`

---

### Step 2: Add All Nodes

Create these nodes in order:

#### Node 1: Schedule Trigger
- **Type:** Schedule Trigger
- **Settings:**
  - Trigger Interval: `Seconds`
  - Seconds Between Triggers: `15`

#### Node 2: HTTP Request
- **Type:** HTTP Request
- **Settings:**
  - Method: `GET`
  - URL: `https://opensky-network.org/api/states/all?lamin=45.0&lomin=5.0&lamax=55.0&lomax=15.0`
  - **Options → Continue On Fail:** `true` ✓

#### Node 3: IF (Check API Success) ⭐ FIXED
- **Type:** IF
- **Settings:**
  - **Condition 1:**
    - Value 1: `{{ $json.states }}`
    - Operation: `Is Not Empty`

#### Node 4: Code (Transform Flight Data) ⭐ UPDATED
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 5: Code (Detect Anomalies)
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 6: Code (Prepare Snapshot File) ⭐ NEW
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 6b: Read/Write Files from Disk (Write Snapshot) ⭐ FIXED
- **Type:** Read/Write Files from Disk
- **Settings:**
  - **Operation:** `Append file to list`
  - **Put Output in Field:** `data`
  - **File Path:** `/data/flight_snapshots/region1_latest.json`
  - **Options → Overwrite File:** `true` ✓

**Note:** This node expects binary input from Node 6 code.

#### Node 7: IF (Has Anomalies?)
- **Type:** IF
- **Settings:**
  - **Condition 1:**
    - Value 1: `{{ $json.anomaly_count }}`
    - Operation: `Larger`
    - Value 2: `0`

#### Node 8: Code (Save Alerts)
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 9: Code (Load Cached Data)
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 10: Code (Format Log Entry)
- **Type:** Code
- **Language:** JavaScript
- **Code:** See below ⬇

#### Node 11: Read/Write Files from Disk (Append Log)
- **Type:** Read/Write Files from Disk
- **Settings:**
  - **Operation:** `Append file to list`
  - **Put Output in Field:** `data`
  - **File Path:** `/data/logs/fetch_history.log`

---

### Step 3: Connect Nodes

```
[Schedule Trigger] → [HTTP Request] → [IF: Check API Success]
                                              ↓
                                    true ↙          ↘ false
                          [Transform Flight Data]  [Read File: Load Cache]
                                    ↓                      ↓
                          [Detect Anomalies] ←─── [Parse Cached Data]
                                    ↓
                    [Code: Prepare Snapshot] → [Write File: Snapshot]
                                    ↓
                          [IF: Has Anomalies?]
                               ↓         ↓
                        true ↙             ↘ false
                [Code: Save Alerts]          ↓
                        ↓                    ↓
           [Code: Prepare Alerts]            ↓
                        ↓                    ↓
           [Write File: Alerts]              ↓
                        ↓────────────────────┘
                   [Code: Format Log Entry]
                                    ↓
                          [Write File: Log]
```

---

## 📝 Complete Code for All JavaScript Nodes

### Node 4: Transform Flight Data ⭐ UPDATED CODE

````javascript
const items = $input.all();

// Handle both array-wrapped and direct responses
let responseData;
if (Array.isArray(items[0].json)) {
  // Data is wrapped in array: [{ time: ..., states: [...] }]
  responseData = items[0].json[0];
} else {
  // Data is direct object: { time: ..., states: [...] }
  responseData = items[0].json;
}

// Validate we have states
if (!responseData || !responseData.states || responseData.states.length === 0) {
  return [{
    json: {
      error: 'No flight data received',
      timestamp: Math.floor(Date.now() / 1000),
      datetime: new Date().toISOString(),
      region: 'region1',
      region_name: 'Central Europe (Frankfurt, Munich, Vienna, Zurich)',
      flight_count: 0,
      flights: [],
      anomalies: [],
      anomaly_count: 0,
      bounding_box: {
        lat_min: 45.0,
        lat_max: 55.0,
        lon_min: 5.0,
        lon_max: 15.0
      }
    }
  }];
}

const states = responseData.states;

// Transform each flight state into structured format
const flights = states.map(state => ({
  icao24: state[0],
  callsign: state[1] ? state[1].trim() : null,
  origin_country: state[2],
  time_position: state[3],
  last_contact: state[4],
  longitude: state[5],
  latitude: state[6],
  baro_altitude: state[7],
  on_ground: state[8],
  velocity: state[9],
  true_track: state[10],
  vertical_rate: state[11],
  sensors: state[12],
  geo_altitude: state[13],
  squawk: state[14],
  spi: state[15],
  position_source: state[16]
}));

// Create snapshot with metadata
const snapshot = {
  timestamp: Math.floor(Date.now() / 1000),
  datetime: new Date().toISOString(),
  region: 'region1',
  region_name: 'Central Europe (Frankfurt, Munich, Vienna, Zurich)',
  flight_count: flights.length,
  flights: flights,
  bounding_box: {
    lat_min: 45.0,
    lat_max: 55.0,
    lon_min: 5.0,
    lon_max: 15.0
  },
  metadata: {
    api_status: 'success',
    api_timestamp: responseData.time,
    fetch_time: new Date().toISOString()
  }
};

return [{ json: snapshot }];
````

### Node 5: Detect Anomalies ⭐ FIXED (No fs Module)

````javascript
// Get the current snapshot from input
const items = $input.all();
const currentSnapshot = items[0].json;

// Initialize anomalies array
const anomalies = [];

// Define anomaly detection rules
const anomalyRules = [
  {
    name: "low_speed_at_altitude",
    check: (flight) => {
      return flight.velocity < 50 && flight.baro_altitude > 8000 && !flight.on_ground;
    },
    severity: "high",
    message: (flight) => `Low speed at altitude for ${flight.callsign || 'Unknown'}: ${flight.velocity} m/s at ${flight.baro_altitude}m`
  },
  {
    name: "rapid_descent",
    check: (flight) => {
      return flight.vertical_rate < -15 && flight.baro_altitude > 1000;
    },
    severity: "high",
    message: (flight) => `Rapid descent detected for ${flight.callsign || 'Unknown'}: ${flight.vertical_rate} m/s from ${flight.baro_altitude}m`
  },
  {
    name: "stationary_aircraft",
    check: (flight) => {
      return flight.velocity < 10 && flight.baro_altitude > 100 && !flight.on_ground;
    },
    severity: "low",
    message: (flight) => `Stationary aircraft detected: ${flight.callsign || 'Unknown'} at ${flight.baro_altitude}m`
  }
];

// Detect anomalies in current flights
if (currentSnapshot.flights && Array.isArray(currentSnapshot.flights)) {
  currentSnapshot.flights.forEach(flight => {
    anomalyRules.forEach(rule => {
      if (rule.check(flight)) {
        anomalies.push({
          type: rule.name,
          severity: rule.severity,
          callsign: flight.callsign || "Unknown",
          icao24: flight.icao24,
          latitude: flight.latitude,
          longitude: flight.longitude,
          altitude: flight.baro_altitude,
          velocity: flight.velocity,
          vertical_rate: flight.vertical_rate,
          message: rule.message(flight),
          detected_at: new Date().toISOString(),
          timestamp: currentSnapshot.timestamp,
          region: currentSnapshot.region || 'region1'
        });
      }
    });
  });
}

// Add anomalies to snapshot
currentSnapshot.anomalies = anomalies;
currentSnapshot.anomaly_count = anomalies.length;

return [{ json: currentSnapshot }];
````

### Node 6: Prepare Snapshot File ⭐ NEW

````javascript
const items = $input.all();
const snapshot = items[0].json;

// Convert JSON to binary data
const jsonString = JSON.stringify(snapshot, null, 2);
const binaryData = Buffer.from(jsonString, 'utf-8');

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
````

### Node 8: Save Alerts ⭐ SIMPLIFIED (No fs)

````javascript
const items = $input.all();
const snapshot = items[0].json;

// Prepare alerts data
const alertsData = {
  last_updated: new Date().toISOString(),x
  alerts: snapshot.anomalies || [],
  alert_count: snapshot.anomaly_count || 0,
  region: snapshot.region,
  snapshot_timestamp: snapshot.timestamp
};

// Return both snapshot (for next node) and alerts data (for file write)
return [
  { json: snapshot },           // Main path continues with snapshot
  { json: alertsData }          // Branch path for alerts file
];
````

**Note:** Add a second output from Node 8:
- Connect **Output 1** → Node 10 (Format Log Entry)
- Connect **Output 2** → New Node 8b (Read/Write Files from Disk for alerts)

### Node 9: Read/Write Files from Disk (Load Cached Data) ⭐ CHANGED TO FILE READ NODE

**Instead of Code node, use Read/Write Files from Disk:**

- **Type:** Read/Write Files from Disk
- **Settings:**
  - **Operation:** `Read a file`
  - **File Path:** `/data/flight_snapshots/region1_latest.json`
  - **Options → Continue On Fail:** `true` ✓

**Then add Node 9b: Code (Parse Cached Data)**

````javascript
const items = $input.all();

// Check if file read succeeded
if (items[0].json && items[0].json.data) {
  try {
    const snapshot = JSON.parse(items[0].json.data);
    
    // Mark as cached
    snapshot.metadata = snapshot.metadata || {};
    snapshot.metadata.from_cache = true;
    snapshot.metadata.cache_reason = 'API request failed or returned empty data';
    snapshot.metadata.attempted_at = new Date().toISOString();
    
    return [{ json: snapshot }];
  } catch (err) {
    console.log('Could not parse cached data:', err.message);
  }
}

// Return empty snapshot if no cache available
return [{
  json: {
    error: 'API failed and no cached data available',
    timestamp: Math.floor(Date.now() / 1000),
    datetime: new Date().toISOString(),
    region: 'region1',
    region_name: 'Central Europe (Frankfurt, Munich, Vienna, Zurich)',
    flight_count: 0,
    flights: [],
    anomalies: [],
    anomaly_count: 0,
    bounding_box: {
      lat_min: 45.0,
      lat_max: 55.0,
      lon_min: 5.0,
      lon_max: 15.0
    },
    metadata: {
      api_status: 'failed',
      from_cache: false
    }
  }
}];
````

### Node 10: Format Log Entry

````javascript
const items = $input.all();
const snapshot = items[0].json;

const status = snapshot.metadata?.from_cache ? 'CACHED' : 'SUCCESS';
const flightCount = snapshot.flight_count || 0;
const anomalyCount = snapshot.anomaly_count || 0;

const logEntry = `[${new Date().toISOString()}] ${status} | Region: ${snapshot.region} | Flights: ${flightCount} | Anomalies: ${anomalyCount}`;

// Convert log entry to binary for file append
const binaryData = Buffer.from(logEntry + '\n', 'utf-8');

return [{
  json: {
    ...snapshot,
    log_entry: logEntry
  },
  binary: {
    data: {
      data: binaryData,
      mimeType: 'text/plain',
      fileName: 'fetch_history.log'
    }
  }
}];
````

---

## 🤝 Agent-to-Agent (A2A) Communication Support

This workflow includes **A2A (Agent-to-Agent) communication** features, enabling multiple agents to interact, delegate, and collaborate within the automation system.

### What is A2A Communication?

A2A communication allows one agent (for example, the Airspace Operations Analyst) to:
- Request information or actions from another agent (such as the Traveler Support agent)
- Share data, alerts, or analysis results
- Trigger workflows or tasks in response to another agent's output

### How is A2A Implemented in This Workflow?

- **Shared Data Files:** Snapshots and alerts are written to shared files (e.g., `region1_latest.json`, `active_alerts.json`). Any agent can read these files to get the latest data or alerts.
- **Workflow Triggers:** Agents can trigger each other's workflows by updating shared files or by sending HTTP requests to endpoints exposed by the n8n server.
- **Delegation Logic:** Some workflow steps are designed to pass tasks or data from one agent to another, such as when an anomaly is detected and the Traveler Support agent is notified.
- **Integration Tests:** The test suite includes `test_a2a_communication`, which verifies that agents can successfully delegate and respond to each other's requests using the workflow.

### Example Scenarios

- **Anomaly Detected:** The Airspace Operations Analyst detects an anomaly and writes an alert. The Traveler Support agent reads the alert and contacts affected travelers.
- **Flight Lookup:** The Traveler Support agent receives a user query, requests the latest flight snapshot from the shared file, and provides a response.
- **Collaborative Decision:** Agents can update logs or status files that are monitored by other agents, enabling coordinated actions.

### How to Extend or Use A2A Features

- **Add More Agents:** You can add new agents by creating additional workflows that read/write to the same shared files or communicate via HTTP/Webhook nodes.
- **Monitor Shared Files:** Agents should monitor changes in shared files to react to new data or alerts.
- **Custom Triggers:** Use n8n's HTTP/Webhook nodes to allow agents to trigger each other directly if needed.

**If you are building or testing agent-based automation, this workflow is ready for A2A scenarios and can be extended for more complex agent collaboration.**

---

## 🧪 Testing the Workflow

### Step 1: Execute Manually
1. Click **"Execute Workflow"** button (top right)
2. Watch nodes turn green in sequence
3. Check for any red (error) nodes

### Step 2: Verify Output Files

```powershell
# Check snapshot file
Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json | Format-List

# Check log file
Get-Content "data\logs\fetch_history.log" -Tail 5

# Check alerts file (if anomalies detected)
Get-Content "data\alerts\active_alerts.json" | ConvertFrom-Json | Format-List
```

### Step 3: Activate Workflow
1. Toggle the **"Active"** switch (top right)
2. Workflow will now run every 15 seconds automatically
3. Check **"Executions"** tab to see history

---

## 🎯 Expected Results

After successful execution:

**Snapshot File (`region1_latest.json`):**
```json
{
  "timestamp": 1764247656,
  "datetime": "2025-11-27T12:00:00.000Z",
  "region": "region1",
  "region_name": "Central Europe (Frankfurt, Munich, Vienna, Zurich)",
  "flight_count": 150,
  "flights": [...],
  "anomalies": [...],
  "anomaly_count": 2,
  "bounding_box": {...},
  "metadata": {
    "api_status": "success",
    "api_timestamp": 1764247656,
    "fetch_time": "2025-11-27T12:00:00.000Z"
  }
}
```

**Log File (`fetch_history.log`):**
```
[2025-11-27T12:00:00.000Z] SUCCESS | Region: region1 | Flights: 150 | Anomalies: 2
[2025-11-27T12:00:15.000Z] SUCCESS | Region: region1 | Flights: 152 | Anomalies: 1
```

---

## 🚨 Troubleshooting

### Error: "This operation expects the node's input data to contain a binary file"
**Fix:** The "Read/Write Files from Disk" node requires binary input. Add a Code node BEFORE each file write node to convert JSON to binary using `Buffer.from()`. See Node 6, 8b, and 10 code examples.

### Error: "Cannot find module 'fs'"
**Fix:** The updated workflow no longer uses `fs` module. All file operations now use **"Read/Write Files from Disk"** nodes with binary conversion. Use the updated code provided above.

### Error: "ENOENT: no such file or directory"
**Fix:** Create directories manually:
```powershell
New-Item -ItemType Directory -Path "data\flight_snapshots" -Force
New-Item -ItemType Directory -Path "data\logs" -Force
New-Item -ItemType Directory -Path "data\alerts" -Force
```

### Node 3 still returns false
**Fix:** Double-check the IF condition:
- Value 1: `{{ $json.states }}`
- Operation: `Is Not Empty`
- NO second condition needed

### Node 4 errors with "Cannot read property..."
**Fix:** Add debug logging at the top of Node 4:
```javascript
console.log('Input data:', JSON.stringify($input.all()[0].json, null, 2));
```
Check n8n logs to see actual structure.

---

## ✅ Summary of All Fixes

| Issue | Original | Fixed |
|-------|----------|-------|
| Node Type | `n8n-nodes-base.writeFile` | Use "Read/Write Files from Disk" node manually |
| Node 3 Condition | `{{ $json.statusCode }}` | `{{ $json.states }}` Is Not Empty |
| Node 4 Code | `items[0].json.states` | Handle array wrapper: `items[0].json[0].states` |
| Node 5 fs Error | `const fs = require('fs')` | Removed fs, use rule-based detection only |
| Node 6 Binary Input | Direct JSON write | Add Code node to convert JSON to Buffer |
| Node 8/9 fs Error | File operations with `fs` | Use Code + Read/Write Files nodes |
| Node 10/11 Binary | Text append | Add binary conversion with Buffer.from() |

---

## 📤 What to Send Your Team Member

**Send them THIS file:** `N8N_COMPLETE_SETUP_GUIDE.md`

**Tell them:**
1. Open n8n at http://localhost:5678
2. Create a new workflow manually (don't import JSON)
3. Follow this guide step-by-step
4. Copy-paste the JavaScript code for each Code node
5. Test by executing the workflow
6. Activate when working

**Key Points to Emphasize:**
- ⚠️ **DO NOT import JSON workflows** - they contain deprecated nodes
- ✅ **Use "Read/Write Files from Disk" nodes** - NOT "Write Binary File"
- ✅ **Node 5 has NO fs module** - use simplified code provided
- ✅ **Node 3 checks for `states`** - NOT `statusCode`
- ✅ **Node 4 handles array wrapper** - updated code provided

This guide has all the working code ready to copy-paste! 🚀
