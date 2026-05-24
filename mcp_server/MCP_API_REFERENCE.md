# MCP Server API Reference

Complete reference for the Airspace Copilot MCP Server API endpoints.

---

## 🌐 Base URL

```
http://localhost:8000
```

---

## 📋 Endpoints

### 1. Root Endpoint

**GET /**

Get API information and health status.

**Response:**
```json
{
  "name": "Airspace Copilot MCP Server",
  "version": "1.0.0",
  "status": "operational",
  "tools": [
    "flights.list_region_snapshot",
    "flights.get_by_callsign",
    "alerts.list_active"
  ]
}
```

---

### 2. List Region Snapshot

**GET /tools/flights/region/{region_name}**

Get complete flight snapshot for a specific region.

**Parameters:**
- `region_name` (path, required): Region identifier
  - Allowed values: `region1`, `region2`, `region3`

**Example Request:**
```bash
curl http://localhost:8000/tools/flights/region/region1
```

**Example Response:**
```json
{
  "timestamp": 1764249304,
  "datetime": "2025-11-27T13:15:04.983Z",
  "region": "region1",
  "region_name": "Central Europe (Frankfurt, Munich, Vienna, Zurich)",
  "bounding_box": {
    "lamin": 45.0,
    "lomin": 5.0,
    "lamax": 55.0,
    "lomax": 15.0
  },
  "flight_count": 623,
  "flights": [
    {
      "icao24": "4b1815",
      "callsign": "SWR123",
      "origin_country": "Switzerland",
      "time_position": 1764249300,
      "last_contact": 1764249304,
      "longitude": 8.5481,
      "latitude": 47.3769,
      "baro_altitude": 10668.0,
      "on_ground": false,
      "velocity": 234.5,
      "true_track": 89.7,
      "vertical_rate": 0.0,
      "geo_altitude": 10972.8,
      "squawk": null,
      "spi": false,
      "position_source": 0
    }
  ],
  "anomalies": [],
  "anomaly_count": 0,
  "metadata": {
    "api_status": "success",
    "api_timestamp": 1764249304,
    "fetch_time": "2025-11-27T13:15:04.983Z"
  }
}
```

**Error Responses:**

| Code | Reason | Response |
|------|--------|----------|
| 404 | Invalid region | `{"detail": "Region not found: invalid_region"}` |
| 500 | Data file missing | `{"detail": "Data file not found: ..."}` |
| 500 | Invalid JSON | `{"detail": "Failed to parse snapshot data"}` |

---

### 3. Get Flight by Callsign

**GET /tools/flights/callsign**

Find a specific flight across all regions by callsign.

**Query Parameters:**
- `callsign` (query, required): Flight callsign (e.g., "SWR123")
  - Case-sensitive
  - Whitespace trimmed automatically

**Example Request:**
```bash
curl "http://localhost:8000/tools/flights/callsign?callsign=SWR123"
```

**Example Response (Found):**
```json
{
  "icao24": "4b1815",
  "callsign": "SWR123",
  "origin_country": "Switzerland",
  "longitude": 8.5481,
  "latitude": 47.3769,
  "baro_altitude": 10668.0,
  "on_ground": false,
  "velocity": 234.5,
  "true_track": 89.7,
  "vertical_rate": 0.0,
  "region": "region1",
  "fetch_timestamp": 1764249304
}
```

**Example Response (Not Found):**
```json
{
  "detail": "Flight with callsign NONEXISTENT not found in any region"
}
```

**Error Responses:**

| Code | Reason | Response |
|------|--------|----------|
| 400 | Missing callsign | `{"detail": "Callsign parameter is required"}` |
| 404 | Flight not found | `{"detail": "Flight with callsign ... not found"}` |
| 500 | Data access error | `{"detail": "Error searching for flight"}` |

---

### 4. List Active Alerts

**GET /tools/alerts/active**

Get all current anomaly alerts.

**Example Request:**
```bash
curl http://localhost:8000/tools/alerts/active
```

**Example Response (No Alerts):**
```json
{
  "alert_count": 0,
  "alerts": [],
  "last_updated": "2025-11-27T13:15:04.983Z",
  "regions": ["region1", "region2", "region3"]
}
```

**Example Response (With Alerts):**
```json
{
  "alert_count": 3,
  "alerts": [
    {
      "type": "low_speed_at_altitude",
      "severity": "high",
      "callsign": "LH456",
      "icao24": "3c6481",
      "latitude": 50.1,
      "longitude": 8.6,
      "altitude": 9500,
      "velocity": 45,
      "vertical_rate": 0,
      "message": "Low speed at altitude for LH456: 45 m/s at 9500m",
      "detected_at": "2025-11-27T13:14:55.123Z",
      "timestamp": 1764249295,
      "region": "region1"
    },
    {
      "type": "rapid_descent",
      "severity": "high",
      "callsign": "BAW789",
      "icao24": "400b12",
      "altitude": 7500,
      "velocity": 220,
      "vertical_rate": -18,
      "message": "Rapid descent detected for BAW789: -18 m/s from 7500m",
      "detected_at": "2025-11-27T13:15:02.456Z",
      "timestamp": 1764249302,
      "region": "region2"
    }
  ],
  "last_updated": "2025-11-27T13:15:04.983Z",
  "regions": ["region1", "region2", "region3"]
}
```

**Error Responses:**

| Code | Reason | Response |
|------|--------|----------|
| 404 | Alerts file missing | `{"detail": "No alerts file found"}` |
| 500 | Invalid alerts data | `{"detail": "Failed to parse alerts data"}` |

---

## 📊 Data Models

### Flight Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `icao24` | string | Unique aircraft identifier | "4b1815" |
| `callsign` | string\|null | Flight identifier | "SWR123" |
| `origin_country` | string | Aircraft registration country | "Switzerland" |
| `time_position` | int\|null | Unix timestamp of position | 1764249300 |
| `last_contact` | int | Last contact timestamp | 1764249304 |
| `longitude` | float\|null | Longitude in degrees | 8.5481 |
| `latitude` | float\|null | Latitude in degrees | 47.3769 |
| `baro_altitude` | float\|null | Barometric altitude in meters | 10668.0 |
| `on_ground` | boolean | Ground status | false |
| `velocity` | float\|null | Ground speed in m/s | 234.5 |
| `true_track` | float\|null | Track angle in degrees | 89.7 |
| `vertical_rate` | float\|null | Climb rate in m/s | 0.0 |
| `geo_altitude` | float\|null | GPS altitude in meters | 10972.8 |
| `squawk` | string\|null | Transponder code | "7000" |
| `spi` | boolean | Special position indicator | false |
| `position_source` | int | Source of position (0-3) | 0 |

### Anomaly Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `type` | string | Anomaly type | "low_speed_at_altitude" |
| `severity` | string | Alert level | "high" |
| `callsign` | string | Affected flight | "LH456" |
| `icao24` | string | Aircraft ID | "3c6481" |
| `message` | string | Human-readable description | "Low speed..." |
| `detected_at` | string | ISO timestamp | "2025-11-27T13:14:55Z" |
| `timestamp` | int | Unix timestamp | 1764249295 |
| `region` | string | Region where detected | "region1" |

**Anomaly Types:**
- `low_speed_at_altitude` - Aircraft moving too slowly at high altitude
- `rapid_descent` - Fast descent rate
- `stationary_aircraft` - Nearly stationary while airborne
- `rapid_altitude_change` - Sudden altitude change

**Severity Levels:**
- `low` - Minor issue, informational
- `medium` - Potential issue, monitor
- `high` - Significant issue, review required
- `critical` - Urgent issue, immediate attention

---

## 🔒 Authentication

Currently, no authentication is required. All endpoints are publicly accessible on localhost.

**For production deployment, add:**
- API key authentication
- Rate limiting
- HTTPS encryption

---

## 🚦 Rate Limiting

No rate limiting currently implemented.

**Recommended for production:**
- 100 requests per minute per IP
- Burst limit: 20 requests per second

---

## 📡 Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Data source unavailable |

---

## 🧪 Testing Examples

### Python (requests)

```python
import requests

# Get Region 1 snapshot
response = requests.get("http://localhost:8000/tools/flights/region/region1")
data = response.json()
print(f"Found {data['flight_count']} flights in {data['region_name']}")

# Find specific flight
callsign = "SWR123"
response = requests.get(f"http://localhost:8000/tools/flights/callsign?callsign={callsign}")
flight = response.json()
print(f"Flight {flight['callsign']} at altitude {flight['baro_altitude']}m")

# Get alerts
response = requests.get("http://localhost:8000/tools/alerts/active")
alerts = response.json()
print(f"Current alerts: {alerts['alert_count']}")
```

### PowerShell

```powershell
# Get Region 1 snapshot
$snapshot = Invoke-RestMethod http://localhost:8000/tools/flights/region/region1
Write-Host "Flights: $($snapshot.flight_count)"

# Find specific flight
$callsign = "SWR123"
$flight = Invoke-RestMethod "http://localhost:8000/tools/flights/callsign?callsign=$callsign"
Write-Host "Flight: $($flight.callsign) at $($flight.baro_altitude)m"

# Get alerts
$alerts = Invoke-RestMethod http://localhost:8000/tools/alerts/active
Write-Host "Alerts: $($alerts.alert_count)"
```

### JavaScript (fetch)

```javascript
// Get Region 1 snapshot
fetch('http://localhost:8000/tools/flights/region/region1')
  .then(res => res.json())
  .then(data => console.log(`Flights: ${data.flight_count}`));

// Find specific flight
const callsign = 'SWR123';
fetch(`http://localhost:8000/tools/flights/callsign?callsign=${callsign}`)
  .then(res => res.json())
  .then(flight => console.log(`${flight.callsign} at ${flight.baro_altitude}m`));

// Get alerts
fetch('http://localhost:8000/tools/alerts/active')
  .then(res => res.json())
  .then(alerts => console.log(`Alerts: ${alerts.alert_count}`));
```

---

## 🔧 Integration with Phase 4 (CrewAI)

**How agents will use these tools:**

### Ops Analyst Agent
```python
# Get all flights in a region
snapshot = list_region_snapshot("region1")
# Analyze for patterns, congestion, etc.

# Check for alerts
alerts = list_active_alerts()
# Report critical issues
```

### Traveler Support Agent
```python
# User: "Where is flight SWR123?"
flight = get_by_callsign("SWR123")
# Respond with location, altitude, speed

# User: "Are there any issues near Frankfurt?"
snapshot = list_region_snapshot("region1")
# Filter flights near Frankfurt
# Check alerts for that region
```

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial release
- 3 core tools implemented
- Basic error handling
- JSON data source

### Planned Features (Future)
- WebSocket support for real-time updates
- Historical data queries
- Flight path tracking
- Prediction/forecasting
- Additional anomaly types

---

## 🆘 Support

**Common Issues:**

1. **404 on all endpoints** → Server not running, start with `python run_mcp_server.py`
2. **Empty flight data** → n8n workflows not active or OpenSky API rate limited
3. **Stale data** → n8n workflows not updating, check execution logs
4. **No alerts** → Normal if no anomalies detected, lower thresholds to test

---

## 🔗 Related Documentation

- **Phase 3 Guide:** `PHASE3_GUIDE.md`
- **Testing Guide:** `test_mcp_server.py`
- **Data Models:** `mcp_server/models.py`
- **n8n Workflows:** `n8n_workflows/`

---

**✅ This API reference should be shared with Phase 4 (Agentic Layer) team for integration!**
