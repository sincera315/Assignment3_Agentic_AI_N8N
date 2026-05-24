"""
MCP Server Package
FastAPI-based Model Context Protocol server for flight data
"""
from .main import app
from .tools import list_region_snapshot, get_by_callsign, list_active_alerts
from .models import Flight, FlightSnapshot, Alert

__version__ = "1.0.0"
__all__ = [
    "app",
    "list_region_snapshot",
    "get_by_callsign",
    "list_active_alerts",
    "Flight",
    "FlightSnapshot",
    "Alert"
]
