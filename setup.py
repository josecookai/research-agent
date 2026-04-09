"""
ONE-TIME SETUP — run once, save AGENT_ID and ENV_ID to .env
"""
import anthropic
from dotenv import set_key

client = anthropic.Anthropic()

# 1. Create Environment
print("Creating environment...")
environment = client.beta.environments.create(
    name="research-agent-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)
print(f"Environment ID: {environment.id}")

# 2. Create Agent (with bash + GitHub MCP)
print("Creating agent...")
agent = client.beta.agents.create(
    name="Research Report Agent",
    model="claude-opus-4-6",
    system="""You are a professional research analyst.
Given a research topic and a GitHub repository path, you will:
1. Use web_search and web_fetch to gather the latest information on the topic
2. Synthesize the findings into a structured Markdown report
3. Write the report to the mounted repo directory (default: reports/report.md)
4. Use bash to commit and push:
   git -C <repo_path> add <file>
   git -C <repo_path> commit -m "docs: add research report - <topic>"
   git -C <repo_path> push

Match the report language to the user's language. Be objective and cite sources.""",
    mcp_servers=[
        {
            "type": "url",
            "name": "github",
            "url": "https://api.githubcopilot.com/mcp/",
        }
    ],
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": True},
        },
        {"type": "mcp_toolset", "mcp_server_name": "github"},
    ],
)
print(f"Agent ID: {agent.id}, Version: {agent.version}")

# 3. Save IDs to .env
set_key(".env", "AGENT_ID", agent.id)
set_key(".env", "ENV_ID", environment.id)
print(f"\n✅ Setup complete! IDs saved to .env")
print(f"   AGENT_ID={agent.id}")
print(f"   ENV_ID={environment.id}")
