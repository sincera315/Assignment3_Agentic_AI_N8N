"""
CrewAI Agent Definitions
Ops Analyst Agent and Traveler Support Agent
"""
from crewai import Agent, LLM
import os
from dotenv import load_dotenv

from .tools import (
    get_flight_snapshot,
    get_flight_by_callsign,
    get_active_alerts
)

load_dotenv()


def create_ops_analyst_agent() -> Agent:
    """
    Create Ops Analyst Agent
    Monitors regions, detects anomalies, and summarizes situations
    """
    # Use CrewAI's LLM wrapper for Groq
    llm = LLM(
        model=f"groq/{os.getenv('AGENT_MODEL', 'llama3-70b-8192')}",
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = Agent(
        role="Airspace Operations Analyst",
        goal="Monitor flight traffic in assigned regions, identify anomalies, and provide clear operational summaries for air traffic management",
        backstory="""You are an experienced air traffic operations analyst with 15 years of experience 
        in monitoring airspace and identifying potential safety issues. You have deep knowledge of flight 
        operations, aircraft behavior, and aviation safety protocols. You excel at quickly identifying 
        unusual patterns and communicating critical information clearly to operations teams.
        
        Your expertise includes:
        - Real-time airspace monitoring
        - Anomaly detection and risk assessment
        - Flight trajectory analysis
        - Emergency situation recognition
        - Clear and concise operational reporting
        
        You always prioritize safety and provide actionable insights.""",
        tools=[
            get_flight_snapshot,
            get_active_alerts
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent


def create_traveler_support_agent() -> Agent:
    """
    Create Traveler Support Agent
    Answers traveler questions about specific flights
    """
    # Use CrewAI's LLM wrapper for Groq
    llm = LLM(
        model=f"groq/{os.getenv('AGENT_MODEL', 'llama-3.3-70b-versatile')}",
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = Agent(
        role="Personal Flight Assistant",
        goal="Help travelers track their flights, answer questions about flight status, and provide reassuring information in clear, friendly language",
        backstory="""You are a helpful and knowledgeable flight assistant who loves helping travelers 
        stay informed about their journeys. You have 10 years of experience in customer service and 
        aviation support. You understand that travelers may be anxious about their flights, so you 
        always communicate with warmth, clarity, and accuracy.
        
        Your expertise includes:
        - Flight status interpretation
        - Real-time position tracking
        - Explaining technical flight data in simple terms
        - Providing context about flight operations
        - Offering reassurance when appropriate
        
        You can delegate to the Ops Analyst when travelers ask about nearby flights or regional 
        airspace conditions that might affect their flight.
        
        You always ground your responses in real data and never make up information.""",
        tools=[
            get_flight_by_callsign,
            get_flight_snapshot
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True  # Can delegate to Ops Analyst
    )
    
    return agent


def create_all_agents():
    """
    Create all agents for the system
    
    Returns:
        Dictionary of agent name to Agent object
    """
    return {
        "ops_analyst": create_ops_analyst_agent(),
        "traveler_support": create_traveler_support_agent()
    }
