"""
CrewAI Task Definitions
Tasks for Ops Analyst and Traveler Support agents
"""
from crewai import Task
from typing import Dict, Any


def create_ops_analysis_task(agent, region: str) -> Task:
    """
    Create task for ops analyst to analyze a region
    
    Args:
        agent: Ops Analyst Agent
        region: Region to analyze (region1, region2, or region3)
        
    Returns:
        Task object
    """
    task = Task(
        description=f"""Analyze the current airspace situation in {region}.
        
        Your task:
        1. Get the latest flight snapshot for {region}
        2. Get all active alerts
        3. Identify any anomalies or concerning patterns
        4. Assess the overall situation
        5. Provide a clear operational summary
        
        Your summary should include:
        - Total number of flights currently tracked
        - Number and types of anomalies detected
        - Most critical cases (if any)
        - Overall airspace status assessment
        - Any recommended actions or areas of concern
        
        Be specific about flight callsigns and anomaly details.""",
        agent=agent,
        expected_output="""A comprehensive operational summary including:
        - Flight count
        - Anomaly summary with severity levels
        - Specific details about critical cases
        - Overall situation assessment
        - Recommendations (if needed)"""
    )
    
    return task


def create_traveler_query_task(agent, callsign: str, question: str = None) -> Task:
    """
    Create task for traveler support to answer flight query
    
    Args:
        agent: Traveler Support Agent
        callsign: Flight callsign to query
        question: Specific question from traveler (optional)
        
    Returns:
        Task object
    """
    if question:
        description = f"""A traveler is tracking flight {callsign} and has asked: "{question}"
        
        Your task:
        1. Find the flight using callsign {callsign}
        2. Get current flight details (position, altitude, speed, status)
        3. Answer the traveler's specific question based on real data
        4. Provide any additional helpful context
        
        If you need information about nearby flights or regional conditions, you can delegate 
        to the Ops Analyst agent.
        
        Always be friendly, clear, and reassuring while staying accurate."""
    else:
        description = f"""A traveler wants to know the current status of flight {callsign}.
        
        Your task:
        1. Find the flight using callsign {callsign}
        2. Get current flight details (position, altitude, speed, status)
        3. Provide a clear, friendly summary of the flight's current status
        4. Mention if there are any anomalies or concerns
        
        Present the information in a way that's easy for a non-technical traveler to understand."""
    
    task = Task(
        description=description,
        agent=agent,
        expected_output="""A friendly, clear response that:
        - Confirms the flight identification
        - Provides current position and status
        - Answers the specific question (if asked)
        - Includes relevant context
        - Is written in simple, non-technical language"""
    )
    
    return task


def create_nearby_issues_task(agent, callsign: str) -> Task:
    """
    Create task to check for issues near a specific flight
    Demonstrates A2A communication
    
    Args:
        agent: Traveler Support Agent (will delegate to Ops Analyst)
        callsign: Flight callsign
        
    Returns:
        Task object
    """
    task = Task(
        description=f"""A traveler wants to know if there are any issues with flights near {callsign}.
        
        Your task:
        1. Find flight {callsign} to determine its region
        2. Delegate to the Ops Analyst to get regional situation analysis
        3. Interpret the ops analysis in traveler-friendly language
        4. Let the traveler know if their flight area has any concerning activity
        
        Be honest but reassuring. If there are anomalies, explain what they mean without 
        causing unnecessary alarm.""",
        agent=agent,
        expected_output="""A response that:
        - Confirms the flight's location/region
        - Summarizes any nearby issues in simple terms
        - Provides context about what the anomalies mean
        - Reassures when appropriate"""
    )
    
    return task


def create_fleet_monitoring_task(agent, regions: list) -> Task:
    """
    Create task for comprehensive fleet monitoring across multiple regions
    
    Args:
        agent: Ops Analyst Agent
        regions: List of regions to monitor
        
    Returns:
        Task object
    """
    regions_str = ", ".join(regions)
    
    task = Task(
        description=f"""Perform comprehensive airspace monitoring across multiple regions: {regions_str}.
        
        Your task:
        1. Get snapshots for each region: {regions_str}
        2. Get all active alerts
        3. Compare anomaly levels across regions
        4. Identify any patterns or trends
        5. Provide executive summary
        
        Your report should include:
        - Region-by-region breakdown
        - Total flights across all regions
        - Comparative anomaly analysis
        - Highest priority items
        - Overall assessment""",
        agent=agent,
        expected_output="""An executive summary containing:
        - Multi-region statistics
        - Cross-region comparisons
        - Priority alerts and recommendations
        - Overall airspace health assessment"""
    )
    
    return task
