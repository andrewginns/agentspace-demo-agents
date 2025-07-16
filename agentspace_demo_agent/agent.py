"""
ADK Agent for adk web compatibility.

This file exposes the root_agent at the package level so that 'adk web' can discover it.
"""

# Import the root_agent from the existing implementation
from agentspace_demo_agent.agents.adk_agent import root_agent

# Expose root_agent at module level for adk web discovery
__all__ = ["root_agent"]
