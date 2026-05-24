"""
Utility functions for MCP server
"""
import json
from typing import Dict, Any, List
from datetime import datetime


def format_timestamp(timestamp: int) -> str:
    """
    Convert Unix timestamp to human-readable format
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        Formatted datetime string
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance between two points using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth radius in kilometers
    R = 6371.0
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def filter_flights_by_criteria(
    flights: List[Dict[str, Any]],
    min_altitude: float = None,
    max_altitude: float = None,
    on_ground: bool = None,
    country: str = None
) -> List[Dict[str, Any]]:
    """
    Filter flights based on various criteria
    
    Args:
        flights: List of flight dictionaries
        min_altitude: Minimum altitude filter (meters)
        max_altitude: Maximum altitude filter (meters)
        on_ground: Filter for ground status
        country: Filter by origin country
        
    Returns:
        Filtered list of flights
    """
    filtered = flights
    
    if min_altitude is not None:
        filtered = [f for f in filtered if f.get("baro_altitude", 0) >= min_altitude]
    
    if max_altitude is not None:
        filtered = [f for f in filtered if f.get("baro_altitude", float('inf')) <= max_altitude]
    
    if on_ground is not None:
        filtered = [f for f in filtered if f.get("on_ground", False) == on_ground]
    
    if country is not None:
        filtered = [f for f in filtered if f.get("origin_country", "").lower() == country.lower()]
    
    return filtered


def summarize_flight_info(flight: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of flight information
    
    Args:
        flight: Flight data dictionary
        
    Returns:
        Natural language summary string
    """
    callsign = flight.get("callsign", "Unknown")
    icao24 = flight.get("icao24", "Unknown")
    country = flight.get("origin_country", "Unknown")
    
    # Position
    lat = flight.get("latitude")
    lon = flight.get("longitude")
    position = f"({lat:.2f}°, {lon:.2f}°)" if lat and lon else "Unknown position"
    
    # Altitude
    altitude = flight.get("baro_altitude")
    if altitude is not None:
        altitude_str = f"{altitude:.0f} meters ({altitude * 3.28084:.0f} feet)"
    else:
        altitude_str = "Unknown altitude"
    
    # Velocity
    velocity = flight.get("velocity")
    if velocity is not None:
        velocity_kmh = velocity * 3.6
        velocity_str = f"{velocity:.1f} m/s ({velocity_kmh:.1f} km/h)"
    else:
        velocity_str = "Unknown velocity"
    
    # Vertical rate
    vertical_rate = flight.get("vertical_rate")
    if vertical_rate is not None:
        if vertical_rate > 0:
            vr_str = f"climbing at {vertical_rate:.1f} m/s"
        elif vertical_rate < 0:
            vr_str = f"descending at {abs(vertical_rate):.1f} m/s"
        else:
            vr_str = "level flight"
    else:
        vr_str = "Unknown vertical rate"
    
    # Status
    on_ground = flight.get("on_ground", False)
    status = "on ground" if on_ground else "in flight"
    
    summary = f"""
Flight {callsign} (ICAO24: {icao24})
Origin: {country}
Status: {status}
Position: {position}
Altitude: {altitude_str}
Speed: {velocity_str}
Vertical Movement: {vr_str}
    """.strip()
    
    return summary


def validate_snapshot_data(snapshot: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate that snapshot data has required fields
    
    Args:
        snapshot: Snapshot data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["timestamp", "region", "flights"]
    
    for field in required_fields:
        if field not in snapshot:
            return False, f"Missing required field: {field}"
    
    if not isinstance(snapshot["flights"], list):
        return False, "Field 'flights' must be a list"
    
    return True, ""
