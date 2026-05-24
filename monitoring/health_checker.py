"""
System Health Checker
Monitors all services and provides status dashboard
"""
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class HealthChecker:
    """Monitor system health across all services"""
    
    def __init__(self):
        self.mcp_url = "http://localhost:8000"
        self.n8n_url = "http://localhost:5678"
        self.streamlit_url = "http://localhost:8501"
        self.data_dir = Path("./data/flight_snapshots")
        self.alerts_dir = Path("./data/alerts")
    
    def check_mcp_server(self) -> Dict[str, Any]:
        """Check MCP server health"""
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "🟢 Online",
                    "healthy": True,
                    "response_time": response.elapsed.total_seconds(),
                    "details": response.json()
                }
            else:
                return {
                    "status": "🔴 Error",
                    "healthy": False,
                    "details": f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "🔴 Offline",
                "healthy": False,
                "details": "Connection refused"
            }
        except Exception as e:
            return {
                "status": "🔴 Error",
                "healthy": False,
                "details": str(e)
            }
    
    def check_n8n(self) -> Dict[str, Any]:
        """Check n8n server health"""
        try:
            response = requests.get(self.n8n_url, timeout=5)
            if response.status_code == 200:
                return {
                    "status": "🟢 Online",
                    "healthy": True,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "🔴 Error",
                    "healthy": False,
                    "details": f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "🔴 Offline",
                "healthy": False,
                "details": "Connection refused"
            }
        except Exception as e:
            return {
                "status": "🔴 Error",
                "healthy": False,
                "details": str(e)
            }
    
    def check_streamlit(self) -> Dict[str, Any]:
        """Check Streamlit UI health"""
        try:
            response = requests.get(f"{self.streamlit_url}/_stcore/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "🟢 Online",
                    "healthy": True,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "🔴 Error",
                    "healthy": False,
                    "details": f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "🔴 Offline",
                "healthy": False,
                "details": "Connection refused"
            }
        except Exception as e:
            return {
                "status": "🔴 Error",
                "healthy": False,
                "details": str(e)
            }
    
    def check_data_pipeline(self) -> Dict[str, Any]:
        """Check if data pipeline is working"""
        status = {
            "status": "🟢 Operational",
            "healthy": True,
            "regions": {}
        }
        
        # Check each region
        for region in ["region1", "region2", "region3"]:
            file_path = self.data_dir / f"{region}_latest.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Get file age
                    mtime = file_path.stat().st_mtime
                    age_seconds = (datetime.now().timestamp() - mtime)
                    
                    flight_count = len(data.get('flights', []))
                    
                    region_status = {
                        "status": "🟢 Active",
                        "flights": flight_count,
                        "data_age_seconds": int(age_seconds),
                        "last_update": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Warn if data is stale (> 60 seconds)
                    if age_seconds > 60:
                        region_status["status"] = "🟡 Stale"
                        region_status["warning"] = f"Data is {int(age_seconds)}s old"
                    
                    status["regions"][region] = region_status
                    
                except Exception as e:
                    status["regions"][region] = {
                        "status": "🔴 Error",
                        "details": str(e)
                    }
                    status["healthy"] = False
            else:
                status["regions"][region] = {
                    "status": "🔴 Missing",
                    "details": "Snapshot file not found"
                }
                status["healthy"] = False
        
        # Overall status
        if not status["healthy"]:
            status["status"] = "🔴 Degraded"
        elif any(r.get("status") == "🟡 Stale" for r in status["regions"].values()):
            status["status"] = "🟡 Warning"
        
        return status
    
    def check_anomaly_detection(self) -> Dict[str, Any]:
        """Check anomaly detection system"""
        alerts_file = self.alerts_dir / "active_alerts.json"
        
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                
                alert_count = alerts_data.get('alert_count', 0)
                
                return {
                    "status": "🟢 Active",
                    "healthy": True,
                    "total_alerts": alert_count,
                    "details": f"{alert_count} active alerts"
                }
            except Exception as e:
                return {
                    "status": "🔴 Error",
                    "healthy": False,
                    "details": str(e)
                }
        else:
            return {
                "status": "🟡 No Data",
                "healthy": True,
                "details": "Alerts file not created yet"
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        print("=" * 70)
        print("SYSTEM HEALTH CHECK")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check MCP Server
        print("🔍 Checking MCP Server...")
        mcp_health = self.check_mcp_server()
        results["checks"]["mcp_server"] = mcp_health
        print(f"   Status: {mcp_health['status']}")
        if 'response_time' in mcp_health:
            print(f"   Response Time: {mcp_health['response_time']:.3f}s")
        print()
        
        # Check n8n
        print("🔍 Checking n8n...")
        n8n_health = self.check_n8n()
        results["checks"]["n8n"] = n8n_health
        print(f"   Status: {n8n_health['status']}")
        if 'response_time' in n8n_health:
            print(f"   Response Time: {n8n_health['response_time']:.3f}s")
        print()
        
        # Check Streamlit
        print("🔍 Checking Streamlit UI...")
        streamlit_health = self.check_streamlit()
        results["checks"]["streamlit"] = streamlit_health
        print(f"   Status: {streamlit_health['status']}")
        if 'response_time' in streamlit_health:
            print(f"   Response Time: {streamlit_health['response_time']:.3f}s")
        print()
        
        # Check Data Pipeline
        print("🔍 Checking Data Pipeline...")
        pipeline_health = self.check_data_pipeline()
        results["checks"]["data_pipeline"] = pipeline_health
        print(f"   Status: {pipeline_health['status']}")
        for region, region_data in pipeline_health.get("regions", {}).items():
            print(f"   {region}: {region_data['status']}")
            if 'flights' in region_data:
                print(f"      Flights: {region_data['flights']}")
                print(f"      Data Age: {region_data['data_age_seconds']}s")
        print()
        
        # Check Anomaly Detection
        print("🔍 Checking Anomaly Detection...")
        anomaly_health = self.check_anomaly_detection()
        results["checks"]["anomaly_detection"] = anomaly_health
        print(f"   Status: {anomaly_health['status']}")
        if 'total_alerts' in anomaly_health:
            print(f"   Total Alerts: {anomaly_health['total_alerts']}")
        print()
        
        # Overall System Health
        print("=" * 70)
        all_healthy = all(
            check.get("healthy", False) 
            for check in results["checks"].values()
        )
        
        if all_healthy:
            overall_status = "🟢 ALL SYSTEMS OPERATIONAL"
            results["overall_status"] = "healthy"
        else:
            overall_status = "🔴 SOME SYSTEMS DEGRADED"
            results["overall_status"] = "degraded"
        
        print(f"OVERALL: {overall_status}")
        print("=" * 70)
        
        return results


def main():
    """Run health checks"""
    checker = HealthChecker()
    results = checker.run_all_checks()
    
    # Save results to file
    output_file = Path("./monitoring/health_report.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Health report saved to: {output_file}")
    
    # Exit code based on health
    if results["overall_status"] == "healthy":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
