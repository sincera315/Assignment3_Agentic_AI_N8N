"""
Custom Tools for CrewAI Agents
Wraps MCP server tools for use with CrewAI
"""
from crewai.tools import tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")


# Store original functions before tool decoration for direct testing
def _get_flight_snapshot_impl(region_name: str) -> str:
    """
    Get the latest flight snapshot for a specific region.
    Returns all flights currently tracked in that region with their positions, altitudes,
    speeds, and any detected anomalies. Use this when you need to analyze airspace
    conditions or monitor all flights in a region.
    
    Args:
        region_name: Region identifier - must be 'region1', 'region2', or 'region3'
                    region1 = Central Europe
                    region2 = North Atlantic  
                    region3 = Middle East Hub
    
    Returns:
        Formatted string with flight data and anomalies
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/flights.list_region_snapshot",
            json={"region_name": region_name},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success"):
            snapshot = data.get("data", {})
            
            # Format for LLM consumption
            result = f"""Region: {snapshot.get('region_name', 'Unknown')} ({snapshot.get('region')})
Last Updated: {snapshot.get('datetime')}
Total Flights: {snapshot.get('flight_count', 0)}
Anomalies Detected: {snapshot.get('anomaly_count', 0)}

Flights:"""
            
            for flight in snapshot.get('flights', [])[:20]:  # Limit to 20 for token efficiency
                callsign = flight.get('callsign', 'N/A')
                icao24 = flight.get('icao24', 'N/A')
                lat = flight.get('latitude', 0)
                lon = flight.get('longitude', 0)
                alt = flight.get('baro_altitude', 0)
                vel = flight.get('velocity', 0)
                vr = flight.get('vertical_rate', 0)
                on_ground = flight.get('on_ground', False)
                
                result += f"\n- {callsign} ({icao24}): Position ({lat:.2f}, {lon:.2f}), "
                result += f"Alt {alt:.0f}m, Speed {vel:.1f}m/s"
                if vr is not None:
                    result += f", VRate {vr:.1f}m/s"
                if on_ground:
                    result += " [ON GROUND]"
            
            if snapshot.get('anomaly_count', 0) > 0:
                result += f"\n\nAnomalies ({snapshot['anomaly_count']}):"
                for anomaly in snapshot.get('anomalies', [])[:10]:
                    result += f"\n- {anomaly.get('type')}: {anomaly.get('callsign')} - {anomaly.get('details')} (Severity: {anomaly.get('severity')})"
            
            return result
        else:
            return f"Error: {data.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Error calling MCP server: {str(e)}"

# Create tool from function
get_flight_snapshot = tool("Get Flight Snapshot")(_get_flight_snapshot_impl)

# Export function version for direct testing
get_flight_snapshot_func = _get_flight_snapshot_impl


# Store original function before tool decoration
def _get_flight_by_callsign_impl(callsign: str) -> str:
    """
    Find a specific flight by its callsign across all monitored regions.
    Returns detailed information about that flight including current position, altitude,
    speed, heading, and status. Use this when a traveler asks about their specific flight.
    
    Args:
        callsign: Flight callsign to search for (e.g., 'THY4KZ', 'AAL100')
    
    Returns:
        Detailed flight information or error message if not found
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/flights.get_by_callsign",
            json={"callsign": callsign.strip().upper()},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success") and data.get("data"):
            flight = data["data"]
            
            # Format comprehensive flight info
            result = f"""Flight Found: {flight.get('callsign', 'N/A')}
ICAO24: {flight.get('icao24', 'N/A')}
Origin Country: {flight.get('origin_country', 'Unknown')}
Region: {flight.get('region', 'Unknown')}

Position:
- Latitude: {flight.get('latitude', 0):.4f}°
- Longitude: {flight.get('longitude', 0):.4f}°

Altitude:
- Barometric: {flight.get('baro_altitude', 0):.0f} meters ({flight.get('baro_altitude', 0) * 3.28084:.0f} feet)
- Geometric: {flight.get('geo_altitude', 0):.0f} meters

Speed & Movement:
- Velocity: {flight.get('velocity', 0):.1f} m/s ({flight.get('velocity', 0) * 3.6:.1f} km/h)
- True Track: {flight.get('true_track', 0):.1f}°
- Vertical Rate: {flight.get('vertical_rate', 0):.1f} m/s"""

            if flight.get('vertical_rate'):
                vr = flight['vertical_rate']
                if vr > 0:
                    result += " (CLIMBING)"
                elif vr < 0:
                    result += " (DESCENDING)"
                else:
                    result += " (LEVEL)"
            
            result += f"\n\nStatus: {'ON GROUND' if flight.get('on_ground') else 'IN FLIGHT'}"
            result += f"\nLast Contact: {flight.get('last_contact', 'Unknown')}"
            result += f"\nData Timestamp: {flight.get('snapshot_datetime', 'Unknown')}"
            
            return result
        else:
            return f"Flight '{callsign}' not found in any monitored region. The flight may not be in our coverage areas or the callsign may be incorrect."
            
    except Exception as e:
        return f"Error calling MCP server: {str(e)}"

# Create tool from function
get_flight_by_callsign = tool("Find Flight by Callsign")(_get_flight_by_callsign_impl)

# Export function version for direct testing
get_flight_by_callsign_func = _get_flight_by_callsign_impl


# Store original function before tool decoration
def _get_active_alerts_impl() -> str:
    """
    Get all currently active anomaly alerts across all regions.
    Returns a list of detected anomalies with severity levels, affected flights, and
    descriptions. Use this when analyzing overall airspace safety or looking for
    concerning patterns.
    
    No input required.
    
    Returns:
        Formatted string with all active alerts grouped by severity
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/alerts.list_active",
            json={},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success"):
            alerts_data = data.get("data", {})
            alert_count = alerts_data.get("alert_count", 0)
            
            if alert_count == 0:
                return "No active alerts. All flights are operating normally."
            
            result = f"""Active Alerts: {alert_count}
Last Updated: {alerts_data.get('last_updated', 'Unknown')}

Alerts by Severity:"""
            
            # Group by severity
            severity_counts = {}
            for alert in alerts_data.get("alerts", []):
                sev = alert.get("severity", "unknown")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            for sev, count in sorted(severity_counts.items(), key=lambda x: ["critical", "high", "medium", "low"].index(x[0]) if x[0] in ["critical", "high", "medium", "low"] else 999):
                result += f"\n- {sev.upper()}: {count}"
            
            result += "\n\nRecent Alerts:"
            
            # Show first 15 alerts
            for alert in alerts_data.get("alerts", [])[:15]:
                result += f"\n\n[{alert.get('severity', 'unknown').upper()}] {alert.get('type', 'unknown')}"
                result += f"\nFlight: {alert.get('callsign', 'N/A')} ({alert.get('icao24', 'N/A')})"
                result += f"\nRegion: {alert.get('region', 'unknown')}"
                result += f"\nDetails: {alert.get('details', 'No details')}"
                result += f"\nTime: {alert.get('datetime', 'Unknown')}"
            
            if alert_count > 15:
                result += f"\n\n... and {alert_count - 15} more alerts"
            
            return result
        else:
            return f"Error: {data.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Error calling MCP server: {str(e)}"

# Create tool from function
get_active_alerts = tool("Get Active Alerts")(_get_active_alerts_impl)

# Export function version for direct testing
get_active_alerts_func = _get_active_alerts_impl


# Export the tools and functions for easy import
__all__ = [
    'get_flight_snapshot',
    'get_flight_by_callsign',
    'get_active_alerts',
    'get_flight_snapshot_func',
    'get_flight_by_callsign_func',
    'get_active_alerts_func'
]
