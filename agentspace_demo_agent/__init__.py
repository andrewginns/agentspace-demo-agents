"""App package for ADK agent deployment."""

# Import from the new agent.py file for adk web compatibility
from . import agent
from agentspace_demo_agent.agents.adk_agent import root_agent

__all__ = ["root_agent", "agent"]
