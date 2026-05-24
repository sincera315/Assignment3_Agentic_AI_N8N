"""
Anomaly Detection Package
Rule-based anomaly detection for flight data
"""
from .detector import AnomalyDetector, save_alerts
from .rules import (
    load_anomaly_rules,
    AnomalyRules,
    get_severity_color,
    get_severity_emoji
)

__version__ = "1.0.0"
__all__ = [
    "AnomalyDetector",
    "save_alerts",
    "load_anomaly_rules",
    "AnomalyRules",
    "get_severity_color",
    "get_severity_emoji"
]
