# Real-Time Airspace Copilot

A comprehensive multi-agent system for real-time airspace monitoring, anomaly detection, and intelligent assistance using n8n orchestration, MCP protocol, CrewAI agents, and Streamlit UI.

## 🎯 Project Overview

This system monitors real-time airspace data from OpenSky Network, detects anomalies using rule-based detection, and provides intelligent assistance through specialized AI agents. The architecture demonstrates:

- **n8n** for workflow orchestration and data ingestion
- **MCP (Model Context Protocol)** for structured tool access
- **CrewAI** for multi-agent collaboration with Agent-to-Agent (A2A) communication
- **Groq LLM** (Llama3-70B) for natural language understanding
- **Streamlit** for dual-mode user interface (Traveler + Operations)

### Key Features

✅ Real-time flight tracking across 3 predefined regions  
✅ Rule-based anomaly detection (6 anomaly types)  
✅ Two specialized AI agents with A2A delegation  
✅ Dual-mode UI: Traveler support & Operations monitoring  
✅ Webhook-based data access for integration  
✅ Comprehensive logging and error handling  

---

## 📁 Project Structure

```
Assignment 3/
├── config/
│   ├── regions.json           # 3 monitored regions with bounding boxes
│   └── thresholds.json        # Anomaly detection rules & thresholds
├── n8n_workflows/
│   ├── opensky_data_fetcher_region1.json    # Main data fetcher workflow
│   └── snapshot_webhook_endpoints.json      # HTTP endpoints for data access
├── mcp_server/
│   ├── __init__.py
│   ├── main.py               # FastAPI MCP server
│   ├── models.py             # Pydantic data models
│   ├── tools.py              # 3 MCP tools implementation
│   └── utils.py              # Helper functions
├── anomaly_detection/
│   ├── __init__.py
│   ├── detector.py           # AnomalyDetector class
│   └── rules.py              # Rule definitions & config loader
├── agents/
│   ├── __init__.py
│   ├── agents.py             # 2 specialized agents (Ops + Traveler)
│   ├── tasks.py              # Task definitions
│   ├── tools.py              # CrewAI tool wrappers
│   └── crew_config.py        # Crew setup & execution
├── ui/
│   ├── __init__.py
│   ├── app.py                # Main Streamlit application
│   └── components/
│       ├── __init__.py
│       ├── traveler_mode.py  # Traveler interface
│       └── ops_mode.py       # Operations dashboard
├── data/
│   ├── flight_snapshots/     # JSON flight data (auto-generated)
│   └── alerts/               # Anomaly alerts (auto-generated)
├── docker-compose.yml        # n8n container setup
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
├── PROJECT_PLAN.md           # Master plan document
└── PHASE2_DETAILED_GUIDE.md  # n8n setup instructions
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Docker & Docker Compose** (for n8n)
- **Groq API Key** (free tier available at [groq.com](https://console.groq.com))
- Internet connection (for OpenSky Network API)

### Step 1: Clone & Setup Python Environment

```powershell
# Navigate to project directory
cd "d:\FAST\Semester 7\Agentic AI\Assignments\Assignment 3"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_key_here
```

**Required Environment Variables:**

```env
# API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# n8n Configuration
N8N_HOST=http://localhost:5678
N8N_WEBHOOK_BASE=http://localhost:5678/webhook

# MCP Server
MCP_SERVER_URL=http://localhost:8000

# Data Storage

Note: The project includes a small helper at `config/groq.py` that centralizes access to the
Groq API key. Use `get_groq_api_key()` to read the key, `get_auth_headers()` for HTTP calls,
or `init_groq_client()` to try initializing the Groq SDK client if it's installed.
SNAPSHOTS_DIR=./data/flight_snapshots
ALERTS_DIR=./data/alerts

# LLM Configuration
LLM_MODEL=llama3-70b-8192
LLM_TEMPERATURE=0.7

# Regions (optional override)
REGION1_NAME=Central Europe (Frankfurt, Munich, Vienna, Zurich)
REGION2_NAME=North Atlantic (London, Dublin, Manchester)
REGION3_NAME=Middle East Hub (Istanbul, Cyprus, Tel Aviv)
```

### Step 3: Start n8n (Data Orchestration)

```powershell
# Start n8n container
docker-compose up -d

# Verify n8n is running
docker ps

# Access n8n UI
# Open browser: http://localhost:5678
```

**Import n8n Workflows:**

1. Open n8n at http://localhost:5678
2. Click **Import from File**
3. Import `n8n_workflows/opensky_data_fetcher_region1.json`
4. Import `n8n_workflows/snapshot_webhook_endpoints.json`
5. **Activate both workflows** (toggle switch)
6. Verify execution: workflows should run every 15 seconds

### Step 4: Start MCP Server

```powershell
# In a new terminal, activate venv
.\venv\Scripts\Activate

# Run MCP server
python -m mcp_server.main

# Server starts at http://localhost:8000
# Health check: http://localhost:8000/health
```

**Verify MCP Server:**

```powershell
# Check health endpoint
Invoke-RestMethod -Uri http://localhost:8000/health

# List available tools
Invoke-RestMethod -Uri http://localhost:8000/mcp/tools
```

### Step 5: Launch Streamlit UI

```powershell
# In a new terminal, activate venv
.\venv\Scripts\Activate

# Run Streamlit app
streamlit run ui/app.py

# UI opens at http://localhost:8501
```

---

## 🎮 Usage Guide

### Traveler Mode

For passengers tracking flights and asking travel-related questions.

**Features:**
- 🔍 Track specific flights by callsign
- 💬 Chat with AI travel assistant
- ❓ Quick questions (delays, weather, connections, baggage)
- 🤝 Agent delegation (traveler → ops analyst for technical queries)

**Example Queries:**
- "Is flight LH123 delayed?"
- "What's the weather at my destination?"
- "Tell me about flights near Frankfurt right now"
- "Are there any airspace issues affecting my connection?"

### Operations Mode

For air traffic controllers and operations teams.

**Features:**
- 📊 Real-time regional airspace overview
- ⚠️ Anomaly detection dashboard
- 🤖 AI-generated operational summaries
- 📋 Detailed flight tables with status flags
- 🔄 Auto-refresh & manual refresh

**Workflow:**
1. Select region (Central Europe, North Atlantic, Middle East)
2. Review metrics (total flights, anomalies, in-flight count)
3. Click "Generate AI Analysis" for intelligent summary
4. Review anomalies by severity
5. Inspect detailed flight table

---

## 🛠️ Configuration

### Regions (config/regions.json)

Define monitored airspace regions with bounding boxes:

```json
[
  {
    "id": "region1",
    "name": "Central Europe (Frankfurt, Munich, Vienna, Zurich)",
    "bbox": {
      "lat_min": 45.0, "lat_max": 55.0,
      "lon_min": 5.0, "lon_max": 15.0
    }
  }
]
```

### Anomaly Rules (config/thresholds.json)

Configure detection thresholds:

```json
{
  "rules": {
    "low_speed_at_altitude": {
      "enabled": true,
      "min_altitude_m": 5000,
      "max_speed_mps": 50,
      "severity": "high"
    }
  }
}
```

**Available Rules:**
1. `low_speed_at_altitude` - Slow aircraft at high altitude
2. `stationary_aircraft` - Zero velocity mid-flight
3. `rapid_altitude_change` - >50m/s vertical speed
4. `rapid_descent` - Steep descent rate
5. `extreme_velocity` - Unrealistic speed
6. `altitude_bounds` - Outside safe altitude range

---

## 🔧 Troubleshooting

### Issue: n8n workflows not executing

**Solutions:**
- Verify container is running: `docker ps`
- Check n8n logs: `docker logs n8n`
- Ensure workflows are activated (toggle switch in n8n UI)
- Verify OpenSky API is accessible: https://opensky-network.org/api/states/all

### Issue: MCP server connection failed

**Solutions:**
- Check if server is running: `http://localhost:8000/health`
- Verify port 8000 is not in use: `netstat -ano | findstr :8000`
- Review MCP server logs for errors
- Ensure `.env` file has `MCP_SERVER_URL=http://localhost:8000`

### Issue: No data in UI

**Solutions:**
- Wait 15-30 seconds for first n8n execution
- Check `data/flight_snapshots/` directory exists and has JSON files
- Verify n8n webhook endpoints are responding:
  - http://localhost:5678/webhook/latest-region1
- Review n8n execution history for errors

### Issue: Agent not responding

**Solutions:**
- Verify Groq API key is valid in `.env`
- Check internet connection (agents need LLM API access)
- Review MCP server logs for tool call errors
- Ensure CrewAI dependencies are installed: `pip list | findstr crewai`

### Issue: OpenSky API rate limit

**Symptoms:**
- n8n logs show "API rate limit" errors
- Snapshots have `"api_status": "rate_limited"`

**Solutions:**
- Workflows use cached data automatically when rate-limited
- Wait 10 seconds between manual API calls
- Consider increasing cron interval from 15s to 30s in n8n

---

## 📊 System Architecture

### Data Flow

```
OpenSky API → n8n (fetch) → Transform → Anomaly Detection → JSON Storage
                ↓
          Webhooks (HTTP)
                ↓
         MCP Server (FastAPI) ← CrewAI Agents
                ↓
         Streamlit UI (User)
```

### Component Interaction

1. **n8n** fetches data from OpenSky Network every 15 seconds
2. **Anomaly Detector** processes snapshots and flags issues
3. **MCP Server** exposes 3 tools via REST API
4. **CrewAI Agents** call MCP tools via HTTP
5. **Streamlit UI** displays data and agent responses

### MCP Tools

| Tool | Endpoint | Purpose |
|------|----------|---------|
| `flights.list_region_snapshot` | POST `/mcp/tools/flights.list_region_snapshot` | Get all flights in a region |
| `flights.get_by_callsign` | POST `/mcp/tools/flights.get_by_callsign` | Find specific flight by callsign |
| `alerts.list_active` | POST `/mcp/tools/alerts.list_active` | Retrieve active anomaly alerts |

---

## 🤖 AI Agents

### 1. Operations Analyst Agent

**Role:** Air traffic operations specialist  
**Experience:** 15 years in ATC, flight operations, and safety analysis  
**Tools:** FlightSnapshotTool, ActiveAlertsTool  

**Capabilities:**
- Analyze regional airspace snapshots
- Identify patterns and trends
- Provide operational recommendations
- Generate executive summaries

### 2. Traveler Support Agent

**Role:** Travel assistance and customer support  
**Experience:** 10 years in airline customer service  
**Tools:** FlightByCallsignTool, FlightSnapshotTool  
**Delegation:** Can escalate to Operations Analyst for technical queries  

**Capabilities:**
- Track specific flights
- Answer travel-related questions
- Provide real-time updates
- Delegate complex airspace queries (A2A)

---

## 📈 Performance & Limits

### OpenSky Network API
- **Rate Limit:** ~100 requests/day (anonymous)
- **Update Frequency:** 10-15 seconds
- **Data Coverage:** Global airspace
- **Fields:** Position, altitude, velocity, heading, callsign, ICAO24

### System Requirements
- **RAM:** 2GB minimum (4GB recommended)
- **CPU:** 2 cores minimum
- **Storage:** 500MB for logs and data
- **Network:** Stable internet connection

### Scalability
- Handles 50-200 flights per region
- Processes 15-30 snapshots per minute
- Supports 5-10 concurrent UI users

---

## 🧪 Testing

### Manual Testing Checklist

**n8n Workflows:**
- [ ] Data fetcher executes every 15 seconds
- [ ] Snapshots saved to `data/flight_snapshots/`
- [ ] Webhooks respond with JSON data
- [ ] Error handling logs failures

**MCP Server:**
- [ ] Health endpoint returns 200 OK
- [ ] Tools endpoint lists 3 tools
- [ ] Flight snapshot tool returns data
- [ ] Callsign search works correctly

**Anomaly Detection:**
- [ ] Rules loaded from config
- [ ] Anomalies detected and saved
- [ ] Severity levels assigned correctly
- [ ] Alerts appear in `active_alerts.json`

**UI - Traveler Mode:**
- [ ] Flight search by callsign
- [ ] Chat interface responds
- [ ] Quick questions work
- [ ] Flight details display correctly

**UI - Operations Mode:**
- [ ] Region selection switches data
- [ ] Metrics display correctly
- [ ] AI analysis generates summary
- [ ] Flight table shows anomalies
- [ ] Refresh updates data

---

## 📚 Additional Documentation

- **PROJECT_PLAN.md** - Master implementation plan with architecture
- **PHASE2_DETAILED_GUIDE.md** - Detailed n8n setup instructions
- **config/regions.json** - Region definitions and bounding boxes
- **config/thresholds.json** - Anomaly detection rules

---

## 🔐 Security Notes

- **API Keys:** Never commit `.env` file to version control
- **n8n:** Runs locally on localhost:5678 (not exposed externally)
- **MCP Server:** Uses CORS for localhost access only
- **OpenSky API:** Uses anonymous public access (no authentication)

---

## 🐛 Known Issues

1. **Rate Limiting:** OpenSky API has strict rate limits; workflows handle this with caching
2. **Data Latency:** 15-30 second delay between real-world events and UI display
3. **Agent Response Time:** 3-10 seconds for complex queries (depends on Groq API)

---

## 🚀 Future Enhancements

- [ ] Historical data analysis and trend detection
- [ ] Email/SMS notifications for critical anomalies
- [ ] Map visualization of flight paths
- [ ] Multi-user authentication and role-based access
- [ ] Integration with additional data sources (weather, NOTAMs)
- [ ] Advanced ML-based anomaly detection

---

## 📞 Support & Contact

For questions or issues:
1. Review troubleshooting section above
2. Check n8n and MCP server logs
3. Verify all prerequisites are met
4. Ensure `.env` is configured correctly

---

## 📄 License

This project is for educational purposes (FAST University - Agentic AI Course, Assignment 3).

---

## 🙏 Acknowledgments

- **OpenSky Network** - Real-time flight data API
- **n8n** - Workflow automation platform
- **CrewAI** - Multi-agent framework
- **Groq** - Fast LLM inference
- **Streamlit** - UI framework

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Course:** Agentic AI (Semester 7)  
**Institution:** FAST University
 
