# Testing n8n Workflow - Complete Guide

## 🧪 How to Test Each Node

### Test 1: Basic Workflow Execution (No Anomalies Expected)

**Purpose:** Verify all nodes execute without errors and files are created.

#### Step 1: Execute the Workflow

1. In n8n, click **"Execute Workflow"** button (top right)
2. Watch nodes turn green as they execute
3. Red nodes = errors, click to see details

#### Step 2: Verify File Creation

```powershell
# Check if snapshot file exists
Test-Path "data\flight_snapshots\region1_latest.json"

# Check if log file exists
Test-Path "data\logs\fetch_history.log"

# View snapshot file (should show flights)
Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json | Select-Object flight_count, anomaly_count, timestamp

# View log file (last 5 entries)
Get-Content "data\logs\fetch_history.log" -Tail 5
```

**Expected Results:**
- ✅ Snapshot file exists and contains flight data
- ✅ Log file exists with entries like: `[2025-11-27T...] SUCCESS | Region: region1 | Flights: 623 | Anomalies: 0`
- ✅ No alerts file (if no anomalies detected)

---

### Test 2: Verify Node 10 & 11 (Log Entry)

**Purpose:** Test that log formatting and file append work correctly.

#### Method 1: Check Log File Contents

```powershell
# View log file
Get-Content "data\logs\fetch_history.log"

# Expected format:
# [2025-11-27T13:15:04.983Z] SUCCESS | Region: region1 | Flights: 623 | Anomalies: 0
# [2025-11-27T13:15:19.234Z] SUCCESS | Region: region1 | Flights: 625 | Anomalies: 0
```

#### Method 2: Activate Workflow and Monitor

```powershell
# Activate the workflow (runs every 15 seconds)
# Wait 1 minute, then check log file

Start-Sleep -Seconds 60

# Count log entries (should have ~4 entries if workflow ran 4 times)
(Get-Content "data\logs\fetch_history.log").Count

# Show last 10 entries
Get-Content "data\logs\fetch_history.log" -Tail 10
```

**Expected Results:**
- ✅ Log file has multiple entries (one per execution)
- ✅ Each entry shows timestamp, status, flight count, anomaly count
- ✅ File grows with each execution (append works)

#### Method 3: Check Node Execution Output in n8n

1. Click on **Node 10** (Format Log Entry)
2. View output - should see:
   ```json
   {
     "log_entry": "[2025-11-27T...] SUCCESS | Region: region1 | Flights: 623 | Anomalies: 0",
     "binary": {
       "data": { /* binary data */ }
     }
   }
   ```

3. Click on **Node 11** (Write Log File)
4. Should see success (no errors)

---

### Test 3: Simulate Anomalies (Force Anomaly Detection)

**Purpose:** Test Node 5, 8, 8b, 8c to verify anomaly detection and alerts work.

#### Method 1: Lower Anomaly Thresholds

**Update Node 5 code to detect more anomalies:**

```javascript
// Change these rules to be MORE sensitive:

{
  name: "low_speed_at_altitude",
  check: (flight) => {
    // Changed from 50 to 200 (more flights will trigger)
    return flight.velocity < 200 && flight.baro_altitude > 8000 && !flight.on_ground;
  },
  severity: "high",
  message: (flight) => `Low speed at altitude for ${flight.callsign || 'Unknown'}: ${flight.velocity} m/s at ${flight.baro_altitude}m`
},
{
  name: "rapid_descent",
  check: (flight) => {
    // Changed from -15 to -5 (more descents will trigger)
    return flight.vertical_rate < -5 && flight.baro_altitude > 1000;
  },
  severity: "high",
  message: (flight) => `Rapid descent detected for ${flight.callsign || 'Unknown'}: ${flight.vertical_rate} m/s from ${flight.baro_altitude}m`
},
{
  name: "stationary_aircraft",
  check: (flight) => {
    // Changed from 10 to 50 (more slow flights will trigger)
    return flight.velocity < 50 && flight.baro_altitude > 100 && !flight.on_ground;
  },
  severity: "low",
  message: (flight) => `Stationary aircraft detected: ${flight.callsign || 'Unknown'} at ${flight.baro_altitude}m`
}
```

**Then execute workflow and check:**

```powershell
# Check for alerts file
Test-Path "data\alerts\active_alerts.json"

# View alerts
Get-Content "data\alerts\active_alerts.json" | ConvertFrom-Json | Format-List

# Check snapshot has anomalies
$snapshot = Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json
$snapshot.anomaly_count
$snapshot.anomalies | Format-Table
```

**Expected Results:**
- ✅ `anomaly_count` > 0
- ✅ `alerts/active_alerts.json` file exists
- ✅ Alerts contain anomaly details (callsign, type, severity, message)

---

### Test 4: Test API Failure & Cache Loading (Node 9)

**Purpose:** Verify Node 9 (Load Cached Data) works when API fails.

#### Method 1: Simulate API Failure

1. In Node 2 (HTTP Request), temporarily change URL to invalid:
   ```
   https://opensky-network.org/api/INVALID
   ```

2. Execute workflow

3. Check that:
   - Node 3 (IF) takes FALSE path
   - Node 9 (Read File) loads cached data
   - Node 9b (Parse Cached Data) parses it successfully
   - Log shows "CACHED" status instead of "SUCCESS"

```powershell
# Check log for CACHED entry
Get-Content "data\logs\fetch_history.log" -Tail 1

# Expected: [2025-11-27T...] CACHED | Region: region1 | Flights: 623 | Anomalies: 0
```

4. **Restore the correct URL** after testing!

---

## 📊 Complete Testing Checklist

### Basic Functionality
- [ ] Workflow executes without errors
- [ ] Node 1 (Schedule) triggers every 15 seconds when active
- [ ] Node 2 (HTTP Request) fetches OpenSky data
- [ ] Node 3 (IF) correctly checks for `states` field
- [ ] Node 4 (Transform) processes flight data
- [ ] Node 5 (Detect Anomalies) runs without "fs" error

### File Operations
- [ ] Node 6 (Prepare Snapshot) creates binary output
- [ ] Node 6b (Write Snapshot) creates `region1_latest.json`
- [ ] Snapshot file contains valid JSON
- [ ] Snapshot has `flight_count`, `flights`, `anomalies` fields

### Anomaly Detection (with lowered thresholds)
- [ ] Node 5 detects anomalies when thresholds lowered
- [ ] `anomaly_count` > 0 in snapshot
- [ ] Node 7 (IF Has Anomalies) takes TRUE path
- [ ] Node 8 (Save Alerts) prepares alerts data
- [ ] Node 8b (Prepare Alerts) creates binary output
- [ ] Node 8c (Write Alerts) creates `active_alerts.json`
- [ ] Alerts file contains anomaly details

### Log Operations
- [ ] Node 10 (Format Log) creates log entry
- [ ] Node 10 creates binary output for log
- [ ] Node 11 (Write Log) appends to `fetch_history.log`
- [ ] Log file grows with each execution
- [ ] Log entries have correct format
- [ ] Log shows SUCCESS when API works
- [ ] Log shows CACHED when API fails (after testing Node 9)

### Cache & Fallback
- [ ] Node 9 (Read File) loads cache when API fails
- [ ] Node 9b (Parse) correctly parses cached JSON
- [ ] Workflow continues with cached data
- [ ] Log shows CACHED status

---

## 🔬 Advanced Testing: Inspect Each Node Output

### In n8n UI:

1. **Execute workflow**
2. Click on each node to see output
3. Verify data structure at each step:

#### Node 4 Output (Transform Flight Data):
```json
{
  "timestamp": 1764249304,
  "datetime": "2025-11-27T13:15:04.983Z",
  "region": "region1",
  "flight_count": 623,
  "flights": [
    {
      "icao24": "4b1815",
      "callsign": "SWR123",
      "velocity": 234.5,
      "baro_altitude": 10668,
      // ... more fields
    }
  ],
  "bounding_box": { /* ... */ },
  "metadata": { /* ... */ }
}
```

#### Node 5 Output (Detect Anomalies):
```json
{
  // ... same as Node 4, plus:
  "anomalies": [
    {
      "type": "low_speed_at_altitude",
      "severity": "high",
      "callsign": "LH456",
      "message": "Low speed at altitude..."
    }
  ],
  "anomaly_count": 1
}
```

#### Node 6 Output (Prepare Snapshot):
```json
{
  "json": { /* snapshot data */ },
  "binary": {
    "data": {
      "data": "<Buffer ...>",
      "mimeType": "application/json",
      "fileName": "region1_latest.json"
    }
  }
}
```

#### Node 10 Output (Format Log):
```json
{
  "json": {
    // ... snapshot data
    "log_entry": "[2025-11-27T...] SUCCESS | Region: region1 | Flights: 623 | Anomalies: 0"
  },
  "binary": {
    "data": {
      "data": "<Buffer ...>",
      "mimeType": "text/plain",
      "fileName": "fetch_history.log"
    }
  }
}
```

---

## 🐛 Troubleshooting

### Log File Not Growing

**Problem:** Log file stays at 1 entry

**Check:**
1. Is Node 11 configured correctly?
   - Operation: `Append file to list`
   - Put Output in Field: `data`
   - File Path: `/data/logs/fetch_history.log`

2. Does Node 10 output binary data?
   - Click Node 10, check for `binary.data` in output

3. Is "Overwrite File" disabled for Node 11?
   - Should be OFF (unchecked) for logs
   - Should be ON (checked) for snapshot/alerts

```powershell
# Manually check file permissions
Test-Path "data\logs"
New-Item -ItemType Directory -Path "data\logs" -Force
```

### No Anomalies Detected

**Solution:** Lower thresholds in Node 5 (see Test 3 above)

**Or check real-time for anomalies:**

```powershell
# Check current flights for slow ones
$snapshot = Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json
$snapshot.flights | Where-Object { $_.velocity -lt 100 } | Format-Table callsign, velocity, baro_altitude

# Check for rapid descents
$snapshot.flights | Where-Object { $_.vertical_rate -lt -5 } | Format-Table callsign, vertical_rate, baro_altitude
```

### Binary Field Error

**Problem:** "This operation expects binary file"

**Solution:** Make sure Code nodes output binary structure:

```javascript
return [{
  json: data,
  binary: {
    data: {              // Key must be 'data'
      data: binaryData,  // Buffer object
      mimeType: 'application/json',
      fileName: 'file.json'
    }
  }
}];
```

---

## ✅ Success Criteria

Your workflow is working correctly when:

1. ✅ Workflow executes every 15 seconds without errors
2. ✅ `region1_latest.json` updates every 15 seconds
3. ✅ `fetch_history.log` grows with each execution
4. ✅ When anomalies detected: `active_alerts.json` is created/updated
5. ✅ When API fails: workflow uses cached data and logs "CACHED"
6. ✅ All files contain valid data (not empty or corrupted)

---

## 📝 Quick Test Commands

```powershell
# 1. Check all files exist
Test-Path "data\flight_snapshots\region1_latest.json"
Test-Path "data\logs\fetch_history.log"

# 2. View current snapshot summary
$s = Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json
"Flights: $($s.flight_count), Anomalies: $($s.anomaly_count), Time: $($s.datetime)"

# 3. View log tail
Get-Content "data\logs\fetch_history.log" -Tail 5

# 4. Count log entries
(Get-Content "data\logs\fetch_history.log").Count

# 5. Check for alerts
if (Test-Path "data\alerts\active_alerts.json") {
    $a = Get-Content "data\alerts\active_alerts.json" | ConvertFrom-Json
    "Alert count: $($a.alert_count)"
    $a.alerts | Format-Table type, severity, callsign
} else {
    "No alerts file - no anomalies detected yet"
}

# 6. Watch log file grow (run workflow, wait, run again)
$before = (Get-Content "data\logs\fetch_history.log").Count
Write-Host "Entries before: $before"
Start-Sleep -Seconds 20
$after = (Get-Content "data\logs\fetch_history.log").Count
Write-Host "Entries after: $after"
Write-Host "New entries: $($after - $before)"
```

---

**🎯 Start with Test 1 & 2, then move to Test 3 to verify anomaly detection!**
