#!/usr/bin/env python3
"""
Deploy ADK Agent to GCP Agent Engine

This script handles the deployment of the weather/time agent to Google Cloud
Agent Engine, allowing it to be accessed as a hosted service.
"""

import os
import sys
import logging
import subprocess
from typing import Optional, List
from dotenv import load_dotenv

from vertexai import agent_engines

# The agentspace_demo_agent directory is included as extra_packages during deployment
# This approach allows us to maintain modular code while ensuring
# Agent Engine can access all necessary modules at runtime
from agentspace_demo_agent.agents.adk_agent import root_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Load environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")


def generate_requirements() -> List[str]:
    """Generate requirements dynamically using uv export.

    This approach has several advantages over hardcoded requirements:
    - Automatically stays in sync with pyproject.toml dependencies
    - Includes all transitive dependencies with correct versions
    - Handles platform-specific requirements (e.g., Windows-only packages)
    - No manual updates needed when adding/updating packages
    - Agent Engine can still resolve version conflicts if needed

    Returns:
        List of requirements strings in pip format.

    Raises:
        subprocess.CalledProcessError: If uv export command fails.
    """
    logger.info("Generating requirements using uv export...")

    try:
        # Run uv export command
        result = subprocess.run(
            [
                "uv",
                "export",
                "--no-hashes",  # Don't include hashes for cleaner output
                "--no-header",  # Skip the header comment
                "--no-dev",  # Exclude development dependencies
                "--no-emit-project",  # Don't include the project itself
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse requirements directly from the output
        requirements = [
            line.strip() for line in result.stdout.splitlines() if line.strip()
        ]

        logger.info(f"Generated {len(requirements)} requirements")
        return requirements

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate requirements: {e}")
        logger.error(f"Error output: {e.stderr}")
        # Fallback to essential requirements if uv export fails
        logger.warning("Falling back to essential requirements...")
        return [
            "google-cloud-aiplatform[adk,agent_engines]==1.95.1",
            "google-adk==1.4.2",
            "vertexai>=1.43.0",
            "cloudpickle==3.1.1",
            "pydantic==2.11.3",
            "pytz>=2024.1",
        ]


def deploy_agent() -> Optional[str]:
    """Deploy the ADK agent to Google Cloud Agent Engine.

    Returns:
        Resource name of the deployed agent or None if deployment failed.

    Raises:
        Exception: If deployment fails for any reason.
    """
    display_name = "Weather Time Agent"
    description = "An ADK agent that provides weather and time information"

    try:
        logger.info("Creating deployment package...")

        # Generate requirements dynamically from pyproject.toml using uv export
        # This ensures requirements stay in sync with project dependencies
        requirements = generate_requirements()

        # Deploy new agent
        logger.info("Deploying agent to Agent Engine...")
        logger.info("This may take several minutes...")

        remote_app = agent_engines.create(
            agent_engine=root_agent,
            requirements=requirements,
            display_name=display_name,
            description=description,
            extra_packages=["./agentspace_demo_agent"],
            # Environment variables can be added if needed
            env_vars={
                "PROJECT_ID": PROJECT_ID,
                "LOCATION": LOCATION,
            },
        )

        resource_name = remote_app.resource_name
        logger.info("Successfully deployed agent!")
        logger.info(f"Resource name: {resource_name}")

        # Extract resource ID for easy reference
        resource_id = resource_name.split("/")[-1]
        logger.info(f"Resource ID: {resource_id}")

        # Test the deployed agent
        logger.info("Testing deployed agent...")
        try:
            test_session = remote_app.create_session(user_id="deployment_test")
            logger.info(f"Created test session: {test_session['id']}")

            # Send a test query
            test_response = []
            for event in remote_app.stream_query(
                user_id="deployment_test",
                session_id=test_session["id"],
                message="What's the weather in New York?",
            ):
                test_response.append(event)

            if test_response:
                logger.info("Test query successful!")
            else:
                logger.warning("Test query returned no response")

        except Exception as e:
            logger.warning(f"Test query failed: {e}")
            logger.info(
                "Agent deployed but test failed - you may need to check permissions"
            )

        return resource_name

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        logger.error("Please check your permissions and configuration")
        return None


def main() -> None:
    """Main deployment function that orchestrates the agent deployment process."""
    logger.info("Starting agent deployment...")
    # Deploy the agent
    resource_name = deploy_agent()
    if resource_name:
        logger.info("\nDeployment successful!")
        logger.info(f"Your agent is now available at: {resource_name}")
        logger.info("\nTo use the deployed agent:")
        logger.info("1. Note the resource name above")
        logger.info("2. Use the agent_engines.get() API to access it")
        logger.info("3. Create sessions and send queries")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
