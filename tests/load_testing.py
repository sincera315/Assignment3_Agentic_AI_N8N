"""
Load Testing Script
Simulates concurrent users and stress tests the system
"""
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.crew_config import run_traveler_query, run_ops_analysis


class LoadTester:
    """Load testing for the Aviation Monitoring System"""
    
    def __init__(self):
        self.mcp_url = "http://localhost:8000"
        self.results = []
    
    def test_mcp_endpoint(self, region: str) -> dict:
        """Test MCP server endpoint performance"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.mcp_url}/mcp/tools/flights.list_region_snapshot",
                json={"region_name": region},
                timeout=10
            )
            
            elapsed = time.time() - start_time
            
            return {
                "success": response.status_code == 200,
                "elapsed": elapsed,
                "status_code": response.status_code
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "elapsed": elapsed,
                "error": str(e)
            }
    
    def test_agent_query(self, callsign: str) -> dict:
        """Test agent query performance"""
        start_time = time.time()
        
        try:
            result = run_traveler_query(callsign)
            elapsed = time.time() - start_time
            
            return {
                "success": result is not None and len(result) > 0,
                "elapsed": elapsed,
                "response_length": len(result) if result else 0
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "elapsed": elapsed,
                "error": str(e)
            }
    
    def test_concurrent_mcp_requests(self, num_requests: int = 50):
        """Test concurrent MCP server requests"""
        print(f"\n🔥 Testing {num_requests} concurrent MCP requests...")
        
        regions = ["region1", "region2", "region3"]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i in range(num_requests):
                region = regions[i % len(regions)]
                future = executor.submit(self.test_mcp_endpoint, region)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        # Calculate statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        elapsed_times = [r["elapsed"] for r in results if r["success"]]
        
        avg_time = sum(elapsed_times) / len(elapsed_times) if elapsed_times else 0
        max_time = max(elapsed_times) if elapsed_times else 0
        min_time = min(elapsed_times) if elapsed_times else 0
        
        print(f"   ✅ Successful: {successful}/{num_requests}")
        print(f"   ❌ Failed: {failed}/{num_requests}")
        print(f"   ⏱️  Avg Response Time: {avg_time:.3f}s")
        print(f"   ⏱️  Max Response Time: {max_time:.3f}s")
        print(f"   ⏱️  Min Response Time: {min_time:.3f}s")
        
        return {
            "test": "concurrent_mcp_requests",
            "total_requests": num_requests,
            "successful": successful,
            "failed": failed,
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time
        }
    
    def test_concurrent_agent_queries(self, num_queries: int = 20):
        """Test concurrent agent queries"""
        print(f"\n🤖 Testing {num_queries} concurrent agent queries...")
        
        test_callsigns = [f"TEST{i:03d}" for i in range(num_queries)]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for callsign in test_callsigns:
                future = executor.submit(self.test_agent_query, callsign)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        # Calculate statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        elapsed_times = [r["elapsed"] for r in results if r["success"]]
        
        avg_time = sum(elapsed_times) / len(elapsed_times) if elapsed_times else 0
        max_time = max(elapsed_times) if elapsed_times else 0
        min_time = min(elapsed_times) if elapsed_times else 0
        
        print(f"   ✅ Successful: {successful}/{num_queries}")
        print(f"   ❌ Failed: {failed}/{num_queries}")
        print(f"   ⏱️  Avg Response Time: {avg_time:.3f}s")
        print(f"   ⏱️  Max Response Time: {max_time:.3f}s")
        print(f"   ⏱️  Min Response Time: {min_time:.3f}s")
        
        return {
            "test": "concurrent_agent_queries",
            "total_queries": num_queries,
            "successful": successful,
            "failed": failed,
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time
        }
    
    def test_sustained_load(self, duration_seconds: int = 60, requests_per_second: int = 5):
        """Test sustained load over time"""
        print(f"\n⏱️  Testing sustained load ({duration_seconds}s at {requests_per_second} req/s)...")
        
        start_time = time.time()
        total_requests = 0
        successful = 0
        failed = 0
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Send batch of requests
            for _ in range(requests_per_second):
                result = self.test_mcp_endpoint("region1")
                total_requests += 1
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            
            # Sleep to maintain rate
            batch_elapsed = time.time() - batch_start
            if batch_elapsed < 1.0:
                time.sleep(1.0 - batch_elapsed)
        
        total_elapsed = time.time() - start_time
        actual_rps = total_requests / total_elapsed
        
        print(f"   📊 Total Requests: {total_requests}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Actual Rate: {actual_rps:.2f} req/s")
        print(f"   ⏱️  Duration: {total_elapsed:.1f}s")
        
        return {
            "test": "sustained_load",
            "duration": total_elapsed,
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "target_rps": requests_per_second,
            "actual_rps": actual_rps
        }
    
    def run_all_tests(self):
        """Run all load tests"""
        print("=" * 70)
        print("LOAD TESTING SUITE")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = []
        
        # Test 1: Concurrent MCP requests
        result1 = self.test_concurrent_mcp_requests(num_requests=50)
        all_results.append(result1)
        
        # Test 2: Concurrent agent queries (fewer due to LLM rate limits)
        result2 = self.test_concurrent_agent_queries(num_queries=10)
        all_results.append(result2)
        
        # Test 3: Sustained load
        result3 = self.test_sustained_load(duration_seconds=30, requests_per_second=5)
        all_results.append(result3)
        
        # Save results
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        for result in all_results:
            print(f"\n📊 {result['test']}")
            for key, value in result.items():
                if key != 'test':
                    print(f"   {key}: {value}")
        
        # Save to file
        output_file = Path("./tests/load_test_results.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": all_results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("\n" + "=" * 70)
        
        # Performance assessment
        print("\n🎯 PERFORMANCE ASSESSMENT")
        print("=" * 70)
        
        mcp_avg = result1["avg_time"]
        agent_avg = result2["avg_time"]
        sustained_success_rate = result3["successful"] / result3["total_requests"] * 100
        
        print(f"\nMCP Server Response Time: {mcp_avg:.3f}s")
        if mcp_avg < 2.0:
            print("   ✅ EXCELLENT (< 2s)")
        elif mcp_avg < 5.0:
            print("   ⚠️  ACCEPTABLE (< 5s)")
        else:
            print("   ❌ NEEDS IMPROVEMENT (> 5s)")
        
        print(f"\nAgent Response Time: {agent_avg:.3f}s")
        if agent_avg < 5.0:
            print("   ✅ EXCELLENT (< 5s)")
        elif agent_avg < 10.0:
            print("   ⚠️  ACCEPTABLE (< 10s)")
        else:
            print("   ❌ NEEDS IMPROVEMENT (> 10s)")
        
        print(f"\nSustained Load Success Rate: {sustained_success_rate:.1f}%")
        if sustained_success_rate > 95:
            print("   ✅ EXCELLENT (> 95%)")
        elif sustained_success_rate > 90:
            print("   ⚠️  ACCEPTABLE (> 90%)")
        else:
            print("   ❌ NEEDS IMPROVEMENT (< 90%)")
        
        print("\n" + "=" * 70)


def main():
    """Run load tests"""
    tester = LoadTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
