"""
MCP Server Main Application
FastAPI-based server that exposes flight data tools via MCP protocol
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

from .tools import (
    list_region_snapshot,
    get_by_callsign,
    list_active_alerts
)
from .models import (
    FlightSnapshot,
    Flight,
    Alert,
    MCPToolRequest,
    MCPToolResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Airspace Copilot MCP Server",
    description="Model Context Protocol server for flight data access",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Airspace Copilot MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "tools": "/mcp/tools",
            "list_region_snapshot": "/mcp/tools/flights.list_region_snapshot",
            "get_by_callsign": "/mcp/tools/flights.get_by_callsign",
            "list_active_alerts": "/mcp/tools/alerts.list_active"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_directory": os.getenv("DATA_DIR", "./data"),
        "snapshots_available": os.path.exists(os.path.join(
            os.getenv("SNAPSHOTS_DIR", "./data/flight_snapshots"),
            "region1_latest.json"
        ))
    }


@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "flights.list_region_snapshot",
                "description": "Get the latest flight snapshot for a specified region",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "region_name": {
                            "type": "string",
                            "description": "Region identifier (region1, region2, or region3)",
                            "enum": ["region1", "region2", "region3"]
                        }
                    },
                    "required": ["region_name"]
                }
            },
            {
                "name": "flights.get_by_callsign",
                "description": "Find a specific flight by its callsign across all regions",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "callsign": {
                            "type": "string",
                            "description": "Flight callsign (e.g., THY4KZ)"
                        }
                    },
                    "required": ["callsign"]
                }
            },
            {
                "name": "alerts.list_active",
                "description": "Get all currently active anomaly alerts",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }


class RegionSnapshotRequest(BaseModel):
    region_name: str


class FlightByCallsignRequest(BaseModel):
    callsign: str


@app.post("/mcp/tools/flights.list_region_snapshot")
async def tool_list_region_snapshot(request: RegionSnapshotRequest):
    """
    MCP Tool: Get latest flight snapshot for a region
    """
    try:
        result = list_region_snapshot(request.region_name)
        # Use dict() to ensure proper serialization
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        # Handle ValueError from JSON parsing
        raise HTTPException(status_code=500, detail=f"Data parsing error: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"Internal server error: {str(e)}"
        # Log full traceback for debugging
        print(f"Error in tool_list_region_snapshot: {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/mcp/tools/flights.get_by_callsign")
async def tool_get_by_callsign(request: FlightByCallsignRequest):
    """
    MCP Tool: Get flight by callsign
    """
    try:
        result = get_by_callsign(request.callsign)
        if result is None:
            return {
                "success": False,
                "data": None,
                "error": f"Flight with callsign '{request.callsign}' not found"
            }
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except ValueError as e:
        # Handle ValueError from JSON parsing
        raise HTTPException(status_code=500, detail=f"Data parsing error: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"Internal server error: {str(e)}"
        # Log full traceback for debugging
        print(f"Error in tool_get_by_callsign: {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/mcp/tools/alerts.list_active")
async def tool_list_active_alerts():
    """
    MCP Tool: Get all active alerts
    """
    try:
        result = list_active_alerts()
        # Use dict() to ensure proper serialization
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        # Handle ValueError from JSON parsing
        raise HTTPException(status_code=500, detail=f"Data parsing error: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"Internal server error: {str(e)}"
        # Log full traceback for debugging
        print(f"Error in tool_list_active_alerts: {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


# ============================================================================
# REST API Endpoints (for direct HTTP access)
# ============================================================================

@app.get("/tools/flights/region/{region_name}")
async def get_region_snapshot(region_name: str):
    """
    REST API: Get latest flight snapshot for a region
    """
    if region_name not in ["region1", "region2", "region3"]:
        raise HTTPException(
            status_code=404,
            detail=f"Region not found: {region_name}. Valid regions: region1, region2, region3"
        )
    
    try:
        result = list_region_snapshot(region_name)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/tools/flights/callsign")
async def get_flight_by_callsign(callsign: Optional[str] = None):
    """
    REST API: Get flight by callsign
    """
    if not callsign:
        raise HTTPException(
            status_code=400,
            detail="Callsign parameter is required"
        )
    
    try:
        result = get_by_callsign(callsign.strip())
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Flight with callsign {callsign} not found in any region"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for flight: {str(e)}")


@app.get("/tools/alerts/active")
async def get_active_alerts():
    """
    REST API: Get all active alerts
    """
    try:
        result = list_active_alerts()
        return result
    except FileNotFoundError:
        # If alerts file doesn't exist, return empty alerts
        return {
            "alert_count": 0,
            "alerts": [],
            "last_updated": None,
            "regions": ["region1", "region2", "region3"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    
    print(f"Starting MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
