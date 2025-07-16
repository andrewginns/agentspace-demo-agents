# Weather Time ADK Agent

An ADK (Agent Development Kit) agent that provides weather and time information for major cities, deployable to Google Cloud Platform's Agent Engine.

## Features

- Get current weather information for supported cities
- Get current time in different time zones
- Supports 10 major cities: New York, London, Tokyo, Paris, Sydney, Los Angeles, Chicago, Singapore, Dubai, and Hong Kong
- Can run locally for testing
- Interactive web interface via `adk web` command
- Deployable to GCP Agent Engine for production use

## Prerequisites

- Python 3.13+
- Google Cloud SDK (`gcloud`) installed and configured
- GCP Project with appropriate permissions
- Vertex AI API enabled in your GCP project
- uv package manager (`pip install uv` or see [installation guide](https://github.com/astral-sh/uv))

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up authentication:
```bash
gcloud auth application-default login
```

3. Configure your environment variables:
```bash
cp .env.example .env
```

## Local Usage

### Interactive Web Interface (Recommended):
```bash
adk web
```
This will start a local web server (typically at http://localhost:8000) with an interactive interface where you can chat with your agent. The agent should appear as "agentspace_demo_agent" in the dropdown.

### Invoke the ADK agent directly:
```bash
uv run agentspace_demo_agent/agents/adk_agent.py
```

### Invoke the ADK agent through vertexai reasoning_engines locally:
```bash
uv run agentspace_demo_agent/invocations/invoke_adk_agent_local.py
```

## Deployment to GCP Agent Engine

### Deploy the agent:
```bash
uv run agentspace_demo_agent/deployments/deploy_adk_agent.py
```

### Invoke the ADK agent through vertexai reasoning_engines remotely:
```bash
uv run agentspace_demo_agent/invocations/invoke_adk_agent_deployed.py --id projects/567858375422/locations/us-central1/reasoningEngines/{deployment_id}
```

## Project Structure

```
agentspace-demo-agent/
├── agentspace_demo_agent/
│   ├── __init__.py
│   ├── agent.py                      # ADK web interface compatibility layer
│   ├── agents/
│   │   └── adk_agent.py              # Main ADK agent implementation
│   ├── deployments/
│   │   └── deploy_adk_agent.py       # Deployment script for GCP Agent Engine
│   └── invocations/
│       ├── invoke_adk_agent_local.py     # Local testing with reasoning engines
│       ├── invoke_adk_agent_deployed.py  # Remote testing with deployed agent
│       └── response_utils.py             # Utility functions for response processing
├── .env.example                      # Environment variables template
├── pyproject.toml                    # Project dependencies and configuration
├── Makefile                          # Build and deployment shortcuts
└── README.md                         # This file
```

## Environment Variables

- `PROJECT_ID` - GCP project ID (default: agentspace)
- `PROJECT_NUMBER` - GCP project number (default: 556507418306)
- `LOCATION` - GCP region (default: us-central1)
- `STAGING_BUCKET` - GCS bucket for deployment staging (default: gs://agentspace-demo)

## ADK Web Interface

The project has been configured to work with the ADK web interface (`adk web` command). This provides an interactive browser-based UI for testing your agent locally before deployment.

**Key Files for ADK Web Compatibility:**
- `agentspace_demo_agent/agent.py` - Exposes the `root_agent` for discovery by the ADK web interface
- `agentspace_demo_agent/__init__.py` - Updated to import the agent module properly

When you run `adk web`, it scans your project directory for agent definitions and automatically creates a web interface where you can interact with your "weather_time_agent".


## Troubleshooting

### Authentication Issues
- Ensure you're logged in: `gcloud auth application-default login`
- Check your project: `gcloud config get-value project`

### Deployment Failures
- Verify Vertex AI API is enabled: `gcloud services list --enabled | grep aiplatform`
- Check IAM permissions for Vertex AI
- Ensure staging bucket exists and is accessible


## Setup Service Account for Reasoning Engines
gcloud beta services identity create --service=aiplatform.googleapis.com --project=agentspace-demo
- service-123456789012@gcp-sa-aiplatform.iam.gserviceaccount.com