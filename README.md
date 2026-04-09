# Research Agent

An autonomous research agent built with [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview.md).

Given a topic, the agent:
1. Searches the web autonomously (multiple queries)
2. Fetches and reads relevant pages
3. Writes a structured Markdown report
4. Commits and pushes the report to a GitHub repository

## How It Works

Uses the **Anthropic Managed Agents API** — Anthropic hosts the agent loop and a sandboxed container where tools run. The agent autonomously decides when to search, fetch, write, and push.

```
Your Script → Session → Agent Loop (Anthropic) → Container (bash, web_search, git)
                                                       ↓
                                               GitHub Repository
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY and GITHUB_TOKEN
```

`GITHUB_TOKEN` requires a GitHub PAT with **Contents: Read+Write** permission.

### 3. Create the Agent (one-time)

```bash
python setup.py
```

This creates a persistent Agent and Environment on Anthropic's platform and saves their IDs to `.env`.

### 4. (Optional) Set up GitHub MCP for PR creation

```bash
# Set GITHUB_MCP_ACCESS_TOKEN, GITHUB_MCP_REFRESH_TOKEN, etc. in .env first
python vault_setup.py
```

Only needed if you want the agent to create Pull Requests (not just push commits).

## Usage

```bash
python run.py "<research topic>" <owner/repo> [branch]
```

**Examples:**

```bash
# Research a topic and push report to your repo
python run.py "AI Agent market landscape 2025" josecookai/research-reports main

# Chinese topic
python run.py "2025年 Rust vs Go 生态对比" josecookai/research-reports main
```

The report will be saved to `reports/report.md` in the target repository.

## Architecture

| File | Purpose |
|---|---|
| `setup.py` | One-time: create Agent + Environment, save IDs |
| `vault_setup.py` | One-time (optional): store GitHub OAuth for MCP |
| `run.py` | Per-task: create Session, stream events, push report |
| `.env` | API keys and resource IDs |

## Tools Used

| Tool | Purpose |
|---|---|
| `web_search` | Find relevant articles and data |
| `web_fetch` | Read full page content |
| `write` | Save the Markdown report to disk |
| `bash` | Run `git add`, `git commit`, `git push` |
| GitHub MCP `create_pull_request` | (optional) Open a PR |

## Why Managed Agents?

Unlike the standard Messages API, Managed Agents:
- Run the agent loop server-side (no while loop in your code)
- Provision a real container per session (file system, bash, git)
- Handle context compaction and prompt caching automatically
- Support long-running tasks without timeout concerns
