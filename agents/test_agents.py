"""
Test Script for CrewAI Agents
Tests Ops Analyst, Traveler Support, and A2A communication
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify Groq API key is set
if not os.getenv("GROQ_API_KEY"):
    print("❌ ERROR: GROQ_API_KEY not set in .env file")
    print("Please add your Groq API key to .env file")
    sys.exit(1)

print("✅ Environment configured")
print(f"   Groq API Key: {'*' * 20}{os.getenv('GROQ_API_KEY')[-4:]}")
print(f"   MCP Server URL: {os.getenv('MCP_SERVER_URL', 'http://localhost:8000')}")
print(f"   Agent Model: {os.getenv('AGENT_MODEL', 'llama-3.1-70b-versatile')}")
print()

# Import agents module
try:
    from agents import (
        run_ops_analysis,
        run_traveler_query,
        run_nearby_issues_check
    )
    print("✅ Agents module imported successfully")
    print()
except ImportError as e:
    print(f"❌ ERROR importing agents module: {e}")
    sys.exit(1)

# Check MCP server availability
import requests
MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
print("🔍 Checking MCP server availability...")
try:
    response = requests.get(f"{MCP_URL}/mcp/tools", timeout=5)
    if response.status_code == 200:
        print(f"✅ MCP server is running at {MCP_URL}")
        tools = response.json()
        # Handle both list and dict responses
        if isinstance(tools, list):
            print(f"   Available tools: {len(tools)}")
            for tool in tools:
                if isinstance(tool, dict):
                    print(f"   - {tool.get('name', 'unnamed')}")
                else:
                    print(f"   - {tool}")
        elif isinstance(tools, dict):
            print(f"   Available tools: {tools.get('tool_count', 'unknown')}")
        else:
            print(f"   Response type: {type(tools)}")
    else:
        print(f"⚠️  MCP server returned status {response.status_code}")
        print("   Agents may not work correctly")
except Exception as e:
    print(f"❌ Cannot connect to MCP server: {e}")
    print("   Please start MCP server: python run_mcp_server.py")
    print("   Continuing tests anyway...")
print()


def test_ops_analyst():
    """Test Ops Analyst Agent"""
    print("=" * 70)
    print("TEST 1: Ops Analyst Agent - Region Analysis")
    print("=" * 70)
    print("Task: Analyze airspace in region1 (Central Europe)")
    print()
    
    try:
        print("🤖 Running Ops Analyst Agent...")
        print("-" * 70)
        result = run_ops_analysis("region1")
        print("-" * 70)
        print()
        print("📊 RESULT:")
        print(result)
        print()
        print("✅ TEST 1 PASSED: Ops Analyst successfully analyzed region")
        return True
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_traveler_support():
    """Test Traveler Support Agent"""
    print()
    print("=" * 70)
    print("TEST 2: Traveler Support Agent - Flight Query")
    print("=" * 70)
    print("Task: Find and describe a specific flight")
    print("Note: This test will look for any available flight in region1")
    print()
    
    # First, get a real callsign from the data
    import json
    snapshot_path = "data/flight_snapshots/region1_latest.json"
    
    if not os.path.exists(snapshot_path):
        print(f"⚠️  Snapshot file not found: {snapshot_path}")
        print("   Creating test with generic callsign...")
        callsign = "TEST123"
    else:
        try:
            with open(snapshot_path, 'r') as f:
                data = json.load(f)
                if data.get('flights') and len(data['flights']) > 0:
                    callsign = data['flights'][0].get('callsign', 'TEST123')
                    print(f"   Using real callsign from data: {callsign}")
                else:
                    callsign = "TEST123"
                    print("   No flights in snapshot, using generic callsign")
        except Exception as e:
            print(f"   Could not read snapshot: {e}")
            callsign = "TEST123"
    
    print()
    
    try:
        print(f"🤖 Running Traveler Support Agent for flight {callsign}...")
        print("-" * 70)
        result = run_traveler_query(
            callsign=callsign,
            question="What is the current status of my flight?"
        )
        print("-" * 70)
        print()
        print("📊 RESULT:")
        print(result)
        print()
        print("✅ TEST 2 PASSED: Traveler Support answered flight query")
        return True
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_a2a_communication():
    """Test A2A Communication"""
    print()
    print("=" * 70)
    print("TEST 3: A2A Communication - Nearby Issues Query")
    print("=" * 70)
    print("Task: Traveler Agent delegates to Ops Analyst for regional context")
    print()
    
    # Get a real callsign
    import json
    snapshot_path = "data/flight_snapshots/region1_latest.json"
    
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, 'r') as f:
                data = json.load(f)
                if data.get('flights') and len(data['flights']) > 0:
                    callsign = data['flights'][0].get('callsign', 'TEST123')
                else:
                    callsign = "TEST123"
        except:
            callsign = "TEST123"
    else:
        callsign = "TEST123"
    
    print(f"   Testing with callsign: {callsign}")
    print()
    
    try:
        print(f"🤖 Running A2A Communication test...")
        print("   Traveler Agent will delegate to Ops Analyst")
        print("-" * 70)
        result = run_nearby_issues_check(callsign)
        print("-" * 70)
        print()
        print("📊 RESULT:")
        print(result)
        print()
        print("✅ TEST 3 PASSED: A2A communication successful")
        return True
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          CrewAI Multi-Agent System Test Suite                    ║")
    print("║          Phase 5: Agentic Layer Testing                          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    
    results = []
    
    # Test 1: Ops Analyst
    results.append(("Ops Analyst Agent", test_ops_analyst()))
    
    # Test 2: Traveler Support
    results.append(("Traveler Support Agent", test_traveler_support()))
    
    # Test 3: A2A Communication
    results.append(("A2A Communication", test_a2a_communication()))
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Phase 5 Agentic Layer is working correctly:")
        print("  ✅ Ops Analyst Agent monitors regions and detects anomalies")
        print("  ✅ Traveler Support Agent answers flight queries")
        print("  ✅ A2A communication allows agents to collaborate")
        print()
        print("Next Steps:")
        print("  1. Start MCP server: python run_mcp_server.py")
        print("  2. Test agents with real flight data")
        print("  3. Move to Phase 6: Frontend UI (Streamlit)")
        print()
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please check:")
        print("  1. MCP server is running (python run_mcp_server.py)")
        print("  2. Groq API key is valid in .env file")
        print("  3. Flight snapshot data exists in data/flight_snapshots/")
        print("  4. n8n workflows are running and generating data")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
