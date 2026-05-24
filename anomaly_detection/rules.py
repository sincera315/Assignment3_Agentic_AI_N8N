"""
Anomaly Detection Rules
Configuration and rule definitions
"""
import json
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class AnomalyRule:
    """Base class for anomaly detection rules"""
    enabled: bool
    description: str
    severity: str


@dataclass
class LowSpeedAtAltitudeRule(AnomalyRule):
    """Rule for detecting low speed at high altitude"""
    velocity_threshold_ms: float
    altitude_threshold_m: float


@dataclass
class StationaryAircraftRule(AnomalyRule):
    """Rule for detecting stationary aircraft"""
    velocity_threshold_ms: float
    time_limit_seconds: int


@dataclass
class RapidAltitudeChangeRule(AnomalyRule):
    """Rule for detecting rapid altitude changes"""
    altitude_change_threshold_m: float
    time_window_seconds: int


@dataclass
class RapidDescentRule(AnomalyRule):
    """Rule for detecting rapid descent"""
    vertical_rate_threshold_ms: float
    altitude_minimum_m: float


@dataclass
class ExtremeVelocityRule(AnomalyRule):
    """Rule for detecting extreme velocities"""
    max_velocity_ms: float
    min_velocity_ms: float


@dataclass
class AltitudeBoundsRule(AnomalyRule):
    """Rule for detecting altitude outside normal bounds"""
    max_altitude_m: float
    min_altitude_m: float


@dataclass
class AnomalyRules:
    """Collection of all anomaly detection rules"""
    low_speed_at_altitude: LowSpeedAtAltitudeRule
    stationary_aircraft: StationaryAircraftRule
    rapid_altitude_change: RapidAltitudeChangeRule
    rapid_descent: RapidDescentRule
    extreme_velocity: ExtremeVelocityRule
    altitude_bounds: AltitudeBoundsRule
    alert_expiry: Dict[str, int]


def load_anomaly_rules(config_path: str) -> AnomalyRules:
    """
    Load anomaly rules from JSON configuration file
    
    Args:
        config_path: Path to thresholds.json file
        
    Returns:
        AnomalyRules object with all rules
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    rules_data = config.get("anomaly_rules", {})
    
    # Load each rule
    low_speed = rules_data.get("low_speed_at_altitude", {})
    low_speed_rule = LowSpeedAtAltitudeRule(
        enabled=low_speed.get("enabled", True),
        description=low_speed.get("description", ""),
        severity=low_speed.get("severity", "high"),
        velocity_threshold_ms=low_speed.get("velocity_threshold_ms", 50),
        altitude_threshold_m=low_speed.get("altitude_threshold_m", 8000)
    )
    
    stationary = rules_data.get("stationary_aircraft", {})
    stationary_rule = StationaryAircraftRule(
        enabled=stationary.get("enabled", True),
        description=stationary.get("description", ""),
        severity=stationary.get("severity", "medium"),
        velocity_threshold_ms=stationary.get("velocity_threshold_ms", 10),
        time_limit_seconds=stationary.get("time_limit_seconds", 120)
    )
    
    rapid_alt = rules_data.get("rapid_altitude_change", {})
    rapid_alt_rule = RapidAltitudeChangeRule(
        enabled=rapid_alt.get("enabled", True),
        description=rapid_alt.get("description", ""),
        severity=rapid_alt.get("severity", "high"),
        altitude_change_threshold_m=rapid_alt.get("altitude_change_threshold_m", 500),
        time_window_seconds=rapid_alt.get("time_window_seconds", 15)
    )
    
    rapid_desc = rules_data.get("rapid_descent", {})
    rapid_desc_rule = RapidDescentRule(
        enabled=rapid_desc.get("enabled", True),
        description=rapid_desc.get("description", ""),
        severity=rapid_desc.get("severity", "critical"),
        vertical_rate_threshold_ms=rapid_desc.get("vertical_rate_threshold_ms", -15),
        altitude_minimum_m=rapid_desc.get("altitude_minimum_m", 1000)
    )
    
    extreme_vel = rules_data.get("extreme_velocity", {})
    extreme_vel_rule = ExtremeVelocityRule(
        enabled=extreme_vel.get("enabled", True),
        description=extreme_vel.get("description", ""),
        severity=extreme_vel.get("severity", "medium"),
        max_velocity_ms=extreme_vel.get("max_velocity_ms", 350),
        min_velocity_ms=extreme_vel.get("min_velocity_ms", -10)
    )
    
    alt_bounds = rules_data.get("altitude_bounds", {})
    alt_bounds_rule = AltitudeBoundsRule(
        enabled=alt_bounds.get("enabled", True),
        description=alt_bounds.get("description", ""),
        severity=alt_bounds.get("severity", "low"),
        max_altitude_m=alt_bounds.get("max_altitude_m", 15000),
        min_altitude_m=alt_bounds.get("min_altitude_m", -100)
    )
    
    alert_expiry = config.get("alert_expiry", {
        "critical": 300,
        "high": 600,
        "medium": 900,
        "low": 1200
    })
    
    return AnomalyRules(
        low_speed_at_altitude=low_speed_rule,
        stationary_aircraft=stationary_rule,
        rapid_altitude_change=rapid_alt_rule,
        rapid_descent=rapid_desc_rule,
        extreme_velocity=extreme_vel_rule,
        altitude_bounds=alt_bounds_rule,
        alert_expiry=alert_expiry
    )


def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level
    
    Args:
        severity: Severity level (critical, high, medium, low)
        
    Returns:
        Color name or hex code
    """
    colors = {
        "critical": "#FF0000",  # Red
        "high": "#FF6600",      # Orange
        "medium": "#FFCC00",    # Yellow
        "low": "#00CC00"        # Green
    }
    return colors.get(severity.lower(), "#808080")  # Gray as default


def get_severity_emoji(severity: str) -> str:
    """
    Get emoji for severity level
    
    Args:
        severity: Severity level
        
    Returns:
        Emoji string
    """
    emojis = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "⚡",
        "low": "ℹ️"
    }
    return emojis.get(severity.lower(), "📋")
