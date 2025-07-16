#!/usr/bin/env python3
"""
Test the ADK agent deployed on Agent Engine.
"""

import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv
from agentspace_demo_agent.invocations.response_utils import (
    process_stream_response,
    display_response_parts,
)

load_dotenv()

# Load environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
ADK_DEPLOYMENT_ID = os.getenv("ADK_DEPLOYMENT_ID")


def test_deployed_agent(agent_resource_name: str) -> None:
    """Test the deployed agent with various queries.

    Args:
        agent_resource_name: The resource name of the deployed agent to test.

    Raises:
        Exception: If there are issues connecting to or testing the deployed agent.
    """

    test_queries = [
        "What's the weather in London?",
        "What time is it in Tokyo?",
        "Tell me about the weather in Paris",
        "What's the current time in Dubai?",
        "Give me weather for Singapore and time for Hong Kong",
    ]

    print("Testing ADK Agent on Agent Engine...")
    print("=" * 60)
    print(f"Agent Resource: {agent_resource_name}")
    print("=" * 60)

    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    try:
        # Get the deployed agent
        agent = agent_engines.get(agent_resource_name)
        print("✓ Successfully connected to deployed agent")

        # Create a session for testing
        session = agent.create_session(user_id="test_user")
        print(f"✓ Session created: {session['id']}")

    except Exception as e:
        print(f"✗ Error connecting to deployed agent: {e}")
        return

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 60)

        try:
            stream_events = agent.stream_query(
                user_id="test_user", session_id=session["id"], message=query
            )
            response_parts = process_stream_response(stream_events)
            display_response_parts(response_parts)

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Deployed agent testing completed!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test deployed ADK agent")
    
    # Construct default resource name from environment variables
    default_resource_name = None
    if PROJECT_ID and LOCATION and ADK_DEPLOYMENT_ID:
        default_resource_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ADK_DEPLOYMENT_ID}"
    
    parser.add_argument(
        "--id",
        type=str,
        help="Agent resource ID (full resource name)",
        default=default_resource_name,
    )
    args = parser.parse_args()

    if not args.id:
        print("Error: No agent resource ID provided.")
        print("Either provide --id argument or ensure ADK_DEPLOYMENT_ID is set in .env file")
        exit(1)
    
    test_deployed_agent(args.id)
