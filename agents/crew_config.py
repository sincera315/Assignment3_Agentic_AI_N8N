"""
CrewAI Crew Configuration
Sets up the crew of agents for different operational modes
"""
from crewai import Crew, Process
from typing import Dict, Any

from .agents import create_ops_analyst_agent, create_traveler_support_agent
from .tasks import (
    create_ops_analysis_task,
    create_traveler_query_task,
    create_nearby_issues_task,
    create_fleet_monitoring_task
)


def create_ops_crew(region: str) -> Crew:
    """
    Create crew for operations mode
    Single agent analyzing a region
    
    Args:
        region: Region to analyze
        
    Returns:
        Crew object
    """
    ops_agent = create_ops_analyst_agent()
    task = create_ops_analysis_task(ops_agent, region)
    
    crew = Crew(
        agents=[ops_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


def create_traveler_crew(callsign: str, question: str = None) -> Crew:
    """
    Create crew for traveler mode
    Single agent answering traveler question
    
    Args:
        callsign: Flight callsign
        question: Optional specific question
        
    Returns:
        Crew object
    """
    traveler_agent = create_traveler_support_agent()
    task = create_traveler_query_task(traveler_agent, callsign, question)
    
    crew = Crew(
        agents=[traveler_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


def create_a2a_crew(callsign: str) -> Crew:
    """
    Create crew demonstrating A2A communication
    Traveler agent delegates to Ops agent
    
    Args:
        callsign: Flight callsign
        
    Returns:
        Crew object
    """
    # Create both agents
    ops_agent = create_ops_analyst_agent()
    traveler_agent = create_traveler_support_agent()
    
    # Create task that requires delegation
    task = create_nearby_issues_task(traveler_agent, callsign)
    
    crew = Crew(
        agents=[traveler_agent, ops_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


def create_multi_region_crew(regions: list) -> Crew:
    """
    Create crew for multi-region analysis
    
    Args:
        regions: List of regions to analyze
        
    Returns:
        Crew object
    """
    ops_agent = create_ops_analyst_agent()
    task = create_fleet_monitoring_task(ops_agent, regions)
    
    crew = Crew(
        agents=[ops_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


def run_ops_analysis(region: str) -> str:
    """
    Run operations analysis for a region
    
    Args:
        region: Region identifier
        
    Returns:
        Analysis result as string
    """
    crew = create_ops_crew(region)
    result = crew.kickoff()
    return str(result)


def run_traveler_query(callsign: str, question: str = None) -> str:
    """
    Run traveler query
    
    Args:
        callsign: Flight callsign
        question: Optional question
        
    Returns:
        Response as string
    """
    crew = create_traveler_crew(callsign, question)
    result = crew.kickoff()
    return str(result)


def run_nearby_issues_check(callsign: str) -> str:
    """
    Check for issues near a flight (A2A demo)
    
    Args:
        callsign: Flight callsign
        
    Returns:
        Response as string
    """
    crew = create_a2a_crew(callsign)
    result = crew.kickoff()
    return str(result)
