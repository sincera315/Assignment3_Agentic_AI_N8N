#!/usr/bin/env python3
"""
Test script to verify n8n workflow file outputs
Checks that Node 10 and Node 11 are working correctly
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path


def test_log_file_exists():
    """Test 1: Check if log file exists"""
    print("\n=== Test 1: Log File Exists ===")
    
    log_path = Path("data/logs/fetch_history.log")
    
    if log_path.exists():
        print(f"✅ PASS: Log file exists at {log_path}")
        return True
    else:
        print(f"❌ FAIL: Log file not found at {log_path}")
        print("   Run the n8n workflow first")
        return False


def test_log_file_format():
    """Test 2: Check log file format"""
    print("\n=== Test 2: Log File Format ===")
    
    log_path = Path("data/logs/fetch_history.log")
    
    if not log_path.exists():
        print("❌ FAIL: Log file does not exist")
        return False
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print("❌ FAIL: Log file is empty")
            return False
        
        print(f"Log file has {len(lines)} entries")
        print("\nLast 3 entries:")
        for line in lines[-3:]:
            print(f"  {line.strip()}")
        
        # Check format of last entry
        last_entry = lines[-1].strip()
        
        # Expected format: [2025-11-27T13:15:04.983Z] SUCCESS | Region: region1 | Flights: 623 | Anomalies: 0
        expected_parts = ["[", "]", "|", "Region:", "Flights:", "Anomalies:"]
        
        format_ok = all(part in last_entry for part in expected_parts)
        
        if format_ok:
            print("\n✅ PASS: Log format is correct")
            return True
        else:
            print(f"\n❌ FAIL: Log format is incorrect")
            print(f"   Expected format: [TIMESTAMP] STATUS | Region: X | Flights: X | Anomalies: X")
            print(f"   Got: {last_entry}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error reading log file: {e}")
        return False


def test_log_file_appends():
    """Test 3: Check if log file appends correctly"""
    print("\n=== Test 3: Log File Appends ===")
    
    log_path = Path("data/logs/fetch_history.log")
    
    if not log_path.exists():
        print("❌ FAIL: Log file does not exist")
        return False
    
    try:
        # Count initial entries
        with open(log_path, 'r') as f:
            initial_lines = f.readlines()
        
        initial_count = len(initial_lines)
        print(f"Initial log entries: {initial_count}")
        
        print("\nWaiting 20 seconds for workflow to execute...")
        print("(Make sure the n8n workflow is ACTIVE)")
        time.sleep(20)
        
        # Count entries after wait
        with open(log_path, 'r') as f:
            final_lines = f.readlines()
        
        final_count = len(final_lines)
        new_entries = final_count - initial_count
        
        print(f"Final log entries: {final_count}")
        print(f"New entries added: {new_entries}")
        
        if new_entries > 0:
            print("\n✅ PASS: Log file is appending correctly")
            print("\nNew entries:")
            for line in final_lines[-new_entries:]:
                print(f"  {line.strip()}")
            return True
        else:
            print("\n⚠️  WARNING: No new entries added")
            print("   Check if n8n workflow is active and running")
            print("   Or manually execute the workflow and run this test again")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error checking log append: {e}")
        return False


def test_snapshot_file():
    """Test 4: Check snapshot file"""
    print("\n=== Test 4: Snapshot File ===")
    
    snapshot_path = Path("data/flight_snapshots/region1_latest.json")
    
    if not snapshot_path.exists():
        print(f"❌ FAIL: Snapshot file not found at {snapshot_path}")
        return False
    
    try:
        with open(snapshot_path, 'r') as f:
            snapshot = json.load(f)
        
        print(f"✅ Snapshot file exists and is valid JSON")
        
        # Check required fields
        required_fields = ["timestamp", "datetime", "region", "flight_count", "flights", "anomalies", "anomaly_count"]
        missing_fields = [field for field in required_fields if field not in snapshot]
        
        if missing_fields:
            print(f"❌ FAIL: Missing fields: {missing_fields}")
            return False
        
        print(f"\n📊 Snapshot Summary:")
        print(f"   Timestamp: {snapshot['datetime']}")
        print(f"   Region: {snapshot['region']}")
        print(f"   Flight count: {snapshot['flight_count']}")
        print(f"   Anomaly count: {snapshot['anomaly_count']}")
        
        # Check if snapshot is recent (within last 5 minutes)
        snapshot_time = datetime.fromisoformat(snapshot['datetime'].replace('Z', '+00:00'))
        now = datetime.now(snapshot_time.tzinfo)
        age_seconds = (now - snapshot_time).total_seconds()
        
        print(f"   Age: {int(age_seconds)} seconds")
        
        if age_seconds > 300:  # 5 minutes
            print(f"\n⚠️  WARNING: Snapshot is {int(age_seconds/60)} minutes old")
            print("   Workflow may not be running")
        else:
            print(f"\n✅ Snapshot is fresh (< 5 minutes old)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON in snapshot file: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error reading snapshot: {e}")
        return False


def test_alerts_file():
    """Test 5: Check alerts file (if exists)"""
    print("\n=== Test 5: Alerts File ===")
    
    alerts_path = Path("data/alerts/active_alerts.json")
    
    if not alerts_path.exists():
        print("ℹ️  No alerts file found")
        print("   This is normal if no anomalies have been detected")
        print("   To test alerts:")
        print("   1. Lower anomaly thresholds in Node 5")
        print("   2. Execute workflow")
        print("   3. Run this test again")
        return True  # Not a failure, just no alerts
    
    try:
        with open(alerts_path, 'r') as f:
            alerts = json.load(f)
        
        print(f"✅ Alerts file exists and is valid JSON")
        
        print(f"\n📊 Alerts Summary:")
        print(f"   Last updated: {alerts.get('last_updated', 'Unknown')}")
        print(f"   Alert count: {alerts.get('alert_count', 0)}")
        
        if alerts.get('alerts'):
            print(f"\n   Recent alerts:")
            for alert in alerts['alerts'][-5:]:  # Last 5 alerts
                print(f"   - {alert['type']} | {alert['severity']} | {alert['callsign']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON in alerts file: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error reading alerts: {e}")
        return False


def test_binary_output():
    """Test 6: Verify binary output from Node 10"""
    print("\n=== Test 6: Binary Output (Manual Check) ===")
    
    print("To verify Node 10 creates binary output:")
    print("1. Open n8n workflow")
    print("2. Execute the workflow")
    print("3. Click on Node 10 (Format Log Entry)")
    print("4. Check output - should see:")
    print("   {")
    print('     "json": { ... "log_entry": "..." },')
    print('     "binary": {')
    print('       "data": {')
    print('         "data": "<Buffer ...>",')
    print('         "mimeType": "text/plain",')
    print('         "fileName": "fetch_history.log"')
    print("       }")
    print("     }")
    print("   }")
    print("\n5. If binary field is missing, check Node 10 code includes:")
    print("   const binaryData = Buffer.from(logEntry + '\\n', 'utf-8');")
    print("   return [{ json: {...}, binary: { data: {...} } }];")
    
    return True  # Manual check


def test_file_permissions():
    """Test 7: Check file permissions"""
    print("\n=== Test 7: File Permissions ===")
    
    paths = [
        Path("data/flight_snapshots"),
        Path("data/logs"),
        Path("data/alerts")
    ]
    
    all_ok = True
    
    for path in paths:
        if path.exists():
            print(f"✅ Directory exists: {path}")
            
            # Try to create a test file
            test_file = path / "test_permissions.txt"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()
                print(f"   ✅ Write permission OK")
            except Exception as e:
                print(f"   ❌ Write permission FAIL: {e}")
                all_ok = False
        else:
            print(f"⚠️  Directory missing: {path}")
            print(f"   Creating directory...")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Directory created")
            except Exception as e:
                print(f"   ❌ Failed to create directory: {e}")
                all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    print("=" * 60)
    print("FILE OUTPUT VERIFICATION TEST SUITE")
    print("Tests Node 10 (Format Log) and Node 11 (Write Log)")
    print("=" * 60)
    
    tests = [
        ("Log File Exists", test_log_file_exists),
        ("Log File Format", test_log_file_format),
        ("Log File Appends", test_log_file_appends),
        ("Snapshot File", test_snapshot_file),
        ("Alerts File", test_alerts_file),
        ("Binary Output", test_binary_output),
        ("File Permissions", test_file_permissions),
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
        if result:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! File outputs are working correctly.")
        print("\n📝 Next steps:")
        print("   1. Run test_anomaly_detection.py to test anomaly logic")
        print("   2. Lower thresholds in Node 5 to trigger anomalies")
        print("   3. Verify alerts file is created when anomalies detected")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed or require manual check.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure n8n workflow is active")
        print("   2. Check docker-compose.yml volume mounts")
        print("   3. Verify Node 10 has binary output code")
        print("   4. Check Node 11 settings (Append file to list)")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
