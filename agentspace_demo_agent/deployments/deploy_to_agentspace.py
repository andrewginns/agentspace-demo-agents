#!/usr/bin/env python3
"""
Deploy ADK Agent to Google Agentspace

This script deploys the ADK agent from Agent Engine to Agentspace,
making it available as an assistant in the Agentspace app.
"""

import os
import sys
import json
import logging
import subprocess
from typing import Optional
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Required environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
APP_ID = os.getenv("APP_ID")
ADK_DEPLOYMENT_ID = os.getenv("ADK_DEPLOYMENT_ID")


def get_access_token() -> Optional[str]:
    """Get Google Cloud access token for authentication.
    
    Returns:
        Access token string or None if failed.
    """
    try:
        # Try to get access token using gcloud
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        if token:
            logger.info("Successfully obtained access token")
            return token
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get access token via gcloud: {e}")
    except FileNotFoundError:
        logger.error("gcloud CLI not found. Please install Google Cloud SDK.")
    
    # Alternative: Try using Application Default Credentials
    try:
        import google.auth
        import google.auth.transport.requests
        
        credentials, project = google.auth.default()
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        
        if credentials.token:
            logger.info("Successfully obtained access token via ADC")
            return credentials.token
    except Exception as e:
        logger.error(f"Failed to get access token via ADC: {e}")
    
    return None


def deploy_to_agentspace(
    project_id: str,
    app_id: str,
    adk_deployment_id: str,
    adk_location: str = "europe-west1"
) -> bool:
    """Deploy the ADK agent to Agentspace.
    
    Args:
        project_id: Google Cloud project ID
        app_id: Agentspace app ID
        adk_deployment_id: ADK deployment ID from Agent Engine
        adk_location: Location of the ADK deployment
        
    Returns:
        True if deployment successful, False otherwise.
    """
    # Get access token
    access_token = get_access_token()
    if not access_token:
        logger.error("Unable to obtain access token. Cannot proceed with deployment.")
        return False
    
    # Construct the API endpoint
    # Note: Using EU endpoint since the app is in EU location
    base_url = "https://eu-discoveryengine.googleapis.com"
    endpoint = (
        f"{base_url}/v1alpha/projects/{project_id}/locations/eu/"
        f"collections/default_collection/engines/{app_id}/"
        f"assistants/default_assistant/agents"
    )
    
    # Prepare the request payload
    payload = {
        "displayName": "Weather Time Agent",
        "description": "An ADK agent that provides weather and time information for major cities",
        "icon": {
            "uri": "https://fonts.gstatic.com/s/i/materialicons/wb_sunny/v1/24px.svg"
        },
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": (
                    "This agent provides weather and time information for 10 major cities: "
                    "New York, London, Tokyo, Paris, Sydney, Los Angeles, Chicago, Singapore, "
                    "Dubai, and Hong Kong"
                )
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": (
                    f"projects/{project_id}/locations/{adk_location}/"
                    f"reasoningEngines/{adk_deployment_id}"
                )
            }
        }
    }
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id
    }
    
    # Log the deployment details
    logger.info("Deploying agent to Agentspace...")
    logger.info(f"Project ID: {project_id}")
    logger.info(f"App ID: {app_id}")
    logger.info(f"ADK Deployment ID: {adk_deployment_id}")
    logger.info(f"ADK Location: {adk_location}")
    logger.info(f"Endpoint: {endpoint}")
    
    try:
        # Make the API request
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Check response
        if response.status_code == 200 or response.status_code == 201:
            logger.info("✓ Successfully deployed agent to Agentspace!")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Extract agent details from response
            agent_data = response.json()
            if "name" in agent_data:
                logger.info(f"Agent resource name: {agent_data['name']}")
            
            return True
        else:
            logger.error(f"✗ Deployment failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            
            # Provide helpful error messages
            if response.status_code == 404:
                logger.error("The app or endpoint was not found. Please check:")
                logger.error(f"- App ID is correct: {app_id}")
                logger.error(f"- The app exists in project: {project_id}")
                logger.error("- The app is in the EU location")
            elif response.status_code == 403:
                logger.error("Permission denied. Please check:")
                logger.error("- You have the necessary IAM roles (Discovery Engine Admin)")
                logger.error("- The project has the Discovery Engine API enabled")
            elif response.status_code == 400:
                logger.error("Bad request. Please check:")
                logger.error("- The ADK deployment exists and is accessible")
                logger.error("- The payload format is correct")
                
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request timed out. The deployment might still be in progress.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Main function to deploy the agent."""
    logger.info("Starting Agentspace deployment...")
    logger.info("=" * 60)
    
    # Display configuration
    logger.info("Configuration:")
    logger.info(f"  PROJECT_ID: {PROJECT_ID}")
    logger.info(f"  APP_ID: {APP_ID}")
    logger.info(f"  ADK_DEPLOYMENT_ID: {ADK_DEPLOYMENT_ID}")
    logger.info(f"  ADK_LOCATION: {LOCATION}")
    logger.info("=" * 60)
    
    # Deploy the agent
    success = deploy_to_agentspace(
        project_id=PROJECT_ID,
        app_id=APP_ID,
        adk_deployment_id=ADK_DEPLOYMENT_ID,
        adk_location=LOCATION
    )
    
    if success:
        logger.info("\n✓ Deployment completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Go to the Agentspace console to verify the deployment")
        logger.info(f"2. Test the agent at: https://console.cloud.google.com/gen-app-builder/locations/eu/engines/{APP_ID}")
        logger.info("3. Configure any additional settings as needed")
    else:
        logger.error("\n✗ Deployment failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
