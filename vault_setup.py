"""
OPTIONAL: only needed if using GitHub MCP tools (e.g., create_pull_request)
Run once, save VAULT_ID to .env

Requires GitHub OAuth tokens obtained via GitHub OAuth App authorization flow.
"""
import anthropic
import os
from dotenv import load_dotenv, set_key

load_dotenv()
client = anthropic.Anthropic()

vault = client.beta.vaults.create(name="github-credentials")

client.beta.vaults.credentials.create(
    vault_id=vault.id,
    display_name="GitHub MCP OAuth",
    auth={
        "type": "mcp_oauth",
        "mcp_server_url": "https://api.githubcopilot.com/mcp/",
        "access_token": os.environ["GITHUB_MCP_ACCESS_TOKEN"],
        "expires_at": os.environ["GITHUB_MCP_EXPIRES_AT"],   # ISO 8601
        "refresh": {
            "refresh_token": os.environ["GITHUB_MCP_REFRESH_TOKEN"],
            "client_id": os.environ["GITHUB_OAUTH_CLIENT_ID"],
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "token_endpoint_auth": {"type": "none"},
        },
    },
)

set_key(".env", "VAULT_ID", vault.id)
print(f"✅ Vault created: {vault.id}")
