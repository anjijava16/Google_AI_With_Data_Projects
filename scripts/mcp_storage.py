import os
from google.adk.integrations.agent_registry import AgentRegistry
from google.auth import default
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

_, project_id = default()
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "agentregistry-00000000-0000-0000-5831-a7128042146e")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
registry = AgentRegistry(project_id=project_id, location=LOCATION)

mcp_toolset = registry.get_mcp_toolset(
    f"projects/project-52e8c95d-822f-4563-a7e/locations/global/mcpServers/agentregistry-00000000-0000-0000-5831-a7128042146e"
)

root_agent = Agent(
        name="sample",
        description=(
            "You are a helpful AI Assistant who can answer questions."
        ),
        model=Gemini(
            model="gemini-3.6-flash",
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        tools=[mcp_toolset],
)