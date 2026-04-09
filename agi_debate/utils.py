"""
Shared utilities for AGI debate orchestration.
"""
import anthropic
import os
import time
from pathlib import Path

client = anthropic.Anthropic()


def run_session(
    agent_id: str,
    env_id: str,
    message: str,
    label: str = "",
    title: str = "",
    resources: list = None,
    verbose: bool = True,
) -> tuple[str, str]:
    """
    Create a session, send one message, stream events, archive.
    Returns (session_id, collected_text_output).
    """
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        title=title or label,
        resources=resources or [],
    )

    if verbose:
        print(f"\n  [{label}] session={session.id}")

    output_parts: list[str] = []
    tool_count = 0

    with client.beta.sessions.stream(session_id=session.id) as stream:
        # Stream-first: open stream before sending message
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": message}],
            }],
        )

        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text" and block.text.strip():
                        output_parts.append(block.text)
                        if verbose:
                            preview = block.text.replace("\n", " ")[:90]
                            print(f"  [{label}] 💬 {preview}")

            elif event.type == "agent.tool_use":
                tool_count += 1
                name = getattr(event, "tool_name", "")
                inp  = getattr(event, "input", {})
                if verbose:
                    if name == "web_search":
                        print(f"  [{label}] 🔎 {inp.get('query', '')[:60]}")
                    elif name == "web_fetch":
                        print(f"  [{label}] 📄 {inp.get('url', '')[:65]}...")
                    elif name == "write":
                        print(f"  [{label}] ✏️  {inp.get('path', '')}")
                    elif name == "bash":
                        print(f"  [{label}] 💻 {inp.get('command', '')[:65]}")
                    else:
                        print(f"  [{label}] 🛠  {name}")

            elif event.type == "session.status_idle":
                sr = getattr(getattr(event, "stop_reason", None), "type", None)
                if sr != "requires_action":
                    if verbose:
                        print(f"  [{label}] ✅ done ({tool_count} tool calls)")
                    break

            elif event.type == "session.status_terminated":
                if verbose:
                    print(f"  [{label}] ❌ terminated")
                break

    client.beta.sessions.archive(session_id=session.id)
    return session.id, "\n\n".join(output_parts)


def download_session_files(session_id: str, output_dir: str) -> list[str]:
    """Download files written to /mnt/session/outputs/ during a session."""
    time.sleep(3)  # brief indexing lag after session goes idle
    saved = []
    try:
        files = client.beta.files.list(session_id=session_id)
        for f in files.data:
            name = Path(f.filename).name
            if not name or name in (".", ".."):
                continue
            path = os.path.join(output_dir, name)
            content = client.beta.files.download(f.id)
            content.write_to_file(path)
            saved.append(path)
            print(f"  📥 {path}  ({f.size_bytes:,} bytes)")
    except Exception as e:
        print(f"  ⚠️  download error: {e}")
    return saved
