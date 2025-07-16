local_agent:
	uv run agentspace_demo_agent/agents/adk_agent.py

test_local:
	uv run agentspace_demo_agent/invocations/invoke_adk_agent_local.py

adk_web:
	uv run adk web

deploy:
	uv run agentspace_demo_agent/deployments/deploy_adk_agent.py

test_deployed:
	uv run agentspace_demo_agent/invocations/invoke_adk_agent_deployed.py

deploy_to_agentspace:
	uv run agentspace_demo_agent/deployments/deploy_to_agentspace.py