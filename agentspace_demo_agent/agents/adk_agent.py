import os
import vertexai
import datetime
import uuid
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Get configuration from environment
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

# Initialize Vertex AI with validated configuration
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city: The name of the city for which to retrieve the weather report.

    Returns:
        A dictionary containing status and result or error message.
    """
    # Mock weather data for demonstration
    # In production, this would call a real weather API
    mock_weather_data = {
        "new york": "sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit)",
        "london": "cloudy with a temperature of 15 degrees Celsius (59 degrees Fahrenheit)",
        "tokyo": "clear with a temperature of 28 degrees Celsius (82 degrees Fahrenheit)",
        "paris": "rainy with a temperature of 18 degrees Celsius (64 degrees Fahrenheit)",
        "sydney": "partly cloudy with a temperature of 22 degrees Celsius (72 degrees Fahrenheit)",
        "los angeles": "sunny with a temperature of 26 degrees Celsius (79 degrees Fahrenheit)",
        "chicago": "windy with a temperature of 20 degrees Celsius (68 degrees Fahrenheit)",
        "singapore": "humid with a temperature of 30 degrees Celsius (86 degrees Fahrenheit)",
        "dubai": "hot and sunny with a temperature of 35 degrees Celsius (95 degrees Fahrenheit)",
        "hong kong": "warm with a temperature of 27 degrees Celsius (81 degrees Fahrenheit)",
    }

    city_lower = city.lower()
    if city_lower in mock_weather_data:
        return {
            "status": "success",
            "report": f"The weather in {city} is {mock_weather_data[city_lower]}.",
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city for which to retrieve the current time.

    Returns:
        A dictionary containing status and result or error message.
    """
    # Timezone mapping for major cities
    city_timezones = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris",
        "sydney": "Australia/Sydney",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "singapore": "Asia/Singapore",
        "dubai": "Asia/Dubai",
        "hong kong": "Asia/Hong_Kong",
    }

    city_lower = city.lower()
    if city_lower in city_timezones:
        tz_identifier = city_timezones[city_lower]
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = (
            f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
        )
        return {"status": "success", "report": report}
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}.",
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="""You are a helpful agent who can answer user questions about the time and weather in a city.
    
    Currently supported cities: New York, London, Tokyo, Paris, Sydney, Los Angeles, 
    Chicago, Singapore, Dubai, and Hong Kong.
    
    Be friendly and conversational in your responses.""",
    tools=[get_weather, get_current_time],
)


async def main() -> None:
    """Run demo queries to test the ADK agent functionality."""
    # Use Runner approach
    session_service = InMemorySessionService()

    # Create the runner
    runner = Runner(
        app_name="native_adk_agent_tools",
        agent=root_agent,
        session_service=session_service,
    )

    # Run demo queries
    print("Running ADK Agent Demo...")
    print("=" * 50)

    # Demo queries
    demo_queries = [
        "What's the weather like in New York?",
        "What time is it in Tokyo?",
        "Tell me the weather in London and the time in Paris.",
        "What's the current time in Singapore?",
    ]

    for query in demo_queries:
        print(f"\n{'=' * 50}")
        print(f"Query: {query}")
        print("-" * 50)

        # Create a fresh session for each query (following the article's pattern)
        session_id = f"session_{uuid.uuid4().hex[:8]}"  # Unique session per query
        user_id = "demo_user"

        # Create session right before use
        _ = await session_service.create_session(
            app_name="native_adk_agent_tools", user_id=user_id, session_id=session_id
        )

        # Verify session exists and is valid
        existing_session = await session_service.get_session(
            app_name="native_adk_agent_tools", user_id=user_id, session_id=session_id
        )

        if existing_session is None:
            print(f"Warning: Session {session_id} not found after creation")
            continue

        # Format the query as content
        content = types.Content(role="user", parts=[types.Part(text=query)])
        print("\nStreaming response...")
        response_text = ""
        function_calls = []
        function_responses = []

        # Process events as they stream
        events_async = runner.run_async(
            session_id=session_id, user_id=user_id, new_message=content
        )

        async for event in events_async:
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if part.text:
                        text_chunk = part.text.strip()
                        if text_chunk:
                            print(text_chunk, end=" ", flush=True)
                            response_text += text_chunk + " "
                    elif part.function_call:
                        call_info = {
                            "name": part.function_call.name,
                            "args": part.function_call.args,
                        }
                        function_calls.append(call_info)
                        print(f"\n[Calling {call_info['name']}...]")
                    elif part.function_response:
                        resp_info = {
                            "name": part.function_response.name,
                            "response": part.function_response.response,
                        }
                        function_responses.append(resp_info)
                        print(f"[{resp_info['name']} completed]")

        # Print summary at the end
        print("\n\n" + "-" * 50)

        if function_calls:
            print("\nFunction calls summary:")
            for fc in function_calls:
                print(f"  - {fc['name']}: {fc['args']}")

        if function_responses:
            print("\nFunction responses summary:")
            for fr in function_responses:
                print(f"  - {fr['name']}: {fr['response']}")

        if not response_text.strip():
            print("\nNo text response received")

        print("\n" + "=" * 50)


# If running this file directly, demonstrate local usage
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

    print(f"\n{'=' * 50}")
    print("Local demo completed!")
    print("\nTo run with a custom query:")
    print("  uv run adk_agent.py 'What is the weather in Paris?'")
