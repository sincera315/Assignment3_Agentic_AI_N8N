"""
Anomaly Detection Module
Rule-based anomaly detector for flight data

NOTE: The primary anomaly detection runs in n8n workflows (Node 5).
This module provides standalone detection for testing and validation.
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from .rules import load_anomaly_rules

load_dotenv()

SNAPSHOTS_DIR = os.getenv("SNAPSHOTS_DIR", "./data/flight_snapshots")
ALERTS_DIR = os.getenv("ALERTS_DIR", "./data/alerts")
CONFIG_DIR = os.getenv("CONFIG_DIR", "./config")


class AnomalyDetector:
    """
    Detects anomalies in flight data based on configurable rules
    """
    
    def __init__(self, rules_config_path: Optional[str] = None):
        """
        Initialize anomaly detector
        
        Args:
            rules_config_path: Path to thresholds.json config file
        """
        if rules_config_path is None:
            rules_config_path = os.path.join(CONFIG_DIR, "thresholds.json")
        
        self.rules = load_anomaly_rules(rules_config_path)
        self.previous_snapshots: Dict[str, Dict] = {}
    
    def detect_anomalies(
        self,
        current_snapshot: Dict[str, Any],
        previous_snapshot: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in current snapshot
        
        Args:
            current_snapshot: Current flight snapshot
            previous_snapshot: Previous snapshot for comparison (optional)
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        flights = current_snapshot.get("flights", [])
        region = current_snapshot.get("region", "unknown")
        timestamp = current_snapshot.get("timestamp", 0)
        datetime_str = current_snapshot.get("datetime", "")
        
        # Build previous flight lookup
        prev_flight_map = {}
        if previous_snapshot and previous_snapshot.get("flights"):
            for flight in previous_snapshot["flights"]:
                icao24 = flight.get("icao24")
                if icao24:
                    prev_flight_map[icao24] = flight
        
        # Check each flight
        for flight in flights:
            # Check individual flight rules
            flight_anomalies = self._check_flight_rules(
                flight, 
                prev_flight_map.get(flight.get("icao24")),
                region,
                timestamp,
                datetime_str
            )
            anomalies.extend(flight_anomalies)
        
        return anomalies
    
    def _check_flight_rules(
        self,
        flight: Dict[str, Any],
        prev_flight: Optional[Dict[str, Any]],
        region: str,
        timestamp: int,
        datetime_str: str
    ) -> List[Dict[str, Any]]:
        """
        Check all rules for a single flight
        
        Returns:
            List of anomalies detected for this flight
        """
        anomalies = []
        
        icao24 = flight.get("icao24", "unknown")
        callsign = flight.get("callsign", "").strip() or icao24
        
        # Rule 1: Low speed at high altitude
        if self.rules.low_speed_at_altitude.enabled:
            velocity = flight.get("velocity")
            altitude = flight.get("baro_altitude")
            
            if velocity is not None and altitude is not None:
                if (velocity < self.rules.low_speed_at_altitude.velocity_threshold_ms and
                    altitude > self.rules.low_speed_at_altitude.altitude_threshold_m):
                    anomalies.append({
                        "type": "low_speed_at_altitude",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.low_speed_at_altitude.severity,
                        "details": f"Low speed {velocity:.1f} m/s at altitude {altitude:.0f}m",
                        "velocity": velocity,
                        "altitude": altitude,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_low_speed_{timestamp}"
                    })
        
        # Rule 2: Stationary aircraft
        if self.rules.stationary_aircraft.enabled:
            velocity = flight.get("velocity")
            on_ground = flight.get("on_ground", False)
            
            if velocity is not None and not on_ground:
                if velocity < self.rules.stationary_aircraft.velocity_threshold_ms:
                    anomalies.append({
                        "type": "stationary_aircraft",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.stationary_aircraft.severity,
                        "details": f"Nearly stationary at {velocity:.1f} m/s (not on ground)",
                        "velocity": velocity,
                        "on_ground": on_ground,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_stationary_{timestamp}"
                    })
        
        # Rule 3: Rapid altitude change (requires previous snapshot)
        if self.rules.rapid_altitude_change.enabled and prev_flight:
            current_alt = flight.get("baro_altitude")
            prev_alt = prev_flight.get("baro_altitude")
            
            if current_alt is not None and prev_alt is not None:
                alt_change = abs(current_alt - prev_alt)
                if alt_change > self.rules.rapid_altitude_change.altitude_change_threshold_m:
                    anomalies.append({
                        "type": "rapid_altitude_change",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.rapid_altitude_change.severity,
                        "details": f"Altitude changed by {alt_change:.0f}m",
                        "current_altitude": current_alt,
                        "previous_altitude": prev_alt,
                        "altitude_change": alt_change,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_altitude_change_{timestamp}"
                    })
        
        # Rule 4: Rapid descent
        if self.rules.rapid_descent.enabled:
            vertical_rate = flight.get("vertical_rate")
            altitude = flight.get("baro_altitude")
            
            if vertical_rate is not None and altitude is not None:
                if (vertical_rate < self.rules.rapid_descent.vertical_rate_threshold_ms and
                    altitude > self.rules.rapid_descent.altitude_minimum_m):
                    anomalies.append({
                        "type": "rapid_descent",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.rapid_descent.severity,
                        "details": f"Rapid descent at {vertical_rate:.1f} m/s",
                        "vertical_rate": vertical_rate,
                        "altitude": altitude,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_rapid_descent_{timestamp}"
                    })
        
        # Rule 5: Extreme velocity
        if self.rules.extreme_velocity.enabled:
            velocity = flight.get("velocity")
            
            if velocity is not None:
                if (velocity > self.rules.extreme_velocity.max_velocity_ms or
                    velocity < self.rules.extreme_velocity.min_velocity_ms):
                    anomalies.append({
                        "type": "extreme_velocity",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.extreme_velocity.severity,
                        "details": f"Extreme velocity: {velocity:.1f} m/s",
                        "velocity": velocity,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_extreme_velocity_{timestamp}"
                    })
        
        # Rule 6: Altitude bounds
        if self.rules.altitude_bounds.enabled:
            altitude = flight.get("baro_altitude")
            
            if altitude is not None:
                if (altitude > self.rules.altitude_bounds.max_altitude_m or
                    altitude < self.rules.altitude_bounds.min_altitude_m):
                    anomalies.append({
                        "type": "altitude_bounds",
                        "icao24": icao24,
                        "callsign": callsign,
                        "severity": self.rules.altitude_bounds.severity,
                        "details": f"Altitude {altitude:.0f}m outside normal bounds",
                        "altitude": altitude,
                        "timestamp": timestamp,
                        "datetime": datetime_str,
                        "region": region,
                        "alert_id": f"{icao24}_altitude_bounds_{timestamp}"
                    })
        
        return anomalies
    
    def process_snapshot_file(self, snapshot_path: str) -> Dict[str, Any]:
        """
        Process a snapshot file and detect anomalies
        
        Args:
            snapshot_path: Path to snapshot JSON file
            
        Returns:
            Snapshot with added anomaly information
        """
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
        
        region = snapshot.get("region", "unknown")
        
        # Get previous snapshot for this region
        prev_snapshot = self.previous_snapshots.get(region)
        
        # Detect anomalies
        anomalies = self.detect_anomalies(snapshot, prev_snapshot)
        
        # Add to snapshot
        snapshot["anomalies"] = anomalies
        snapshot["anomaly_count"] = len(anomalies)
        
        # Store as previous snapshot for next time
        self.previous_snapshots[region] = snapshot
        
        return snapshot


def save_alerts(anomalies: List[Dict[str, Any]], alerts_file: str = None):
    """
    Save anomalies to alerts file
    
    Args:
        anomalies: List of anomaly dictionaries
        alerts_file: Path to alerts file (default: from env)
    """
    if alerts_file is None:
        alerts_file = os.path.join(ALERTS_DIR, "active_alerts.json")
    
    # Load existing alerts
    existing_alerts = []
    if os.path.exists(alerts_file):
        try:
            with open(alerts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_alerts = data.get("alerts", [])
        except:
            pass
    
    # Combine with new anomalies (keep last 100)
    all_alerts = anomalies + existing_alerts
    all_alerts = all_alerts[:100]
    
    # Save
    alerts_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "alert_count": len(all_alerts),
        "alerts": all_alerts
    }
    
    os.makedirs(os.path.dirname(alerts_file), exist_ok=True)
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump(alerts_data, f, indent=2)


if __name__ == "__main__":
    # Example usage
    detector = AnomalyDetector()
    
    # Process all region snapshots
    for region in ["region1", "region2", "region3"]:
        snapshot_path = os.path.join(SNAPSHOTS_DIR, f"{region}_latest.json")
        if os.path.exists(snapshot_path):
            print(f"Processing {region}...")
            snapshot = detector.process_snapshot_file(snapshot_path)
            print(f"  Detected {snapshot['anomaly_count']} anomalies")
            
            if snapshot['anomaly_count'] > 0:
                save_alerts(snapshot['anomalies'])
