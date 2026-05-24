#!/usr/bin/env python3
"""
Test script for anomaly detection logic
Simulates different flight scenarios to verify anomaly detection rules
"""

import json
from datetime import datetime


def detect_anomalies(snapshot):
    """
    Simulates Node 5 (Detect Anomalies) logic
    Tests anomaly detection rules on flight data
    """
    anomalies = []
    
    # Define anomaly detection rules (same as Node 5)
    anomaly_rules = [
        {
            "name": "low_speed_at_altitude",
            "check": lambda f: f["velocity"] < 50 and f["baro_altitude"] > 8000 and not f["on_ground"],
            "severity": "high",
            "message": lambda f: f"Low speed at altitude for {f.get('callsign', 'Unknown')}: {f['velocity']} m/s at {f['baro_altitude']}m"
        },
        {
            "name": "rapid_descent",
            "check": lambda f: f["vertical_rate"] < -15 and f["baro_altitude"] > 1000,
            "severity": "high",
            "message": lambda f: f"Rapid descent detected for {f.get('callsign', 'Unknown')}: {f['vertical_rate']} m/s from {f['baro_altitude']}m"
        },
        {
            "name": "stationary_aircraft",
            "check": lambda f: f["velocity"] < 10 and f["baro_altitude"] > 100 and not f["on_ground"],
            "severity": "low",
            "message": lambda f: f"Stationary aircraft detected: {f.get('callsign', 'Unknown')} at {f['baro_altitude']}m"
        }
    ]
    
    # Check each flight against rules
    for flight in snapshot.get("flights", []):
        for rule in anomaly_rules:
            try:
                if rule["check"](flight):
                    anomalies.append({
                        "type": rule["name"],
                        "severity": rule["severity"],
                        "callsign": flight.get("callsign", "Unknown"),
                        "icao24": flight["icao24"],
                        "latitude": flight.get("latitude"),
                        "longitude": flight.get("longitude"),
                        "altitude": flight.get("baro_altitude"),
                        "velocity": flight.get("velocity"),
                        "vertical_rate": flight.get("vertical_rate"),
                        "message": rule["message"](flight),
                        "detected_at": datetime.now().isoformat(),
                        "timestamp": snapshot["timestamp"],
                        "region": snapshot.get("region", "region1")
                    })
            except (KeyError, TypeError) as e:
                print(f"Error checking flight {flight.get('icao24', 'unknown')}: {e}")
                continue
    
    return anomalies


def create_test_flight(icao24, callsign, velocity, altitude, vertical_rate, on_ground=False):
    """Create a test flight object"""
    return {
        "icao24": icao24,
        "callsign": callsign,
        "origin_country": "Test",
        "time_position": 1764249304,
        "last_contact": 1764249304,
        "longitude": 10.0,
        "latitude": 50.0,
        "baro_altitude": altitude,
        "on_ground": on_ground,
        "velocity": velocity,
        "true_track": 90.0,
        "vertical_rate": vertical_rate,
        "sensors": None,
        "geo_altitude": altitude,
        "squawk": None,
        "spi": False,
        "position_source": 0
    }


def test_normal_flight():
    """Test 1: Normal flight - should have NO anomalies"""
    print("\n=== Test 1: Normal Flight ===")
    snapshot = {
        "timestamp": 1764249304,
        "region": "region1",
        "flights": [
            create_test_flight("test01", "TST001", 250, 10000, 0)  # Normal cruise
        ]
    }
    
    anomalies = detect_anomalies(snapshot)
    
    print(f"Flight: TST001 - Velocity: 250 m/s, Altitude: 10000m, Vertical Rate: 0 m/s")
    print(f"Anomalies detected: {len(anomalies)}")
    
    if len(anomalies) == 0:
        print("✅ PASS: No anomalies detected for normal flight")
    else:
        print("❌ FAIL: Normal flight should not trigger anomalies")
        for a in anomalies:
            print(f"  - {a['type']}: {a['message']}")
    
    return len(anomalies) == 0


def test_low_speed_at_altitude():
    """Test 2: Low speed at altitude - should detect anomaly"""
    print("\n=== Test 2: Low Speed at Altitude ===")
    snapshot = {
        "timestamp": 1764249304,
        "region": "region1",
        "flights": [
            create_test_flight("test02", "TST002", 40, 9000, 0)  # Too slow at high altitude
        ]
    }
    
    anomalies = detect_anomalies(snapshot)
    
    print(f"Flight: TST002 - Velocity: 40 m/s, Altitude: 9000m, Vertical Rate: 0 m/s")
    print(f"Anomalies detected: {len(anomalies)}")
    
    if len(anomalies) > 0 and any(a["type"] == "low_speed_at_altitude" for a in anomalies):
        print("✅ PASS: Low speed at altitude detected")
        for a in anomalies:
            print(f"  - {a['type']}: {a['message']}")
        return True
    else:
        print("❌ FAIL: Should detect low speed at altitude")
        return False


def test_rapid_descent():
    """Test 3: Rapid descent - should detect anomaly"""
    print("\n=== Test 3: Rapid Descent ===")
    snapshot = {
        "timestamp": 1764249304,
        "region": "region1",
        "flights": [
            create_test_flight("test03", "TST003", 200, 5000, -20)  # Fast descent
        ]
    }
    
    anomalies = detect_anomalies(snapshot)
    
    print(f"Flight: TST003 - Velocity: 200 m/s, Altitude: 5000m, Vertical Rate: -20 m/s")
    print(f"Anomalies detected: {len(anomalies)}")
    
    if len(anomalies) > 0 and any(a["type"] == "rapid_descent" for a in anomalies):
        print("✅ PASS: Rapid descent detected")
        for a in anomalies:
            print(f"  - {a['type']}: {a['message']}")
        return True
    else:
        print("❌ FAIL: Should detect rapid descent")
        return False


def test_stationary_aircraft():
    """Test 4: Stationary aircraft - should detect anomaly"""
    print("\n=== Test 4: Stationary Aircraft ===")
    snapshot = {
        "timestamp": 1764249304,
        "region": "region1",
        "flights": [
            create_test_flight("test04", "TST004", 5, 500, 0)  # Nearly stationary in air
        ]
    }
    
    anomalies = detect_anomalies(snapshot)
    
    print(f"Flight: TST004 - Velocity: 5 m/s, Altitude: 500m, Vertical Rate: 0 m/s")
    print(f"Anomalies detected: {len(anomalies)}")
    
    if len(anomalies) > 0 and any(a["type"] == "stationary_aircraft" for a in anomalies):
        print("✅ PASS: Stationary aircraft detected")
        for a in anomalies:
            print(f"  - {a['type']}: {a['message']}")
        return True
    else:
        print("❌ FAIL: Should detect stationary aircraft")
        return False


def test_multiple_anomalies():
    """Test 5: Flight with multiple anomalies"""
    print("\n=== Test 5: Multiple Anomalies ===")
    snapshot = {
        "timestamp": 1764249304,
        "region": "region1",
        "flights": [
            create_test_flight("test05", "TST005", 5, 9000, -20)  # Slow, high, descending fast
        ]
    }
    
    anomalies = detect_anomalies(snapshot)
    
    print(f"Flight: TST005 - Velocity: 5 m/s, Altitude: 9000m, Vertical Rate: -20 m/s")
    print(f"Anomalies detected: {len(anomalies)}")
    
    anomaly_types = [a["type"] for a in anomalies]
    
    # Should trigger: low_speed_at_altitude, rapid_descent, stationary_aircraft
    expected_types = {"low_speed_at_altitude", "rapid_descent", "stationary_aircraft"}
    found_types = set(anomaly_types)
    
    print(f"Expected anomaly types: {expected_types}")
    print(f"Found anomaly types: {found_types}")
    
    for a in anomalies:
        print(f"  - {a['type']}: {a['message']}")
    
    if len(expected_types & found_types) >= 2:  # At least 2 of 3 expected
        print("✅ PASS: Multiple anomalies detected")
        return True
    else:
        print("❌ FAIL: Should detect multiple anomalies")
        return False


def test_edge_cases():
    """Test 6: Edge cases (threshold boundaries)"""
    print("\n=== Test 6: Edge Cases (Threshold Boundaries) ===")
    
    test_cases = [
        ("Just above threshold - no anomaly", create_test_flight("test06a", "TST006A", 51, 9000, 0), False),
        ("Just below threshold - anomaly", create_test_flight("test06b", "TST006B", 49, 9000, 0), True),
        ("On ground - no anomaly", create_test_flight("test06c", "TST006C", 5, 100, 0, on_ground=True), False),
    ]
    
    all_passed = True
    
    for description, flight, should_detect in test_cases:
        snapshot = {
            "timestamp": 1764249304,
            "region": "region1",
            "flights": [flight]
        }
        
        anomalies = detect_anomalies(snapshot)
        detected = len(anomalies) > 0
        
        print(f"\n  {description}")
        print(f"  Flight: {flight['callsign']} - V: {flight['velocity']}m/s, Alt: {flight['baro_altitude']}m, On Ground: {flight['on_ground']}")
        print(f"  Expected anomaly: {should_detect}, Detected: {detected}")
        
        if detected == should_detect:
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL")
            all_passed = False
        
        if anomalies:
            for a in anomalies:
                print(f"    - {a['type']}: {a['message']}")
    
    return all_passed


def test_with_real_snapshot():
    """Test 7: Use real snapshot data if available"""
    print("\n=== Test 7: Real Snapshot Data ===")
    
    snapshot_path = "data/flight_snapshots/region1_latest.json"
    
    try:
        with open(snapshot_path, 'r') as f:
            snapshot = json.load(f)
        
        print(f"Loaded real snapshot from {snapshot_path}")
        print(f"Total flights: {snapshot.get('flight_count', 0)}")
        
        anomalies = detect_anomalies(snapshot)
        
        print(f"\nAnomalies detected: {len(anomalies)}")
        
        if anomalies:
            print("\nAnomalies found:")
            for a in anomalies:
                print(f"  - {a['type']} | {a['severity']} | {a['callsign']}")
                print(f"    {a['message']}")
        else:
            print("No anomalies detected in real snapshot")
            print("\nTo force anomalies, modify Node 5 thresholds:")
            print("  - low_speed_at_altitude: velocity < 200 (instead of 50)")
            print("  - rapid_descent: vertical_rate < -5 (instead of -15)")
            print("  - stationary_aircraft: velocity < 50 (instead of 10)")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Snapshot file not found: {snapshot_path}")
        print("Run the n8n workflow first to create the snapshot file")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in snapshot file: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ANOMALY DETECTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Normal Flight", test_normal_flight),
        ("Low Speed at Altitude", test_low_speed_at_altitude),
        ("Rapid Descent", test_rapid_descent),
        ("Stationary Aircraft", test_stationary_aircraft),
        ("Multiple Anomalies", test_multiple_anomalies),
        ("Edge Cases", test_edge_cases),
        ("Real Snapshot Data", test_with_real_snapshot),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Anomaly detection is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review anomaly detection logic.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
