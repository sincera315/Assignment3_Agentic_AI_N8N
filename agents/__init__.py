"""
Agents Package
CrewAI-based multi-agent system for airspace monitoring
"""
from .agents import (
    create_ops_analyst_agent,
    create_traveler_support_agent,
    create_all_agents
)
from .tasks import (
    create_ops_analysis_task,
    create_traveler_query_task,
    create_nearby_issues_task
)
from .crew_config import (
    create_ops_crew,
    create_traveler_crew,
    create_a2a_crew,
    run_ops_analysis,
    run_traveler_query,
    run_nearby_issues_check
)
from .tools import (
    get_flight_snapshot,
    get_flight_by_callsign,
    get_active_alerts
)

__version__ = "1.0.0"
__all__ = [
    # Agents
    "create_ops_analyst_agent",
    "create_traveler_support_agent",
    "create_all_agents",
    # Tasks
    "create_ops_analysis_task",
    "create_traveler_query_task",
    "create_nearby_issues_task",
    # Crew
    "create_ops_crew",
    "create_traveler_crew",
    "create_a2a_crew",
    "run_ops_analysis",
    "run_traveler_query",
    "run_nearby_issues_check",
    # Tools
    "get_flight_snapshot",
    "get_flight_by_callsign",
    "get_active_alerts"
]
