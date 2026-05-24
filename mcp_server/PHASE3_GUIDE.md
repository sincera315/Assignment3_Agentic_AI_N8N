# Phase 3: MCP Server Implementation - Complete Guide

## 📋 Overview

Your team has already created the **n8n workflows (Phase 2)** and the **MCP server structure**. This guide will help you complete Phase 3: testing, deployment, and integration of the MCP server.

---

## ✅ What Your Team Has Already Done

### Phase 2 Completed:
- ✅ **4 n8n workflows created:**
  - OpenSky Data Fetcher - Region 1
  - OpenSky Data Fetcher - Region 2
  - OpenSky Data Fetcher - Region 3
  - Snapshot Webhook Endpoints

- ✅ **MCP Server files created:**
  - `mcp_server/main.py` - FastAPI application with endpoints
  - `mcp_server/models.py` - Pydantic data models
  - `mcp_server/tools.py` - MCP tools implementation
  - `mcp_server/utils.py` - Utility functions
  - `mcp_server/__init__.py` - Package initialization

---

## 🎯 Phase 3 Goals

1. **Test MCP Server** with real data from n8n workflows
2. **Verify all 3 MCP tools** work correctly
3. **Document API endpoints** for Phase 4 (Agentic Layer)
4. **Create integration tests**
5. **Prepare for Phase 4 handoff**

---

## 📁 Files to Send Your Team

### Required Files (Already Created):
✅ All files in `mcp_server/` folder
✅ `requirements.txt`
✅ `docker-compose.yml`
✅ `.env.example`

### New Files to Create and Send:

1. **`test_mcp_server.py`** ⭐ - Test script for MCP server
2. **`run_mcp_server.py`** ⭐ - Launcher script
3. **`PHASE3_GUIDE.md`** ⭐ - This guide
4. **`MCP_API_REFERENCE.md`** ⭐ - API documentation
5. **Updated `README.md`** - Include Phase 3 instructions

---

## 🚀 Step-by-Step Implementation

### Step 1: Ensure n8n Workflows Are Running

**Before starting MCP server, verify n8n is collecting data:**

```powershell
# Check if n8n is running
docker ps | Select-String "n8n"

# Check if data files exist
Test-Path "data\flight_snapshots\region1_latest.json"
Test-Path "data\flight_snapshots\region2_latest.json"
Test-Path "data\flight_snapshots\region3_latest.json"
Test-Path "data\alerts\active_alerts.json"

# View a snapshot
Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json | Select-Object region, flight_count, anomaly_count
```

**Expected Results:**
- ✅ n8n container is running
- ✅ All 3 region snapshot files exist
- ✅ Files are being updated every 15 seconds
- ✅ Alerts file exists (if anomalies detected)

**If files don't exist:**
1. Open n8n: http://localhost:5678
2. Activate all 3 "OpenSky Data Fetcher" workflows
3. Activate "Snapshot Webhook Endpoints" workflow
4. Wait 30 seconds for first data collection

---

### Step 2: Configure Environment Variables

**Create `.env` file in project root:**

```env
# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000

# Data Directories (relative to project root)
SNAPSHOTS_DIR=./data/flight_snapshots
ALERTS_DIR=./data/alerts
LOGS_DIR=./data/logs

# Groq API (for Phase 4 - Agentic Layer)
GROQ_API_KEY=your_groq_api_key_here

# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678
```

**Your team should:**
- Copy `.env.example` to `.env`
- Keep default values for now
- Update `GROQ_API_KEY` when starting Phase 4

---

### Step 3: Install Python Dependencies

**Ensure all dependencies are installed:**

```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Install/update dependencies
pip install -r requirements.txt

# Verify installations
pip list | Select-String "fastapi|uvicorn|pydantic|python-dotenv"
```

**Expected packages:**
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0

---

### Step 4: Start MCP Server

**Option A: Using the launcher script (Recommended)**

```powershell
python run_mcp_server.py
```

**Option B: Direct uvicorn command**

```powershell
python -m uvicorn mcp_server.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify server is running:**

```powershell
# Test root endpoint
curl http://localhost:8000

# Expected response:
# {"name":"Airspace Copilot MCP Server","version":"1.0.0","status":"operational"}
```

---

### Step 5: Test MCP Tools

**Run the test script:**

```powershell
python test_mcp_server.py
```

**This will test:**
1. ✅ Server is reachable
2. ✅ Tool 1: `flights.list_region_snapshot` (Region 1, 2, 3)
3. ✅ Tool 2: `flights.get_by_callsign` (with real callsign from data)
4. ✅ Tool 3: `alerts.list_active` (anomaly alerts)
5. ✅ Error handling (invalid region, missing callsign)
6. ✅ Response format validation

**Expected Test Results:**
```
=== MCP Server Test Suite ===

✅ PASS - Server is reachable
✅ PASS - Tool: list_region_snapshot (Region 1) - 623 flights
✅ PASS - Tool: list_region_snapshot (Region 2) - 145 flights
✅ PASS - Tool: list_region_snapshot (Region 3) - 89 flights
✅ PASS - Tool: get_by_callsign - Found flight SWR123
✅ PASS - Tool: list_active_alerts - 0 alerts
✅ PASS - Error handling - Invalid region rejected
✅ PASS - Error handling - Missing callsign handled

Results: 8/8 tests passed
```

---

### Step 6: Manual API Testing

**Test each tool individually using curl or browser:**

#### Tool 1: List Region Snapshot

```powershell
# Get Region 1 flights
curl http://localhost:8000/tools/flights/region/region1

# Get Region 2 flights
curl http://localhost:8000/tools/flights/region/region2

# Get Region 3 flights
curl http://localhost:8000/tools/flights/region/region3
```

**Expected Response:**
```json
{
  "timestamp": 1764249304,
  "region": "region1",
  "flight_count": 623,
  "flights": [
    {
      "icao24": "4b1815",
      "callsign": "SWR123",
      "velocity": 234.5,
      "baro_altitude": 10668,
      ...
    }
  ],
  "anomaly_count": 0
}
```

#### Tool 2: Get Flight by Callsign

```powershell
# First, find a callsign from region snapshot
$snapshot = Invoke-RestMethod http://localhost:8000/tools/flights/region/region1
$callsign = $snapshot.flights[0].callsign
Write-Host "Testing with callsign: $callsign"

# Query that specific flight
curl "http://localhost:8000/tools/flights/callsign?callsign=$callsign"
```

**Expected Response:**
```json
{
  "callsign": "SWR123",
  "icao24": "4b1815",
  "region": "region1",
  "velocity": 234.5,
  "baro_altitude": 10668,
  "latitude": 47.5,
  "longitude": 8.5,
  ...
}
```

#### Tool 3: List Active Alerts

```powershell
curl http://localhost:8000/tools/alerts/active
```

**Expected Response (if no anomalies):**
```json
{
  "alert_count": 0,
  "alerts": [],
  "last_updated": "2025-11-27T13:15:04.983Z"
}
```

**Expected Response (with anomalies):**
```json
{
  "alert_count": 2,
  "alerts": [
    {
      "type": "low_speed_at_altitude",
      "severity": "high",
      "callsign": "LH456",
      "message": "Low speed at altitude for LH456: 45 m/s at 9500m"
    }
  ],
  "last_updated": "2025-11-27T13:15:04.983Z"
}
```

---

### Step 7: Verify Data Flow

**Test the complete pipeline:**

```powershell
# 1. Check n8n is collecting data
Get-Content "data\flight_snapshots\region1_latest.json" | ConvertFrom-Json | Select-Object datetime, flight_count

# 2. Query same data via MCP server
curl http://localhost:8000/tools/flights/region/region1 | ConvertFrom-Json | Select-Object datetime, flight_count

# 3. Compare - should match!
```

**They should show the same data!**

---

### Step 8: Test Error Handling

**Test various error scenarios:**

```powershell
# Invalid region
curl http://localhost:8000/tools/flights/region/invalid_region
# Expected: 404 Not Found

# Missing callsign
curl "http://localhost:8000/tools/flights/callsign?callsign=NONEXISTENT"
# Expected: 404 Not Found with helpful message

# Missing data file (simulate by temporarily renaming file)
Rename-Item "data\flight_snapshots\region1_latest.json" "data\flight_snapshots\region1_latest.json.bak"
curl http://localhost:8000/tools/flights/region/region1
# Expected: 500 Internal Server Error with message
Rename-Item "data\flight_snapshots\region1_latest.json.bak" "data\flight_snapshots\region1_latest.json"
```

---

## 📊 Understanding the MCP Tools

### Tool 1: `flights.list_region_snapshot`

**Purpose:** Get all flights in a region

**Input:** 
- `region_name`: "region1", "region2", or "region3"

**Output:**
- Complete snapshot with all flights
- Metadata (timestamp, region name, bounding box)
- Anomaly count and list

**Use Case (Phase 4):**
- Ops Analyst Agent: "Show me all flights in Region 1"
- Traveler Agent: "Are there any flights near Frankfurt?"

---

### Tool 2: `flights.get_by_callsign`

**Purpose:** Find a specific flight by callsign

**Input:**
- `callsign`: Flight identifier (e.g., "SWR123")

**Output:**
- Single flight object with full details
- Region where flight was found
- Null if not found

**Use Case (Phase 4):**
- Traveler Agent: "Where is flight SWR123?"
- User query: "What's the status of LH456?"

---

### Tool 3: `alerts.list_active`

**Purpose:** Get all current anomaly alerts

**Input:** None

**Output:**
- List of anomalies detected by n8n workflows
- Severity levels (low, medium, high)
- Affected flights and details

**Use Case (Phase 4):**
- Ops Analyst Agent: "Show me all current alerts"
- User query: "Are there any issues in the airspace?"

---

## 🔧 Troubleshooting

### Problem: MCP Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
pip install -r requirements.txt
```

---

### Problem: "Data file not found"

**Error:** `FileNotFoundError: Data file not found: ./data/flight_snapshots/region1_latest.json`

**Solution:**
1. Verify n8n workflows are active
2. Check data directory exists:
   ```powershell
   Test-Path "data\flight_snapshots"
   ```
3. Wait 30 seconds for n8n to collect data
4. Check n8n execution logs

---

### Problem: "Empty flight data"

**Symptom:** `flight_count: 0` in all snapshots

**Possible Causes:**
1. **OpenSky API rate limit** - Check n8n logs
2. **Invalid bounding box** - Check workflow configuration
3. **Network issue** - Test API manually

**Solution:**
```powershell
# Test OpenSky API directly
curl "https://opensky-network.org/api/states/all?lamin=45.0&lomin=5.0&lamax=55.0&lomax=15.0"

# If this works, check n8n workflow configuration
```

---

### Problem: Port 8000 Already in Use

**Error:** `OSError: [WinError 10048] Only one usage of each socket address`

**Solution:**
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
$pid = (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Stop the process
Stop-Process -Id $pid -Force

# Or use a different port
python run_mcp_server.py --port 8001
```

---

## 📝 Phase 3 Checklist

Before moving to Phase 4, ensure:

### Data Layer
- [ ] n8n workflows are active and collecting data
- [ ] All 3 region snapshots exist and update every 15 seconds
- [ ] Alert file exists (even if empty)
- [ ] Log files show successful executions

### MCP Server
- [y] Server starts without errors
- [y] Root endpoint responds with API info
- [N] All 3 tools return valid data
- [ ] Error handling works correctly
- [y] Test script passes all tests

### Documentation
- [ ] API endpoints documented
- [ ] Example requests and responses provided
- [ ] Error codes explained
- [ ] Data models documented

### Testing
- [ ] Manual tests completed for all tools
- [ ] Automated test script passes
- [ ] Error scenarios tested
- [ ] Performance acceptable (< 100ms response time)

---

## 🎯 Phase 4 Preparation

**What Phase 4 (Agentic Layer) needs from you:**

1. **MCP Server URL:** `http://localhost:8000`
2. **Tool Endpoints:**
   - `POST /tools/flights/region/{region_name}`
   - `GET /tools/flights/callsign?callsign={callsign}`
   - `GET /tools/alerts/active`

3. **Data Models:** Share `mcp_server/models.py`
4. **API Reference:** Share `MCP_API_REFERENCE.md`

**The agentic layer (Phase 4) will:**
- Use these tools to answer user queries
- Combine data from multiple tools
- Provide natural language responses
- Handle edge cases and errors

---

## 📦 Files to Send Your Team

**Send these files:**

1. ✅ `mcp_server/` folder (all Python files)
2. ✅ `test_mcp_server.py`
3. ✅ `run_mcp_server.py`
4. ✅ `PHASE3_GUIDE.md` (this file)
5. ✅ `MCP_API_REFERENCE.md`
6. ✅ `requirements.txt`
7. ✅ `.env.example`
8. ✅ Updated `README.md`

**Tell your team:**
- "Phase 2 (n8n) is complete ✅"
- "Phase 3 (MCP Server) is ready for testing"
- "Follow PHASE3_GUIDE.md to test and verify"
- "Once all tests pass, we can start Phase 4 (Agentic Layer)"

---

## 🚀 Quick Start Commands

```powershell
# 1. Ensure n8n is running
docker ps

# 2. Activate Python environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start MCP server
python run_mcp_server.py

# 5. Run tests (in new terminal)
python test_mcp_server.py

# 6. View API documentation
# Open browser: http://localhost:8000/docs
```

---

## 📚 Next Steps

**After Phase 3 is complete:**

1. ✅ MCP server is running and tested
2. ➡️ **Phase 4:** Build Agentic Layer (CrewAI)
   - Create Ops Analyst Agent
   - Create Traveler Support Agent
   - Implement A2A communication
   - Connect agents to MCP tools

3. ➡️ **Phase 5:** Build Frontend UI (Streamlit)
   - Traveler Mode interface
   - Operations Mode dashboard
   - Chat interface

---

**✅ Phase 3 Complete When:**
- All MCP tools work correctly
- Test script passes all tests
- API documentation is ready
- Team can query flight data via HTTP

**🎉 You're ready for Phase 4 when you can successfully query flights, find specific callsigns, and view alerts through the MCP server!**
