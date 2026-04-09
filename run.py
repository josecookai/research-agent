"""
RUNTIME — run for each research task
Usage: python run.py "<topic>" <owner/repo> [branch]
Example: python run.py "AI Agent market 2025" josecookai/research-reports main
"""
import anthropic
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

AGENT_ID     = os.environ["AGENT_ID"]
ENV_ID       = os.environ["ENV_ID"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]       # PAT: Contents Read+Write
VAULT_ID     = os.environ.get("VAULT_ID")       # optional, for GitHub MCP (PR creation)


def run_research(topic: str, repo: str, branch: str = "main"):
    repo_url   = f"https://github.com/{repo}"
    mount_path = "/workspace/repo"
    report_rel = "reports/report.md"
    report_abs = f"{mount_path}/{report_rel}"

    print(f"\n🔍 Topic: {topic}")
    print(f"📦 Repo:  {repo_url}  (branch: {branch})")
    print("─" * 55)

    # 1. Create Session with mounted GitHub repo
    create_kwargs = dict(
        agent=AGENT_ID,
        environment_id=ENV_ID,
        title=f"Research: {topic[:40]}",
        resources=[
            {
                "type": "github_repository",
                "url": repo_url,
                "authorization_token": GITHUB_TOKEN,
                "mount_path": mount_path,
                "checkout": {"type": "branch", "name": branch},
            }
        ],
    )
    if VAULT_ID:
        create_kwargs["vault_ids"] = [VAULT_ID]

    session = client.beta.sessions.create(**create_kwargs)
    print(f"📋 Session: {session.id}\n")

    # 2. Stream events (open stream before sending message)
    with client.beta.sessions.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{
                "type": "user.message",
                "content": [{
                    "type": "text",
                    "text": (
                        f"Please research the following topic and push the report to GitHub:\n\n"
                        f"Topic: {topic}\n"
                        f"Report path: {report_abs}\n"
                        f"Repo path: {mount_path}\n\n"
                        f"After pushing, confirm success and output the commit hash."
                    ),
                }],
            }],
        )

        tool_calls = 0
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text" and block.text.strip():
                        for line in block.text.strip().splitlines()[-5:]:
                            print(f"🤖 {line}")

            elif event.type == "agent.tool_use":
                tool_calls += 1
                name = getattr(event, "tool_name", "unknown")
                inp  = getattr(event, "input", {})
                if name == "web_search":
                    print(f"🔎 Search: {inp.get('query', '')}")
                elif name == "web_fetch":
                    print(f"📄 Fetch:  {inp.get('url', '')[:70]}...")
                elif name == "bash":
                    print(f"💻 bash:   {inp.get('command', '')[:80]}")
                elif name == "write":
                    print(f"✏️  Write:  {inp.get('path', '')}")
                elif name == "create_pull_request":
                    print(f"🔀 PR:     {inp.get('title', '')}")
                else:
                    print(f"🛠  {name}")

            elif event.type == "session.status_idle":
                sr_type = getattr(getattr(event, "stop_reason", None), "type", None)
                if sr_type == "requires_action":
                    continue
                print(f"\n✅ Done! Tool calls: {tool_calls}")
                break

            elif event.type == "session.status_terminated":
                print("\n❌ Session terminated")
                break

    # 3. Archive session
    time.sleep(1)
    client.beta.sessions.archive(session_id=session.id)
    print(f"🗂  Session archived")
    print(f"\n🔗 View report: {repo_url}/blob/{branch}/{report_rel}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run.py <topic> <owner/repo> [branch]")
        print('Example: python run.py "AI Agent market 2025" josecookai/research-reports main')
        sys.exit(1)

    topic  = sys.argv[1]
    repo   = sys.argv[2]
    branch = sys.argv[3] if len(sys.argv) > 3 else "main"
    run_research(topic, repo, branch)
