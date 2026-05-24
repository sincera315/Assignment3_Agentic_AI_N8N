"""
Test MCP Server Tools
Verify all MCP endpoints are working
"""
import sys
from pathlib import Path
import requests
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
import os

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")


def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_list_tools():
    """Test tools listing endpoint"""
    print("\n" + "=" * 60)
    print("Testing Tools List Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{MCP_SERVER_URL}/mcp/tools", timeout=5)
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📋 Found {len(data.get('tools', []))} tools:")
        for tool in data.get('tools', []):
            print(f"  - {tool.get('name')}: {tool.get('description')[:60]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_region_snapshot():
    """Test region snapshot tool"""
    print("\n" + "=" * 60)
    print("Testing Region Snapshot Tool")
    print("=" * 60)
    
    payload = {
        "name": "flights.list_region_snapshot",
        "arguments": {
            "region": "region1"
        }
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/flights.list_region_snapshot",
            json=payload,
            timeout=10
        )
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        
        if data.get('isError'):
            print(f"⚠️  Tool Error: {data.get('content', [{}])[0].get('text', 'Unknown')}")
        else:
            result_text = data.get('content', [{}])[0].get('text', '')
            if len(result_text) > 200:
                print(f"📄 Response: {result_text[:200]}...")
            else:
                print(f"📄 Response: {result_text}")
        
        return not data.get('isError')
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_callsign_search():
    """Test callsign search tool"""
    print("\n" + "=" * 60)
    print("Testing Callsign Search Tool")
    print("=" * 60)
    
    payload = {
        "name": "flights.get_by_callsign",
        "arguments": {
            "callsign": "TEST123"  # This will likely not exist, but tests the endpoint
        }
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/flights.get_by_callsign",
            json=payload,
            timeout=10
        )
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        
        result_text = data.get('content', [{}])[0].get('text', '')
        if len(result_text) > 200:
            print(f"📄 Response: {result_text[:200]}...")
        else:
            print(f"📄 Response: {result_text}")
        
        return True  # Even "not found" is a valid response
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_active_alerts():
    """Test active alerts tool"""
    print("\n" + "=" * 60)
    print("Testing Active Alerts Tool")
    print("=" * 60)
    
    payload = {
        "name": "alerts.list_active",
        "arguments": {}
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/alerts.list_active",
            json=payload,
            timeout=10
        )
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        
        if data.get('isError'):
            print(f"⚠️  Tool Error: {data.get('content', [{}])[0].get('text', 'Unknown')}")
        else:
            result_text = data.get('content', [{}])[0].get('text', '')
            if len(result_text) > 200:
                print(f"📄 Response: {result_text[:200]}...")
            else:
                print(f"📄 Response: {result_text}")
        
        return not data.get('isError')
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 MCP Server Test Suite")
    print("=" * 60)
    print(f"🎯 Target: {MCP_SERVER_URL}")
    
    results = {
        "Health Check": test_health(),
        "List Tools": test_list_tools(),
        "Region Snapshot": test_region_snapshot(),
        "Callsign Search": test_callsign_search(),
        "Active Alerts": test_active_alerts()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check MCP server logs.")
        return 1


if __name__ == "__main__":
    exit(main())
