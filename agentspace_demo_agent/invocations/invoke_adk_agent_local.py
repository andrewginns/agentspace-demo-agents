#!/usr/bin/env python3
"""
Test the ADK agent locally before deployment.
"""

from vertexai.preview import reasoning_engines
from agentspace_demo_agent.agents.adk_agent import root_agent
from agentspace_demo_agent.invocations.response_utils import (
    process_stream_response,
    display_response_parts,
)


def test_agent() -> None:
    """Test the agent locally with various queries.

    Raises:
        Exception: If there are issues during local agent testing.
    """
    test_queries = [
        "What's the weather in London?",
        "What time is it in Tokyo?",
        "Tell me about the weather in Paris",
        "What's the current time in Dubai?",
        "Give me weather for Singapore and time for Hong Kong",
    ]

    print("Testing ADK Agent locally...")
    print("=" * 60)

    # Create the app once for all tests
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Create a session for testing
    session = app.create_session(user_id="local_test_user")

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 60)

        try:
            stream_events = app.stream_query(
                user_id="local_test_user", session_id=session.id, message=query
            )
            response_parts = process_stream_response(stream_events)
            display_response_parts(response_parts)

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Local invocation with vertexai reasoning engine completed!")


if __name__ == "__main__":
    test_agent()
