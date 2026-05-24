"""
MCP Tools Implementation
Functions that read and process flight data from JSON files
"""
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Get data directories from environment
SNAPSHOTS_DIR = os.getenv("SNAPSHOTS_DIR", "./data/flight_snapshots")
ALERTS_DIR = os.getenv("ALERTS_DIR", "./data/alerts")


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file
    Handles both single JSON objects and arrays
    Also handles malformed files with multiple concatenated JSON objects
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data (for snapshot files, returns the latest snapshot)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file cannot be parsed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        raise ValueError(f"File is empty: {file_path}")
    
    # Try to parse as single JSON object/array first
    try:
        data = json.loads(content)
        # If it's an array, return the last (latest) snapshot
        if isinstance(data, list) and len(data) > 0:
            return data[-1]
        return data
    except json.JSONDecodeError:
        # File might contain multiple concatenated JSON objects
        # Try to parse each line as a separate JSON object
        lines = content.split('\n')
        parsed_objects = []
        
        current_obj = ""
        brace_count = 0
        
        for line in lines:
            current_obj += line + "\n"
            brace_count += line.count('{') - line.count('}')
            
            # When braces are balanced, we have a complete JSON object
            if brace_count == 0 and current_obj.strip():
                try:
                    obj = json.loads(current_obj.strip())
                    parsed_objects.append(obj)
                    current_obj = ""
                except json.JSONDecodeError:
                    # Skip malformed objects
                    current_obj = ""
                    continue
        
        if parsed_objects:
            # Return the latest snapshot (last object in file)
            return parsed_objects[-1]
        else:
            # Raise a proper ValueError instead of JSONDecodeError
            # JSONDecodeError requires specific parameters that are hard to construct
            raise ValueError(f"Could not parse any valid JSON objects from {file_path}")


def list_region_snapshot(region_name: str) -> Dict[str, Any]:
    """
    MCP Tool: Get latest flight snapshot for a region
    
    Args:
        region_name: Region identifier (region1, region2, or region3)
        
    Returns:
        Flight snapshot data including all flights and metadata
        
    Raises:
        FileNotFoundError: If snapshot file doesn't exist
        ValueError: If region_name is invalid
    """
    # Validate region name
    valid_regions = ["region1", "region2", "region3"]
    if region_name not in valid_regions:
        raise ValueError(f"Invalid region_name. Must be one of: {valid_regions}")
    
    # Build file path
    file_path = os.path.join(SNAPSHOTS_DIR, f"{region_name}_latest.json")
    
    # Load snapshot
    snapshot = load_json_file(file_path)
    
    return snapshot


def get_by_callsign(callsign: str) -> Optional[Dict[str, Any]]:
    """
    MCP Tool: Find a flight by callsign across all regions
    
    Args:
        callsign: Flight callsign to search for (e.g., "THY4KZ")
        
    Returns:
        Flight data if found, None otherwise
    """
    # Normalize callsign (trim whitespace, uppercase)
    callsign = callsign.strip().upper()
    
    # Search in all regions
    regions = ["region1", "region2", "region3"]
    
    for region in regions:
        try:
            snapshot = list_region_snapshot(region)
            
            # Search through flights
            for flight in snapshot.get("flights", []):
                flight_callsign = flight.get("callsign", "")
                if flight_callsign:
                    flight_callsign = flight_callsign.strip().upper()
                    if flight_callsign == callsign:
                        # Add snapshot metadata for context
                        flight["snapshot_datetime"] = snapshot.get("datetime")
                        flight["snapshot_timestamp"] = snapshot.get("timestamp")
                        return flight
        except FileNotFoundError:
            # Region snapshot doesn't exist, continue to next
            continue
        except Exception as e:
            # Log error but continue searching
            print(f"Error searching region {region}: {e}")
            continue
    
    # Flight not found in any region
    return None


def list_active_alerts() -> Dict[str, Any]:
    """
    MCP Tool: Get all currently active anomaly alerts
    
    Returns:
        Alerts data including count and list of all alerts
        
    Raises:
        FileNotFoundError: If alerts file doesn't exist
    """
    file_path = os.path.join(ALERTS_DIR, "active_alerts.json")
    alerts_data = load_json_file(file_path)
    return alerts_data


def get_flight_by_icao24(icao24: str) -> Optional[Dict[str, Any]]:
    """
    Helper function: Find a flight by ICAO24 identifier
    
    Args:
        icao24: ICAO24 identifier (e.g., "4baa1a")
        
    Returns:
        Flight data if found, None otherwise
    """
    icao24 = icao24.strip().lower()
    
    regions = ["region1", "region2", "region3"]
    
    for region in regions:
        try:
            snapshot = list_region_snapshot(region)
            
            for flight in snapshot.get("flights", []):
                if flight.get("icao24", "").lower() == icao24:
                    flight["snapshot_datetime"] = snapshot.get("datetime")
                    flight["snapshot_timestamp"] = snapshot.get("timestamp")
                    return flight
        except:
            continue
    
    return None


def get_region_statistics(region_name: str) -> Dict[str, Any]:
    """
    Helper function: Get statistical summary of a region
    
    Args:
        region_name: Region identifier
        
    Returns:
        Statistics including flight count, anomalies, etc.
    """
    try:
        snapshot = list_region_snapshot(region_name)
        
        # Calculate statistics
        flights = snapshot.get("flights", [])
        anomalies = snapshot.get("anomalies", [])
        
        # Count flights by status
        on_ground = sum(1 for f in flights if f.get("on_ground", False))
        in_air = len(flights) - on_ground
        
        # Count anomalies by severity
        anomaly_by_severity = {}
        for anomaly in anomalies:
            severity = anomaly.get("severity", "unknown")
            anomaly_by_severity[severity] = anomaly_by_severity.get(severity, 0) + 1
        
        return {
            "region": region_name,
            "region_name": snapshot.get("region_name"),
            "last_updated": snapshot.get("datetime"),
            "total_flights": len(flights),
            "flights_in_air": in_air,
            "flights_on_ground": on_ground,
            "total_anomalies": len(anomalies),
            "anomalies_by_severity": anomaly_by_severity,
            "api_status": snapshot.get("metadata", {}).get("api_status", "unknown")
        }
    except Exception as e:
        return {
            "region": region_name,
            "error": str(e)
        }
