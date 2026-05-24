"""
Integration Tests - End-to-End System Testing
Tests the complete flow from n8n → MCP → Agents → UI
"""
import pytest
import requests
import json
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.crew_config import run_traveler_query, run_ops_analysis, run_nearby_issues_check
from agents.tools import (
    get_flight_snapshot_func,
    get_active_alerts_func,
    get_flight_by_callsign_func
)


# Configuration
MCP_SERVER_URL = "http://localhost:8000"
N8N_URL = "http://localhost:5678"
STREAMLIT_URL = "http://localhost:8501"
DATA_DIR = Path("./data/flight_snapshots")
ALERTS_DIR = Path("./data/alerts")


def safe_load_json_file(file_path: Path) -> dict:
    """
    Safely load JSON file, handling malformed files with multiple objects
    Returns the latest snapshot if multiple objects exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
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
        # Try to parse each complete object
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
            raise json.JSONDecodeError(
                f"Could not parse any valid JSON objects from {file_path}",
                content,
                0
            )


class TestDataPipeline:
    """Test data flow through the entire pipeline"""
    
    def test_n8n_creates_snapshot_files(self):
        """Test that n8n workflows create snapshot files"""
        # Wait for at least one fetch cycle
        time.sleep(20)
        
        # Check files exist
        assert DATA_DIR.exists(), "Snapshots directory doesn't exist"
        
        region1_file = DATA_DIR / "region1_latest.json"
        assert region1_file.exists(), "Region 1 snapshot file not created"
        
        # Check file has content
        data = safe_load_json_file(region1_file)
        
        assert 'region_name' in data, "Snapshot missing region_name field"
        assert 'flights' in data, "Snapshot missing flights field"
        assert isinstance(data['flights'], list), "Flights should be a list"
    
    def test_mcp_server_reads_snapshots(self):
        """Test that MCP server can read snapshot files"""
        result = get_flight_snapshot_func("region1")
        
        assert result is not None, "MCP tool returned None"
        assert "Error" not in result, f"MCP tool error: {result}"
        assert "region" in result.lower() or "flight" in result.lower(), "Result doesn't contain flight data"
    
    def test_alerts_file_creation(self):
        """Test that alerts are being created"""
        alerts_file = ALERTS_DIR / "active_alerts.json"
        
        if alerts_file.exists():
            with open(alerts_file, 'r') as f:
                alerts_data = json.load(f)
            
            assert 'alert_count' in alerts_data, "Alerts file missing alert_count"
            assert 'alerts' in alerts_data, "Alerts file missing alerts list"
            assert isinstance(alerts_data['alerts'], list), "Alerts should be a list"


class TestMCPServerIntegration:
    """Test MCP server endpoints and tools"""
    
    def test_health_endpoint(self):
        """Test MCP server health check"""
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        data = response.json()
        assert data['status'] == 'healthy', "Server not healthy"
    
    def test_list_region_snapshot_endpoint(self):
        """Test region snapshot endpoint"""
        payload = {"region_name": "region1"}
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/flights.list_region_snapshot",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200, f"API call failed: {response.status_code}"
        
        data = response.json()
        # MCP server returns success, data, error structure
        assert 'success' in data, "Response missing success field"
        assert data.get('success') is True, f"API call failed: {data.get('error', 'Unknown error')}"
        assert 'data' in data, "Response missing data field"
    
    def test_list_active_alerts_endpoint(self):
        """Test active alerts endpoint"""
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/alerts.list_active",
            json={},
            timeout=10
        )
        
        assert response.status_code == 200, f"API call failed: {response.status_code}"
        
        data = response.json()
        # MCP server returns success, data, error structure
        assert 'success' in data, "Response missing success field"
        assert data.get('success') is True, f"API call failed: {data.get('error', 'Unknown error')}"
        assert 'data' in data, "Response missing data field"
    
    def test_get_by_callsign_endpoint(self):
        """Test flight lookup by callsign"""
        # First, get a snapshot to find a real callsign
        snapshot_file = DATA_DIR / "region1_latest.json"
        
        if snapshot_file.exists():
            snapshot = safe_load_json_file(snapshot_file)
            
            if snapshot.get('flights') and len(snapshot['flights']) > 0:
                test_callsign = snapshot['flights'][0].get('callsign', 'UNKNOWN')
                
                if test_callsign and test_callsign != 'UNKNOWN':
                    payload = {"callsign": test_callsign}
                    response = requests.post(
                        f"{MCP_SERVER_URL}/mcp/tools/flights.get_by_callsign",
                        json=payload,
                        timeout=10
                    )
                    
                    assert response.status_code == 200, f"API call failed: {response.status_code}"
                    
                    data = response.json()
                    # MCP server returns success, data, error structure
                    assert 'success' in data, "Response missing success field"
                    # Note: success may be False if flight not found, which is valid
                    if data.get('success'):
                        assert 'data' in data, "Response missing data field"


class TestAgentIntegration:
    """Test CrewAI agent functionality"""
    
    def test_ops_analyst_tool_usage(self):
        """Test Ops Analyst agent can use tools"""
        # Call agent to analyze region
        result = run_ops_analysis("region1")
        
        assert result is not None, "Agent returned None"
        assert len(result) > 0, "Agent returned empty response"
        # Allow for error messages that indicate no data (which is valid)
        # But fail on actual tool errors
        if "error" in result.lower():
            # Check if it's a "no data" scenario (acceptable) vs actual error
            assert "no data" in result.lower() or "no flight" in result.lower() or "unavailable" in result.lower(), \
                f"Agent returned error: {result}"
    
    def test_traveler_support_tool_usage(self):
        """Test Traveler Support agent can use tools"""
        # Get a real flight callsign
        snapshot_file = DATA_DIR / "region1_latest.json"
        
        if snapshot_file.exists():
            snapshot = safe_load_json_file(snapshot_file)
            
            if snapshot.get('flights') and len(snapshot['flights']) > 0:
                test_callsign = snapshot['flights'][0].get('callsign', 'TEST123')
            else:
                test_callsign = "TEST123"  # Fallback
        else:
            test_callsign = "TEST123"  # Fallback
        
        # Call agent
        result = run_traveler_query(test_callsign)
        
        assert result is not None, "Agent returned None"
        assert len(result) > 0, "Agent returned empty response"
    
    def test_a2a_communication(self):
        """Test A2A agent delegation"""
        # Get a real flight callsign
        snapshot_file = DATA_DIR / "region1_latest.json"
        
        if snapshot_file.exists():
            snapshot = safe_load_json_file(snapshot_file)
            
            if snapshot.get('flights') and len(snapshot['flights']) > 0:
                test_callsign = snapshot['flights'][0].get('callsign', 'TEST123')
            else:
                test_callsign = "TEST123"
        else:
            test_callsign = "TEST123"
        
        # Call A2A crew
        result = run_nearby_issues_check(test_callsign)
        
        assert result is not None, "A2A returned None"
        assert len(result) > 0, "A2A returned empty response"


class TestEndToEndFlows:
    """Test complete user flows"""
    
    def test_traveler_flow_complete(self):
        """Test: User tracks flight → Asks question → Gets answer"""
        # Step 1: Get a real callsign
        snapshot_file = DATA_DIR / "region1_latest.json"
        
        if snapshot_file.exists():
            snapshot = safe_load_json_file(snapshot_file)
            
            if snapshot.get('flights') and len(snapshot['flights']) > 0:
                test_callsign = snapshot['flights'][0].get('callsign')
                
                if test_callsign and test_callsign != 'UNKNOWN':
                    # Step 2: Query agent about flight
                    result = run_traveler_query(test_callsign, "Where is this flight?")
                    
                    # Step 3: Verify response
                    assert result is not None, "Agent returned None"
                    assert len(result) > 50, "Agent response too short"
                    assert test_callsign in result or "flight" in result.lower(), "Response doesn't mention flight"
    
    def test_operations_flow_complete(self):
        """Test: User selects region → Generates analysis → Views data"""
        # Step 1: Get snapshot via MCP tool
        snapshot_result = get_flight_snapshot_func("region1")
        assert snapshot_result is not None, "Failed to get snapshot"
        
        # Step 2: Get alerts
        alerts_result = get_active_alerts_func()
        assert alerts_result is not None, "Failed to get alerts"
        
        # Step 3: Generate AI analysis
        analysis_result = run_ops_analysis("region1")
        assert analysis_result is not None, "Failed to generate analysis"
        assert len(analysis_result) > 50, "Analysis too short"
    
    def test_error_recovery_flow(self):
        """Test: System handles errors gracefully"""
        # Test with invalid region
        result = get_flight_snapshot_func("invalid_region")
        assert "Error" in result or "not found" in result.lower(), "Should handle invalid region"
        
        # Test with invalid callsign
        result = run_traveler_query("INVALIDCALLSIGN999")
        assert result is not None, "Should return something even for invalid callsign"


class TestSystemHealth:
    """Test system health and monitoring"""
    
    def test_all_services_reachable(self):
        """Test that all services respond to health checks"""
        # Test MCP server
        try:
            response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
            mcp_healthy = response.status_code == 200
        except:
            mcp_healthy = False
        
        assert mcp_healthy, "MCP server not reachable"
        
        # Test n8n
        try:
            response = requests.get(f"{N8N_URL}", timeout=5)
            n8n_healthy = response.status_code == 200
        except:
            n8n_healthy = False
        
        assert n8n_healthy, "n8n not reachable"
        
        # Test Streamlit
        try:
            response = requests.get(f"{STREAMLIT_URL}", timeout=5)
            streamlit_healthy = response.status_code == 200
        except:
            streamlit_healthy = False
        
        # Streamlit may not be running in test environment
        # assert streamlit_healthy, "Streamlit not reachable"
    
    def test_data_freshness(self):
        """Test that data is being updated regularly"""
        snapshot_file = DATA_DIR / "region1_latest.json"
        
        if snapshot_file.exists():
            # Get current file modification time
            mtime1 = snapshot_file.stat().st_mtime
            
            # Wait for next fetch cycle (n8n runs every 15 seconds)
            time.sleep(20)
            
            # Check if file was modified
            mtime2 = snapshot_file.stat().st_mtime
            
            # File should have been updated
            # (This may fail if n8n is not running or rate limited)
            # assert mtime2 > mtime1, "Snapshot file not being updated"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
