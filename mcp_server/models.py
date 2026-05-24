"""
Pydantic models for MCP server data structures
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BoundingBox(BaseModel):
    """Geographic bounding box"""
    lamin: float
    lomin: float
    lamax: float
    lomax: float


class Flight(BaseModel):
    """Individual flight data"""
    icao24: Optional[str] = None
    callsign: Optional[str] = None
    origin_country: Optional[str] = None
    time_position: Optional[int] = None
    last_contact: Optional[int] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    baro_altitude: Optional[float] = None
    on_ground: bool = False
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    geo_altitude: Optional[float] = None
    squawk: Optional[str] = None
    spi: bool = False
    position_source: int = 0
    fetch_timestamp: Optional[int] = None
    region: Optional[str] = None


class FlightSnapshot(BaseModel):
    """Complete flight snapshot for a region"""
    timestamp: int
    datetime: str
    region: str
    region_name: str
    bounding_box: BoundingBox
    flight_count: int
    flights: List[Flight]
    anomalies: Optional[List[Dict[str, Any]]] = []
    anomaly_count: int = 0
    metadata: Dict[str, Any] = {}


class Alert(BaseModel):
    """Anomaly alert"""
    type: str
    icao24: str
    callsign: Optional[str] = None
    severity: str
    details: str
    timestamp: int
    datetime: str
    region: str
    alert_id: str


class AlertsData(BaseModel):
    """Collection of alerts"""
    last_updated: str
    alert_count: int
    alerts: List[Alert]


class MCPToolRequest(BaseModel):
    """Generic MCP tool request"""
    tool_name: str
    parameters: Dict[str, Any] = {}


class MCPToolResponse(BaseModel):
    """Generic MCP tool response"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
