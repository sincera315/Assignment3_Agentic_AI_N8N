"""
Validate Anomaly Detection
Tests the anomaly detection logic against real flight data.

NOTE: The n8n workflows (Node 5) handle primary anomaly detection.
This script validates that detection logic works correctly.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from anomaly_detection.detector import AnomalyDetector, save_alerts


def load_snapshot(region: str) -> dict:
    """Load snapshot file for a region"""
    snapshot_path = f"./data/flight_snapshots/{region}_latest.json"
    
    if not os.path.exists(snapshot_path):
        print(f"❌ Snapshot file not found: {snapshot_path}")
        print(f"   Ensure n8n workflows are active and collecting data")
        return None
    
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_detection():
    """Validate anomaly detection on real data"""
    print("=" * 70)
    print("  Anomaly Detection Validation")
    print("=" * 70)
    print()
    
    # Initialize detector
    print("Initializing detector...")
    detector = AnomalyDetector()
    print("✅ Detector initialized")
    print()
    
    # Test each region
    all_anomalies = []
    total_flights = 0
    
    for region in ["region1", "region2", "region3"]:
        print(f"📊 Processing {region}...")
        
        snapshot = load_snapshot(region)
        if not snapshot:
            continue
        
        flight_count = len(snapshot.get("flights", []))
        total_flights += flight_count
        print(f"   Loaded {flight_count} flights")
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(snapshot)
        all_anomalies.extend(anomalies)
        
        print(f"   Detected {len(anomalies)} anomalies")
        
        # Show anomaly breakdown
        if anomalies:
            anomaly_types = {}
            for anomaly in anomalies:
                atype = anomaly.get("type", "unknown")
                anomaly_types[atype] = anomaly_types.get(atype, 0) + 1
            
            for atype, count in sorted(anomaly_types.items()):
                print(f"     - {atype}: {count}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("  Detection Summary")
    print("=" * 70)
    print(f"Total flights analyzed: {total_flights}")
    print(f"Total anomalies detected: {len(all_anomalies)}")
    print()
    
    if all_anomalies:
        # Group by severity
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for anomaly in all_anomalies:
            severity = anomaly.get("severity", "low")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        print("Severity breakdown:")
        for severity in ["critical", "high", "medium", "low"]:
            count = by_severity.get(severity, 0)
            if count > 0:
                print(f"  🔴 {severity.upper()}: {count}" if severity == "critical" else
                      f"  🟠 {severity.upper()}: {count}" if severity == "high" else
                      f"  🟡 {severity.upper()}: {count}" if severity == "medium" else
                      f"  🟢 {severity.upper()}: {count}")
        print()
        
        # Show sample anomalies
        print("Sample anomalies (first 5):")
        for i, anomaly in enumerate(all_anomalies[:5]):
            print(f"\n  {i+1}. {anomaly['type'].upper()}")
            print(f"     Callsign: {anomaly['callsign']}")
            print(f"     Severity: {anomaly['severity']}")
            print(f"     Details: {anomaly['details']}")
            print(f"     Region: {anomaly['region']}")
        
        # Save alerts
        print()
        print("Saving alerts to data/alerts/active_alerts.json...")
        save_alerts(all_anomalies)
        print("✅ Alerts saved")
        
    else:
        print("✅ No anomalies detected - all flights operating normally")
    
    print()
    print("=" * 70)
    print("  Validation Complete")
    print("=" * 70)
    
    return len(all_anomalies) > 0


def test_specific_conditions():
    """Test specific anomaly conditions with synthetic data"""
    print()
    print("=" * 70)
    print("  Testing Specific Conditions")
    print("=" * 70)
    print()
    
    detector = AnomalyDetector()
    
    test_cases = [
        {
            "name": "Low speed at altitude",
            "flight": {
                "icao24": "test001",
                "callsign": "TEST001",
                "velocity": 40,  # Below 50 m/s
                "baro_altitude": 9000,  # Above 8000m
                "on_ground": False
            }
        },
        {
            "name": "Rapid descent",
            "flight": {
                "icao24": "test002",
                "callsign": "TEST002",
                "velocity": 200,
                "baro_altitude": 5000,
                "vertical_rate": -20,  # Below -15 m/s
                "on_ground": False
            }
        },
        {
            "name": "Stationary aircraft",
            "flight": {
                "icao24": "test003",
                "callsign": "TEST003",
                "velocity": 5,  # Below 10 m/s
                "baro_altitude": 3000,
                "on_ground": False
            }
        },
        {
            "name": "Normal flight (no anomaly)",
            "flight": {
                "icao24": "test004",
                "callsign": "TEST004",
                "velocity": 250,
                "baro_altitude": 10000,
                "vertical_rate": 0,
                "on_ground": False
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        # Create test snapshot
        snapshot = {
            "timestamp": int(datetime.utcnow().timestamp()),
            "datetime": datetime.utcnow().isoformat() + "Z",
            "region": "test",
            "flights": [test_case["flight"]]
        }
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(snapshot)
        
        if test_case['name'] == "Normal flight (no anomaly)":
            if len(anomalies) == 0:
                print("  ✅ Correctly detected no anomalies")
            else:
                print(f"  ❌ False positive: detected {len(anomalies)} anomalies")
        else:
            if len(anomalies) > 0:
                print(f"  ✅ Detected: {anomalies[0]['type']}")
            else:
                print(f"  ❌ Failed to detect anomaly")
        print()


if __name__ == "__main__":
    print()
    
    # Run validation on real data
    has_anomalies = validate_detection()
    
    # Run synthetic tests
    test_specific_conditions()
    
    print()
    print("📋 Next Steps:")
    print("   1. Check data/alerts/active_alerts.json for detected anomalies")
    print("   2. Test MCP server: curl http://localhost:8000/tools/alerts/active")
    print("   3. View alerts in n8n workflow execution logs")
    print()
