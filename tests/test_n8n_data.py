"""
Test n8n Data Availability
Check if n8n workflows are generating data
"""
import sys
from pathlib import Path
import json
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SNAPSHOTS_DIR = os.getenv("SNAPSHOTS_DIR", "./data/flight_snapshots")
ALERTS_DIR = os.getenv("ALERTS_DIR", "./data/alerts")


def check_directory(dir_path: str, dir_name: str) -> bool:
    """Check if directory exists"""
    print(f"\n{'=' * 60}")
    print(f"Checking {dir_name} Directory")
    print("=" * 60)
    
    if not os.path.exists(dir_path):
        print(f"❌ Directory not found: {dir_path}")
        print(f"💡 Tip: n8n workflows should create this automatically")
        return False
    
    print(f"✅ Directory exists: {dir_path}")
    return True


def check_snapshots():
    """Check flight snapshot files"""
    print(f"\n{'=' * 60}")
    print("Checking Flight Snapshots")
    print("=" * 60)
    
    if not os.path.exists(SNAPSHOTS_DIR):
        print(f"❌ Snapshots directory not found")
        return False
    
    regions = ["region1", "region2", "region3"]
    found_snapshots = 0
    
    for region in regions:
        filepath = os.path.join(SNAPSHOTS_DIR, f"{region}_latest.json")
        
        if os.path.exists(filepath):
            found_snapshots += 1
            
            # Get file info
            size = os.path.getsize(filepath)
            mtime = os.path.getmtime(filepath)
            age = datetime.now().timestamp() - mtime
            
            print(f"✅ {region}: {size:,} bytes, {age:.0f}s old")
            
            # Check content
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    flight_count = data.get('flight_count', 0)
                    anomaly_count = data.get('anomaly_count', 0)
                    print(f"   📊 {flight_count} flights, {anomaly_count} anomalies")
            except Exception as e:
                print(f"   ⚠️  Could not parse JSON: {e}")
        else:
            print(f"❌ {region}: not found")
    
    if found_snapshots == 0:
        print("\n⚠️  No snapshot files found")
        print("💡 Ensure n8n workflows are running and activated")
        return False
    
    print(f"\n✅ Found {found_snapshots}/3 region snapshots")
    return found_snapshots > 0


def check_alerts():
    """Check alerts file"""
    print(f"\n{'=' * 60}")
    print("Checking Active Alerts")
    print("=" * 60)
    
    if not os.path.exists(ALERTS_DIR):
        print(f"❌ Alerts directory not found")
        return False
    
    filepath = os.path.join(ALERTS_DIR, "active_alerts.json")
    
    if not os.path.exists(filepath):
        print(f"❌ active_alerts.json not found")
        print(f"💡 Alerts are created when anomalies are detected")
        return False
    
    # Get file info
    size = os.path.getsize(filepath)
    mtime = os.path.getmtime(filepath)
    age = datetime.now().timestamp() - mtime
    
    print(f"✅ active_alerts.json: {size:,} bytes, {age:.0f}s old")
    
    # Check content
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            alert_count = data.get('alert_count', 0)
            alerts = data.get('alerts', [])
            
            print(f"📊 {alert_count} active alerts")
            
            if alert_count > 0:
                # Show severity breakdown
                severity_counts = {}
                for alert in alerts:
                    sev = alert.get('severity', 'unknown')
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                print("📋 Severity breakdown:")
                for sev, count in severity_counts.items():
                    print(f"   - {sev}: {count}")
            
            return True
    except Exception as e:
        print(f"⚠️  Could not parse JSON: {e}")
        return False


def check_n8n_webhooks():
    """Test n8n webhook endpoints"""
    print(f"\n{'=' * 60}")
    print("Testing n8n Webhook Endpoints")
    print("=" * 60)
    
    try:
        import requests
        
        n8n_base = os.getenv("N8N_WEBHOOK_BASE", "http://localhost:5678/webhook")
        endpoints = [
            f"{n8n_base}/latest-region1",
            f"{n8n_base}/latest-region2",
            f"{n8n_base}/latest-region3",
            f"{n8n_base}/active-alerts"
        ]
        
        working = 0
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=3)
                if response.status_code == 200:
                    print(f"✅ {endpoint}")
                    working += 1
                else:
                    print(f"⚠️  {endpoint} - Status {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {endpoint} - Connection failed")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
        
        if working == 0:
            print("\n⚠️  No webhook endpoints responding")
            print("💡 Check if n8n is running: docker ps")
            print("💡 Import and activate snapshot_webhook_endpoints.json")
            return False
        
        print(f"\n✅ {working}/4 webhook endpoints working")
        return working > 0
        
    except ImportError:
        print("⚠️  'requests' library not available, skipping webhook tests")
        return None


def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("🧪 n8n Data Availability Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Directory checks
    results["Snapshots Directory"] = check_directory(SNAPSHOTS_DIR, "Snapshots")
    results["Alerts Directory"] = check_directory(ALERTS_DIR, "Alerts")
    
    # File checks
    results["Flight Snapshots"] = check_snapshots()
    results["Active Alerts"] = check_alerts()
    
    # Webhook checks
    webhook_result = check_n8n_webhooks()
    if webhook_result is not None:
        results["Webhook Endpoints"] = webhook_result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Data is available.")
        return 0
    elif passed > 0:
        print("⚠️  Some checks failed. System partially working.")
        print("\n💡 Troubleshooting:")
        print("  1. Verify n8n is running: docker ps")
        print("  2. Check n8n logs: docker logs n8n")
        print("  3. Ensure workflows are activated in n8n UI")
        print("  4. Wait 30 seconds for first execution")
        return 1
    else:
        print("❌ All checks failed. n8n may not be running.")
        print("\n💡 Quick fix:")
        print("  docker-compose up -d")
        print("  # Then import and activate workflows in http://localhost:5678")
        return 2


if __name__ == "__main__":
    exit(main())
