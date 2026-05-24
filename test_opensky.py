# Test OpenSky API Response
# Quick diagnostic to see what's happening

import requests
import json
from datetime import datetime

print("=" * 70)
print("OpenSky API Diagnostic Test")
print("=" * 70)
print()

# Test with broader region (all of Europe)
regions = [
    {
        "name": "Central Europe (region1)",
        "params": {"lamin": 45.0, "lomin": 5.0, "lamax": 55.0, "lomax": 15.0}
    },
    {
        "name": "North Atlantic (region2)",
        "params": {"lamin": 48.0, "lomin": -10.0, "lamax": 60.0, "lomax": 2.0}
    },
    {
        "name": "Middle East (region3)",
        "params": {"lamin": 35.0, "lomin": 25.0, "lamax": 42.0, "lomax": 45.0}
    },
    {
        "name": "BROAD TEST - All of Europe",
        "params": {"lamin": 35.0, "lomin": -10.0, "lamax": 60.0, "lomax": 45.0}
    }
]

for region in regions:
    print(f"\n📍 Testing: {region['name']}")
    print(f"   Bbox: {region['params']}")
    
    try:
        url = "https://opensky-network.org/api/states/all"
        response = requests.get(url, params=region['params'], timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            states = data.get('states', [])
            flight_count = len(states) if states else 0
            
            print(f"   ✅ Flights found: {flight_count}")
            
            if flight_count > 0:
                print(f"   Sample flights:")
                for state in states[:3]:  # Show first 3
                    callsign = (state[1] or 'UNKNOWN').strip()
                    lat = state[6]
                    lon = state[5]
                    alt = state[7]
                    print(f"      - {callsign}: lat={lat}, lon={lon}, alt={alt}m")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print()
print("=" * 70)
print("Diagnostic Complete")
print("=" * 70)
print()

# Test without bounding box (global)
print("\n🌍 Testing GLOBAL query (no bbox filter)...")
try:
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        states = data.get('states', [])
        flight_count = len(states) if states else 0
        
        print(f"✅ Global flights: {flight_count}")
        if flight_count == 0:
            print("⚠️  OpenSky API is returning ZERO flights globally!")
            print("   Possible reasons:")
            print("   1. API is down or in maintenance")
            print("   2. Rate limiting (anonymous users limited)")
            print("   3. Network/firewall blocking")
    else:
        print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("💡 Recommendations:")
print("   1. If ALL queries return 0 flights → OpenSky API issue")
print("   2. If GLOBAL returns flights but regions don't → Check bbox coordinates")
print("   3. If rate limited → Sign up for OpenSky account")
print()
